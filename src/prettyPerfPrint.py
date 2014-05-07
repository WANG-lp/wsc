
import os
import sys

f = open("graph.tmp", "w")

for ln in sys.stdin:
	ln = ln.split("\t")
	
	print >>f, "\t".join([ln[0], ln[1+12*0+7], ln[1+12*1+7], ln[1+12*2+7], ln[1+12*3+7]])

f.close()

f = open("graph.tmp.gnuplot", "w")

print >>f, """
set terminal pdf;
set xlabel "K";
set ylabel "Acc.";

plot "graph.tmp" using 1:2 with lp title "Baseline", \
     "graph.tmp" using 1:3 with lp title "PMI", \
     "graph.tmp" using 1:4 with lp title "PMI+arg", \
     "graph.tmp" using 1:5 with lp title "PMI+arg+con"
"""

f.close()

os.system("gnuplot graph.tmp.gnuplot")
