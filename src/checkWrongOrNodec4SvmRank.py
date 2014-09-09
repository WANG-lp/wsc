"""
   checkWrongOrNoDec4SvmRank.py <NAME_OF_ROW> <TEST DATA> <PREDICTION>
"""

import sys, re
import collections

rangeEval = None

if 5 == len(sys.argv):
	rangeEval = []
	
	for ln in open(sys.argv[4]):
		matches = re.findall("pid=(.*?) ", ln)
		
		if len(matches) > 0:
			rangeEval += [int(matches[0])]

	print >>sys.stderr, "Range evaluation enabled: ", rangeEval
	
fsPrediction = open(sys.argv[3])
votes = collections.defaultdict(list)

for lnTestData in open(sys.argv[2]):
	lnPrediction  = fsPrediction.readline().strip().split("\t")[0]
	lnTestData    = lnTestData.split(" ", 2)
	can, qid      = lnTestData[:2]
	qid           = qid[len("qid:"):]

	if None != rangeEval and int(qid) not in rangeEval:
		continue
		
	votes[qid] += [(can, float(lnPrediction))]

fsOut = open("tmp", "w")

for K in xrange(2, 3):
	freq			= collections.defaultdict(int)
	
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
			print >>fsOut, "\t".join([str(int(qid)-1), "CORRECT"])
			freq["CORRECT"] += 1
		elif vote[1] > vote[2]:
			print >>fsOut, "\t".join([str(int(qid)-1), "WRONG"])
			freq["WRONG"]   += 1
		else:
			print >>fsOut, "\t".join([str(int(qid)-1), "NO DEC"])
			freq["NO_DECISION"] += 1

	rows = []

	for t in "CORRECT WRONG NO_DECISION".split():
		rows += ["%.1f\\%% (%3d/%3d)" % (
			100.0 * freq[t] / sum(freq.values()), freq[t],
			sum(freq.values()) )]

	print " & ".join(map(lambda x: x.replace("_", "\\_").replace("|", " + ").replace("^", "\\^"), [sys.argv[1], "K=%d" % K] + rows)), "\\\\"
		
