
import re

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
	def __init__(self, fnCorefEventsTsv, pathServer, dirKb, pa, fnWeightMap = "data/weightmap.tsv", numPara = 12, fUseMemoryMap = False):
		# LOADING THE HASH TABLE.5
		print >>sys.stderr, "Loading..."

		opts = []

		if fUseMemoryMap: opts += ["-q"]
                if pa.kbsmall:
                    opts += ["-c /work/jun-s/kb/corefevents.0909small.cdblist/"]
                else:
                    if pa.oldkb == True:
                        opts += ["-c /work/jun-s/kb/corefevents.cdblist/"]
                    else:
                        opts += ["-c /work/jun-s/kb/corefevents.0909.cdblist/"]
                        
                print >>sys.stderr, "OPTS = %s" % (" ".join(opts))
		
		self.procSearchServer = subprocess.Popen(
			"%s -k %s -d %s -m %d -w %s %s" % (
				os.path.join(pathServer, "similaritySearch"), dirKb,
				fnCorefEventsTsv, numPara, fnWeightMap, " ".join(opts)),
			shell = True,
			stdin = subprocess.PIPE, stdout = subprocess.PIPE, )#stderr = subprocess.PIPE)
		
		# FOR PMI
                if pa.oldkb == True:
                    self.cdbPreds = cdb.init(os.path.join(dirKb, "tuples.cdb"))
                    self.totalFreqPreds = int(open(os.path.join(dirKb, "tuples.totalfreq.txt")).read())
                else:
                    self.cdbPreds = cdb.init(os.path.join(dirKb, "tuples.0909.cdb"))
                    self.totalFreqPreds = int(open(os.path.join(dirKb, "tuples.0909.totalfreq.txt")).read())


		self.corefeventsFile = open(fnCorefEventsTsv, "r")
		self.corefeventsMmap = mmap.mmap(self.corefeventsFile.fileno(), 0, prot=mmap.PROT_READ)

		self.fnWeightMap = fnWeightMap
		self.fEnumMode    = False
		
		assert("200 OK" == self.procSearchServer.stdout.readline().strip())

	def setWNSimilaritySearch(self, flag):
		print >>self.procSearchServer.stdin, "w", "y" if flag else "n"
        
	def setW2VSimilaritySearch(self, flag):
		print >>self.procSearchServer.stdin, "+", "y" if flag else "n"

	def setEnumMode(self, flag):
		self.fEnumMode = flag
		print >>self.procSearchServer.stdin, "e", "y" if flag else "n"
                
        # def getNumRules(self, predicate, context, slot, focusedArgument,
	# 						predictedPredicate = None, predictedContext = None, predictedSlot = None, predictedFocusedArgument = None,
	# 						threshold = 0, limit = 10000, pos1 = '', pos2 = '', fVectorMode = False):
        #         keyCache = predicate + context + str(threshold)

        #         if "" != pos1: pos1 = pos1.lower()[0]
	# 	if "" != pos2: pos2 = pos2.lower()[0]
		
	# 	print >>self.procSearchServer.stdin, "p", predicate
	# 	print >>self.procSearchServer.stdin, "c", context
	# 	print >>self.procSearchServer.stdin, "s", slot
	# 	#print >>self.procSearchServer.stdin, "a", focusedArgument
	# 	print >>self.procSearchServer.stdin, "a", predictedFocusedArgument

	# 	if None != predictedFocusedArgument:
	# 		print >>self.procSearchServer.stdin, "~p", predictedPredicate
	# 		print >>self.procSearchServer.stdin, "~c", predictedContext
	# 		print >>self.procSearchServer.stdin, "~s", predictedSlot
	# 		print >>self.procSearchServer.stdin, "~a", predictedFocusedArgument

	# 	print >>self.procSearchServer.stdin, "t", threshold
	# 	print >>self.procSearchServer.stdin, "m", limit
	# 	print >>self.procSearchServer.stdin, "v", "y" if fVectorMode else "n"
	# 	print >>self.procSearchServer.stdin, ""
                
        #         numExactMatchIRIs = int(self.procSearchServer.stdout.readline())
	# 	numIRIs = int(self.procSearchServer.stdout.readline())
        #         return numIRIs
            
	def predict(self, predicate, context, slot, focusedArgument, simretry,
                    predictedPredicate = None, predictedContext = None, predictedSlot = None, predictedFocusedArgument = None,  
                    threshold = 0, limit = 10000, pos1 = '', pos2 = '', fVectorMode = False):
		keyCache = predicate + context + str(threshold)

		if "" != pos1: pos1 = pos1.lower()[0]
		if "" != pos2: pos2 = pos2.lower()[0]
		
		print >>self.procSearchServer.stdin, "p", predicate
		print >>self.procSearchServer.stdin, "c", context
		print >>self.procSearchServer.stdin, "s", slot
		#print >>self.procSearchServer.stdin, "a", focusedArgument
		print >>self.procSearchServer.stdin, "a", predictedFocusedArgument

		if None != predictedFocusedArgument:
			print >>self.procSearchServer.stdin, "~p", predictedPredicate
			print >>self.procSearchServer.stdin, "~c", predictedContext
			print >>self.procSearchServer.stdin, "~s", predictedSlot
			print >>self.procSearchServer.stdin, "~a", predictedFocusedArgument

		print >>self.procSearchServer.stdin, "t", threshold
		print >>self.procSearchServer.stdin, "m", limit
		print >>self.procSearchServer.stdin, "v", "y" if fVectorMode else "n"
		print >>self.procSearchServer.stdin, ""

		# READ THE NUMBER OF IRIs.
		numExactMatchIRIs = int(self.procSearchServer.stdout.readline())
		numIRIs = int(self.procSearchServer.stdout.readline())
                
		ret     = []

                if numIRIs == 0 and simretry == True:
                    print >>sys.stderr, "CHANGE SIMWN ON"    
                    self.setWNSimilaritySearch(True)
                    simretry = False
                    # print >>sys.stderr, predicate, context, slot, focusedArgument, simretry, ff, predictedPredicate, predictedContext, predictedSlot, predictedFocusedArgument, threshold, limit, pos1, pos2, fVectorMode
                    for retx, rawx, vecx in self.predict(predicate, context, slot, focusedArgument, simretry, predictedPredicate, predictedContext, predictedSlot, predictedFocusedArgument, threshold, limit, pos1, pos2, fVectorMode):
                        yield retx, rawx, vecx
                    return
                
		# CALCULATE PMI
		pr1, pr2 = "%s:%s" % (predicate, slot), "%s:%s" % (predictedPredicate, predictedSlot)
		if pr1 > pr2: pr1, pr2 = pr2, pr1

		spassoc = _npmi(1.0*numExactMatchIRIs / self.totalFreqPreds,
					1.0*int(_cdbdefget(self.cdbPreds, pr1, 1)) / self.totalFreqPreds,
					1.0*int(_cdbdefget(self.cdbPreds, pr2, 1)) / self.totalFreqPreds)
		print >>sys.stderr, pr1, pr2, numExactMatchIRIs, int(_cdbdefget(self.cdbPreds, pr1, 1)), int(_cdbdefget(self.cdbPreds, pr2, 1))

                # if numIRIs == 0 and simretry == True:
                #     print >>sys.stderr, "CHANGE SIMWN ON"    
                #     self.setWNSimilaritySearch(True)
                #     simretry = False
                #     # print >>sys.stderr, predicate, context, slot, focusedArgument, simretry, ff, predictedPredicate, predictedContext, predictedSlot, predictedFocusedArgument, threshold, limit, pos1, pos2, fVectorMode
                #     for retx, rawx, vecx in self.predict(predicate, context, slot, focusedArgument, simretry, predictedPredicate, predictedContext, predictedSlot, predictedFocusedArgument, threshold, limit, pos1, pos2, fVectorMode):
                #         yield retx, rawx, vecx
                #     return
                    
                
		for i in xrange(numIRIs):
			if self.fEnumMode:
				yield self.procSearchServer.stdout.readline().strip().split("\t")
				continue
				
			if fVectorMode:
				yield map(lambda x: tuple(x.rsplit(":", 1)), self.procSearchServer.stdout.readline().strip().split(" "))
				continue
				
			iIndexed, iPredicted, offset, length, \
					score, \
			 		spm1, scm1, sm1, sam1, \
			 		spm2, scm2, sm2, sam2, \
			 		spm, scm, sm, sam \
			 		= struct.unpack("=HHQHf" + "f"*(4*3), self.procSearchServer.stdout.read(2+2+8+2+4+4*4*3))

			try:
				line   = self.procSearchServer.stdout.readline().strip().split("\t")
				vector = map(lambda y: map(lambda x: tuple(x.rsplit(":", 1)), y.split(" ")), self.procSearchServer.stdout.readline().strip().split("\t"))
				
			except ValueError:
				raise "Protocol Error"
				continue

                        if numExactMatchIRIs == 0:
                            npr1 = line[0]
                            npr2 = line[1]
                            if npr1 > npr2: npr1, npr2 = npr2, npr1
                            spassoc = _npmi(1.0*numIRIs / self.totalFreqPreds,
                                        1.0*int(_cdbdefget(self.cdbPreds, npr1, 1)) / self.totalFreqPreds,
                                        1.0*int(_cdbdefget(self.cdbPreds, npr2, 1)) / self.totalFreqPreds)
                        
			score *= spassoc
			
                                
                        # result_t = collections.namedtuple(
                        #     "result_t",
                        #     "score iPredicted iIndexed sRuleAssoc" +\
                        #     " sIndexPred sIndexArg sIndexContext sIndexSlot" +\
                        #     " sPredictedPred sPredictedArg sPredictedContext sPredictedSlot" +\
                        #     " offset length"
                        # )
                        # print >>sys.stderr, iPredicted, iIndexed, line, numExactMatchIRIs, numIRIs, spassoc, score
        
			yield result_t(score, iPredicted, iIndexed, spassoc,
										 (spm1, spm2), (sam1, sam2), (scm1, scm2), (sm1, sm2),
										 spm, sam, scm, sm,
										 offset, length,
										 ), line, vector

if "__main__" == __name__:
	# UNIT TEST.
	iri = iri_t(
		"/work/jun-s/kb/corefevents.tsv",
		"/home/napya-i/work/wsc/bin",
		"/work/jun-s/kb",
		fUseMemoryMap=True
	)

	try:
		threshold = 0
		limit     = 1000
		vectorMode = False
		
		while True:
			x					 = raw_input("? ")
			numResults = 0

			if x.startswith("v "):
				vectorMode = "v y" == x.strip()
				continue

			if x.startswith("w "):
				iri.setWNSimilaritySearch("w y" == x.strip())
				continue
				
			if x.startswith("s "):
				iri.setW2VSimilaritySearch("s y" == x.strip())
				continue
				
			if x.startswith("t "):
				threshold = int(x[2:])
				print "Threshold =", threshold
				continue

			if x.startswith("l "):
				limit = int(x[2:])
				print "Limit =", limit
				continue
			
			if len(re.split("[,\t]", x.strip())) != 4 and len(re.split("[,\t]", x.strip())) != 8:
				print "Format: predicate[TAB]context[TAB]slot[TAB]focused argument", "or"
				print "Format: predicate[TAB]context[TAB]slot[TAB]focused argument[TAB]predicate[TAB]context[TAB]slot[TAB]focused argument", "or"
				continue

			try:
				ip1, ic1, is1, ia1, ip2, ic2, is2, ia2 = re.split("[,\t]", x.strip())
				ret = iri.predict(*re.split("[,\t]", x.strip()), threshold=threshold, limit=limit, fVectorMode=vectorMode)
									
				if vectorMode:
					for vector in ret:
						print vector
						
				else:
					iris = sorted(ret,
												key=lambda x:
												x[0].sIndexPred[x[0].iIndexed]*x[0].sPredictedPred*\
												x[0].sIndexSlot[x[0].iIndexed]*x[0].sPredictedSlot*\
												x[0].sIndexContext[x[0].iIndexed]*x[0].sPredictedContext*\
												x[0].sPredictedArg,
												reverse=True)

			except KeyboardInterrupt:
				print "Aborted."
				continue

			if vectorMode:
				continue
			
			try:
				f = open("/home/naoya-i/work/wsc/local/webint/kbsearch-%s.html" % sys.argv[1], "w")

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
				
				for ir, raw, vec in iris:
					raw = iri.corefeventsMmap[ir.offset:ir.offset+ir.length].split("\t")
					raw[-1] = raw[-1][2:]
					
					numResults += 1
					#print ir, raw
					print >>f, "<tr><td>%s</td></tr>" % "</td><td>".join(
						["%.4f<br />P: %.2f, %.2f<br />C: <a target=\"_blank\" href=\"cgi-bin/siminspect.py?c1=%s&c2=%s\">%.2f</a>, <a target=\"_blank\" href=\"cgi-bin/siminspect.py?c1=%s&c2=%s\">%.2f</a><br />S: %.2f, %.2f<br />A: %.2f" % (
							ir.score,
							ir.sIndexPred[ir.iIndexed], ir.sPredictedPred,
							urllib2.quote(raw[4]), urllib2.quote(ic1 if 0 == ir.iIndexed else ic2),
							ir.sIndexContext[ir.iIndexed],
							urllib2.quote(raw[5]), urllib2.quote(ic2 if 0 == ir.iIndexed else ic1),
							ir.sPredictedContext,
							ir.sIndexSlot[ir.iIndexed], ir.sPredictedSlot,
							ir.sPredictedArg)] + \
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
		
