
import os
import sys
import subprocess

import collections
import readline

proposition_t = collections.namedtuple("proposition_t", "predicate context slot argument")

class distance_t:
	def __init__(self, pathServer = "/home/naoya-i/work/wsc/bin/", pathKB = "/work/naoya-i/kb/", fUseMemoryMap = True):
		print >>sys.stderr, "Loading..."

		opts = []

		if fUseMemoryMap: opts += ["-q"]
		
		self.procSearchServer = subprocess.Popen(
			"%s -k %s %s" % (os.path.join(pathServer, "distance"), pathKB, " ".join(opts)),
			shell = True,
			stdin = subprocess.PIPE, stdout = subprocess.PIPE, )
		
		assert("200 OK" == self.procSearchServer.stdout.readline().strip())
		

	def calc(self, p1, p2):
		"""
		p1, p2: instances of proposition_t, e.g.:
  		        p1.predicate = "have"
    		      p1.context = "d:dobj:error-n"
  	  	      p1.slot = "nsubj"
		          p1.argument = "John"
		"""
		assert(isinstance(p1, proposition_t) and isinstance(p2, proposition_t))

		print >>self.procSearchServer.stdin, "\t".join([
			p1.predicate, p1.context, p1.slot, p1.argument,
			p2.predicate, p2.context, p2.slot, p2.argument])

		return float(self.procSearchServer.stdout.readline().strip())


if "__main__" == __name__:
	
	# CREATE THE INSTANCE.
	d = distance_t()

	print >>sys.stderr, """
Welcome to distance.py unit test!
	
Input format (tab separated):
  predicate|context|slot|argument|predicate|context|slot|argument
  (Write two propositions to be comapred in tab-separated format.)

e.g.:
  kill\td:dobj:Mary-n\tnsubj\tJohn\tassasinate\td:dobj:Bob-n\tnsubj\tTom
  (This will give you similarity between "John kills Mary" and "Tom assassinates Bob".)
	
Hope you enjoy it!
"""
	
	while True:
		# WAIT FOR USER INPUT.
		try:
			x = raw_input("? ")

		except EOFError:
			break
				
		x = x.split("\t")

		if 8 != len(x):
			print >>sys.stderr, "Format: predicate|context|slot|argument|predicate|context|slot|argument"
			continue

		# CALCULATE THE SIMILARITY BETWEEN TWO PROPOSITIONS.
		print d.calc(
			proposition_t(*x[0:4]),
			proposition_t(*x[4:8]),
			)
