import CGIHTTPServer
import BaseHTTPServer

print CGIHTTPServer.CGIHTTPRequestHandler.cgi_directories

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
	pass

PORT = 8000

httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()
