#
# HELPER FUNCTIONS FOR STANFORD CORE NLP RESULT.
import collections
import sys

import featureGenerator as fgn


def _isPredicativeGovernorRel(x): return x in "nsubjpass nsubj dobj iobj".split() or x.startswith("prep")

governor_t = collections.namedtuple("governor_t", "rel token lemma POS")

def getFirstOrderContext(sent, tk):
	return " ".join(
		["d:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getDependents(sent, tk)] +
		["g:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getGovernors(sent, tk)] )

def getFirstOrderContext4phrasal(sent, tk):
	return " ".join(
		["d:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getDependents4phrasal(sent, tk)] +
		["g:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getGovernors(sent, tk)] )

        
def getToken(sent, x, conn = None):
	r = sent.xpath("./tokens/token/word[text()='%s']/.." % x.split(" ")[-1].strip().replace("'", ""))

	if 0 == len(r):
		r = sent.xpath("./tokens/token/word[text()=\"%s\"]/.." % x.split(" ")[-1].strip().replace("\"", ""))
		
		if 0 == len(r):
			r = sent.xpath("./tokens/token/lemma[text()='%s']/.." % x.split(" ")[-1].strip().replace("'", ""))

	# DISAMBIGUATE
	if 1 < len(x.split(" ")) and 1 < len(r):
		new_r = []
		
		for tk in r:
			tk_prev = tk.getprevious()

			if "%s %s" % (tk_prev.xpath("word/text()")[0], tk.xpath("word/text()")[0]) == " ".join(x.split(" ")[-2:]):
				new_r += [tk]

		r = new_r

	if 1 < len(r):
		r.sort(key=lambda x: int(x.attrib["id"]))

	if None != conn:
		r = filter(lambda x: int(x.attrib["id"]) > int(conn.attrib["id"]), r)
		
	if None != r and 1 < len(r):
		#print >>sys.stderr, "Ambig!", " ".join([x.xpath("./word/text()")[0] for x in r])
		pass
		
	return r[0] if 0 < len(r) else None

def getTokenById(sent, x):
	r = sent.xpath("./tokens/token[@id='%s']" % x)
	return r[0] if 1 <= len(r) else None

def getNextToken(sent, x):
	return getTokenById(sent, int(x.attrib["id"])+1)

def getNextPredicateToken(sent, x):
	for i in xrange(1000):
		tk = getTokenById(sent, int(x.attrib["id"])+(1+i))
		if None == tk:
			return x
			
		if "VB" in getPOS(tk) or "JJ" in getPOS(tk):
			return tk
			
	return x
	
def getPreviousToken(sent, x):
	return getTokenById(sent, int(x.attrib["id"])-1)
	
def getConn(sent):
	for tk in sent.xpath("./tokens/token/POS[contains(text(),'VB') or contains(text(),'JJ')]/.."):
		id_cnj_mk = sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='mark']/governor[@idx='%s']/../dependent/@idx" % (tk.attrib["id"]))
		id_cnj_cc = sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='cc']/governor[@idx='%s']/../dependent/@idx" % (tk.attrib["id"]))

		if 0 < len(id_cnj_mk):
			return getTokenById(sent, id_cnj_mk[0])
		
		if 0 < len(id_cnj_cc):
			return getTokenById(sent, id_cnj_cc[0])
		
def getMod(sent, x):
	mod_pred  = sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='amod']/dependent[@idx='%s']/../governor/@idx" % x.attrib["id"])
		
	if 0 < len(mod_pred):
		mod_pred  = getTokenById(sent, mod_pred[0])
		return mod_pred.xpath("./lemma/text()")[0]

	return ""


def getNEtype(x): return x.find("NER").text
def getLemma(x):  return x.find("lemma").text
def getSurf(x):  return x.find("word").text
def getPOS(x):  return x.find("POS").text

def getDependents(sent, x):
	return [
		(y.attrib["type"], getTokenById(sent, y.find("dependent").attrib["idx"]))
		for y in 
		sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % x.attrib["id"])]

def getDependents4phrasal(sent, x):
    ret = []
    phrasedeplist = ["advmod", "prt", "prep", "amod", "dobj"]
    for y in sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % x.attrib["id"]):
        # print "Phrasal verb context"
        # print y.attrib["type"]        
        if not y.attrib["type"].strip() in phrasedeplist:
            # print y.attrib["type"]
            ret.append((y.attrib["type"], getTokenById(sent, y.find("dependent").attrib["idx"])))
    return ret
	
        
def convRel(r, tk, sent):
	# if "agent" == r:
	# 	return "dobj"
	
	if "nsubjpass" == r:
		return "nsubj_pass"
		# for g in getDependents(sent, tk):
		# 	if "dobj" == g[0]:
		# 		return "iobj"
			
		# return "dobj"
	
	if "prep" in r and "VBN" == getPOS(tk):
		return r + "_pass"

	return r

def getGovernors(sent, x):
	return [
		(y.attrib["type"], getTokenById(sent, y.find("governor").attrib["idx"]))
		for y in 
		sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/dependent[@idx='%s']/.." % x.attrib["id"])]

def getDeepSubject(sent, x):
	ret = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='agent']/governor[@idx='%s']/../dependent/@idx" % x.attrib["id"])
	return ret[0] if 0 < len(ret) else None
	
def getPrimaryPredicativeGovernor(sent, x, pa, contentGovernor = True):
	if contentGovernor:
		cg = getContentPredicativeGovernor(sent, x)
		
		if 0 < len(cg):
			ps = getPOS(cg[-1][2])
			
			if "VB" in ps or "JJ" in ps:
				# return governor_t(convRel(cg[-1][0], cg[-1][2], sent), cg[-1][2], cg[-1][1], getPOS(cg[-1][2]))
				tmp1 = governor_t(convRel(cg[-1][0], cg[-1][2], sent), cg[-1][2], cg[-1][1], getPOS(cg[-1][2]))
                                if pa.cat:
                                    tmp1 = fgn._catenativeget(tmp1, sent)
                                if pa.ph:
                                    tmp1 = fgn._phrasalget(tmp1, sent, pa.extkb)
                                return tmp1
                                
	for y in sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/dependent[@idx='%s']/.." % x.attrib["id"]):
		tk = getTokenById(sent, y.find("governor").attrib["idx"])

		if _isPredicativeGovernorRel(y.attrib["type"]):
			ps = getPOS(tk)
			
			if "VB" in ps or "JJ" in ps:
				# return governor_t(convRel(y.attrib["type"], tk, sent), tk, getLemma(tk), getPOS(tk))
				tmp1 = governor_t(convRel(y.attrib["type"], tk, sent), tk, getLemma(tk), getPOS(tk))
                                if pa.cat:
                                    tmp1 = fgn._catenativeget(tmp1, sent)
                                if pa.ph:
                                    tmp1 = fgn._phrasalget(tmp1, sent, pa.extkb) 
                                return tmp1

def checkObjectCatenative(sent, idx):
    depend2step_items = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[not(@type='conj_and')]/governor[@idx='%s']" % idx)
    for dep2item in depend2step_items:
        tp2  = dep2item.xpath("..")[0].attrib["type"]
        # lm2 = sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx2
        # print "Checking..."
        # print tp2, lm2        
        if "nsubj" == tp2:
            return True
    return False    

def getCatenativeDependent(sent, cate):
    	dependent_items = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[not(@type='conj_and')]/governor[@idx='%s']" % cate.token.attrib["id"])
        ret = []
        # print dependent_predicate
        for depitem in dependent_items:
            idx = depitem.xpath("../dependent")[0].attrib["idx"]
            tp  = depitem.xpath("..")[0].attrib["type"]

            lm = sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)
            ps = sent.xpath("./tokens/token[@id='%s']/POS/text()" % idx)
            
            if 0 == len(lm): lm = ["?"]
            # if 0 == int(idx): continue
            # ret += [(tp, lm[0], sent.xpath("./tokens/token[@id='%s']" % idx)[0])]

            # FOLLOWED BY A TO-INFINITIVE or A GERUND
            if "xcomp" == tp or "ccomp" == tp:
                if checkObjectCatenative(sent, idx):
                    continue
                else:                
                    # ret += getContentPredicativeGovernor(sent, sent.xpath("./tokens/token[@id='%s']" % idx)[0])
                    ret += [(tp, sent.xpath("./tokens/token[@id='%s']" % idx)[0], lm[0], ps[0])]

        if ret != []:
            return governor_t(cate.rel, ret[0][1], ret[0][2], ret[0][3])
        else:
            return cate

def getPhrasal(sent, phgv, phdict):
    dependent_items = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[not(@type='conj_and')]/governor[@idx='%s']" % phgv.token.attrib["id"])
    ret = []
    phrasedeplist = ["advmod", "prt", "prep", "amod", "dobj"]
    for depitem in dependent_items:
        idx = depitem.xpath("../dependent")[0].attrib["idx"]
        tp  = depitem.xpath("..")[0].attrib["type"]
        
        lm = sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)
        ps = sent.xpath("./tokens/token[@id='%s']/POS/text()" % idx)
        
        if 0 == len(lm): lm = ["?"]
        # if 0 == int(idx): continue
        # ret += [(tp, lm[0], sent.xpath("./tokens/token[@id='%s']" % idx)[0])]
        
        # FOLLOWED BY A TO-INFINITIVE or A GERUND
        if tp in phrasedeplist:
            ret += lm
            
            # print "xcomp = "
            # print sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)
            # ret += getContentPredicativeGovernor(sent, sent.xpath("./tokens/token[@id='%s']" % idx)[0])
            # ret += [(tp, sent.xpath("./tokens/token[@id='%s']" % idx)[0], lm[0], ps[0])]
            
    if ret != []:
        candphrase = phgv.lemma + "_" + "_".join(ret)
        # print phgv.lemma
        # print "_"
        # print "_".join(ret)
        # print candphrase
        
        if candphrase in phdict:
            paraphraselist = phdict[candphrase]
            # print candphrase, paraphraselist, "Match Phrase"
            if len(paraphraselist) == 1:
                return governor_t(phgv.rel, phgv.token, paraphraselist[0], phgv.POS)
            else:
                return governor_t(phgv.rel, phgv.token, paraphraselist, phgv.POS)
        else:
            return phgv
    else:
        return phgv

    

            
def getContentPredicativeGovernor(sent, p):
	governing_predicate = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[not(@type='conj_and')]/dependent[@idx='%s']" % p.attrib["id"])
	ret                 = []

	governing_predicate.sort(key=lambda x: x.xpath("../@type")[0])
	
	for pred in governing_predicate:
		idx = pred.xpath("../governor")[0].attrib["idx"]
		tp  = pred.xpath("..")[0].attrib["type"]

		if "advcl" == tp: continue
		
		lm = sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)
		ps = sent.xpath("./tokens/token[@id='%s']/POS/text()" % idx)
		
		if 0 == len(lm): lm = ["?"]
		if 0 == int(idx): continue
		
		ret += [(tp, lm[0], sent.xpath("./tokens/token[@id='%s']" % idx)[0])]

		if "NN" in ps[0]:
			if "prep_of" == tp:
				ret += getContentPredicativeGovernor(sent, sent.xpath("./tokens/token[@id='%s']" % idx)[0])
					
			# else:
			# 	governing_adj = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='amod']/governor[@idx='%s']" % idx)

			# 	if 0 < len(governing_adj):
			# 		governing_adj = governing_adj[0].xpath("../dependent")[0].attrib["idx"]
			# 		ret += [("subj", sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0])]

		if "DT" in ps[0]:
			governing_adj = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/dependent[@idx='%s']" % idx)

			if 0 < len(governing_adj):
				governing_tp  = governing_adj[0].xpath("..")[0].attrib["type"]
				governing_adj = governing_adj[0].xpath("../governor")[0].attrib["idx"]
				ret += [(governing_tp, sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0])]
				
		if 0 < len(lm) and (lm[0] in "ask continue forget refuse tend try want be able unable willing much seem need fail manage hope attempt".split()):
			
			# If it has different subject, abort.
				governing_adj = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='xcomp' or @type='advmod']/governor[@idx='%s']" % idx)

				if 0 < len(governing_adj):
					governing_adj = governing_adj[0].xpath("../dependent")[0].attrib["idx"]
					nsubj_ga      = sent.find("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='nsubj']/governor[@idx='%s']/../dependent" % governing_adj)
					
					if None != nsubj_ga and idx == nsubj_ga.attrib["idx"]:
						ret += [(tp, sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0])]

						governing_adj = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='dep']/governor[@idx='%s']" % governing_adj)

						if 0 < len(governing_adj):
							governing_adj = governing_adj[0].xpath("../dependent")[0].attrib["idx"]
							ret += [(tp, sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0])]
				
		if "num" == tp or "amod" == tp:
			tk = sent.xpath("./tokens/token[@id='%s']" % idx)
			
			if 0 < len(tk):
				ret += getContentPredicativeGovernor(sent, tk[0])

	return ret
		
def getNeg(sent, x):
	return 0 < len(sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='neg']/governor[@idx='%s']" % x.attrib["id"])) or \
			0 < len(sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='advmod']/governor[@idx='%s']/../dependent[text()='less']" % x.attrib["id"]))
