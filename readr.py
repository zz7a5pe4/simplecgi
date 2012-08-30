import os, stat

filename = os.path.join("/tmp", 'xxfifo')
print filename
try:
    os.mkfifo(filename)
except OSError, e:
    print "Failed to create FIFO: %s" % e

#fifo=os.open(filename,os.O_RDONLY)
#fifo = open(filename, 'w')
# write stuff to fifo
#print >> fifo, "hello"
fifo=os.open(filename,os.O_RDONLY)
while 1:
	x=os.read(fifo,1024)
	if x :
		print x
	else:
		break

os.close(fifo)

def openfifo_read(filename):
	try:
		os.mkfifo(filename)
	except OSError, e:
		print "create fifo return %s" % e
	ret = os.open(filename,os.O_RDONLY)

def closefifo_read

