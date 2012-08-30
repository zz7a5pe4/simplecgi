#!/usr/bin/python

import os, sys, socket

# def main():
#     #filename = os.path.join("/tmp", sys.argv[1])
#     filename = os.path.join("/tmp", "xcmdfifo")
#     print filename
#     try:
#         os.mkfifo(filename)
#     except OSError, e:
#         print "Failed to create FIFO: %s" % e   
#     #fifo=os.open(filename,os.O_RDONLY|os.O_NONBLOCK)
#     #fifo = open(filename, 'w')
#     # write stuff to fifo
#     #print >> fifo, "hello" 
#     f=os.open(filename,os.O_WRONLY) 
#     os.write(f,sys.argv[2])   
#     os.close(f)

def main():
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    # Connect the socket to the port where the server is listening
    server_address = "/tmp/xcmdfifo"
    my_address = "/tmp/xcmdclient"
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
    
    sock.sendall(sys.argv[2])
    data = sock.recv(16)
    print >>sys.stderr, 'received "%s"' % data
    sock.close()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        main()
