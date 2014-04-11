#!/usr/bin/python

from xml.sax.saxutils import escape
import os, sys, glob, re

print "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n<root>"

numProcessed = 0

for fn in glob.glob(sys.argv[1]):
	if "running" in fn: continue
	
	for ln in open(fn):
		sys.stdout.write(re.sub(">(.*?)(<[^<]+)$", lambda x: ">%s%s" % (escape(x.group(1)), x.group(2)), ln)) if ln.startswith("<") else None
		# 		streamOutThin.write(re.sub(">(.*?)(<[^<]+)$", lambda x: ">%s%s" % (escape(x.group(1)), x.group(2)), ln)) if ln.startswith("<") and not "cirInstances" in ln else None

	sys.stderr.write(".")
	
	numProcessed += 1
	if 0 == numProcessed % 100: sys.stderr.write("%d\n" % numProcessed)
		
print "</root>"
print >>sys.stderr, numProcessed, ""

