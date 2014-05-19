
import os
import sys

offset = 7 #7 #0
MAX_DATA = 9
names = "Baseline PMI PMI*arg PMI*arg*con PMI*con kNN-PMI PMI+arg PMI+con PMI+arg+con".split()

for idData, fnData in enumerate(sys.argv[1:]):
	f = open("graph%d.tmp" % idData, "w")

	maxAccuracy = [(0, 0, []) for i in xrange(MAX_DATA)]
	k = 0

	for ln in open(fnData):
		ln = ln.strip().split("\t")
		k += 1
	
		print >>f, "\t".join([ln[0]] + [ln[1+12*i+offset] if 1+12*i+offset < len(ln) else "0" for i in xrange(MAX_DATA)])

		for i in xrange(MAX_DATA):
			maxAccuracy[i] = max(maxAccuracy[i], (ln[1+12*i+offset] if 1+12*i+offset < len(ln) else "0", k, ln), key=lambda x: float(x[0]))

	print >>sys.stderr, "=== Best results for %s:" % fnData

	for i in xrange(MAX_DATA):
		if 1+12*i+offset < len(maxAccuracy[i][2]):
			print >>sys.stderr, "%s K=%s Acc:%s%% (%s/%s)" % (names[i].ljust(15), str(maxAccuracy[i][1]).ljust(5), maxAccuracy[i][0], maxAccuracy[i][2][1+12*i+offset+2], maxAccuracy[i][2][1+12*i+offset+4])

	print >>sys.stderr, ""
	
	f.close()

f = open("graph.tmp.gnuplot", "w")

print >>f, """
set terminal pdf;

set xlabel "K";
set ylabel "Acc.";
set yrange [52:65];

set key font "Helvetica,4";
set tics font "Helvetica,4";
set multiplot layout %s;

""" % "1,1 1,2 2,2 2,2".split()[len(sys.argv[1:])-1]

for idData, fnData in enumerate(sys.argv[1:]):
	print >>f, """
set title "%s";
plot """ % (os.path.basename(fnData)),
	
	print >>f, ", ".join(["\"graph%s.tmp\" using 1:%d with lp ps 0.2 title \"%s\"" % (idData, 2+i, names[i])
												for i in xrange(MAX_DATA)])

	print >>f, ""
		
f.close()

os.system("gnuplot graph.tmp.gnuplot")
