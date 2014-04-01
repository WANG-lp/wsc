import sys
import cgi
import BaseHTTPServer,CGIHTTPServer

BaseHTTPServer.HTTPServer(('192.168.100.122', int(sys.argv[1])), CGIHTTPServer.CGIHTTPRequestHandler).serve_forever()
