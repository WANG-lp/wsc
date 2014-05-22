#!/usr/bin/python

import subprocess
import struct

import collections

import cgitb; cgitb.enable()
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
		f														= open("/work/naoya-i/kb/corefevents.tsv")
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

	def _sortedScore(x):
		if "p" == fs.getvalue("sortkey"):
			return x.sRuleAssoc * x.sIndexPred[x.iIndexed] * x.sPredictedPred * \
				x.sIndexSlot[x.iIndexed] * x.sPredictedSlot

		elif "a" == fs.getvalue("sortkey"):
			return \
				0.2 * x.sPredictedArg

		elif "pa" == fs.getvalue("sortkey"):
			return \
				x.sRuleAssoc * x.sIndexPred[x.iIndexed] * x.sPredictedPred + \
				0.2 * x.sPredictedArg
			
		elif "c" == fs.getvalue("sortkey"):
			return \
				0.5 * x.sIndexContext[x.iIndexed] * x.sPredictedContext

		elif "pc" == fs.getvalue("sortkey"):
			return \
				(x.sRuleAssoc * x.sIndexPred[x.iIndexed] * x.sPredictedPred) + \
				(0.5 * x.sIndexContext[x.iIndexed] * x.sPredictedContext)
			
		elif "pac" == fs.getvalue("sortkey"):
			return \
				(x.sRuleAssoc * x.sIndexPred[x.iIndexed] * x.sPredictedPred) + \
				(0.2 * x.sPredictedArg) + \
				(0.5 * x.sIndexContext[x.iIndexed] * x.sPredictedContext)
			
		return x.sRuleAssoc * x.sIndexPred[x.iIndexed] * x.sPredictedPred * \
			x.sIndexSlot[x.iIndexed] * x.sPredictedSlot + \
			(0.2 * x.sPredictedArg) + \
			(0.5 * x.sIndexContext[x.iIndexed] * x.sPredictedContext)

	if 0 > int(fs.getvalue("k")):
		examplesCorrect, examplesWrong = filter(lambda x: 1 == x[0], results.examples), filter(lambda x: 0 == x[0], results.examples)
		sortedRetCor, sortedRetWrong = sorted(examplesCorrect, key=lambda x: _sortedScore(x[1]), reverse=True)[:min(len(results.examples), -int(fs.getvalue("k")))], \
																	 sorted(examplesWrong, key=lambda x: _sortedScore(x[1]), reverse=True)[:min(len(results.examples), -int(fs.getvalue("k")))]
		sortedRet = sorted(sortedRetCor + sortedRetWrong, key=lambda x: _sortedScore(x[1]), reverse=True)
		
	else:
		sortedRet = sorted(results.examples, key=lambda x: _sortedScore(x[1]), reverse=True)[:min(len(results.examples), int(fs.getvalue("k")))]
		
	timeSort, timeStart = time.time() - timeStart, time.time()

	def _coloring(t):
		return t.replace(
			results.ante_lemma.split("-")[0], "<strong style=\"color:red\">%s<sup>+</sup></strong>" % results.ante_lemma.split("-")[0]).replace(
			results.ante_false_lemma.split("-")[0], "<strong style=\"color:blue\">%s<sup>-</sup></strong>" % results.ante_false_lemma.split("-")[0]).replace(
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
		
		header = "R Score Predicates Shared&nbsp;Arg Contexts"

		votesCorrect, votesWrong = 0, 0
		scoreCorrect, scoreWrong = 0, 0
		
		for r, ret in enumerate(sortedRet):
			if   0 == ret[0]: votesCorrect += 1; scoreCorrect += _sortedScore(ret[1])
			elif 1 == ret[0]: votesWrong += 1; scoreWrong += _sortedScore(ret[1])
			
		print "<div class=\"col-md-6\">"
		print "<h3>%s Votes (Score: %.2f) for %s Candidate (%s -- %s)</h3>" % ((votesCorrect, scoreCorrect, "Correct", p1, p2) if 0 == tp else (votesWrong, scoreWrong, "Wrong", p1, p2))
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

			irp1, irp2, ia12, sentdist, irc1, irc2, ig1, ig2, src = ir.split("\t")
			a1,   a2																		= ia12.split(",")
			a12																					= "%s,%s" % (a1, a2)
			sentdist																		= str(sentdist)

			if results.ana_gov == irp1:
				corcon1 = results.ana_con
			elif results.ante_gov == irp1:
				corcon1 = results.ante_con
			elif results.ante_false_gov ==  irp1:
				corcon1 = results.ante_false_con

			if results.ana_gov == irp2:
				corcon2 = results.ana_con
			elif results.ante_gov == irp2:
				corcon2 = results.ante_con
			elif results.ante_false_gov ==  irp2:
				corcon2 = results.ante_false_con

			docfile, docid = src.lstrip("# ").split(":")
			
			print "<tr height=\"150px\"><td><a name=\"next%s\"></a>%s</td></tr>" % (nextAnchor, "</td><td>".join([
				"%d" % (1+r),
				("%.4f <br />p: %.2f<br />a: %.2f<br /><a target=\"_blank\" href=\"siminspect.py?c1=%s&c2=%s\">c: %.2f</a><br />s: %.2f") % (
					(float(inst.sIndexPred[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedPred))*
					(float(inst.sIndexArg[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedArg))*
					(float(inst.sIndexContext[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedContext))*
					(float(inst.sIndexSlot[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedSlot)),
					
					float(inst.sIndexPred[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedPred),
					float(inst.sIndexArg[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedArg),
					urllib2.quote(irc1), corcon1,
					float(inst.sIndexContext[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedContext),
					float(inst.sIndexSlot[int(inst.iIndexed)]) if 0 == inst.iIndexed else float(inst.sPredictedSlot),
				),
				"%s <br />(%s)" % (irp1, "indexed" if 0 == inst.iIndexed else "predicted"),
				"<br />".join(a12.split(",")[0].split("-")),
				_prettyC(c1, irc1) + "<br />(<a target=\"_blank\" href=\"./viewText.py?file=%s&docid=%s&s1=%s&s2=%s\">G</a>)" % (
					docfile, docid, irp1.split("-")[0], irp2.split("-")[0],
					),
			]))

			print "<tr height=\"150px\"><td><a name=\"next%s\"></a>%s</td></tr>" % (nextAnchor, "</td><td>".join([
				"%.2f<br />(p: %.2f)" % (_sortedScore(inst), inst.sRuleAssoc),
				("%.4f <br />p: %.2f<br />a: %.2f<br /><a target=\"_blank\" href=\"siminspect.py?c1=%s&c2=%s\">c: %.2f</a><br />s: %.2f") % (
					(float(inst.sIndexPred[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedPred))*
					(float(inst.sIndexArg[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedArg))*
					(float(inst.sIndexContext[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedContext))*
					(float(inst.sIndexSlot[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedSlot)),
							
					float(inst.sIndexPred[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedPred),
					float(inst.sIndexArg[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedArg),
					urllib2.quote(irc2), corcon2,
					float(inst.sIndexContext[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedContext),
					float(inst.sIndexSlot[int(inst.iIndexed)]) if 1 == inst.iIndexed else float(inst.sPredictedSlot),
				),
				"%s <br />(%s)" % (irp2, "indexed" if 1 == inst.iIndexed else "predicted"),
				"<br />".join(a12.split(",")[1].split("-")),
				_prettyC(c2, irc2),
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
          <a class="navbar-brand" href="#">Nearest Neighbors Viewer - %s</a>
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
<input type="submit" name="sortkey" value="p" class="btn btn-success"/>
<input type="submit" name="sortkey" value="a" class="btn btn-success"/>
<input type="submit" name="sortkey" value="c" class="btn btn-success"/>
<input type="submit" name="sortkey" value="pa" class="btn btn-success"/>
<input type="submit" name="sortkey" value="pc" class="btn btn-success"/>

</form>
        </div><!--/.navbar-collapse -->
      </div>
    </div>


<script src="../bootstrap-3.0.3/dist/js/bootstrap.min.js"></script>
</body></html>
""" % (
	fs.getvalue("sortkey", "pac"),
	fs.getvalue("query") if None != fs.getvalue("query") else "",
	fs.getvalue("k") if None != fs.getvalue("query") else "200"
	)


