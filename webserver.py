#Copyright Jon Berg , turtlemeat.com

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import prii
import traceback,sys,os,select

filename = os.path.join("/tmp", 'xxfifo')
fifo=os.open(filename,os.O_RDONLY|os.O_NONBLOCK)

def chunkedwrap(oldstr):
    if oldstr:
        l = len(oldstr)
        ret = ""
        ret += "{0}\r\n".format(hex(l)[2:])
        ret += "{0}\r\n".format(oldstr)                                                                                                                      
    else:
        ret = "0\r\n\r\n"
    #print ret
    return ret


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path==("/esp"):   #our dynamic content
		self.protocol_version="HTTP/1.1"
                self.send_response(200)
                self.send_header('Content-type',	'text/html; charset=UTF-8')
		self.send_header('Transfer-Encoding', "chunked")
		self.send_header('Trailer',  'Expires')
		self.end_headers()
		while 1:
		    x=os.read(fifo,1024)
		    if x :
			self.wfile.write(chunkedwrap(x))
		    else:
			break
		self.wfile.write(chunkedwrap(None))
            else:
		self.send_error(404,'File Not Found: %s' % self.path)
    	except:
	    print("unknown error")
	    traceback.print_exc(file=sys.stdout)
	return


    def do_POST(self):
        global rootnode
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            self.send_response(301)
            
            self.end_headers()
            upfilecontent = query.get('upfile')
            print "filecontent", upfilecontent[0]
            self.wfile.write("<HTML>POST OK.<BR><BR>");
            self.wfile.write(upfilecontent[0]);
            
        except :
            pass

def main():
    try:
        server = HTTPServer(('', 8081), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

