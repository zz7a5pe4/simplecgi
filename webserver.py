#Copyright Jon Berg , turtlemeat.com

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import CGIHTTPServer
import traceback,sys,os,select
import xfifo

#filename = os.path.join("/tmp", 'xxfifo')
#fifo=os.open(filename,os.O_RDONLY|os.O_NONBLOCK)

def transmsg(f):
    for x in range(3):
        msg="<p>hey, today is the " + str(time.localtime()[7]) + " day in the year " + str(time.localtime()[0]) + "</p>"
        r=chunkedwrap(msg)
        f.write(r)
        time.sleep(1)

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


class MyHandler(CGIHTTPServer.CGIHTTPRequestHandler):


    def do_POST(self):
        global rootnode
        try:
            if self.path==("/serverfun"):   #our dynamic content
                self.protocol_version="HTTP/1.1"
                self.send_response(200)
                self.send_header('Content-type',        'text/html; charset=UTF-8')
                self.send_header('Transfer-Encoding', "chunked")
                self.send_header('Trailer',  'Expires')
                self.end_headers()
                transmsg(self.wfile)
                self.wfile.write(chunkedwrap(None))
            else:
                self.send_error(404,'File Not Found: %s' % self.path)
        except:
            print("unknown error")
            traceback.print_exc(file=sys.stdout)
        return

def main():
    try:
        server = HTTPServer(('', 8000), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

