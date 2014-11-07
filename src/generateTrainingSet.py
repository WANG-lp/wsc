
from xml.sax.saxutils import escape

import optparse
import multiprocessing

import re
import itertools
import os
import sys
import collections
import math
import stanfordHelper as scn
import featureGenerator

from progressbar import progressbar_t
from lxml import etree

bypass_t = collections.namedtuple("bypass_t", "xmlText corefChains")

def _isTarget(i, problemlist, options):
	if options.problemno.startswith("%"):
		return 0 == i % int(options.problemno[1:])
	
	try: return i == int(problemlist)
	except ValueError:
		if "-" in problemlist:
			tstart, tend = map(lambda x: int(x), problemlist.split("-"))
			return tstart <= int(i) and int(i) <= tend
		
		return str(i) in problemlist.split(",")
	
def main(options, args):
	xmlText = etree.parse(options.input + ".xml")
        print >>sys.stderr, "Catenative = %s" % (options.cat)
        print >>sys.stderr, "Phrasal = %s" % (options.ph)
        print >>sys.stderr, "Require phrase = %s" % (options.reqph)
        print >>sys.stderr, "New Polarity dict = %s" % (options.newpol)
        print >>sys.stderr, "W2V-based Similarity Search = %s" % (options.simw2v)
        print >>sys.stderr, "WordNet-based Similarity Search = %s" % (options.simwn)
        print >>sys.stderr, "Set predicate similarity:1 = %s" % (options.simpred1)
        print >>sys.stderr, "Using instances from intra-sentential coreference = %s" % (options.insent)
        print >>sys.stderr, "Assign penalty not to use intra-sentential coreference = %s" % (options.insent2)
        print >>sys.stderr, "Use instances with required context = %s" % (options.req)
        print >>sys.stderr, "Not calculate features using KNN= %s" % (options.noknn)
        print >>sys.stderr, "Using small KB = %s" % (options.kbsmall)
        print >>sys.stderr, "Using old KB = %s" % (options.oldkb)
        print >>sys.stderr, "Using path similarity 1/0.5 = %s" % (options.pathsim1)
        print >>sys.stderr, "Using path similarity 1/0 = %s" % (options.pathsim2)
        print >>sys.stderr, "Using path group similarity = %s" % (options.pathgroup)

        
	# EXTRACT COREFERENCE RELATIONS IDENTIFIED BY CORE NLP
	coref				= xmlText.xpath("/root/document/coreference/coreference")
	corefChains = collections.defaultdict(list)

	for id_chain, mens in enumerate(coref):
		for men in mens.xpath("./mention"):
			for tok in xrange(int(men.xpath("./start/text()")[0]), int(men.xpath("./end/text()")[0])):
				corefChains[(int(men.xpath("./sentence/text()")[0]), tok)] += [id_chain]

	ff            = featureGenerator.feature_function_t(options, options.extkb)
	bp            = bypass_t(xmlText, corefChains)

        if options.input.endswith("test.tuples"):
            parseerrlist = open(os.path.join(options.extkb, "parseerrno.txt")).read().strip().split(' ')
        elif options.input.endswith("train.tuples"):
            parseerrlist = open(os.path.join(options.extkb, "parseerrno.train.txt")).read().strip().split(' ')

        # parseerrlist = []
        # parseerrlist = open("./data/parseerrno.txt").read().strip().split(' ')

	if options.fullxml:
		print "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>"
		print "<root>"
		
	for i, ln in enumerate(open(options.input)):
		if None != options.problemno and not _isTarget(i, options.problemno, options):
			continue
                
		print >>sys.stderr, "Processing No. %d..." % (i)

                if str(i) in parseerrlist:
                    print >>sys.stderr, "No. %d has Parse Errors" % (i)
                    continue

		# PARSE THE INPUT TUPLE.
		ti = eval(ln)
		
		_writeFeatures(ff, i, ti, bp, options)
		sys.stdout.flush()

	if options.fullxml:
		print "</root>"
		
def _toWordConstant(w):
	return "W%s%s" % (w.attrib["id"], scn.getLemma(w))
	
def _getBrothers(sent, x):
	return scn.getToken(sent, x[2]), scn.getToken(sent, x[4]), scn.getToken(sent, x[3].split(",")[0] if x[3].split(",")[0] != x[4] else x[3].split(",")[1])

def _printContextualInfo(sent, anaphor, antecedent, antecedent_false, options):
	gvAna, gvAnte, gvFalseAnte = scn.getPrimaryPredicativeGovernor(sent, anaphor, options), scn.getPrimaryPredicativeGovernor(sent, antecedent, options), \
			scn.getPrimaryPredicativeGovernor(sent, antecedent_false, options)
	
	print "<governors anaphor=\"%s-%s:%s\" antecedent=\"%s-%s:%s\" falseAntecedent=\"%s-%s:%s\" />" % (
		gvAna.lemma if None != gvAna else None,
		gvAna.POS[0].lower() if None != gvAna else None,
		gvAna.rel if None != gvAna else None,
		
		gvAnte.lemma if None != gvAnte else None, 
		gvAnte.POS[0].lower() if None != gvAnte else None,
		gvAnte.rel if None != gvAnte else None,
		
		gvFalseAnte.lemma if None != gvFalseAnte else None, 
		gvFalseAnte.POS[0].lower() if None != gvFalseAnte else None,
		gvFalseAnte.rel if None != gvFalseAnte else None
		)
	print "<contexts anaphor=\"%s\" antecedent=\"%s\" falseAntecedent=\"%s\" />" % (
		scn.getFirstOrderContext(sent, gvAna.token) if None != gvAna else "-",
		scn.getFirstOrderContext(sent, gvAnte.token) if None != gvAnte else "-",
		scn.getFirstOrderContext(sent, gvFalseAnte.token) if None != gvFalseAnte else "-"
		)
	
def _writeFeatures(ff, i, tupleInstance, bypass, options):
	sent																	= bypass.xmlText.xpath("/root/document/sentences/sentence[@id='%s']" % (1+i))[0]	
	anaphor, antecedent, antecedent_false =	_getBrothers(sent, tupleInstance)

	if None == anaphor or None == antecedent or None == antecedent_false:
		return

	candidates = [antecedent, antecedent_false]

	# FOR EACH CANDIDATE ANTECEDENT, WE GENERATE THE FEATURES.
	ranker = featureGenerator.ranker_t(ff, anaphor, candidates, sent, options)

	# WRITE THE HEADER AND BASIC INFORMATION OF ANAPHOR AND ANTECEDENTS
	print "<problem id=\"%s\" text=\"%s\" anaphor=\"%s-%s-%s\" antecedent=\"%s-%s-%s\" falseAntecedent=\"%s-%s-%s\">" % (
		i, tupleInstance[1].replace("\"", "&quot;"),
		scn.getLemma(anaphor), scn.getPOS(anaphor)[0].lower(), scn.getNEtype(anaphor),
		scn.getLemma(antecedent), scn.getPOS(antecedent)[0].lower(), scn.getNEtype(antecedent),
		scn.getLemma(antecedent_false), scn.getPOS(antecedent_false)[0].lower(), scn.getNEtype(antecedent_false),
		)

	_printContextualInfo(sent, anaphor, antecedent, antecedent_false, options)

	for can in candidates:
		print "<feature-vector for=\"%s\">%s</feature-vector>" % (
			"correct" if can == antecedent else "wrong",
			"\n".join([
				"%d qid:%d %s" % (
					1 if can == antecedent else 2, 1+i, escape(" ".join(["%s:%s" % x for x in fv])))
				for fv in ff.generateFeatureSet(anaphor, can, sent, ranker, candidates, options)
			])
		)

	#
	# FOR MORE INFORMATIVE OUTPUTS
	print >>sys.stderr, "Writing statistics..."
	
	# RANKING FEATURES
	for fk, fvs in ranker.rankingsRv.iteritems():
		print "<feature type=\"%s\" correct=\"%s\" wrong=\"%s\" />" % (
			fk,
			ranker.getRankValue(antecedent.attrib["id"], fk),
			ranker.getRankValue(antecedent_false.attrib["id"], fk),
			)

	# k-NEAREST NEIGHBOR SCORES
	for fk, fvs in ranker.NN.iteritems():
                if options.noknn == True:
                    continue
		for K in xrange(1, 10):
			print "<feature type=\"kNN_%s,K=%d\" correct=\"%s\" wrong=\"%s\" />" % (
				fk, K,
				ranker.getKNNRankValue(antecedent.attrib["id"], fk, K),
				ranker.getKNNRankValue(antecedent_false.attrib["id"], fk, K),
				)
			print "<feature type=\"kNN_rank_%s,K=%d\" correct=\"%s\" wrong=\"%s\" />" % (
				fk, K,
				ranker.getKNNRank(antecedent.attrib["id"], fk, K),
				ranker.getKNNRank(antecedent_false.attrib["id"], fk, K),
				)
			print "<feature type=\"kNN_score_%s,K=%d\" correct=\"%s\" wrong=\"%s\" />" % (
				fk, K,
				ranker.getKNNRankValue(antecedent.attrib["id"], fk, K, score=True),
				ranker.getKNNRankValue(antecedent_false.attrib["id"], fk, K, score=True),
				)

	# OTHER STATISTICS
	for fk, fvs in ranker.statistics.iteritems():

		NumRulesCorrect = 0
		NumRulesWrong = 0

		if "cirInstances" == fk or "iriInstances" == fk:
                        if options.noknn == True:
                                continue

			for voted, inst in fvs:
				if int(antecedent.attrib["id"]) == int(voted):
					NumRulesCorrect += 1 
				else:
					NumRulesWrong += 1

				if not options.nolog:
					print "<statistics type=\"%s\" label=\"%s\">%s</statistics>" % (
						fk,
						"Correct" if int(antecedent.attrib["id"]) == int(voted) else "Wrong",
						"\t".join([repr(inst._asdict()[v]) for v in inst._fields])
					)

			print "<statistics type=\"%s\" correct=\"%s\" wrong=\"%s\" />" % (
				"iriNumRules",
				NumRulesCorrect,
				NumRulesWrong
			)

		else:
			print "<statistics type=\"%s\" correct=\"%s\" wrong=\"%s\" />" % (
				fk,
				ranker.getRankValue(antecedent.attrib["id"], fk, 0.0, ranker.statistics),
				ranker.getRankValue(antecedent_false.attrib["id"], fk, 0.0, ranker.statistics),
				)
		
	print "</problem>"

def _diff(x, y, th):
	return (x > y) and (1.0*(x-y)/x > th)

def _cdbdefget(f, key, de):
	r = f.get(key)
	return r if None != r else de

if "__main__" == __name__:
	cmdparser		= optparse.OptionParser(description="Feature generator.")
	cmdparser.add_option("--input", help			= "Input difficult pronoun.")
	cmdparser.add_option("--problemno", help  = "(Debug) Process only specified problem.")
	cmdparser.add_option("--extkb", help	= ".", default="/work/naoya-i/kb")
	cmdparser.add_option("--quicktest", help	= ".", action="store_true")
	cmdparser.add_option("--fullxml", help	= ".", action="store_true")
	cmdparser.add_option("--nolog", help	= ".", action="store_true")
	cmdparser.add_option("--simw2v", help	= "Turn on word2vec-based predicate similarity search.", action="store_true", default=False)
	cmdparser.add_option("--simwn", help	= "Turn on WordNet-based predicate similarity search.", action="store_true", default=False)
        cmdparser.add_option("--simpred1", help	= "Set predicate similarity = 1", action="store_true", default=False)
	cmdparser.add_option("--cat", help	= "Catenative ON", action="store_true", default=False)
        cmdparser.add_option("--ph", help	= "Phrasal ON", action="store_true", default=False)
        cmdparser.add_option("--reqph", help	= "Use instances with required phrasal", action="store_true", default=False)
        cmdparser.add_option("--newpol", help	= "Use new polarity dictionaly ON", action="store_true", default=False)
        cmdparser.add_option("--insent", help	= "Using instances from inter-sentential coreference", action="store_true", default=False)
        cmdparser.add_option("--insent2", help	= "assign penalty not to use inter-sentential coreference", action="store_true", default=False)
        cmdparser.add_option("--req", help	= "Use instances with required context", action="store_true", default=False)
        cmdparser.add_option("--noknn", help	= "Not calculate features using KNN", action="store_true", default=False)
        cmdparser.add_option("--kbsmall", help	= "Using small kb", action="store_true", default=False)
        cmdparser.add_option("--oldkb", help	= "Using old kb", action="store_true", default=False)
        cmdparser.add_option("--pathsim1", help	= "Path similarity (conective match: 1 or 0.5 )", action="store_true", default=False)
        cmdparser.add_option("--pathsim2", help	= "Path similarity (conective match: 1 or 0 )", action="store_true", default=False)
        cmdparser.add_option("--pathgroup", help	= "Using path similarity (conective group)", action="store_true", default=False)
        
	main(*cmdparser.parse_args())
