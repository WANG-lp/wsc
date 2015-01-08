import sys

for ln in open(sys.argv[1]):
	x = eval(ln)

	print x[1]
