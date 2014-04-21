#!/usr/bin/python

import subprocess
import struct

import collections
import cgi
import os
import time

import re
import sys
import mmap

import urllib2

import xml.etree.cElementTree as ET

sys.path.append("/home/naoya-i/work/wsc/src")

import iri

print "Content-Type: text/html"
print

fs = cgi.FieldStorage()

print """<html><head>
<link href="../bootstrap-3.0.3/dist/css/bootstrap.min.css" rel="stylesheet" />
</head>
<body>
<div class="wrap">
<div class="container" style="width:2400px">
<h1 style="padding-top: 50px"> </h1>
"""

result_t = collections.namedtuple("result_t", "ana_lemma, ana_gov, ana_con, ante_lemma, ante_gov, ante_con, ante_false_lemma, ante_false_gov, ante_false_con, numRulesC, numRulesW, examples, text")

if None != fs.getvalue("query"):

	# PRINT THE RESULT.
	def _getCached(problemNo):
		f														= open("/work/naoya-i/kb/corefevents.com.tsv")
		m														= mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
		examples										= []
		numCorrect, numWrong				= 0, 0
		governors, contexts, lemmas = [], [], []
		text												= ""
		
		for ln in os.popen("awk '$0 ~ /problem id=\"%s\"/ { fPrint=1; } 1 == fPrint { print $0 } fPrint && $0 ~ /<\/problem>/ {exit}' ./link-to-result" % problemNo):
			if "governors" in ln: governors = re.findall("\"(.*?)\"", ln)
			if "contexts" in ln:  contexts  = re.findall("\"(.*?)\"", ln)
			if "text=" in ln:
				text   = re.findall("text=\"(.*?)\"", ln)[0]
				lemmas = re.findall("anaphor=\"(.*?)\" antecedent=\"(.*?)\" falseAntecedent=\"(.*?)\"", ln)[0]

			if "iriInstances" not in ln: continue

			ir = iri.result_t(*[eval(x) for x in re.findall(">(.*?)<\/statistics", ln)[0].split("\t")])
			examples += [(0 if "Correct" in ln else 1, ir, m[int(ir.offset):int(ir.offset)+int(ir.length)])]

			if "Correct" in ln: numCorrect += 1
			elif "Wrong" in ln: numWrong += 1

		return result_t(*(
				[lemmas[0], governors[0], contexts[0], lemmas[1], governors[1], contexts[1], lemmas[2], governors[2], contexts[2], numCorrect, numWrong, examples, text]
				))

	timeStart								= time.time()
	results									= _getCached(fs.getvalue("query"))
	timeRetrieve, timeStart = time.time() - timeStart, time.time()
	
	sortedRet = sorted(results.examples, key=lambda x: x[1].score, reverse=True)[:min(len(results.examples), int(fs.getvalue("k")))]
	timeSort, timeStart = time.time() - timeStart, time.time()

	def _coloring(t):
		return t.replace(
			results.ante_lemma.split("-")[0], "<strong style=\"color:red\">%s</strong>" % results.ante_lemma.split("-")[0]).replace(
			results.ante_false_lemma.split("-")[0], "<strong style=\"color:blue\">%s</strong>" % results.ante_false_lemma.split("-")[0]).replace(
				results.ana_lemma.split("-")[0], "<strong>%s</strong>" % results.ana_lemma.split("-")[0])

	print """<h2>Problem:</h2>
<h3>Sentence</h3>
<p class="lead">%s</p>

<h3>Compared Queries</h3>

<div class="row">

<div class="col-md-6">
<table class="table table-striped">
<tr><th>%s</th></tr>
<tr><td>%s</td></tr>
<tr><td>%s</td></tr>
</table>
</div>

<div class="col-md-6">
<table class="table table-striped">
<tr><th>%s</th></tr>
<tr><td>%s</td></tr>
<tr><td>%s</td></tr>
</table>
</div>

</div>

""" % (_coloring(results.text),
			 "</th><th>".join("Argument Governor:Role Context".split()),
			 "</td><td>".join([results.ana_lemma, results.ana_gov, results.ana_con]),
			 "</td><td>".join([results.ante_lemma, results.ante_gov, results.ante_con]),
			 "</th><th>".join("Argument Governor:Role Context".split()),
			 "</td><td>".join([results.ana_lemma, results.ana_gov, results.ana_con]),
			 "</td><td>".join([results.ante_false_lemma, results.ante_false_gov, results.ante_false_con]),
			 )
	
	print """<h2>Nearest Neighbors:</h2>"""
	print "<div class=\"row\">"

	def _prettyGR(p):
		p, r = p.split(":")
		p    = p.split("-")[0]
		
		if "nsubj" == r: return "X %s" % p
		if "dobj" == r: return "%s X" % p
		if "iobj" == r: return "%s X" % p
		if r.startswith("prep_"): return "%s %s X" % (p, r.split("_")[-1])
		
		return p

	def _prettyC(empha, c):
		emphaLight = map(lambda x: x.rsplit(":", 1)[0], empha)
		
		return "<br />".join(
			map(
				lambda x:
					"<span style=\"color:red\">%s</span>" % x if x in empha else (
					"<span style=\"color:red\">%s:</span>%s" % tuple(x.rsplit(":", 1)) if x.rsplit(":", 1)[0] in emphaLight else x)
				,
				c.split(" ")
			))
		
	for tp in xrange(2):
		p1, p2 = _prettyGR(results.ante_gov if 0 == tp else results.ante_false_gov), _prettyGR(results.ana_gov)
		c1, c2 = (results.ante_con if 0 == tp else results.ante_false_con).split(" "), results.ana_con.split(" ")

		if p1 > p2: p1, p2, c1, c2 = p2, p1, c2, c1
		
		header = "Rank Scores Predicates Shared&nbsp;Arg Contexts Source"

		votesCorrect, votesWrong = 0, 0
		
		for r, ret in enumerate(sortedRet):
			if   0 == ret[0]: votesCorrect += 1
			elif 1 == ret[0]: votesWrong += 1
			
		print "<div class=\"col-md-6\">"
		print "<h3>%s Votes for %s Candidate (%s -- %s)</h3>" % ((votesCorrect, "Correct", p1, p2) if 0 == tp else (votesWrong, "Wrong", p1, p2))
		print "<table class=\"table table-striped\">"
		print "<tr><th>%s</th></tr>" % "</th><th>".join(header.split())

		nextAnchor = 1
		
		for r, ret in enumerate(sortedRet):
			voted, inst, ir = ret

			if tp != voted:
				print "<tr height=\"150px\">%s</tr>" % "".join(
					map(
						lambda i: "<td></td>" if 4 != i else "<td><br/><br/><a href=\"#next%d\">&#9759;</a></td>" % nextAnchor,
						xrange(len(header.split()))
						))
				print "<tr height=\"150px\">%s</tr>" % "".join(
					map(
						lambda i: "<td></td>" if 4 != i else "<td><br/><br/><a href=\"#next%d\">&#9759;</a></td>" % nextAnchor,
						xrange(len(header.split()))
						))
				continue

			irp1, irp2, ia12, sentdist, irc1, irc2, src = ir.split("\t")
			a1,   a2																		= ia12.split(",")
			a12																					= "%s,%s" % (a1, a2)
			sentdist																		= str(sentdist)
			
			print "<tr height=\"150px\"><td><a name=\"next%s\"></a>%s</td></tr>" % (nextAnchor, "</td><td>".join([
						"%d" % (1+r),
						"%.4f <br />P: %.2f<br />A: %.2f<br />C: %.2f<br />S: %.2f" % (
							inst.score,
							float(inst.sIndexPred[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedPred),
							float(inst.sIndexArg[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedArg),
							float(inst.sIndexContext[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedContext),
							float(inst.sIndexSlot[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedSlot),
							),
						"%s <br />(%s)" % (irp1, "indexed" if 0 == inst.iIndexed else "predicted"),
						a12.split(",")[0], _prettyC(c1, irc1),
						"<a target=\"_blank\" href=\"https://www.google.co.jp/search?q=%s\">G</a>" % (urllib2.quote("\"%s\"+\"%s\"" % (irp1, irp2))),
						]))

			print "<tr height=\"150px\"><td><a name=\"next%s\"></a>%s</td></tr>" % (nextAnchor, "</td><td>".join([
						"%d" % (1+r),
						"%.4f <br />P: %.2f<br />A: %.2f<br />C: %.2f<br />S: %.2f" % (
							inst.score,
							float(inst.sIndexPred[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedPred),
							float(inst.sIndexArg[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedArg),
							float(inst.sIndexContext[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedContext),
							float(inst.sIndexSlot[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedSlot),
							),
						"%s <br />(%s)" % (irp2, "indexed" if 1 == inst.iIndexed else "predicted"),
						a12.split(",")[1], _prettyC(c2, irc2),
						"<a target=\"_blank\" href=\"https://www.google.co.jp/search?q=%s\">G</a>" % (urllib2.quote("\"%s\"+\"%s\"" % (irp1, irp2))),
						]))
			
			# print "<tr height=\"150px\"><td><a name=\"next%s\"></a>%s</td></tr>" % (nextAnchor, "</td><td>".join([
			# 		"%d" % (1+r),
			# 		"%.4f" % inst.combinedScore,
			# 		"%.2f" % inst.simArgType, "%.2f" % inst.simContext, "%.2f" % inst.assoc,
			# 		inst.instArg, _prettyC(c1, inst.context1), _prettyC(c2, inst.context2),
			# 		"<a target=\"_blank\" href=\"https://www.google.co.jp/search?q=%s\">G</a>" % (urllib2.quote("\"%s\"+\"%s\"" % (inst.source1[2:], inst.source2[2:]))),
			# 		]))
			
			nextAnchor += 1

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
          <a class="navbar-brand" href="#">Results Viewer</a>
        </div>
        <div class="navbar-collapse collapse">
<form action ="./comeon-new.py" method="GET" class="navbar-form navbar-right" role="form">

<div class="form-group">
<input class="form-control" name="query" placeholder="Problem No." type="text" value="%s" />
</div>

<div class="form-group">
<input class="form-control" name="k" type="text" placeholder="K" value="%s" />
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
	fs.getvalue("k") if None != fs.getvalue("query") else "200"
	)


