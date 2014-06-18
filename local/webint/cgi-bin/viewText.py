#!/usr/bin/python

import subprocess

import collections
import cgi
import os
import time
import gzip

import cdb
import sys
import mmap
import re

import urllib2

from lxml import etree

print "Content-Type: text/html"
print

fs = cgi.FieldStorage()

print """<html><head>
<link href="../bootstrap-3.0.3/dist/css/bootstrap.min.css" rel="stylesheet" />
</head>
<body>
<div class="wrap">
<div class="container" style="width:2000px">
<h1 style="padding-top: 50px"> </h1>
"""

if None != fs.getvalue("target"):
	f, did = fs.getvalue("target").split(":")
else:
	f, did = fs.getvalue("file"), fs.getvalue("docid")
	
xml		= etree.parse(
	os.popen("/home/naoya-i/work/wsc/src/extractDoc.sh %s %s" % (
		f, did
		)))

def _coloring(t):
	t = re.sub(fs.getvalue("s1"), lambda x: "<b>%s</b>" % x.group(0), t)
	t = re.sub(fs.getvalue("s2"), lambda x: "<b>%s</b>" % x.group(0), t)
	return t
	
for sent in xml.xpath("/root/document/sentences/sentence"):
	print "<p>", _coloring(" ".join(sent.xpath("./tokens/token/word/text()"))), "</p>"

print """</div>
</div>

<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <a class="navbar-brand" href="#">Text Viewer - %s, %s</a>
        </div>	
        <div class="navbar-collapse collapse">
        </div><!--/.navbar-collapse -->
      </div>
    </div>
<script src="../bootstrap-3.0.3/dist/js/bootstrap.min.js"></script>
</body></html>
"""% (fs.getvalue("file"), fs.getvalue("docid"),)
