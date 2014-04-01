
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

class iri_t:
	def __init__(self, fnCorefEventsTsv, pathServer, dirKb, fnBin, numPara = 12, fUseMemoryMap = False):
		# LOADING THE HASH TABLE.5
		print >>sys.stderr, "Loading..."

		opts = []

		if fUseMemoryMap: opts += ["-d"]
		
		self.procSearchServer = subprocess.Popen(
			"%s -k %s -i %s -c %s -v %s -t %s -m %d %s" % (
				os.path.join(pathServer, "similaritySearch"), dirKb, fnBin,
				fnCorefEventsTsv, fnCorefEventsTsv.replace(".tsv", ".vocab.bin"), fnCorefEventsTsv.replace(".tsv", ".vocabct.bin"),
				numPara, " ".join(opts)),
			shell = True,
			stdin = subprocess.PIPE, stdout = subprocess.PIPE, )#stderr = subprocess.PIPE)

		# self.procSimServer = subprocess.Popen(
		# 	"%s -k %s -m %d" % (os.path.join(pathServer, "similarity"), dirKb, numPara),
		# 	shell = True,
		# 	stdin = subprocess.PIPE, stdout = subprocess.PIPE, )#stderr = subprocess.PIPE)
		
		# assert("200 OK" == self.procSimServer.stdout.readline().strip())
		assert("200 OK" == self.procSearchServer.stdout.readline().strip())

		self.cacheSearchServer = {}

	def predict(self, predicate, context, slot, focusedArgument, predictedPredicate = None, predictedContext = None, predictedSlot = None, predictedFocusedArgument = None, threshold = 0):
		keyCache = predicate + context + str(threshold)
		
		if not self.cacheSearchServer.has_key(keyCache):
			print >>self.procSearchServer.stdin, "p", predicate
			print >>self.procSearchServer.stdin, "c", context
			print >>self.procSearchServer.stdin, "s", slot
			print >>self.procSearchServer.stdin, "a", focusedArgument

			if None != predictedFocusedArgument:
				print >>self.procSearchServer.stdin, "~p", predictedPredicate
				print >>self.procSearchServer.stdin, "~c", predictedContext
				print >>self.procSearchServer.stdin, "~s", predictedSlot
				print >>self.procSearchServer.stdin, "~a", predictedFocusedArgument
				
			print >>self.procSearchServer.stdin, "t", threshold
			print >>self.procSearchServer.stdin, ""

			# READ THE NUMBER OF IRIs.
			numIRIs = int(self.procSearchServer.stdout.readline())

		else:
			print >>sys.stderr, "Cache hit! (key=%s)" % keyCache
			numIRIs = len(self.cacheSearchServer[keyCache])
			
		ret     = []
		
		for i in xrange(numIRIs):
			iIndexed, iPredicted, offset, length, \
					score, \
			 		spm1, scm1, sm1, sam1, \
			 		spm2, scm2, sm2, sam2, \
			 		spm, scm, sm, sam \
			 		= struct.unpack("=HHQHf" + "f"*(4*3), self.procSearchServer.stdout.read(2+2+8+2+4+4*4*3))

			try:
				line = self.procSearchServer.stdout.readline().strip().split("\t")
			except ValueError:
				continue
			
			yield result_t(score,
										 iPredicted, iIndexed,
										 0.0,
										 (spm1, spm2), (sam1, sam2), (scm1, scm2), (sm1, sm2),
										 spm, sam, scm, sm,
										 offset, length,
										 ), line

		# if not self.cacheSearchServer.has_key(keyCache):
		# 	self.cacheSearchServer[keyCache] = ret

if "__main__" == __name__:
	# UNIT TEST.
	iri = iri_t(
		sys.argv[2],
		"/home/naoya-i/work/wsc/bin",
		"/work/naoya-i/kb",
		sys.argv[1])

	try:
		threshold = 0
		
		while True:
			x					 = raw_input("? ")
			numResults = 0

			if x.startswith("t "):
				threshold = int(x[2:])
				print "Threshold =", threshold
				continue
				
			if len(x.strip().split("\t")) != 4 and len(x.strip().split("\t")) != 8:
				print "Format: predicate[TAB]context[TAB]slot[TAB]focused argument"
				continue

			try:
				iris = sorted(iri.predict(*x.strip().split("\t"), threshold=threshold), key=lambda x: x[0].score)

			except KeyboardInterrupt:
				print "Aborted."
				continue

			try:
				f = open("/home/naoya-i/work/wsc/local/webint/kb.html", "w")

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
								raw[-1][2:2+9], raw[-1][12:],
								urllib2.quote(raw[-3][2:]), urllib2.quote(raw[-2][2:]),
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
		
