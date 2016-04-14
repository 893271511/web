#!/usr/bin/python
#coding:utf-8
#脚本使用例：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240
import sys,os,sqlite3

import subprocess
status,output = subprocess.getstatusoutput('ls')
print(status)
print(output)



#检查项目运行环境，是否正在发布
def check_run_env():
    pass



#检查脚本参数合法性
def check_script_para():
    if len(sys.argv) == 5:
        #脚本参数
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
            
        servers=[]
        for i in SERVERS:
            servers.append(i[0])
        if server == 'all' or server in servers:
            pass
        else:
            print("不允许发向此IP")
            quit()
    else:
        print("参数错误")
        print("用法：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240")
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
    global script_path,conf_dir,logs_dir
    global script_name,project_name,ver,env,server
    global path,name,repos,start_cmd,stop_cmd,target,port

    #脚本变量
    script_name=sys.argv[0]
    script_path = sys.path[0]
    conf_dir = script_path + "/conf"
    logs_dir = script_path + "/logs"
    jar_pkg=script_path + "/conf/xiaonei-split-version.jar"
    log_file=logs_dir + script_name + ".log"
    SVN="svn"
    path = '/data/staging/new_renren'
    start_cmd = project_attribute[0][2]
    stop_cmd = project_attribute[0][3]
    target = project_attribute[0][4]
    repos = project_attribute[0][5]
    desc = project_attribute[0][6]
    port = project_attribute[0][7]




check_script_para()
set_env()
