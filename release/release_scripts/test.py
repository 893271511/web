#!/usr/bin/python
import os


os.system('klist')


os.system('export PATH="/usr/kerberos/bin:$PATH" &>/dev/null')
os.system('export KRB5CCNAME=/tmp/krb5cc_pub_$$ &>/dev/null')
os.system('trap kdestroy 0 1 2 3 5 15 &>/dev/null')
os.system('kinit -k -t /etc/krb5.keytab &>/dev/null')

print('----------------')

os.system('klist')



import os,time
import paramiko


key = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(hostname='10.2.52.13',username='root',pkey=key,timeout=10)
stdin,stdout,stderr=ssh.exec_command('hostname')




stdout = stdout.readlines()
stderr = stderr.readlines()
ssh.close()
print(stdout)
print(stderr)
print(stdin)




from pexpect.pxssh import pxssh
import getpass
hostname = '10.2.52.13'
user = 'root'
pw = getpass.getpass()
s = pxssh()
s.login(hostname,user,pw)
s.sendline('ls -l')
s.prompt()
print(s.before.decode())

s.logout()




import pexpect
ssh = pexpect.spawn('ssh root@10.2.52.13 "hostname"')
ssh.sendline('rootroot')
ssh.close()
r = ssh.read()
print(r)
