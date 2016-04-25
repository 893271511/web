#!/root/.pyenv/versions/3.4.1/bin/python
#coding:utf-8
#脚本使用例：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240
import sys,os,sqlite3
import subprocess
import logging
import shutil,time,datetime
import pexpect,paramiko,re,urllib.request


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
#logg.addHandler(console_handler)
now = datetime.datetime.now()
timestamp = now.strftime('%Y-%m-%d-%H-%M-%S')
print(timestamp)


class log():
    def info(slef,info):
        print(info)
        logger.info(info)

    def error(slef,info):
        print(info)
        logger.error(info)

logg = log()



def exit_script():
    logg.error('脚本异常退出')
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

        if env == 'test':
            select_sql = '''select release_host.ip
                    from release_project,release_project_test_env,release_host
                    where release_project.id=release_project_test_env.project_id
                    and release_project_test_env.host_id=release_host.id
                    and release_project.name="%s"''' % project_name
        else:
            select_sql = '''select release_host.ip
                    from release_project,release_project_production_env,release_host
                    where release_project.id=release_project_production_env.project_id
                    and release_project_production_env.host_id=release_host.id
                    and release_project.name="%s"''' % project_name
        cu.execute(select_sql)
        SERVERS = cu.fetchall()

        select_sql = '''select release_host.ip
                from release_project,release_project_proxys,release_host
                where release_project.id=release_project_proxys.project_id
                and release_project_proxys.host_id=release_host.id
                and release_project.name="%s"''' % project_name
        cu.execute(select_sql)
        PROXYS = cu.fetchall()

        cu.execute('select * from release_project WHERE name = "%s"' % project_name)
        global project_attribute
        project_attribute = cu.fetchall()
        cu.close()

        global proxys
        proxys=[]
        for i in PROXYS:
            proxys.append(i[0])

        #检查参数合法性
        projects = []
        for i in PROJECTS:
            projects.append(i[0])
        if project_name not in projects:
            print("此项目不存在")
            quit()

        if not str.isdigit(ver):
            print("版本号应该为数字")
            quit()

        if env not in ['test','production']:
            print("此环境不存")
            quit()

        global servers
        servers=[]
        for i in SERVERS:
            servers.append(i[0])
        if server == 'all' or server in servers:
            pass
        else:
            print("不允许发向此IP")
            quit()

        if server != 'all':servers = [server]

        #脚本变量
        global conf_dir,svn_path,repos,start_cmd,stop_cmd,target,port,SVN,nginx_conf
        global static_path,static_repos,static_deploy_path,jar_dir,desc,need_inc,project_bak
        project_bak = '/data/project_bak'
        nginx_conf = '/data/web/nginx/conf/nginx.conf'
        if not os.path.exists(project_bak):os.makedirs(project_bak)
        need_inc = ''
        static_path="/data/staging/new_renren/static"
        static_repos="http://svn.fenqi.d.xiaonei.com/frontend/xn.static"
        static_deploy_path="/data/static"
        script_path = sys.path[0]
        conf_dir = script_path + "/conf"
        jar_dir=script_path + "/jar"
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
                logg.error(i + " 值不能为空")

    else:
        print("参数错误")
        print("用法：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240")
        quit()


#设置环境
def set_env():
    #kerberos
    os.system('export PATH="/usr/kerberos/bin:$PATH" &>/dev/null')
    os.system('export KRB5CCNAME=/tmp/krb5cc_pub_$$ &>/dev/null')
    os.system('trap kdestroy 0 1 2 3 5 15 &>/dev/null')
    os.system('kinit -k -t /etc/krb5.keytab &>/dev/null')
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
        print('此项目正在发布中，请稍后再试！')
        quit()


def svn_update():
    logg.info('开始更新代码')
    if not os.path.exists('%s/%s/.svn' %(svn_path,project_name)):
        status,output = subprocess.getstatusoutput('svn co %s %s/%s' %(repos,svn_path,project_name))
    else:
        status,output = subprocess.getstatusoutput('svn up -r %s %s/%s' %(ver,svn_path,project_name))
    if status == 0:
        logg.info('----svn update 成功')
    else:
        logg.error(output)
        logg.error('----svn update 失败')
        exit_script()

    if os.path.exists(need_inc):
        if not os.path.exists('%s/%s/src/main/webapp/inc/.svn/'):
            shell_cmd = '%s co http://svn/fenqi.d.xiaonei.com/fronted/xn.inc %s/%s/src/main/webapp/inc' %(SVN,svn_path,project_name)
        else:
            shell_cmd = '%s up %s/%s/src/main/webapp/inc' %(SVN,svn_path,project_name)

        status,output = subprocess.getstatusoutput(shell_cmd)
        if status == 0:
            logg.info('----update common inc 成功')
        else:
            logg.error(output)
            logg.error('----update common inc 失败')
            exit_script()
    else:
        logg.info("----不需要处理common inc")
    logg.info("结束更新代码 \n")



def maven_project():
    logg.info('开始编译代码')
    os.system('rm -rf %s/%s/target' %(svn_path,project_name))
    shell_cmd = 'cd %s/%s && mvn -e -f pom.xml -U clean package' %(svn_path,project_name)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logg.info('----编译成功')
    else:
        logg.error(output)
        logg.error('----编译失败')
        exit_script()
    logg.info("结束编译代码 \n")



def ams_unzip():
    os.system('rm -rf %s/%s/target/renren-fenqi-ams' %(svn_path,project_name))
    shell_cmd = 'unzip %s/%s/target/ams.zip -d %s/%s/target/ams_%s' %(svn_path,project_name,svn_path,project_name,ver)
    if not os.path.exists('%s/%s/target/renren-fenqi-ams' %(svn_path,project_name)):
        status,output = subprocess.getstatusoutput(shell_cmd)
        if status == 0:
            logg.info("----解压成功")
        else:
            logg.error(output)
            logg.error("----解压失败")
            exit_script()
    else:
        logg.error('%s/%s/target/renren-fenqi-ams 删除失败' %(svn_path,project_name))
        exit_script()

def update_static():
    logg.info('开始更新静态文件')
    if not os.path.exists('%s/.svn/' % static_path):
        shell_cmd = '%s co %s %s' %(SVN,static_repos,static_path)
    else:
        shell_cmd = '%s up %s' %(SVN,static_path)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logg.info('----static svn update 成功')
    else:
        logg.error(output)
        logg.error('----static svn update 失败')
        exit_script()
    logg.info("结束更新静态文件 \n")


def replace_static():
    logg.info('开始处理静态文件')
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
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logg.info('----replace static 成功')
    else:
        logg.error(output)
        logg.error('----replace static 失败')
        exit_script()
    logg.info("结束处理静态文件 \n")


def ams_config():
    ams_unzip()
    project_war = '%s/%s/target/%s' %(svn_path,project_name,project_name)
    project_war_ver = '%s/%s/target/%s_%s' %(svn_path,project_name,project_name,ver)
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
                logg.error("项目的web.xml配置文件修改错误：%s" %web_xml)
                exit_script()

            if i == '28080':
                ii = 29080
            elif i == '29080':
                ii == 28080
            os.system("sed -i -r 's/(property name=\"port\" value=\")%s/\1%s/g' %s" %(ii,i,applicationContext_xml))
            status,output = subprocess.getstatusoutput('grep -E "name=\"port\" *value=\"%s\"" %s' %(i,applicationContext_xml))
            if status != 0:
                logg.error("项目的配置文件修改错误：%s" %applicationContext_xml)
                exit_script()


def config():
    logg.info("开始配置项目")
    project_war = '%s/%s/target/%s' %(svn_path,project_name,project_name)
    project_war_ver = '%s/%s/target/%s_%s' %(svn_path,project_name,project_name,ver)
    os.system('rm -rf %s' %project_war_ver)
    #if os.path.exists(project_war_ver):shutil.rmtree(project_war_ver)
    try:
        shutil.move(project_war,project_war_ver)
        os.system('echo %s >%s/WEB-INF/classes/version.txt' %(ver,project_war_ver))
    except Exception as e:
        logg.error(e)
        exit_script()

    project_war_ver_xml_file = '%s/WEB-INF/classes/applicationContext_test.xml' %project_war_ver
    if not os.path.exists(project_war_ver_xml_file):
        logg.error('没有发现applicationContext_test.xml配置文件，请添加！')
        exit_script()

    for i in ['test','production']:
        try:
            shutil.copytree(project_war_ver,'%s_%s' %(project_war_ver,i))
        except Exception as e:
            logg.error(e)
            exit_script()

        project_war_ver_env_xml_file = '%s_%s/WEB-INF/classes/applicationContext_test.xml' %(project_war_ver,i)

        if i == 'production':
            os.remove(project_war_ver_env_xml_file)
            if os.path.exists(project_war_ver_env_xml_file):
                logg.error('生产环境项目发现applicationContext_test.xml配置文件，请检查')
                exit_script()
        else:
            if not os.path.exists(project_war_ver_env_xml_file):
                logg.error('测试环境项目没有发现applicationContext_test.xml配置文件，请检查')
                exit_script()

        os.system('rm -rf %s/%s_%s_%s' %(project_bak,project_name,ver,i))
        time.sleep(3)
        if os.path.exists('%s/%s_%s_%s' %(project_bak,project_name,ver,i)):
            logg.error('%s/%s_%s_%s 删除失败，请检查原因' %(project_bak,project_name,ver,i))
            exit_script()
        else:
            try:
                shutil.move('%s_%s' %(project_war_ver,i), '%s/%s_%s_%s' %(project_bak,project_name,ver,i))
            except Exception as e:
                logg.error(e)
                exit_script()

    logg.info("结束配置项目 \n")

def api(host,port):
    #response = urllib.request.urlopen('http://%s:%s/api/system/check' %(host,port),timeout=10)
    response = urllib.request.urlopen('http://10.4.30.145:9000/api/system/check',timeout=10)
    s = '"flag":true'
    html = response.read().decode()
    if s in html:
        return True
    else:
        return False


def nginx_reload(proxy,host):
    shell_cmd = 'ssh %s "/data/web/nginx/sbin/nginx -s reload"' %(proxy)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logg.info("proxy %s nginx reload 成功" %(proxy))
    else:
        logg.error("proxy %s nginx reload 失败，请检查" %(proxy))
        logg.error(output)
        exit_script()

def resin_offline(proxy,host):
    '''real server offline'''
    shell_cmd = 'ssh %s "cp -f %s /tmp/nginx.conf.%s"' %(proxy,nginx_conf,timestamp)
    os.popen(shell_cmd)
    shell_cmd = 'ssh %s \"sed -i -r \'s/(^[ \t]*server[ \t]*%s:%s.*)(;.*$)/\\1 down\\2/g\' %s\"' %(proxy,host,port,nginx_conf)
    os.popen(shell_cmd)
    time.sleep(5)
    shell_cmd = 'ssh %s \'grep -E \"^[ \\t]*[ \\t]*server[ \\t]*[ \\t]*%s:%s.*down;\" %s\'' %(proxy,host,port,nginx_conf)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logg.info("%s nginx配置中%s已标记为down" %(proxy,host))
        logg.info(output)
    else:
        logg.error("%s nginx配置中%s未发现标记为down，请检查" %(proxy,host))
        logg.error(output)
        exit_script()
    nginx_reload(proxy,host)



def resin_online(proxy,host):
    '''real server online'''
    shell_cmd = 'ssh %s "cp -f %s /tmp/nginx.conf.%s"' %(proxy,nginx_conf,timestamp)
    os.popen(shell_cmd)
    shell_cmd = 'ssh %s \"sed -i \'/^[ \t]*[ \t]*server[ ]*[ \t]*%s:%s.* down;.*$/s/ *down//g\' %s\"' %(proxy,host,port,nginx_conf)
    os.popen(shell_cmd)
    time.sleep(5)
    shell_cmd = 'ssh %s \'grep -E \"^[ \t]*[ \t]*server[ \t]*[ \t]*%s:%s;\" %s\'' %(proxy,host,port,nginx_conf)
    status,output = subprocess.getstatusoutput(shell_cmd)
    if status == 0:
        logg.info("%s nginx配置中%s已取消down" %(proxy,host))
        logg.info(output)
    else:
        logg.error("%s nginx配置中%s仍标记为down，请检查" %(proxy,host))
        logg.error(output)
        exit_script()
    nginx_reload(proxy,host)


def deploy():
    i = 0
    count = len(servers)
    for host in servers:
        i = i + 1
        logg.info("共%s台，第%s台：%s" %(count,i ,host))
        shell_cmd1 = 'ssh %s "test ! -e %s && mkdir -pv %s; rm -rf %s/%s_%s_%s"' %(host,project_bak,project_bak,project_bak,project_name,ver,env)
        subprocess.getstatusoutput(shell_cmd1)
        shell_cmd2 = 'rsync -acRztrvl --delete %s/%s_%s_%s %s:/' %(project_bak,project_name,ver,env,host)
        status2,output2 = subprocess.getstatusoutput(shell_cmd2)
        if status2 == 0:
            logg.info('同步项目成功')
        else:
            logg.error(output2)
            logg.error('同步项目失败，请检查')
            exit_script()
        if env == "production":
            if api(host,port):
                logg.info("api调用成功")
            else:
                logg.error("api调用失败，请检查")
                exit_script()



            shell_cmd3 = 'rsync -acztrvl --delete %s:%s/%s %s/%s/' %(host,target,project_name,project_bak,host)
            status3,output3 = subprocess.getstatusoutput(shell_cmd3)
            if status3 == 0:
                logg.info('备份项目成功')
            else:
                logg.error(output2)
                logg.error('备份项目失败，请检查')
                exit_script()

            for proxy in proxys:
                resin_offline(proxy,host)

            key = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_system_host_keys()
            ssh.connect(hostname=host,username='root',pkey=key,timeout=10)
            cmd = 'sh %s' %stop_cmd
            stdin,stdout,stderr=ssh.exec_command(cmd)
            time.sleep(5)
            cmd = 'netstat -antlp |grep LIST |grep :%s' %port
            stdin,stdout,stderr = ssh.exec_command(cmd)
            stdout = stdout.read().decode()
            p = re.compile('^tcp.*java')
            if p.match(stdout) != None:
                PID = stdout.split()[6].split('/')[0]
                print(PID)
                if str.isdigit(PID):
                    stdin,stdout,stderr = ssh.exec_command("cat /proc/%s/status" %PID)
                    stdout = stdout.read().decode()
                    for line in stdout.split('\n'):
                        if line.startswith('PPid:'):
                            print(line)
                            PPID = line.split()[1]
                            print(type(PPID))
                            if PPID != '0' and PPID != '1':
                                cmd = '/bin/kill -9 %s %s' %(PID,PPID)
                                logg.info(cmd)
                                stdin,stdout,stderr = ssh.exec_command(cmd)
                            else:
                                cmd = '/bin/kill -9 %s' %(PID)
                                logg.info(cmd)
                                stdin,stdout,stderr = ssh.exec_command(cmd)
                else:
                    logg.error("pid获取错误，请检查")
                    exit_script()
            else:
                logg.info("resin 停止成功")

            cmd = 'mv %s/%s %s/%s_%s' %(target,project_name,project_bak,project_name,timestamp)
            stdin,stdout,stderr = ssh.exec_command(cmd)
            cmd = 'rm -rf %s/%s' %(target,project_name)
            stdin,stdout,stderr = ssh.exec_command(cmd)

            cmd = 'mv %s/%s_%s_%s %s/%s' %(project_bak,project_name,ver,env,target,project_name)
            stdin,stdout,stderr = ssh.exec_command(cmd)
            stderr = stderr.read().decode()
            if stderr == ""  or stderr == None:
                logg.info('替换项目完成')
            else:
                logg.error('替换项目失败，请检查')
                exit_script()

            cmd = 'sh %s' %start_cmd
            stdin,stdout,stderr=ssh.exec_command(cmd)
            time.sleep(5)

            cmd = 'netstat -antlp |grep LIST |grep :%s' %port
            stdin,stdout,stderr = ssh.exec_command(cmd)
            stdout = stdout.read().decode()
            p = re.compile('^tcp.*java')
            if p.match(stdout) != None:
                logg.info("resin port 监听")
            else:
                logg.error("resin port 未监听，请检查")
                exit_script()

            if api(host,port):
                logg.info("api调用成功")
            else:
                logg.error("api调用失败，请检查")
                exit_script()

            ssh.close()

            for proxy in proxys:
                resin_online(proxy,host)

check_script_para()
set_env()
check_run_env()
#svn_update()
#maven_project()
#update_static()
#replace_static()
#config()
deploy()


