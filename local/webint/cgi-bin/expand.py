#!/usr/bin/python

import collections
import cgi
import os
import time

import cdb
import sys
import mmap
import re

import urllib2

sys.path += ["/home/naoya-i/work/wsc/"]

import cir as conir

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

result_t = collections.namedtuple("result_t", "ana_lemma, ana_gov, ana_con, ante_lemma, ante_gov, ante_con, ante_false_lemma, ante_false_gov, ante_false_con, numRulesC, numRulesW, examples, text")

if None != fs.getvalue("query"):
	def _interpretQuery(x):
		p1, p2, p3 = [(y.strip("(").strip(")").strip(), "-") for y in re.split("[\t ,]+", x)][:3]
		return p2, p1, p3
		
	# PRINT THE RESULT.
	libcir		 = conir.test_cir_t(None, "/work/naoya-i/kb/corefevents.tsv", useMemoryMap=True)
	p1, p2, p3 = _interpretQuery(fs.getvalue("query"))

	print >>sys.stderr, p1, p2, p3
	timeStart								= time.time()
	results12									= list(libcir.getScores(p1, p2))
	results23									= list(libcir.getScores(p2, p3))
	timeRetrieve, timeStart = time.time() - timeStart, time.time()
	timeSort, timeStart = time.time() - timeStart, time.time()

	print """<h2>Instances:</h2>"""
	print "<div class=\"row\">"

	for examples in [results12, results23]:
		header = "Predicate1 Predicate2 SharedArg Context1 Context2 Source"
		trs		 = []
		
		for inst in examples:
			pi, pj = (p1[0], p2[0]) if results12 == examples else (p2[0], p3[0])
			if pi > pj: pi, pj = pj, pi
			
			trs += [
				"<tr height=\"150px\"><td>%s</td></tr>" % ("</td><td>".join([
							pi, pj, inst.instArg,
							inst.context1, inst.context2,
							"<a target=\"_blank\" href=\"https://www.google.co.jp/search?q=%s\">G</a>" % (urllib2.quote("\"%s\"+\"%s\"" % (inst.source1[2:], inst.source2[2:]))),
							]))
				]
			
		print "<div class=\"col-md-6\">"
		print "#:", len(trs)
		print "<table class=\"table table-striped\">"
		print "<tr><th>%s</th></tr>" % "</th><th>".join(header.split())
		print "\n".join(trs)
		print "</table>"
		print "</div>"
	
	print "</div>"

	print """<p>Time elapsed: %.2f s (retrieve: %.2f s, sort: %.2f s)</p>""" % (
		timeRetrieve+timeSort, timeRetrieve, timeSort,
		)
	
print """</div>
</div>

<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <a class="navbar-brand" href="#">Reasoning Instances Viewer</a>
        </div>	
        <div class="navbar-collapse collapse">
<form action ="./expand.py" method="GET" class="navbar-form navbar-right" role="form">

<div class="form-group">
<input class="form-control" name="query" placeholder="Predicates" type="text" style="width:400px" value="%s" />
</div>

<input type="submit" value="Search" class="btn btn-success"/>

</form>
        </div><!--/.navbar-collapse -->
      </div>
    </div>


<script src="../bootstrap-3.0.3/dist/js/bootstrap.min.js"></script>
</body></html>
""" % (
	fs.getvalue("query") if None != fs.getvalue("query") else "",
	)


