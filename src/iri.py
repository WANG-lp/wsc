
import cdb
import math

import urllib2

import struct

import readline
import collections

import os

import mmap
import sys
import subprocess

result_t = collections.namedtuple(
	"result_t",
	"score iPredicted iIndexed sRuleAssoc" +\
		" sIndexPred sIndexArg sIndexContext sIndexSlot" +\
		" sPredictedPred sPredictedArg sPredictedContext sPredictedSlot" +\
		" offset length"
	)

def _cdbdefget(f, key, de):
	r = f.get(key)
	return r if None != r else de

def _npmi(xy, x, y):
        if xy != 0:
                return 0.5*(1+(math.log(1.0 * xy / (x * y), 2) / -math.log(xy, 2)))
        else:
                return 0

class iri_t:
	def __init__(self, fnCorefEventsTsv, pathServer, dirKb, fnLSH, numPara = 12, fUseMemoryMap = False):
		# LOADING THE HASH TABLE.5
		print >>sys.stderr, "Loading..."

		opts = []

		if fUseMemoryMap: opts += ["-d"]
		
		self.procSearchServer = subprocess.Popen(
			"%s -i %s -k %s -d %s -m %d %s" % (
				os.path.join(pathServer, "similaritySearch"), fnLSH, dirKb,
				fnCorefEventsTsv, numPara, " ".join(opts)),
			shell = True,
			stdin = subprocess.PIPE, stdout = subprocess.PIPE, )#stderr = subprocess.PIPE)

		# FOR PMI
		self.cdbPreds = cdb.init(os.path.join(dirKb, "tuples.cdb"))
		self.totalFreqPreds = int(open(os.path.join(dirKb, "tuples.totalfreq.txt")).read())
		
		assert("200 OK" == self.procSearchServer.stdout.readline().strip())

	def predict(self, predicate, context, slot, focusedArgument, predictedPredicate = None, predictedContext = None, predictedSlot = None, predictedFocusedArgument = None, threshold = 0, limit = 10000, pos1 = '', pos2 = ''):
		keyCache = predicate + context + str(threshold)

		if "" != pos1: pos1 = pos1.lower()[0]
		if "" != pos2: pos2 = pos2.lower()[0]
		
		print >>self.procSearchServer.stdin, "p", predicate
		print >>self.procSearchServer.stdin, "c", context
		print >>self.procSearchServer.stdin, "s", slot
		#print >>self.procSearchServer.stdin, "a", focusedArgument
		print >>self.procSearchServer.stdin, "a", predictedFocusedArgument

		# TO TURN ON SIMILARITY SEARCH,
		# print >>self.procSearchServer.stdin, "+", "y"

		# TO TURN OFF SIMILARITY SEARCH,
		# print >>self.procSearchServer.stdin, "+", "n"

		if None != predictedFocusedArgument:
			print >>self.procSearchServer.stdin, "~p", predictedPredicate
			print >>self.procSearchServer.stdin, "~c", predictedContext
			print >>self.procSearchServer.stdin, "~s", predictedSlot
			print >>self.procSearchServer.stdin, "~a", predictedFocusedArgument

		print >>self.procSearchServer.stdin, "t", threshold
		print >>self.procSearchServer.stdin, "m", limit
		print >>self.procSearchServer.stdin, ""

		# READ THE NUMBER OF IRIs.
		numExactMatchIRIs = int(self.procSearchServer.stdout.readline())
		numIRIs = int(self.procSearchServer.stdout.readline())
			
		ret     = []

		# CALCULATE PMI
		pr1, pr2 = "%s:%s" % (predicate, slot), "%s:%s" % (predictedPredicate, predictedSlot)
		if pr1 > pr2: pr1, pr2 = pr2, pr1

		spassoc = _npmi(1.0*numExactMatchIRIs / self.totalFreqPreds,
					1.0*int(_cdbdefget(self.cdbPreds, pr1, 1)) / self.totalFreqPreds,
					1.0*int(_cdbdefget(self.cdbPreds, pr2, 1)) / self.totalFreqPreds)
		print >>sys.stderr, pr1, pr2, numExactMatchIRIs, int(_cdbdefget(self.cdbPreds, pr1, 1)), int(_cdbdefget(self.cdbPreds, pr2, 1))
		
		for i in xrange(numIRIs):
			iIndexed, iPredicted, offset, length, \
					score, \
			 		spm1, scm1, sm1, sam1, \
			 		spm2, scm2, sm2, sam2, \
			 		spm, scm, sm, sam \
			 		= struct.unpack("=HHQHf" + "f"*(4*3), self.procSearchServer.stdout.read(2+2+8+2+4+4*4*3))

			score *= spassoc
			
			try:
				line = self.procSearchServer.stdout.readline().strip().split("\t")
			except ValueError:
				raise "Protocol Error"
				continue

                        # result_t = collections.namedtuple(
                        #     "result_t",
                        #     "score iPredicted iIndexed sRuleAssoc" +\
                        #     " sIndexPred sIndexArg sIndexContext sIndexSlot" +\
                        #     " sPredictedPred sPredictedArg sPredictedContext sPredictedSlot" +\
                        #     " offset length"
                        # )
        
			yield result_t(score, iPredicted, iIndexed, spassoc,
										 (spm1, spm2), (sam1, sam2), (scm1, scm2), (sm1, sm2),
										 spm, sam, scm, sm,
										 offset, length,
										 ), line

if "__main__" == __name__:
	# UNIT TEST.
	iri = iri_t(
		"/work/naoya-i/kb/corefevents.tsv",
		"/home/naoya-i/work/wsc/bin",
		"/work/naoya-i/kb",
		sys.argv[1])

	try:
		threshold = 0
		limit     = 1000
		
		while True:
			x					 = raw_input("? ")
			numResults = 0

			if x.startswith("t "):
				threshold = int(x[2:])
				print "Threshold =", threshold
				continue

			if x.startswith("l "):
				limit = int(x[2:])
				print "Limit =", limit
				continue
			
			if len(x.strip().split("\t")) != 4 and len(x.strip().split("\t")) != 8:
				print "Format: predicate[TAB]context[TAB]slot[TAB]focused argument", "or"
				print "Format: predicate[TAB]context[TAB]slot[TAB]focused argument[TAB]predicate[TAB]context[TAB]slot[TAB]focused argument", "or"
				continue

			try:
				iris = sorted(iri.predict(*x.strip().split("\t"), threshold=threshold, limit=limit),
											key=lambda x:
												x[0].sIndexPred[x[0].iIndexed]*x[0].sPredictedPred+\
												x[0].sIndexSlot[x[0].iIndexed]*x[0].sPredictedSlot+\
												x[0].sIndexContext[x[0].iIndexed]*x[0].sPredictedContext+\
												0.1*(x[0].sIndexArg[x[0].iIndexed]*x[0].sPredictedArg)
											, reverse=True)

			except KeyboardInterrupt:
				print "Aborted."
				continue

			try:
				f = open("/home/naoya-i/work/wsc/local/webint/kbsearch-%s.html" % sys.argv[2], "w")

				print >>f, """<html><head>
<link href="./bootstrap-3.0.3/dist/css/bootstrap.min.css" rel="stylesheet" />
</head>
<body>
<div class="wrap">
<div class="container">
<h1 style="padding-top: 50px">%s</h1>
""" % "&nbsp;&nbsp;&nbsp;&nbsp;".join(x.split("\t"))

				print >>f, """<p>%d entries found. </p>
<table class="table table-striped">
""" % len(iris)
				
				for ir, raw in iris:
					numResults += 1
					print ir, raw
					print >>f, "<tr><td>%s</td></tr>" % "</td><td>".join(
						["%.4f<br />P: %.2f<br />C: %.2f<br />S: %.2f<br />A: %.2f" % (
								ir.score, ir.sIndexPred[ir.iIndexed], ir.sIndexContext[ir.iIndexed],
								ir.sIndexSlot[ir.iIndexed], ir.sIndexArg[ir.iIndexed])] + \
							[raw[0] + ("<br />(indexed)" if 0 == ir.iIndexed else ""),
							 raw[1] + ("<br />(indexed)" if 1 == ir.iIndexed else ""),
							 "<br />".join(raw[2].split(",")),
							 "<br />".join(raw[4].split(" ")),
							 "<br />".join(raw[5].split(" ")), 
							 "<a target=\"_blank\" href=\"http://www.cl.ecei.tohoku.ac.jp/henry/cgi-bin/viewText.py?file=%s&docid=%s&s1=%s&s2=%s\">T</a>" % (
								raw[-1][:9], raw[-1][10:],
								urllib2.quote(raw[0].split(":")[0][:-2]), urllib2.quote(raw[1].split(":")[0][:-2]),
								)
								]
						)

				print numResults, "entries have been found."

				print >>f, "</table>"
				print >>f, """</div>
</div>

<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <a class="navbar-brand" href="#">Inference Rule Instances Viewer</a>
        </div>
        <div class="navbar-collapse collapse">

        </div><!--/.navbar-collapse -->
      </div>
    </div>


<script src="./bootstrap-3.0.3/dist/js/bootstrap.min.js"></script>
</body></html>
"""
				
				f.close()

			except KeyboardInterrupt:
				pass

	except EOFError:
		print "^D"
		print "I'm leaving! Have a nice day!"
		
