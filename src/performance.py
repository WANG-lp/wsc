
import collections
import sys

def _getClass(xk, yk, x, y, fInvertPolarity = False):
	if "None" == xk: xk = "0"
	if "None" == yk: yk = "0"
	if "None" == x: x = "0"
	if "None" == y: y = "0"

	x, y = float(x), float(y)
	xk, yk = float(xk), float(yk)

	if fInvertPolarity: x, y = -x, -y

	return xk != 0, yk != 0, x > y

methods = "numRules cirPMI cirArg cirPMICon cirArgPMI cirArgCon cirArgConPMI iriPred iriPredArg iriPredArgCon".split()
m   	  = dict([(k, collections.defaultdict(int)) for k in methods])

for ln in sys.stdin:
	ln = ln.strip().split("\t")

	# m["numRules"][_getClass(ln[1], ln[2], ln[1], ln[2])] += 1
	# m["cirPMI"][_getClass(ln[1], ln[2], ln[3], ln[4])] += 1
	# m["cirArg"][_getClass(ln[1], ln[2], ln[5], ln[6], fInvertPolarity=True)] += 1
	# m["cirPMICon"][_getClass(ln[1], ln[2], ln[7], ln[8], fInvertPolarity=True)] += 1
	# m["cirArgPMI"][_getClass(ln[1], ln[2], ln[9], ln[10], fInvertPolarity=True)] += 1
	# m["cirArgCon"][_getClass(ln[1], ln[2], ln[11], ln[12], fInvertPolarity=True)] += 1
	# m["cirArgConPMI"][_getClass(ln[1], ln[2], ln[13], ln[14], fInvertPolarity=True)] += 1

	m["iriPred"][_getClass(ln[1], ln[2], ln[5], ln[6])] += 1
	m["iriPredArg"][_getClass(ln[1], ln[2], ln[7], ln[8])] += 1
	m["iriPredArgCon"][_getClass(ln[1], ln[2], ln[9], ln[10])] += 1
		
vec = []

# print m

for k in methods:
	numCorrect, numWrong, numNoDec = 0, 0, 0
	numTTCorrect, numTTWrong, numTTNoDec = 0, 0, 0
	numTFCorrect, numTFWrong, numTFNoDec = 0, 0, 0
	numFTCorrect, numFTWrong, numFTNoDec = 0, 0, 0

	if 0 == len(m[k]): continue

	for c in [(True,True,True), (True,True,False), (True,False,True), (False,True,False), (False,False,True), (False,False,False)]:
		# numCorrect += m[k][c] if (c[0] or c[1]) and c[2] else 0
		# numWrong += m[k][c] if (c[0] or c[1]) and not c[2] else 0
		# numNoDec += m[k][c] if not(c[0] or c[1]) else 0		
		numCorrect += m[k][c] if c[2] else 0
		numWrong += m[k][c] if not c[2] else 0
		# numNoDec += m[k][c] if not(c[0] or c[1]) else 0
		
		numTTCorrect += m[k][c] if (c[0] and c[1]) and c[2] else 0
		numTTWrong += m[k][c] if (c[0] and c[1]) and not c[2] else 0

		numTFCorrect += m[k][c] if (c[0] and not c[1]) and c[2] else 0
		numTFWrong += m[k][c] if (c[0] and not c[1]) and not c[2] else 0

		numFTCorrect += m[k][c] if (not c[0] and c[1]) and c[2] else 0
		numFTWrong += m[k][c] if (not c[0] and c[1]) and not c[2] else 0
		
	numCheckSum = numCorrect + numWrong + numNoDec
	numTTCheckSum = numTTCorrect + numTTWrong

	vec += [
		100.0*numCorrect/numCheckSum if numCheckSum > 0 else 0,
		100.0*numWrong/numCheckSum if numCheckSum > 0 else 0,
		100.0*numNoDec/numCheckSum if numCheckSum > 0 else 0, 
		numCorrect, numWrong, numNoDec, numCheckSum,
		# 100.0*numTTCorrect/numTTCheckSum if numTTCheckSum > 0 else 0, 100.0*numTTWrong/numTTCheckSum if numTTCheckSum > 0 else 0,
		# numTTCorrect, numTTWrong, numTTCheckSum,
#		numTFCorrect, numTFWrong, numFTCorrect, numFTWrong,
		]
	
print "\t".join([sys.argv[1], "\t".join(["%.1f" % x if isinstance(x, float) else "%s" % x for x in vec])])
