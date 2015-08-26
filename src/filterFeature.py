
import re
import sys

# ARGS: exc|inc filter1 filter2 ...
q = 2

for ln in sys.stdin:
	ln = ln.strip().split(" ")

	print " ".join(ln[:q]),

	for e in ln[q:]:
		e				= e.rsplit(":", 1)
		f_print = True if "exc" == sys.argv[1] else False
		
		for c in sys.argv[2:]:
                        if None != re.search(c, e[0]):
				if "inc" == sys.argv[1]:
					f_print = True
				elif "exc" == sys.argv[1]:
					f_print = False
					break

		if f_print: print ":".join(e),
		
	print
