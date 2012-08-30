#!/usr/bin/python
import os, stat, errno, select

class FIFOReadTimeout: pass
class FIFOPeerClosed: pass

# sync operation
class FIFOWtEnd:
	fifoname = "";
	wfd = 0
	def __init__(self, fname):
		self.fifoname = os.path.join("/tmp/", fname)
		mode = os.stat(self.fifoname).st_mode
		if stat.S_ISFIFO(mode):
			self.wfd=os.open(self.fifoname,os.O_WRONLY)
		else:
			raise

	def write(self, s):
		if s:
			return os.write(self.wfd,s)

	def writeEOF(self):
		os.write()

	def close(self):
		os.close(self.wfd)

# async, read file should be created first
class FIFORdEnd:
	fifoname = ""
	rfd = 0
	rd = None
	def __init__(self, fname):
		self.fifoname = os.path.join("/tmp/", fname)
		try:
			os.mkfifo(self.fifoname)
		except OSError, e:
			if not e.errno == errno.EEXIST:
				raise
			else:
				mode = os.stat(self.fifoname).st_mode
				if not stat.S_ISFIFO(mode):
					raise
		self.rfd=os.open(self.fifoname,os.O_RDONLY|os.O_NONBLOCK)
		self.rd = os.fdopen(self.rfd)
		mode = os.stat(self.fifoname).st_mode
		

	def read(self, timeout=30):
		if self.rfd:
			r,w,e = select.select([self.rd],[], [self.rd], timeout)
			if e:
				raise
			elif r:
				data = os.read(self.rfd,1024)
				if not data:
					print "peer closed"
				return data
			else:
				print "timeout......"
				return None
		else:
			print "bad read descriptor"
			return None

	def close(self):
		self.rd.close()
		os.unlink(self.fifoname)

def test():

	r = FIFORdEnd("xfifotest")
	w = FIFOWtEnd("xfifotest")
	r.close()
	w.write("hello")
	w.write("world")

	print r.read(1)
	print r.read()
	w.close()

	print r.read(1)
	print r.read()
	#w.close()
	r.close()

if __name__ == '__main__':
	test()