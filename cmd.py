#!/usr/bin/python

import pexpect
import os

(r,w)=os.pipe()

def startcmd():
    pid = os.fork()
    if pid == 0:
	print "child"
	while(1):
        tmp = os.read(r, 1024)
        if not tmp.find("end") == -1:
            break
        else:
            print tmp
    else:
        child = pexpect.spawn ('ping 127.0.0.1 -c 3')
        print "parent"
        while(1):
            i = child.readline().rstrip()
            if i:
                os.write(w,i)
            else:
                os.write(w,"end")
                break
    print "exiting", os.getpid()


