os.system('export PATH="/usr/kerberos/bin:$PATH" &>/dev/null')
os.system('export KRB5CCNAME=/tmp/krb5cc_pub_$$ &>/dev/null')
os.system('trap kdestroy 0 1 2 3 5 15 &>/dev/null')
os.system('kinit -k -t /etc/krb5.keytab &>/dev/null')


print('aaaa')
print(os.system('klist'))
print('bbbb')