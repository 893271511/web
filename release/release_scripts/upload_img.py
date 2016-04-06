#!/usr/bin/env python
#coding=utf-8

# http://10.4.34.74:8099/?filename=22.png&check=aaaddfddsfkadsfjkfdsjjdskfj

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse, json, os, commands
import imghdr

DIR = "/data/static/licai_banner/"
static_host = "xnimg@10.4.30.42"

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsedPath = urlparse.urlparse(self.path)
        responseDic = {}
        responseDic['ClientAddress'] = self.client_address
        responseDic['Path'] = parsedPath.path
        responseDic['Query'] = {}
        querys = parsedPath.query.split('&')
        for i in querys:
            k, v = i.split('=')
            responseDic['Query'][k] = v
        responseStr = json.dumps(responseDic, sort_keys=True, indent=4)
	file = os.path.join(DIR,responseDic['Query']['filename'])
	if os.path.exists(file) and imghdr.what(file) in "jpgjpegpng" :
		#kerberos设置，使本机访问其它主机
		os.system('export PATH="/usr/kerberos/bin:$PATH"')
		os.system('export KRB5CCNAME=/tmp/krb5cc_pub_$$')
		os.system('trap kdestroy 0 1 2 3 5 15')
		os.system('kinit -k -t /etc/krb5.keytab')
		(status1,output1) = commands.getstatusoutput('scp -r 10.4.34.74:%s %s:%s' %(file,static_host,file))
		md5_value1 = commands.getoutput('md5sum %s' %file)
		md5_value2 = commands.getoutput('ssh %s "md5sum %s"' %(static_host,file))
		print status1
		print output1
		print md5_value1
		print md5_value2
		if md5_value1 == md5_value2:
        		self.send_response(200)
        		self.end_headers()
        		self.wfile.write("ok")
		else:
			print "file copy fail"
			self.send_response(200)
			self.end_headers()
			self.wfile.write("error")

	else:
		print "图片不存在 或 不是图片"
            	with open('/tmp/upload_img.py.log', 'a+b') as f:
               		f.write("%s 图片不存在 或 不是图片\n" % responseDic)
		self.send_response(200)
        	self.end_headers()
        	self.wfile.write("error")

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('10.4.34.74',8099), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
        
