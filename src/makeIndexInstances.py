
import sys

db					 = open(sys.argv[1], "r")
bytesRead		 = 0
numProcessed = 0

for ln in db:
	problemNo, entry = ln.split("\t", 1)
	
	print "\t".join([problemNo, str(bytesRead), str(bytesRead+len(ln))])
	
	bytesRead += len(ln)

	sys.stderr.write(".")
	numProcessed += 1
	if 0 == numProcessed % 100: sys.stderr.write("%d\n" % numProcessed)

print >>sys.stderr, numProcessed, ""
