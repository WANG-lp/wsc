#
# HELPER FUNCTIONS FOR STANFORD CORE NLP RESULT.
import collections
import sys

import featureGenerator as fgn


def _isPredicativeGovernorRel(x): return x in "nsubjpass nsubj dobj iobj".split() or x.startswith("prep")

governor_t = collections.namedtuple("governor_t", "rel token lemma POS")

def getFirstOrderContext(sent, tk):
        # print getGovernors(sent, tk)
        # print getDependents(sent, tk)
        # print "predicate Lemma = %s\n" % getLemma(tk)

        FOCline = " ".join(
		["d:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getDependents(sent, tk)] +
		["g:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getGovernors(sent, tk)] )
        while "  " in FOCline:
            FOCline = FOCline.replace("  ", " ")
        return FOCline
        
	# return " ".join(
	# 	["d:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getDependents(sent, tk)] +
	# 	["g:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getGovernors(sent, tk)] )

def getFirstOrderContext4phrasal(sent, tk, ph, phtype):
	return " ".join(
		["d:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getDependents4phrasal(sent, tk, ph, phtype)] +
		["g:%s:%s-%s" % (d[0], getLemma(d[1]), getPOS(d[1])[0].lower()) if None != d[1] else "" for d in getGovernors(sent, tk)] )

def searchpath(adjacent, goal, path, endflag, paths):
    n = int(path[len(path) - 1])
    if n == goal:
        paths.append(list(path))
    else:
        for x in adjacent[n]:
            if x not in path:
                path.append(x)
                searchpath(adjacent, goal, path, endflag, paths)
                path.pop()
    if path == endflag:
        return paths

def get_dep_adjacent(xmlSent):
    adjlist = []
    deplist = []
    dependencies = xmlSent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep")
    size = len(xmlSent.xpath("./tokens/token/word/text()"))
    for si in range(size):
        adjlist.append([])
        deplist.append([])
    for xmlDep in dependencies:
        if xmlDep.attrib["type"] != "root":
            iGov, iDep		= int(xmlDep.find("governor").attrib["idx"]), int(xmlDep.find("dependent").attrib["idx"])
            tkGov, tkDep	= getTokenById(xmlSent, iGov), getTokenById(xmlSent, iDep)
            poGov,  poDep = getPOS(tkGov), getPOS(tkDep)
            # neDep         = _getNER(tkDep)
            lm1, rel, lm2 = getLemma(tkGov), xmlDep.attrib["type"], getLemma(tkDep)
            # print iGov, iDep, tkGov, tkDep, rel
            adjlist[iGov-1].append(str(iDep-1))
            deplist[iGov-1].append("d:%s:%s-%s" %(rel, lm2, poDep[0].lower()))
            adjlist[iDep-1].append(str(iGov-1))
            deplist[iDep-1].append("g:%s:%s-%s" %(rel, lm1, poGov[0].lower()))
    return deplist, adjlist

def ids2deps(adjacent, adjacentdep, pathids):
    pathdeps = []
    for path2 in pathids:
        prev = None
        pathdep = []
        for present in path2:
            if prev != None:
                targetindex = adjacent[prev].index(present)
                pathdep.append(adjacentdep[prev][targetindex])
            prev = int(present)
        pathdeps.append(pathdep)
    return pathdeps

def getPath(xmlSent, p1, p2, pa):
    ret = []
    deplist, adjlist = get_dep_adjacent(xmlSent)
    paths = []
    p1sentid, p2sentid = 1, 1
    p1nodeid, p2nodeid = int(p1.attrib["id"])-1 , int(p2.attrib["id"])-1
    
    if abs(p1sentid - p2sentid) == 0:
        paths = []
        # print >>sys.stderr, "nodeid"
        # print >>sys.stderr, p1nodeid, p2nodeid 
        # adjacent = p1.adjl
        # adjacentdep = p1.depl
        # print >>sys.stderr, adjlist
        pathids = searchpath(adjlist, p2nodeid, [p1nodeid], [p1nodeid], paths)
        x = ids2deps(adjlist, deplist, pathids)

        ret = "|".join([" ".join(y) for y in x])
    else:
        ret = ""
    # print >>sys.stderr, ret 
    
    return ret
    
def getToken(sent, x, conn = None):
        # print >>sys.stderr, x
        # print >>sys.stderr, sent
        # print >>sys.stderr, x.split(" ")[-1].strip()
        # print >>sys.stderr, x.split(" ")[-1].strip().replace("'", "")
	# print >>sys.stderr, sent.xpath("./tokens/token/word/text()")

        r = sent.xpath("./tokens/token/word[text()='%s']/.." % x.split(" ")[-1].strip().replace("'", ""))

	if 0 == len(r):
		r = sent.xpath("./tokens/token/word[text()=\"%s\"]/.." % x.split(" ")[-1].strip().replace("\"", ""))
		
		if 0 == len(r):
			r = sent.xpath("./tokens/token/lemma[text()='%s']/.." % x.split(" ")[-1].strip().replace("'", ""))

        print >>sys.stderr, r, len(r)
        # print >>sys.stderr,  "%s %s" % (tk.getprevious().xpath("word/text()")[0], tk.xpath("word/text()")[0])
        
	# DISAMBIGUATE
        if 2 < len(x.split(" ")) and 1 < len(r):
		new_r = []
		
		for tk in r:
			tk_prev = tk.getprevious()
                        tk_prev2 = tk_prev.getprevious()
                        if tk_prev2 == None:
                            continue
                        print >>sys.stderr, "%s %s %s" % (tk_prev2.xpath("word/text()")[0], tk_prev.xpath("word/text()")[0], tk.xpath("word/text()")[0])
                        print >>sys.stderr, " ".join(x.split(" ")[-3:])

                        if "%s %s %s" % (tk_prev2.xpath("word/text()")[0], tk_prev.xpath("word/text()")[0], tk.xpath("word/text()")[0]) == " ".join(x.split(" ")[-3:]):
				new_r += [tk]

		r = new_r
	elif 1 < len(x.split(" ")) and 1 < len(r):
		new_r = []
		
		for tk in r:
			tk_prev = tk.getprevious()
			print >>sys.stderr,  "%s %s" % (tk_prev.xpath("word/text()")[0], tk.xpath("word/text()")[0])
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
        if None == x:
                return None
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
        if None == x:
                return None
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

def getSubj(sent, x):
    return [getTokenById(sent, y.find("dependent").attrib["idx"])
            for y in 
            sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='nsubj']/governor[@idx='%s']/.." % x.attrib["id"])][-1]
def getAuxpass(sent, x):
    # print >>sys.stderr,  sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % x.attrib["id"])
    if [] != sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='auxpass']/governor[@idx='%s']/.." % x.attrib["id"]):
        return [getTokenById(sent, y.find("dependent").attrib["idx"])
                for y in 
                sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='auxpass']/governor[@idx='%s']/.." % x.attrib["id"])][-1]
    else:
        return []

def getTarget(sent, x, target):
    # print >>sys.stderr,  sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % x.attrib["id"])
    if [] != sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='%s']/governor[@idx='%s']/.." % (target, x.attrib["id"])):
        return [getTokenById(sent, y.find("dependent").attrib["idx"])
                for y in 
                sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='%s']/governor[@idx='%s']/.." % (target, x.attrib["id"]))][-1]
    else:
        return []        

def getDependents(sent, x):
	return [
		(y.attrib["type"], getTokenById(sent, y.find("dependent").attrib["idx"]))
		for y in 
		sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % x.attrib["id"])]

def getDependents4phrasal(sent, x, ph, phtype):
    ret = []
    # phrasedeplist = ["advmod", "prt", "prep", "amod", "dobj"]
    dependents = getDependents(sent, x)
    print >>sys.stderr, "Dep4ph = %s\n" %(dependents)
    
    if phtype == 0:
        phrasedeplist = ["prt"]

        for y in sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % x.attrib["id"]):
            # print "Phrasal verb context"
            # print y.attrib["type"]        
            if not y.attrib["type"].strip() in phrasedeplist:
                # print y.attrib["type"]
                ret.append((y.attrib["type"], getTokenById(sent, y.find("dependent").attrib["idx"])))
    elif phtype == 1 or phtype == 2:
        phrasetokenlist = ph.split("_")
        for dep in dependents:
            if not dep[1].xpath("./lemma/text()")[0] in phrasetokenlist[1:]:
                ret.append(dep)
            
            # print >>sys.stderr, "Dep4phlemma = %s, phlist = %s\n" %(dep[1].xpath("./lemma/text()"), phrasetokenlist[1:])

    print >>sys.stderr, "NewDep4ph = %s\n" %(ret)             
    return ret
	
        
def convRel(r, tk, sent):
	# if "agent" == r:
	# 	return "nsubj"
	
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

def checkCatenativeNeg(sent, x, gvx, pa, negcontext, negcontext2, catenativelist):
    isCatenative = False
    isNegCatenative = False
    isNegCatenativeConj = False

    # print >>sys.stderr, "gvlemma = %s" % getLemma(gvx.token)
    # target = x
    # for gxcomp in getXcompGovernors(sent, gvx.token):
    #     if gxcomp != None:
    #         if getLemma(gxcomp) in set(catenativelist):
    #             isCatenative = True
    # print >>sys.stderr, "targetanalemma = %s" % scn.getLemma(targetana)
    
    cg = getContentPredicativeGovernor(sent, x)    
    if 0 < len(cg):
        ps = getPOS(cg[-1][2])
        
        if "VB" in ps or "JJ" in ps:
            tmp1 = governor_t(convRel(cg[-1][0], cg[-1][2], sent), cg[-1][2], cg[-1][1], getPOS(cg[-1][2]))
            if pa.cat:
                tmp2 = fgn._catenativeget(tmp1, sent)
            if pa.cat and tmp1 != tmp2:
                isCatenative = True
                # print >>sys.stderr, "isCatenative2 = True"
                catfoc = getFirstOrderContext(sent, tmp1.token) # get first order context of catenative verb
		catfoc = " ".join(filter(lambda x: x.split(":")[1] != tmp1.rel, catfoc.strip().split(" "))) if "" != catfoc.strip() else catfoc
                for catfoce in catfoc.split(" "):
                    if catfoce in negcontext:
                        isNegCatenative = True
                    if catfoce in negcontext2:
                        isNegCatenativeConj = True

            elif pa.cat and tmp1 == tmp2:
                for gxcomp in getXcompGovernors(sent, tmp1.token):
                    if gxcomp != None:
                        if getLemma(gxcomp) in set(catenativelist):
                            isCatenative = True
                            catfoc = getFirstOrderContext(sent, gxcomp) # get first order context of catenative verb
                            catfoc = " ".join(filter(lambda x: x.split(":")[1] != tmp1.rel, catfoc.strip().split(" "))) if "" != catfoc.strip() else catfoc
                            for catfoce in catfoc.split(" "):
                                if catfoce in negcontext:
                                    isNegCatenative = True
                                if catfoce in negcontext2:
                                    isNegCatenativeConj = True
                
    return (isCatenative, isNegCatenative, isNegCatenativeConj)
                
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

                        # For Copula Sentence
                        if "NN" in ps or "PRP" in ps:
                                dependents = []
                                dependencies = [(y.attrib["type"], getTokenById(sent, y.find("dependent").attrib["idx"])) for y in sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % cg[-1][-1])]
                                for dep in dependencies:
                                    dependents += ["d:%s:" %(dep[0])]
                                if "d:cop:" in dependents:
                                    tmp1 = governor_t(convRel(cg[-1][0], cg[-1][2], sent), cg[-1][2], cg[-1][1], getPOS(cg[-1][2]))
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

                        # For Copula Sentence
                        if "NN" in ps or "PRP" in ps:
                                dependents = []
                                dependencies = [(y.attrib["type"], getTokenById(sent, y.find("dependent").attrib["idx"])) for y in sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep/governor[@idx='%s']/.." % cg[-1][-1])]
                                for dep in dependencies:
                                    dependents += ["d:%s:" %(dep[0])]
                                if "d:cop:" in dependents:
                                    tmp1 = governor_t(convRel(cg[-1][0], cg[-1][2], sent), cg[-1][2], cg[-1][1], getPOS(cg[-1][2]))
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

def getCatRel(sent, idx, catrel):
    if catrel == "nsubj_pass":
        auxpass = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='auxpass']/dependent[@idx='%s']/.." % idx)
        if auxpass == []:
            return "nsubj"
        else:
            return catrel
    else:
        return catrel
    
    
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
                if ps[0] == "TO":
                    continue
                if checkObjectCatenative(sent, idx):
                    continue
                else:
                    newrel = getCatRel(sent, idx, cate.rel)
                    # ret += getContentPredicativeGovernor(sent, sent.xpath("./tokens/token[@id='%s']" % idx)[0])
                    ret += [(tp, sent.xpath("./tokens/token[@id='%s']" % idx)[0], lm[0], ps[0], newrel)]

        if ret != []:
            print >>sys.stderr, "isCatenative = True, %s %s" %(cate.lemma, ret[0][2])
            return governor_t(ret[0][4], ret[0][1], ret[0][2], ret[0][3])
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
            # print sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)

    # similarlist = []
    # if phgv.lemma in phdict:
    #     similarlist = phdict[phgv.lemma]
            
    if ret != []:
        candphrase = phgv.lemma + "_" + "_".join(ret)
        
        if candphrase in phdict:
            paraphraselist = phdict[candphrase]
            # print candphrase, paraphraselist, "Match Phrase"
            # paraphraselist = [phrasal verb] + [paraphrases]
            paraphraselist = [candphrase] + paraphraselist 
            # paraphraselist = paraphraselist + similarlist
            
            # if len(paraphraselist) == 1:
            #     return governor_t(phgv.rel, phgv.token, paraphraselist[0], phgv.POS)
            # else:
            return governor_t(phgv.rel, phgv.token, paraphraselist, phgv.POS)
        else:
            return phgv
            # if similarlist == []:
            #     return phgv
            # else:
            #     return governor_t(phgv.rel, phgv.token, similarlist, phgv.POS)
    else:
    #     if similarlist == []:
    #         return phgv
    #     else:
    #         return governor_t(phgv.rel, phgv.token, similarlist, phgv.POS)
        return phgv

    
def getXcompGovernors(sent, x):
    	return [
		getTokenById(sent, y.find("governor").attrib["idx"])
		for y in 
		sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='xcomp']/dependent[@idx='%s']/.." % x.attrib["id"])]
            
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
		
		ret += [(tp, lm[0], sent.xpath("./tokens/token[@id='%s']" % idx)[0], idx)]

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
				ret += [(governing_tp, sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0], governing_adj)]
				
		if 0 < len(lm) and (lm[0] in "ask continue forget refuse tend try want be able unable willing much seem need fail manage hope attempt".split()):
			
			# If it has different subject, abort.
				governing_adj = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='xcomp' or @type='advmod']/governor[@idx='%s']" % idx)

				if 0 < len(governing_adj):
					governing_adj = governing_adj[0].xpath("../dependent")[0].attrib["idx"]
					nsubj_ga      = sent.find("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='nsubj']/governor[@idx='%s']/../dependent" % governing_adj)
					
					if None != nsubj_ga and idx == nsubj_ga.attrib["idx"]:
						ret += [(tp, sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0], governing_adj)]

						governing_adj = sent.xpath("./dependencies[@type='collapsed-ccprocessed-dependencies']/dep[@type='dep']/governor[@idx='%s']" % governing_adj)

						if 0 < len(governing_adj):
							governing_adj = governing_adj[0].xpath("../dependent")[0].attrib["idx"]
							ret += [(tp, sent.xpath("./tokens/token[@id='%s']/lemma/text()" % governing_adj)[0], sent.xpath("./tokens/token[@id='%s']" % governing_adj)[0], governing_adj)]
				
		if "num" == tp or "amod" == tp:
			tk = sent.xpath("./tokens/token[@id='%s']" % idx)
			
			if 0 < len(tk):
				ret += getContentPredicativeGovernor(sent, tk[0])

	return ret
		
def getNeg(sent, x):
	return 0 < len(sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='neg']/governor[@idx='%s']" % x.attrib["id"])) or \
			0 < len(sent.xpath("./dependencies[@type='basic-dependencies']/dep[@type='advmod']/governor[@idx='%s']/../dependent[text()='less' or text()='scarcely' or text()='hardly' or text()='rarely' or text()='seldom' or text()='lower']" % x.attrib["id"]))
