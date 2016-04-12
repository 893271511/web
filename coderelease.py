#!/usr/bin/python
#coding:utf-8
#脚本使用例：python coderelease.py renren-licai-credit-manager 31614 test 10.2.54.240
import sys,os
print(sys.path)
from release.models import *
print("脚本名：" + sys.argv[0])
print("项目名：" + sys.argv[1])
print("版本号：" + sys.argv[2])
print("环  境：" + sys.argv[3])
print("服务器：" + sys.argv[4])

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
    
def check_env():
    pass

script_path = sys.path[0]
conf_dir = script_path + "/conf"
logs_dir = script_path + "/logs"
path = Project.objects.filter(name='renren-licai').values()

name = path[0]['name']
repos = path[0]['repos']
start_cmd = path[0]['start_cmd']
stop_cmd = path[0]['stop_cmd']
target = path[0]['target']
port = path[0]['port']


