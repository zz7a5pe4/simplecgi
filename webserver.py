#!/usr/bin/bash
#Copyright Jon Berg , turtlemeat.com

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler
import SimpleHTTPServer
import traceback,sys,os,select,socket
import xfifo
from pyutil import theIP
import cmdaemon
from cmdmapping import cmdmaps
import SocketServer
import urlparse
import json


class HTTPServer(SocketServer.ForkingTCPServer):

    allow_reuse_address = 1    # Seems to make sense in testing environment                                                                                 

    def server_bind(self):
        """Override server_bind to store the server name."""
        SocketServer.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port



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

    result_fifo = xfifo.FIFORdEnd(msg)
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

def cfg2dic(s):
    l = s.replace(r"%2F",r'/').split("&")
    d={}
    for i in l:
        k,v = i.split("=")
        d[k]=v
    return d

def createrc(d):
    if not d:
        d = {}
    tmpstr = d.get("SSD_PATH","")
    if tmpstr:
        tmpc = open("/home/xeven/x7env","w")
        tmpc.write("SSDDEV={0}\n".format(tmpstr))
        tmpc.close()

    c = open("/home/xeven/localrc_server_template","w")
    
    tmpstr = d.get("FLAT_INTERFACE","eth0")
    ip = theIP(tmpstr)
    c.write("HOST_IP={0}\n".format(ip.ipaddr))
    c.write("FLAT_INTERFACE={0}\n".format(tmpstr))

    tmpstr = d.get("FIXED_RANGE",r"10.10.10.0/24")
    c.write("FIXED_RANGE={0}\n".format(tmpstr))

    tmpstr = d.get("FIXED_NETWORK_SIZE",r"256")
    c.write("FIXED_NETWORK_SIZE={0}\n".format(tmpstr))

    tmpstr = d.get("FLOATING_RANGE", "{0}/25".format(ip.brdcast))
    c.write("FLOATING_RANGE={0}\n".format(tmpstr))
    c.write("MULTI_HOST=1\n")
    c.write("SERVICE_TOKEN=xyzpdqlazydog\n")

    tmpstr = d.get("MYSQL_PASSWORD","gadmei")
    c.write("MYSQL_PASSWORD={0}\n".format(tmpstr))

    tmpstr = d.get("RABBIT_PASSWORD","gadmei")
    c.write("RABBIT_PASSWORD={0}\n".format(tmpstr))

    tmpstr = d.get("ADMIN_PASSWORD","gadmei")
    c.write("ADMIN_PASSWORD={0}\n".format(tmpstr))

    tmpstr = d.get("SERVICE_PASSWORD","gadmei")
    c.write("SERVICE_PASSWORD={0}\n".format(tmpstr))

    servertype = d.get("Select_x7","server")
    if servertype == "server":
        c.write("ENABLED_SERVICES=g-api,g-reg,key,n-api,n-crt,n-obj,n-net,n-vol,n-sch,n-cauth,horizon,mysql,rabbit\n")
    elif servertype == "all":
        c.write("ENABLED_SERVICES=g-api,g-reg,key,n-api,n-crt,n-obj,n-net,n-vol,n-sch,n-cauth,horizon,mysql,rabbit,n-cpu,n-vol,n-novnc,n-xvnc\n")
        c.write("MYSQL_HOST={0}\n".format(ip.ipaddr))
        c.write("RABBIT_HOST={0}\n".format(ip.ipaddr))
        c.write("GLANCE_HOSTPORT={0}:9292\n".format(ip.ipaddr))
        c.write("SERVICE_HOST={0}\n".format(ip.ipaddr))
        c.write("NOVNCPROXY_URL=http://{0}:6080/vnc_auto.html\n".format(ip.ipaddr))
        c.write("XVPVNCPROXY_URL=http://{0}:6081/console\n".format(ip.ipaddr))
    else:
        print servertype
        raise
    c.close()



class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        #p = self.path[1:]
        if self.path[1:] == "ip_default":
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(str(theIP("eth0"))) #call sample function here
            return
        elif self.path[1:11] == "test_query":
            parsed_path = urlparse.urlparse(self.path)
            message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
            for name, value in sorted(self.headers.items()):
                message_parts.append('%s=%s' % (name, value.rstrip()))
            message_parts.append('')
            message = '\r\n'.join(message_parts)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(message)
        elif self.path[1:9] == "ip_query":
            parsed_path = urlparse.urlparse(self.path)
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            if "i=" in parsed_path.query:
                iface= parsed_path.query.replace("i=","")
            self.wfile.write(str(theIP(iface))) #call sample function here
        else:
            #print super
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


    def do_POST(self):
        global rootnode
        try:
            cmd = self.path[1:] 
            #print cmd
            if cmd == "x7": # I know it' ugly. don't laugh at me
                length = int(self.headers.getheader('content-length'))
                usrcfg = self.rfile.read(length)
                print usrcfg.rstrip()
                #d = json.load(usrcfg.rstrip())
                #print d
                d = cfg2dic(usrcfg)
                createrc(d)
            #print cmdmaps.keys()
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
            global ipaddr
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

