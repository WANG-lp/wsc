

import iri
import selpref
import googlengram
import nccj08
import ncnaive
import sentimentpolarity

import stanfordHelper as scn

import sys
import itertools
import re
import collections
import math
import os
import cdb
import marshal

#
def _isPredicate(x):  return x in "VB|VBD|VBG|VBN|VBP|VBZ|JJ|JJR|JJS".split("|")
def _isNounPhrase(x): return x in "NN|NNP|NNS|NNPS".split("|")
def _getPathKB(): return open("./pathKB.txt").read().strip()

def _cdbdefget(f, key, de):
	r = f.get(key)
	return r if None != r else de

def _npmi(_xy, _x, _y):
	if 0 == _x*_y or 0 == _xy: return 0
	
	#return _xy/(_x*_y)
	return math.log(1.0 * _xy / (_x * _y), 2)
	return 0.5*(1+(math.log(1.0 * _xy / (_x * _y), 2) / -math.log(_xy, 2)))

def _catenativeget(gv, sent):
    # catenativelistA = ['afford', 'agree', 'able','aim', 'appear', 'arrange', 'ask', 'attempt', 'beg', 'care', 'choose', 'condescend', 'consent', 'dare', 'decide', 'deserve', 'expect', 'fail', 'happen', 'have', 'help', 'hesitate', 'hope', 'long', 'move', 'need', 'offer', 'plan', 'prepare', 'pretend', 'proceed', 'promise', 'refuse', 'seek', 'seem', 'strive', 'struggle', 'swear', 'tend', 'threaten', 'undertake', 'wait', 'want', 'wish']
    # catenativelistB = ['allowed', 'forbid', 'permit', 'request', 'require']
    # catenativelistC = ['admit', 'advise', 'allow', 'appreciate', 'avoid', 'complete', 'consider', 'delay', 'deny', 'detest', 'dislike', 'enjoy', 'escape', 'finish', 'forbid', 'imagine', 'imply', 'keep', 'mind', 'miss', 'need', 'permit', 'practise', 'quit', 'recall', 'recommend', 'regret', 'resent', 'resist', 'resume', 'risk', 'stand', 'suggest', 'tolerate', 'want']
    # catenativelistD = ['bear', 'begin', 'bother', 'continue', 'disdain', 'intend', 'like', 'love', 'neglect', 'prefer', 'regret', 'start', 'come', 'go', 'get', 'forget', 'like', 'mean', 'need', 'remember', 'propose', 'stop', 'try']
    # # catenativelistOther = ['able']
    # catenativelistObj = ['ask', 'beg', 'allow', 'forbid', 'permit', 'request', 'require', 'admit', 'advise', 'imagine', 'need', 'recommend', 'suggest', 'tolerate', 'want', 'help', 'let', 'tell', 'make']
    # catenativelist = list(set(catenativelistA)|set(catenativelistB)|set(catenativelistC)|set(catenativelistD)|set(catenativelistObj))

    catenativelist = ['love', 'help', 'forbid', 'consent', 'move',
                      'prefer', 'promise', 'go', 'miss', 'consider', 'quit', 'proceed',
                      'prepare', 'long', 'start', 'choose', 'recommend', 'threaten',
                      'dislike', 'practise', 'tell', 'hope', 'risk', 'offer', 'afford',
                      'propose', 'stop', 'bother', 'bear', 'resent', 'deserve',
                      'decide', 'dare', 'arrange', 'deny', 'like', 'recall', 'require',
                      'pretend', 'tolerate', 'beg', 'aim', 'continue', 'wish', 'agree',
                      'care', 'mean', 'enjoy', 'forget', 'have', 'appreciate',
                      'allowed', 'mind', 'resist', 'need', 'imply', 'condescend',
                      'expect', 'want', 'escape', 'fail', 'happen', 'seek', 'seem',
                      'complete', 'hesitate', 'appear', 'suggest', 'avoid', 'get',
                      'able', 'tend', 'delay', 'advise', 'make', 'begin', 'finish',
                      'intend', 'resume', 'detest', 'let', 'plan', 'imagine', 'ask',
                      'come', 'wait', 'regret', 'refuse', 'undertake', 'attempt',
                      'remember', 'disdain', 'try', 'request', 'keep', 'admit', 'swear',
                      'stand', 'allow', 'permit', 'strive', 'neglect', 'struggle']
    
    
    if gv.lemma in catenativelist:
        # print gv.lemma
        newgv = scn.getCatenativeDependent(sent, gv)
        return newgv
    else:
        return gv

def _phrasalget(gv, sent):
    phrasedict = marshal.load( open("/home/jun-s/work/wsc/data/phrasedict.msl") )
    # phrasedict = {'come': {'come_back': ['answer', 'denote', 'reappear', 're-emerge', 'refer', 'reply', 'respond'], 'come_by': ['acquire']}}

    if gv.lemma in phrasedict:
        newgv = scn.getPhrasal(sent, gv, phrasedict[gv.lemma])
        return newgv
    else:
        return gv

        
class ranker_t:
	def __init__(self, ff, ana, candidates, sent, catflag):
		self.NN = collections.defaultdict(list)
		self.rankingsRv = collections.defaultdict(list)
		self.statistics = collections.defaultdict(list)
		# FOR REAL-VALUED FEATURES, WE FIRST CALCULATE THE RANKING VALUES
		# FOR EACH CANDIDATE.
		for can in candidates:
			wPrn, wCan	 = scn.getLemma(ana), scn.getLemma(can)
			vCan				 = can.attrib["id"]
			gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, catflag), scn.getPrimaryPredicativeGovernor(sent, can, catflag)
			
			self.rankingsRv["position"] += [(vCan, -int(can.attrib["id"]))]

			if None != gvAna and None != gvCan:

                                # SELECTIONAL PREFERENCE
                                if "O" == scn.getNEtype(can):
                                    ret = ff.sp.calc("%s-%s" % (gvAna.lemma, gvAna.POS[0].lower()), gvAna.rel, "%s-n-%s" % (wCan, scn.getNEtype(can)))
                                    self.rankingsRv["selpref"] += [(vCan, ret[0])]
                                    self.rankingsRv["selprefCnt"] += [(vCan, ret[1])]
																		
                                # NARRATIVE CHAIN FEATURE (C&J08'S OUTPUT)
                                self.rankingsRv["NCCJ08"] += [(vCan, 1 if 1 <= len(ff.nc.getChains(
                                    ff.nc.createQuery(gvAna.lemma, gvAna.rel),
                                    ff.nc.createQuery(gvCan.lemma, gvCan.rel))) else 0)]
                                self.statistics["NCCJ08"] += [(vCan, "%s ~ %s" % (ff.nc.createQuery(gvAna.lemma, gvAna.rel), ff.nc.createQuery(gvCan.lemma, gvCan.rel)))]
																
                                # NARRATIVE CHAIN FEATURE
                                for th in [0, 5, 10, 25, 50, 100, 200, 400]:
                                    self.rankingsRv["NCNAIVE%sFREQ" % th] += [(vCan,
                                        ff.ncnaive[th].getFreq("%s-%s:%s" % (gvAna.lemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvCan.lemma, gvCan.POS[0].lower(), gvCan.rel)))]

                                    self.rankingsRv["NCNAIVE%sPMI" % th] += [(vCan,
                                        ff.ncnaive[th].getPMI("%s-%s:%s" % (gvAna.lemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvCan.lemma, gvCan.POS[0].lower(), gvCan.rel)))]
																		
                                    self.rankingsRv["NCNAIVE%sNPMI" % th] += [(vCan,
                                        ff.ncnaive[th].getNPMI("%s-%s:%s" % (gvAna.lemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvCan.lemma, gvCan.POS[0].lower(), gvCan.rel)))]
																
                                # Q1, 2: CV
                                if "O" == scn.getNEtype(can):
                                    tkNextAna = scn.getNextPredicateToken(sent, ana)
                                    qCV = [scn.getSurf(can), scn.getSurf(tkNextAna)]
                                    ret = ff.gn.search(qCV)
                                    self.statistics["CV"] += [(vCan, " ".join(qCV))]
                                    self.rankingsRv["googleCV"] += [(vCan, ret)]
																
                                    # Q3, Q4: CVW
                                    tkNeighbor = scn.getNextToken(sent, tkNextAna)
                                    if None != tkNeighbor:
                                        qCV = [scn.getSurf(can), scn.getSurf(tkNextAna), scn.getSurf(tkNeighbor)]
                                        ret = ff.gn.search(qCV)
                                        self.statistics["CVW"] += [(vCan, " ".join(qCV))]
                                        self.rankingsRv["googleCVW"] += [(vCan, ret)]

                                    if "JJ" in gvAna.POS:
                                        # Q5, Q6: JC
                                        qCV = [scn.getSurf(gvAna.token), scn.getSurf(can)]
                                        ret = ff.gn.search(qCV)
                                        self.statistics["JC"] += [(vCan, " ".join(qCV))]
                                        self.rankingsRv["googleJC"] += [(vCan, ret)]
                                
                                if isinstance(gvAna.lemma, list) and isinstance(gvCan.lemma, list):
                                    # print "anaphra govornor and candidate govornor are phrasal verb"
                                    for p1 in gvAna.lemma:
                                        for p2 in gvCan.lemma:
                                            ff.iri(self.NN,
                                                   vCan,
                                                   p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                                                   p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                                                   self.statistics["iriInstances"],
                                            )
                                elif isinstance(gvAna.lemma, list):
                                    print gvAna.lemma
                                    print "anaphora govonor is phrasal verb"
                                    for p1 in gvAna.lemma:
                                        print p1
                                        ff.iri(self.NN,
                                               vCan,
                                               p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                                               gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                                               self.statistics["iriInstances"],
                                        )


                                elif isinstance(gvCan.lemma, list):
                                    # print len(gvCan.lemma)
                                    # print "candidate govonors is phrasal verb"
                                    for p2 in gvCan.lemma:
                                        # print p2
                                        ff.iri(self.NN,
                                               vCan,
                                               gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                                               p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                                               self.statistics["iriInstances"],
                                        )
                                        
                                    # self.rankingsRv["nc"] += [(vCan, ff.nc(gvAna.lemma, gvAna.rel, gvCan.lemma, gvCan.rel))]
                                    # self.rankingsRv["selpref"] += [(vCan, r1[1])]
                                    # self.rankingsRv["selprefcnt"] += [(vCan, math.log(max(1, r1[0])))]

                                    # ff.iri_for_list(self.NN,
                                    #                 vCan,
                                    #                 gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                                    #                 gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                                    #                 self.statistics["iriInstances"],
                                    # )

                                else:                                
                                    # self.rankingsRv["nc"] += [(vCan, ff.nc(gvAna.lemma, gvAna.rel, gvCan.lemma, gvCan.rel))]
                                    # self.rankingsRv["selpref"] += [(vCan, r1[1])]
                                    # self.rankingsRv["selprefcnt"] += [(vCan, math.log(max(1, r1[0])))]
                                
                                    ff.iri(self.NN,
                                           vCan,
                                           gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                                           gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                                           self.statistics["iriInstances"],
                                    )


		for rank in self.rankingsRv.values():
			rank.sort(key=lambda x: x[1], reverse=True)

	def getRankValue(self, x, t, de = 0.0, src = None):
		for xc in src[t] if None != src else self.rankingsRv[t]:
			if x == xc[0]: return xc[1]
			
		return de
		
	def getRank(self, x, t):
		if 1 >= len(self.rankingsRv[t]) or self.rankingsRv[t][0][1] == self.rankingsRv[t][1][1]:
			return None

		for i, xc in enumerate(self.rankingsRv[t]):
			if x == xc[0]: return "R1" if 0 == i else "R2"
		
	def getKNNRank(self, x, t, K=20):
		votes = collections.defaultdict(int)
		Ksorted = sorted(self.NN[t], key=lambda y: y[1], reverse=True)[:K]

		for votedCan, votedScore in Ksorted:
			votes[votedCan] += votedScore

		if len(votes) >= 2 and votes.values()[0] == votes.values()[1]:
			return 0 if Ksorted[-1][0] != x else 1

		for i, xc in enumerate(sorted(votes.iteritems(), key=lambda y: y[1], reverse=True)):
			if x == xc[0]: return i

		return len(votes)
	
	def getKNNRankValue(self, x, t, K=20, score=False, de=0):
		votes = collections.defaultdict(int)

		for votedCan, votedScore in sorted(self.NN[t], key=lambda y: y[1], reverse=True)[:K]:
			votes[votedCan] += 1 if not score else votedScore

		for i, xc in enumerate(votes.iteritems()):
			if x == xc[0]: return xc[1]

		return de

# LOAD THE KEY-VALUE STORE.
class feature_function_t:
	def __init__(self, pa, dirExtKb):
		self.pa							 = pa
                
		self.libiri    = iri.iri_t(
			os.path.join(dirExtKb, "corefevents.tsv"),
			os.path.join(os.path.dirname(sys.argv[0]), "../bin"),
			dirExtKb,
			os.path.join(dirExtKb, "corefevents.com.lsh"),
			fUseMemoryMap=pa.quicktest
			)

		self.ncnaive = {}
		
		for th in [0, 5, 10, 25, 50, 100, 200, 400]:
			self.ncnaive[th] = ncnaive.ncnaive_t(os.path.join(_getPathKB(), "ncnaive%s.cdb" % th), os.path.join(_getPathKB(), "tuples.cdb"))
			
		self.nc        = nccj08.nccj08_t(os.path.join(_getPathKB(), "schemas-size12"), os.path.join(_getPathKB(), "verb-pair-orders"))
		self.sp        = selpref.selpref_t(pathKB=_getPathKB())
		self.sentpol   = sentimentpolarity.sentimentpolarity_t(os.path.join(_getPathKB(), "wilson05_subj/subjclueslen1-HLTEMNLP05.tff"))

		# GOOGLE NGRAMS
		self.gn        = googlengram.googlengram_t(os.path.join(_getPathKB(), "ngrams"))

	def generateFeature(self, ana, can, sent, ranker, candidates, catflag):
		conn				 = scn.getConn(sent)
		position		 = "left" if "R1" == ranker.getRank(can.attrib["id"], "position") else "right"
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, catflag), scn.getPrimaryPredicativeGovernor(sent, can, catflag)

		# kNN FEATURES.
		for K in xrange(50):
			for fk, fnn in ranker.NN.iteritems():
				r = ranker.getKNNRank(can.attrib["id"], fk, K)

				if 0 == r:
					yield "KNN%d_%s_%s" % (K, fk, r), 1
			
		# RANKING FEATURES.
		for fk, fr in ranker.rankingsRv.iteritems():
			if "position" == fk: continue
			
			r	=ranker.getRank(can.attrib["id"], fk)

			if "selpref" == fk:
				yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
					
			if "R1" == r:
				if "google" in fk:
					if min(fr[1][1], fr[0][1]) > 0 and max(fr[1][1], fr[0][1]) > 0 and \
								 float(abs(fr[1][1] - fr[0][1])) / max(fr[1][1], fr[0][1]) > 0.2:
						yield "%s_Rank_%s_%s" % ("x", fk, r), 1
						
				elif "NCCJ08" == fk:
					if 2 > fr[0][1] + fr[1][1]:
						yield "%s_Rank_%s_%s" % ("x", fk, r), 1
						
				elif "NCCJ08_VO" == fk:
					if abs(fr[0][1] - fr[1][1])>25:
						yield "%s_Rank_%s_%s" % ("x", fk, r), 1
						
				else:
					yield "%s_Rank_%s_%s" % ("x", fk, r), 1

		#
		# LEXICAL FEATURES.
		yield "%s_LEX_AD_%s,%s" % (position, scn.getLemma(ana), scn.getLemma(can)), 1
		
		# ANTECEDENT-INDEPENDENT.
		for tk in sent.xpath("./tokens/token"):
			yield "%s_LEX_AI1_%s" % (position, scn.getLemma(tk)), 1

			if None != conn:
				for tk2 in sent.xpath("./tokens/token"):
					if int(tk.attrib["id"]) < int(conn.attrib["id"]) and int(tk2.attrib["id"]) > int(conn.attrib["id"]) and \
								not("NN" in scn.getPOS(tk) or "JJ" in scn.getPOS(tk)) and \
								not("NN" in scn.getPOS(tk2) or "JJ" in scn.getPOS(tk2)):
						yield "%s_LEX_AI2_%s,%s" % (position, scn.getLemma(tk), scn.getLemma(tk2)), 1
						yield "%s_LEX_AI3_%s,%s,%s" % (position, scn.getLemma(tk), scn.getLemma(tk2), scn.getLemma(conn)), 1

		# ANTECEDENT-DEPENDENT.
		if None != gvAna:
			yield "%s_LEX_ADHC1VA_%s,%s" % (position, scn.getLemma(can), gvAna.lemma), 1

		if None != gvCan:
			yield "%s_LEX_ADHC1VC1_%s,%s" % (position, scn.getLemma(can), gvCan.lemma), 1

		# HEURISTIC POLARITY.
		for fHPOL in self.heuristicPolarity(ana, can, sent, ranker, candidates, catflag):
			yield fHPOL

		# NC VERB ORDER.
		if None != gvAna and None != gvCan:
			diff = self.nc.getVerbPairOrder(gvCan.lemma, gvAna.lemma) - self.nc.getVerbPairOrder(gvAna.lemma, gvCan.lemma)
			
			if diff > 25: yield "NCCJ08_VO_SAME_ORDER", 1
			elif diff < -25: yield "NCCJ08_VO_REVERSE_ORDER", 1

	def heuristicPolarity(self, ana, can, sent, ranker, candidates, catflag):
		conn				 = scn.getConn(sent)
		gvCan1, gvCan2 = scn.getPrimaryPredicativeGovernor(sent, candidates[0], catflag), scn.getPrimaryPredicativeGovernor(sent, candidates[1], catflag)
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, catflag), scn.getPrimaryPredicativeGovernor(sent, can, catflag)
		polAna, polCan1, polCan2 = 0, 0, 0
		position		 = "left" if "R1" == ranker.getRank(can.attrib["id"], "position") else "right"

		if None != gvAna:
			polAna = self.sentpol.getPolarity(gvAna.lemma) if gvAna.rel == "nsubj" or scn.getDeepSubject(sent, gvAna.token) == ana.attrib["id"] else None

			# FLIPPING
			if None != polAna and (scn.getNeg(sent, gvAna.token) or (None != conn and scn.getLemma(conn) in "but although though however".split())): polAna *= -1

		if None != gvCan1:
			polCan1 = self.sentpol.getPolarity(gvCan1.lemma) if gvCan1.rel == "nsubj" or scn.getDeepSubject(sent, gvCan1.token) == candidates[0].attrib["id"] else None

			# FLIPPING
			if None != polCan1 and scn.getNeg(sent, gvCan1.token): polCan1 *= -1
			
		if None != gvCan2:
			polCan2 = self.sentpol.getPolarity(gvCan2.lemma) if gvCan2.rel == "nsubj" or scn.getDeepSubject(sent, gvCan2.token) == candidates[1].attrib["id"] else None

			# FLIPPING
			if None != polCan2 and scn.getNeg(sent, gvCan2.token): polCan2 *= -1

		# INFERENCE.
		if 1 == polCan1 and None == polCan2: polCan2 = -1
		if -1 == polCan1 and None == polCan2: polCan2 = 1
		if None == polCan1 and 1 == polCan2: polCan1 = -1
		if None == polCan1 and -1 == polCan2: polCan1 = 1

		def _L(_x):
			if None == _x: return None
			return scn.getLemma(scn.getTokenById(sent, _x))
			
		ranker.statistics["POLDS"] += [(candidates[0].attrib["id"], "%s,%s" % (_L(scn.getDeepSubject(sent, gvAna.token)) if None != gvAna else None, _L(scn.getDeepSubject(sent, gvCan1.token)) if None != gvCan1 else None))]
		ranker.statistics["POLDS"] += [(candidates[1].attrib["id"], "%s,%s" % (_L(scn.getDeepSubject(sent, gvAna.token)) if None != gvAna else None, _L(scn.getDeepSubject(sent, gvCan2.token)) if None != gvCan2 else None))]
		ranker.statistics["POL"] += [(candidates[0].attrib["id"], "%s,%s" % (polAna, polCan1))]
		ranker.statistics["POL"] += [(candidates[1].attrib["id"], "%s,%s" % (polAna, polCan2))]

		if None != polAna and None != polCan1 and None != polCan2 and 0 != polAna*polCan1*polCan2:
			
			# HPOL1
			if can == candidates[0] and polCan1 == polAna: yield "%s_HPOL_MATCH" % position, 1
			if can == candidates[1] and polCan2 == polAna: yield "%s_HPOL_MATCH" % position, 1

			# HPOL2
			if can == candidates[0]: yield "%s_HPOL_%s-%s" % (position, polAna, polCan1), 1
			if can == candidates[1]: yield "%s_HPOL_%s-%s" % (position, polAna, polCan2), 1

			# HPOL3
			if None != conn:
				if can == candidates[0]: yield "%s_HPOL_%s-%s-%s" % (position, polAna, scn.getLemma(conn), polCan1), 1
				if can == candidates[1]: yield "%s_HPOL_%s-%s-%s" % (position, polAna, scn.getLemma(conn), polCan2), 1
				
	def iri(self, outNN, NNvoted, p1, r1, ps1, c1, a1, p2, r2, ps2, c2, a2, cached = None):
		if None == self.libiri: return 0
		
                #for ret, raw in self.libiri.predict(p1, c1, r1, a1, p2, c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2):
                for ret, raw in self.libiri.predict("%s-%s" % (p1, ps1[0].lower()), c1, r1, a1, "%s-%s" % (p2, ps2[0].lower()), c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2, limit=1000000):

			sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred*ret.sRuleAssoc
			spa = sp * ret.sIndexArg[ret.iIndexed]*ret.sPredictedArg
			spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
			spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext

                        if None != cached: cached += [(NNvoted, ret)]
			assert(abs(spac - ret.score) < 0.1)

			outNN["iriPred"] += [(NNvoted, sp)]
			outNN["iriPredArg"] += [(NNvoted, spa)]
			outNN["iriPredCon"] += [(NNvoted, spc)]
			outNN["iriPredArgCon"] += [(NNvoted, spac)]
			outNN["iriArg"] += [(NNvoted, ret.sIndexArg[ret.iIndexed]*ret.sPredictedArg)]
			outNN["iriCon"] += [(NNvoted, ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
			outNN["iriArgCon"] += [(NNvoted, ret.sIndexArg[ret.iIndexed]*ret.sPredictedArg*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]

		return 0
