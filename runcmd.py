#!/usr/bin/python

import os
import pexpect

filename = os.path.join("/tmp", 'xxfifo')
print filename
os.unlink(filename)
try:
    os.mkfifo(filename)
except OSError, e:
    print "Failed to create FIFO: %s" % e

tmpfifo=os.open(filename,os.O_RDONLY|os.O_NONBLOCK)
#fifo = open(filename, 'w')
# write stuff to fifo
#print >> fifo, "hello"

f=os.open(filename,os.O_WRONLY)

child = pexpect.spawn ('ping 127.0.0.1 -c 20')
while(1):
    i = child.readline().rstrip()
    if i:
        os.write(f,i)
    else:
        os.write(f,"end")
        break
print "exiting", os.getpid()


os.close(f)
os.close(tmpfifo)
