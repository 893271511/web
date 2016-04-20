#ssh_cmd.py
#coding:utf-8

import os
os.system('export PATH="/usr/kerberos/bin:$PATH" &>/dev/null')
os.system('export KRB5CCNAME=/tmp/krb5cc_pub_$$ &>/dev/null')
os.system('trap kdestroy 0 1 2 3 5 15 &>/dev/null')
os.system('kinit -k -t /etc/krb5.keytab &>/dev/null')
os.system('klist')
import pexpect
ssh = pexpect.spawn('ssh root@10.2.52.13 "ls -l"')
print(ssh.read().decode())
ssh.close()

