#!/usr/bin/python
#coding:utf-8
#脚本使用例：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240
import sys,os,sqlite3
import subprocess
import logging


#日志配置
script_name=sys.argv[0]
log_file = script_name + ".log"
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def exit_script():
    logging.error('脚本异常退出')
    quit()

#检查脚本参数合法性及
def check_script_para():
    if len(sys.argv) == 5:
        #脚本参数
        global project_name,ver,env,server
        project_name = sys.argv[1]
        ver = sys.argv[2]
        env = sys.argv[3]
        server = sys.argv[4]

        #连库查询
        conn = sqlite3.connect('%s/../../db.sqlite3' % sys.path[0])
        cu = conn.cursor()
        cu.execute('select name FROM release_project')
        PROJECTS = cu.fetchall()

        select_sql = '''select release_host.ip
                from release_project,release_project_test_env,release_host
                where release_project.id=release_project_test_env.project_id
                and release_project_test_env.host_id=release_host.id
                and release_project.name="%s"''' % project_name
        cu.execute(select_sql)
        SERVERS = cu.fetchall()

        cu.execute('select * from release_project WHERE name = "%s"' % project_name)
        global project_attribute
        project_attribute = cu.fetchall()
        cu.close()

        #检查参数合法性
        projects = []
        for i in PROJECTS:
            projects.append(i[0])
        if project_name not in projects:
            logger.error("此项目不存在")
            quit()

        if not str.isdigit(ver):
            logger.error("版本号应该为数字")
            quit()

        if env not in ['test','production']:
            logger.error("此环境不存")
            quit()
            
        servers=[]
        for i in SERVERS:
            servers.append(i[0])
        if server == 'all' or server in servers:
            pass
        else:
            logger.error("不允许发向此IP")
            quit()

        #脚本变量
        global conf_dir,svn_path,repos,start_cmd,stop_cmd,target,port,SVN,project_war,maven_target
        global static_path,static_repos,static_deploy_path,jar_dir,desc,need_inc,project_war_ver
        need_inc = ''
        static_path="/data/staging/new_renren/static"
        static_repos="http://svn.fenqi.d.xiaonei.com/frontend/xn.static"
        static_deploy_path="/data/static"

        script_path = sys.path[0]
        conf_dir = script_path + "/conf"
        jar_dir=script_path + "/jar"
        SVN="svn"
        svn_path = '/data/staging/new_renren'
        project_war = '%s/%s/target/%s' %(svn_path,project_name,project_name)
        project_war_ver = '%s/%s/target/%s_%s' %(svn_path,project_name,project_name,ver)
        maven_target = '%s/%s/target' %(svn_path,project_name)
        start_cmd = project_attribute[0][2]
        stop_cmd = project_attribute[0][3]
        target = project_attribute[0][4]
        repos = project_attribute[0][5]
        desc = project_attribute[0][6]
        port = project_attribute[0][7]
        for i in ['svn_path','start_cmd','stop_cmd','target','repos','port']:
            if eval(i) == '' or eval(i) == None:
                logger.error(i + " 值不能为空")

    else:
        logger.error("参数错误")
        logger.error("用法：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240")
        quit()


#设置环境
def set_env():
    #kerberos
    os.system('export PATH="/usr/kerberos/bin:$PATH"')
    os.system('export KRB5CCNAME=/tmp/krb5cc_pub_$$')
    os.system('trap kdestroy 0 1 2 3 5 15')
    os.system('kinit -k -t /etc/krb5.keytab')
    #lanage
    os.system('export LANG="en_US.UTF-8"')
    os.system('export LC_ALL="en_US.utf8"')
    os.system('export LC_LANG="en_US.utf8"')
    #java_home
    os.system('export JAVA_HOME=/usr/java/jdk')
    os.system('export CLASS_PATH=.:$JAVA_HOME/lib')
    os.system('export PATH=$JAVA_HOME/bin:$PATH')
    #maven
    os.system('export M2_HOME=/usr/local/maven-2.1.0')
    os.system('export M2=$M2_HOME/bin')
    os.system('export MAVEN_OPTS=-Dfile.encoding=utf-8')
    os.system('export PATH=$PATH:$M2')




#检查项目运行环境，是否正在发布
def check_run_env():
    status,output = subprocess.getstatusoutput('ps -ef | grep -v grep | grep "%s %s" | wc -l' %(script_name,project_name))
    if status != 0 or int(output) != 1:
        logger.error('此项目正在发布中，请稍后再试！')
        quit()


def svn_update():
    logger.info('开始更新代码')
    if not os.path.exists('%s/%s/.svn' %(svn_path,project_name)):
        status,output = subprocess.getstatusoutput('svn co %s %s/%s' %(repos,svn_path,project_name))
    else:
        status,output = subprocess.getstatusoutput('svn up -r %s %s/%s' %(ver,svn_path,project_name))
    if status == 0:
        logger.info('----svn update 成功')
    else:
        logger.error(output)
        logger.error('----svn update 失败')
        exit_script()

    if os.path.exists(need_inc):
        if not os.path.exists('%s/%s/src/main/webapp/inc/.svn/'):
            shell_cmd = '%s co http://svn/fenqi.d.xiaonei.com/fronted/xn.inc %s/%s/src/main/webapp/inc' %(SVN,svn_path,project_name)
        else:
            shell_cmd = '%s up %s/%s/src/main/webapp/inc' %(SVN,svn_path,project_name)

        status,output = subprocess.getstatusoutput(shell_cmd)
        if status == 0:
            logger.info('----update common inc 成功')
        else:
            logger.error(output)
            logger.error('----update common inc 失败')
            exit_script()
    else:
        logger.info("----不需要处理common inc")


def maven_project():
    logger.info('开始编译代码')
    os.system('rm -rf %s/%s/target' %(svn_path,project_name))
    shell_cmd = 'cd %s/%s && mvn -e -f pom.xml -U clean package' %(svn_path,project_name)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logger.info('----编译成功')
    else:
        logger.error(output)
        logger.error('----编译失败')
        exit_script()



def ams_unzip():
    os.system('rm -rf %s/%s/target/renren-fenqi-ams' %(svn_path,project_name))
    shell_cmd = 'unzip %s/%s/target/ams.zip -d %s/%s/target/ams_%s' %(svn_path,project_name,svn_path,project_name,ver)
    if not os.path.exists('%s/%s/target/renren-fenqi-ams' %(svn_path,project_name)):
        status,output = subprocess.getstatusoutput(shell_cmd)
        if status == 0:
            logger.info("----解压成功")
        else:
            logger.error(output)
            logger.error("----解压失败")
            exit_script()
    else:
        logger.error('%s/%s/target/renren-fenqi-ams 删除失败' %(svn_path,project_name))
        exit_script()

def update_static():
    logger.info('开始更新静态文件')
    if not os.path.exists('%s/.svn/' % static_path):
        shell_cmd = '%s co %s %s' %(SVN,static_repos,static_path)
    else:
        shell_cmd = '%s up %s' %(SVN,static_path)
    print(shell_cmd)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logger.info('----static svn update 成功')
    else:
        logger.error(output)
        logger.error('----static svn update 失败')
        exit_script()


def replace_static():
    logger.info('开始处理静态文件')
    if not os.path.exists(static_deploy_path):
        os.makedirs(static_deploy_path)

    if project_name == 'ren-licai' or project_name == "renren-licai-mobile-server":
        jar_name = 'renren-split-version-licai2.jar'
    else:
        jar_name = 'xiaonei-split-version.jar'

    jar = '%s/%s' %(jar_dir,jar_name)
    project_path = '%s/%s/target/%s' %(svn_path,project_name,project_name)
    #java -cp ${script_path}/jar/renren-split-version-licai2.jar -Ddebug=true com/xiaonei/deploy/tools/Worker $static_path $static_deploy_path $proj_target
    shell_cmd = 'java -cp %s -Debug=true com/xiaonei/deploy/tools/Worker %s %s %s' %(jar,static_path,static_deploy_path,project_path)
    print(shell_cmd)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logger.info('----replace static 成功')
    else:
        logger.error(output)
        logger.error('----replace static 失败')
        exit_script()


def ams_config():
    ams_unzip()
    os.system('cp -Rf %s %s_%s' %(project_war,project_war,ver))
    for i in ['28080','29080']:
        for j in ['test','production']:
            project_war_ver_env_port = '%s_%s_%s_%s' %(project_war,ver,j,i)
            web_xml = '%s/WEB-INF/web.xml' %(project_war_ver_env_port)
            applicationContext_xml = '%s/WEB-INF/classes/applicationContext.xml' %project_war_ver_env_port
            os.system('cp -Rf %s %s' %(project_war_ver,project_war_ver_env_port))
            os.system("sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1%s\3/g' %s" %(j,web_xml))
            status,output = subprocess.getstatusoutput('grep -E "<param-value>%s</param-value>" %s' %(j,web_xml))
            if status != 0:
                logger.error("项目的配置文件修改错误")
                exit_script()

            if i == '28080':
                ii = 29080
            elif i == '29080':
                ii == 28080
            os.system("sed -i -r 's/(property name=\"port\" value=\")%s/\1%s/g' %s" %(ii,i,applicationContext_xml))
            status,output = subprocess.getstatusoutput('grep -E "name=\"port\" *value=\"%s\"" %s' %(i,applicationContext_xml))
            if status != 0:
                logger.error("项目的配置文件修改错误")
                exit_script()


    # shell_cmd = 'cp -Rf %s %s_%s' %(project_war,project_war,ver)
    # status,output = subprocess.getstatusoutput(shell_cmd)
    # if status == 0:
    #     pass
    # else:
    #     logger.error("复制项目失败")
    #     exit_script()




check_script_para()
set_env()
check_run_env()
svn_update()
maven_project()
update_static()
replace_static()

