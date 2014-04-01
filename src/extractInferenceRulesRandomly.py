
import en

import urllib2

import os
import sys
import random

random.seed(int(sys.argv[2]))

out			 = []
selector = \
		"SELECT _ROWID_, pred1, pred2, source1, source2, sharedArg, sentdist, offset FROM reasoning_example"

def _prettyGR(p):
	p, r = p.split(":")
	p, s = "-".join(p.split("-")[:-1]), p.split("-")[-1]

	if "nsubj" == r:
		if "j" == s:
			return "X is %s" % p
		
		return "X %s" % p
	
	if "nsubj_pass" == r:
		try:
			return "X is %s" % en.verb.past_participle(p)
		except KeyError:
			return "X is %s" % p
	
	if "dobj" == r: return "%s X" % p
	if "iobj" == r: return "%s X" % p
	
	if r.startswith("prep_"):
		if r.endswith("_pass"):
			try:
				return "%s %s X" % (en.verb.past_participle(p), " ".join(r.split("_")[1:-1]))
			except KeyError:
				return "%s %s X" % (p, " ".join(r.split("_")[1:-1]))
			
		return "%s %s X" % (p, " ".join(r.split("_")[1:]))

	return "%s:%s" % (p, r)

maxRowId = int(os.popen(
		"sqlite3 -separator '\t' /work/naoya-i/kb/corefevents.sqlite3 'SELECT max(_ROWID_) FROM reasoning_example'").read())

for i in xrange(int(sys.argv[1])):
	rowid = random.randint(1, maxRowId)
	tsv		= os.popen(
		"sqlite3 -separator '\t' /work/naoya-i/kb/corefevents.sqlite3 '%s'" % (selector + " WHERE _ROWID_ = %d" % rowid))\
		.read().strip().split("\t")

	tsv[1], tsv[2] = _prettyGR(tsv[1]), _prettyGR(tsv[2])
	
	tsv[3] = tsv[3].lstrip("# ")
	tsv[4] = tsv[4].lstrip("# ")
	tsv += ["http://rum:8021/cgi-bin/viewText.py?file=%s&docid=%s&s1=%s&s2=%s" % (
			tsv[7][2:].split(":")[0], tsv[7][2:].split(":")[1],
			urllib2.quote(tsv[3]), urllib2.quote(tsv[4]),
			)]

	tsv += [tsv[0]]
	tsv  = tsv[1:]
	
	print "\t".join(tsv)
	
