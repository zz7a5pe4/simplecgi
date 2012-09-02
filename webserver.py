#Copyright Jon Berg , turtlemeat.com

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SimpleHTTPServer
import traceback,sys,os,select,socket
import xfifo
import cmdaemon
from cmdmapping import cmdmaps


cmdclint_address_prefex = "/tmp/xcmdclient/"
server_address = "/tmp/xcmdqueue"

def timesuffix():
    return hex(int(time.time()))[2:].upper()

def transmsg(f, cmds):
    for x in range(1):
        msg="<p>" + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + "</p>"
        r=chunkedwrap(msg)
        f.write(r)
    
    
    #my_address = os.path.join(cmdclint_address_prefex, 'run') # for communicate with cmd daemon
    my_address = os.tempnam(cmdclint_address_prefex,"run")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        os.mkdir(cmdclint_address_prefex)
    except OSError, e:
        print "socket address gives: %s" % e
    
    
    sock.bind(my_address)
    #print >>sys.stderr, 'connecting to %s' % server_address
    try:
        sock.connect(server_address)
    except socket.error, emsg:
        print >>sys.stderr, emsg
        r = chunkedwrap("<b><em>Error: %s</em></b>" % emsg)
        f.write(r)
        return
    msg = timesuffix()
    msg = cmds + "_" + msg
    sock.sendall(msg)
    data = sock.recv(16)
    print >>sys.stderr, 'received "%s"' % data
    sock.close()
    try:
        os.unlink(my_address)
    except OSError, e:
        print "socket address gives: %s" % e

    if not data == "done":
        print "not support cmd"
        return

    result_fifo = xfifo.FIFORdEnd("x7serverfun")
    while 1:
        s = result_fifo.read()
        if not s:
            # timeout or peer closed
            r = chunkedwrap("<b><em>Error while exec Cmd: timeout or server fault</em></b>")
            f.write(r)
            break
        elif s[-5:] == "xendx":
            print "end of cmd"
            r = chunkedwrap("<b>End of Cmd</b>")
            f.write(r)
            break
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
            cmd = self.path[1:] 
            if cmd in cmdmaps.keys():   #our dynamic content
                self.protocol_version="HTTP/1.1"
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=UTF-8')
                self.send_header('Transfer-Encoding', "chunked")
                #self.send_header('Trailer',  'Expires')
                self.end_headers()
                transmsg(self.wfile, cmd)
                self.wfile.write(chunkedwrap(None))
            else:
                self.send_error(404,'File Not Found: %s' % self.path)
        except:
            print("unknown error")
            traceback.print_exc(file=sys.stdout)
        return

def main():
    pid = os.fork()
    if pid:
        try:
            server = HTTPServer(('', 8000), MyHandler)
            print 'started httpserver...'
            server.serve_forever()
        except KeyboardInterrupt:
            print 'shutting down server'
            server.socket.close()
    else:
        s = cmdaemon.ForkDaemon();
        s.start()

if __name__ == '__main__':
    main()

