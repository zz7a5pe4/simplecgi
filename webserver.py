#Copyright Jon Berg , turtlemeat.com

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SimpleHTTPServer
import traceback,sys,os,select,socket
import xfifo

#filename = os.path.join("/tmp", 'xxfifo')
#fifo=os.open(filename,os.O_RDONLY|os.O_NONBLOCK)
cmdclint_address_prefex = "/tmp/xcmdclient/"
server_address = "/tmp/xcmdfifo"

def transmsg(f):
    for x in range(1):
        msg="<p>hey, today is the " + str(time.localtime()[7]) + " day in the year " + str(time.localtime()[0]) + "</p>"
        r=chunkedwrap(msg)
        f.write(r)
        time.sleep(1)
    
    result_fifo = xfifo.FIFORdEnd("x7serverfun")
    my_address = os.path.join(cmdclint_address_prefex, 'servfun')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        os.unlink(my_address)
    except OSError, e:
        print "Failed to create FIFO: %s" % e

    sock.bind(my_address)
    #print >>sys.stderr, 'connecting to %s' % server_address
    try:
        sock.connect(server_address)
    except socket.error, msg:
        print >>sys.stderr, msg
        sys.exit(1)
    
    sock.sendall("who")
    data = sock.recv(16)
    print >>sys.stderr, 'received "%s"' % data
    sock.close()
    while 1:
        s = result_fifo.read()
        if s[-5:] == "xendx":
            print "end of cmd"
            break
        elif not s:
            continue
        else:
            r = chunkedwrap(s)
            f.write(r)

    result_fifo.close()

def chunkedwrap(oldstr):
    #print "inchunked:" + str(oldstr)
    if oldstr:
        l = len(oldstr)
        ret = ""
        ret += "{0}\r\n".format(hex(l)[2:])
        ret += "{0}\r\n".format(oldstr)                                                                                                                      
    else:
        ret = "0\r\n\r\n"
    #print "inchunked:" + ret
    return ret


class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):


    def do_POST(self):
        global rootnode
        try:
            if self.path==("/serverfun"):   #our dynamic content
                self.protocol_version="HTTP/1.1"
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=UTF-8')
                self.send_header('Transfer-Encoding', "chunked")
                #self.send_header('Trailer',  'Expires')
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

