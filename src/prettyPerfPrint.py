
import os
import sys

offset = 7 #7 #0
f = open("graph.tmp", "w")

for ln in sys.stdin:
	ln = ln.split("\t")
	
	print >>sys.stderr, ln
	print >>f, "\t".join([ln[0], ln[1+12*0+offset], ln[1+12*1+offset], ln[1+12*2+offset], ln[1+12*3+offset], ln[1+12*4+offset], ln[1+12*5+offset]])

f.close()

f = open("graph.tmp.gnuplot", "w")

print >>f, """
set terminal pdf;
set xlabel "K";
set ylabel "Acc.";

plot "graph.tmp" using 1:2 with lp title "Baseline", \
     "graph.tmp" using 1:3 with lp title "PMI", \
     "graph.tmp" using 1:4 with lp title "PMI+arg", \
     "graph.tmp" using 1:5 with lp title "PMI+arg+con", \
     "graph.tmp" using 1:6 with lp title "PMI+con", \
     "graph.tmp" using 1:7 with lp title "PMI (kNN)"
"""

f.close()

os.system("gnuplot graph.tmp.gnuplot")
