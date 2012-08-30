#!/usr/bin/python

import os, socket, sys
import pexpect
import xfifo

class ForkingHandler:
    timeout = 300
    active_children = None
    max_children = 40

    def collect_children(self):
        """Internal routine to wait for children that have exited."""
        if self.active_children is None: return
        while len(self.active_children) >= self.max_children:
            # XXX: This will wait for any child process, not just ones
            # spawned by this library. This could confuse other
            # libraries that expect to be able to wait for their own
            # children.
            try:
                pid, status = os.waitpid(0, 0)
            except os.error:
                pid = None
            if pid not in self.active_children: continue
            self.active_children.remove(pid)

        # XXX: This loop runs more system calls than it ought
        # to. There should be a way to put the active_children into a
        # process group and then use os.waitpid(-pgid) to wait for any
        # of that set, but I couldn't find a way to allocate pgids
        # that couldn't collide.
        for child in self.active_children:
            try:
                pid, status = os.waitpid(child, os.WNOHANG)
            except os.error:
                pid = None
            if not pid: continue
            try:
                self.active_children.remove(pid)
            except ValueError, e:
                raise ValueError('%s. x=%d and list=%r' % (e.message, pid,
                                                           self.active_children))

    def handle_error(self, request, result_df):
        """Handle an error gracefully.  May be overridden.

        The default is to print a traceback and continue.

        """
        print '-'*40
        print 'Exception happened during processing of request',
        print request
        import traceback
        traceback.print_exc() # XXX But this goes to stderr!
        print '-'*40

    def process_request(self, request, result_df):
        """Fork a new subprocess to process the request."""
        self.collect_children()
        pid = os.fork()
        if pid:
            # Parent process
            if self.active_children is None:
                self.active_children = []
            self.active_children.append(pid)
            return
        else:
            # Child process.
            # This must never return, hence os._exit()!
            try:
                #t = open(result_df, "w")
                self.do_request(request, result_df)
                #t.close()
                os._exit(0)
            except:
                print "exception occur"
                try:
                    self.handle_error(request, result_df)
                finally:
                    os._exit(1)
            result_df.close()


cmdmaps={"ls":"ls -l /home","pwd":"pwd","who":"w"}
class CmdDaemon:
    poll_interval = 5;
    sock = 0;
    def __init__(self):
        # open fifo async
        filename = os.path.join("/tmp", 'xcmdfifo')
        print filename
        try:
            os.unlink(filename)
        except OSError, e:
            print ""
            # Create a UDS socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(filename)

        #print "fd is " + str(self.sock.fileno())

    def do_request(self, request, result_df):
        """ process request and write result to result_df """
        child = pexpect.spawn (request)
        t = open(result_df, "w")
        while(1):
            i = child.readline()
            if i:
                t.write(i)
            else:
                t.write(str(request) +" end")
                break
        t.close()

    def prepare_request(self, msg):
        if not msg:
            return None, None
        #print "get msg:" + msg
        req = None
        req = cmdmaps[msg]
        return req, msg


    def start(self):
        while 1:
            print >>sys.stderr, 'waiting for a connection'
            data, client_address = self.sock.recvfrom(1024)
            r, m = self.prepare_request(data)
            print >>sys.stderr, 'connection from', client_address
            print >>sys.stderr, "receive ", data
            self.sock.sendto("done", client_address)
            self.process_request(r,m)


class ForkDaemon(CmdDaemon, ForkingHandler): pass

def main():
    s = ForkDaemon();
    s.start()

if __name__ == '__main__':
    main()
