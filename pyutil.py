#!/usr/bin/python

import commands
import json

class theIP:
    iface=""
    ipaddr=""
    netmask=""
    brdcast=""
    gateway=""
    dns=""
    macaddr=""
    
    def __init__(self, interfaceid):
        self.iface=interfaceid
        cmd = "ifconfig %s | grep 'inet addr:' |cut -d: -f2 | awk '{ print $1}'" % interfaceid
        self.ipaddr = commands.getoutput(cmd)
        if "error" in self.ipaddr: 
            self.ipaddr = ""
            return
        cmd = "ifconfig %s | grep 'inet addr:' |cut -d: -f3 | awk '{ print $1}'" % interfaceid
        self.brdcast = commands.getoutput(cmd)
        
        cmd = "ifconfig %s | grep 'inet addr:' |cut -d: -f4 | awk '{ print $1}'" % interfaceid
        self.netmask = commands.getoutput(cmd)
    
    def __str__(self):
        d = {}
        d["interface"]=self.iface
        d["ipaddr"]=self.ipaddr
        d["netmask"]=self.netmask
        d["brdcast"]=self.brdcast
        return json.dumps(d)
        

def main():
    i = theIP("eth0")
    print i.ipaddr
    print i.netmask
    print i.brdcast
    print i.dns
    print i.gateway
    print i.macaddr
    print i


if __name__ == "__main__":
    main()
