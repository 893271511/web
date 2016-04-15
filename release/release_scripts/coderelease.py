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
        global conf_dir,svn_path,repos,start_cmd,stop_cmd,target,port,SVN
        script_path = sys.path[0]
        conf_dir = script_path + "/conf"
        jar_pkg=script_path + "/conf/xiaonei-split-version.jar"
        SVN="svn"
        svn_path = '/data/staging/new_renren'
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
    if int(status) != 0 or int(output) != 1:
        logger.error('此项目正在发布中，请稍后再试！')
        quit()


def svn_update():
    if not os.path.exists('%s/%s/.svn' %(svn_path,project_name)):
        status = subprocess.getoutput('svn co %s %s/%s' %(repos,svn_path,project_name))
        if status == 0:
            logger.info("svn checkout 成功")
        else:
            logger.error("svn checkout 失败")
            exit_script()
    else:
        logger.info('%s 码已存在，无须checkout！' % project_name)

    status,output = subprocess.getstatusoutput('svn up -r %s %s/%s' %(ver,svn_path,project_name))
    if int(status) == 0:
        logger.info('svn up 成功')
    else:
        logger.error('svn up 失败')
        exit_script()


def maven_project():
    os.popen('rm -rf %s/%s/target' %(svn_path,project_name))
    status,output = subprocess.getstatusoutput('cd %s/%s && test ! -d %s/%s/target && mvn -e -f pom.xml -U clean package' %(svn_path,project_name,svn_path,project_name))
    if status == '0':
        logger.info('编译成功')
        logger.info(output)
    else:
        logger.error('编译失败')
        logger.error(output)
        exit_script()


check_script_para()
set_env()
check_run_env()
svn_update()
maven_project()