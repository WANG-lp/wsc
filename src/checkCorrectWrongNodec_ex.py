"""
   checkCorrectWrongNoDec.py <OutputFilename> <TEST DATA> <PREDICTION>
"""

import sys, re
import collections

rangeEval = None

setting = sys.argv[1]
if setting.startswith("base"):
    filehead = "local/test.google-selpref-LEX-HPOL"
else:
    filehead = "local/test."

predfilename = "%s%s.svmrank.predictions" %(filehead, setting.replace("base", ""))
isvfilename = "%s%s.isv" %(filehead, setting.replace("base", ""))

fsPrediction = open(predfilename)
votes = collections.defaultdict(list)

for lnTestData in open(isvfilename):
	lnPrediction  = fsPrediction.readline().strip().split("\t")[0]
	lnTestData    = lnTestData.split(" ", 2)
	can, qid      = lnTestData[:2]
	qid           = qid[len("qid:"):]

	if None != rangeEval and int(qid) not in rangeEval:
		continue
		
	votes[qid] += [(can, float(lnPrediction))]

for K in xrange(2, 3):
	freq			= collections.defaultdict(int)
	ret = {}
	for qid, NN in votes.iteritems():
		# TAKE k-BEST EXAMPLES.
		kBestExamples = sorted(NN, key=lambda x: x[1])[:K]

		#print kBestExamples
		
		# VOTING
		vote = collections.defaultdict(int)
		
		for can, score in kBestExamples:
			vote[int(can)] += score
		
		if not vote.has_key(1): vote[1] = 99999
		if not vote.has_key(2): vote[2] = 99999

		if vote[1] < vote[2]:
			# print "\t".join([str(int(qid)-1), "CORRECT"])
                        ret[int(qid)-1] = "\t".join([str(int(qid)-1), "CORRECT"])
			# freq["CORRECT"] += 1
		elif vote[1] > vote[2]:
			# print "\t".join([str(int(qid)-1), "WRONG"])
                        ret[int(qid)-1] = "\t".join([str(int(qid)-1), "WRONG"])
			# freq["WRONG"]   += 1
		else:
			# print "\t".join([str(int(qid)-1), "NO DEC"])
                        ret[int(qid)-1] = "\t".join([str(int(qid)-1), "NO DEC"])
			# freq["NO_DECISION"] += 1

        for (k, v) in sorted(ret.items()):
            print v
