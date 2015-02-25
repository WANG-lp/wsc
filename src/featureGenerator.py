
import random

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

import classify_gen.classify_gensent as CG

#
s_final = collections.namedtuple('s_final', 'sp spa spc spac')

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
    # # catenativelistOther = ['able', 'manage']
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
                      'stand', 'allow', 'permit', 'strive', 'neglect', 'struggle', 'manage']
    negcatenativelist = "forbit miss quit dislike stop deny forget resist escape fail hesitate avoid detest refuse neglect".split()
    
    
    if gv.lemma in catenativelist:
        # print gv.lemma
        newgv = scn.getCatenativeDependent(sent, gv)
        return newgv
    else:
        return gv

def _mapconjgroup(word):
    if word in ['because', 'since', 'as', 'so']:
        return 'because'
    elif word in ['but', 'however', 'althogh']:
        return 'but'
    # elif word in ['even though', 'although']:
    #     return 'even though'
    else:
        return word

def get_conjbit(pathline, negconjcol1):
    # print >>sys.stderr, pathline
    for pathe in pathline.replace("|", " ").split(" "):
        # print >>sys.stderr, pathe
        
        if pathe == "":
            continue
        if pathe.find(":") == -1:
            continue
        pathcol1 = pathe.split(":")[1]
        if pathcol1 in negconjcol1:
            # print >>sys.stderr, "BBB"
            return 1
    return 0

def calc_bitsim(pbit, ibit):
    retsim = 1.0
    if pbit == ibit:
        return 1.0, 1
    else:
        psum = pbit[0] + pbit[1] + pbit[2]
        isum = ibit[0] + ibit[1] + ibit[2]
        if psum == isum:
            return 0.5, 1
        elif (psum - isum) ** 2 == 1:
            return 0.5, -1
    return 0, 0
        
        
def _getpathsim(kbpaths, paths, simscore, pa):
    requiredlist = ["d:conj_", "g:conj_", "d:mark:", "g:mark:"]
    if kbpaths == [''] or paths == ['']:
        return simscore
    else:
        for pathpair in itertools.product(kbpaths, paths):
            path1 = pathpair[0].split(" ")
            path2 = pathpair[1].split(" ")
            if pa.pathgroup == True:
                tmppath1 = []
                tmppath2 = []
                for depword in path1:
                    conjword = depword.replace("g:conj_", "").replace("d:conj_", "").replace("d:mark:", "").replace("g:mark:", "").split(":")[0].split("-i")[0]
                    if conjword  != "d" and conjword != "g":
                        # print >>sys.stderr, "conjword = %s, depword = %s" % (conjword, depword)
                        tmppath1.append(_mapconjgroup(conjword))
                for depword in path2:
                    conjword = depword.replace("g:conj_", "").replace("d:conj_", "").replace("d:mark:", "").replace("g:mark:", "").split(":")[0].split("-i")[0]
                    if conjword  != "d" and conjword != "g":
                        # print >>sys.stderr, "conjword = %s, depword = %s" % (conjword, depword)
                        tmppath2.append(_mapconjgroup(conjword))
                for intsec in set(tmppath1) & set(tmppath2):
                    if "because" in intsec or "but" in intsec:
                        simscore = 1.0
            else:
                for intsec in set(path1) & set(path2):
                    # print "intsec = %s" %(intsec)
                    for required in requiredlist:
                        if intsec.startswith(required):
                            simscore = 1.0
        return simscore

def _rmphrasalctx(ctxline, ph):
    ret = []
    phtype = ph[0]
    # print >>sys.stderr, "ctxline = %s" %(ctxline)
    if ctxline == "":
        return ctxline
    if phtype == 0:
        for ctx in ctxline.strip().split(' '):
            # print >>sys.stderr, "ctx = %s" %(ctx)
            if ctx.split(':')[1] == 'prt':
                continue
            ret.append(ctx)
    else:
        targetctx = ph[2].split("_")[1:]
        for ctx in ctxline.strip().split(' '):
            ctxdep = ctx.split(':')[1]
            if ctxdep.startswith("prep"):
                if ctxdep.split('_')[1:] == targetctx:
                    continue
            if ctx.split(':')[2].split('-')[0] in targetctx:
                continue
            ret.append(ctx)
    return " ".join(ret)

def _setphrel(rel, ph):
    phtype = ph[0]
    if phtype == 2:
        if rel.startswith("prep_"):
            if rel.split("_")[1] in ph[2].split("_")[1:]:
                return "dobj"
    
def _calphpenalty(ph, ctxline, rel, penaltyscore, pa):
    if ph[0] == 0:
        return penaltyscore * 1.0
    if ph[0] == 2:
        return penaltyscore * 0.5
    if ph[0] == 1:
        if rel.startswith("prep_"):
            tarctxl = [rel.split("_")[1]]
        else:
            tarctxl = []

        # print >>sys.stderr, "rel = %s" %(rel)
        if ctxline == "" and rel.startswith("prep_") == False:
            return penaltyscore * 0.2

        reqctxl = ph[2].split("_")[1:]
        if not ctxline == "":
            for ctx in ctxline.split(' '):
                ctxdep = ctx.split(':')[1]
                if ctxdep.startswith("prep_"):
                    tarctxl.append(ctxdep.split('_')[1])
                else:
                    tarctxl.append(ctx.split(':')[2].split('-')[0])

        # print >>sys.stderr, "reqctxl, tarctxl = %s, %s" %(reqctxl, tarctxl)
        for reqctx in reqctxl:
            if reqctx not in tarctxl:
                return penaltyscore * 0.2
        # print >>sys.stderr, "reqctxl, tarctxl = %s, %s" %(reqctxl, tarctxl)                
        return penaltyscore * 1.0
        
def _phrasalget(gv, sent, dirPhDic):
    phrasedict = marshal.load( open(os.path.join(dirPhDic, "phrasedict.msl")) )
    # dirPhDic = "/home/jun-s/work/wsc/data"
    # phrasedict = marshal.load( open("/home/jun-s/work/wsc/data/phrasedict.msl") )
    # phrasedict = {'come': {'come_back': ['answer', 'denote', 'reappear', 're-emerge', 'refer', 'reply', 'respond'], 'come_by': ['acquire']}}

    ###
    dependent_items = sent.xpath("./dependencies[@type='basic-dependencies']/dep[not(@type='conj_and')]/governor[@idx='%s']" % gv.token.attrib["id"])
    ret = []
    phrasedeplist = ["prt"]
    for depitem in dependent_items:
        idx = depitem.xpath("../dependent")[0].attrib["idx"]
        tp  = depitem.xpath("..")[0].attrib["type"]
        lm = sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)
        
        if 0 == len(lm): lm = ["?"]
        if tp in phrasedeplist:
            prttpl = (0, "_".join([gv.lemma, lm[0]]))    # datatype = PRT
            ret.append(prttpl)
    ###
    
    if gv.lemma in phrasedict:
        maxlen = 0
        for phkey in phrasedict[gv.lemma].keys():
            if maxlen < len(phkey.split("_")):
                maxlen = len(phkey.split("_"))
        # maxlen = 3
        sid = int(gv.token.attrib["id"])
        eid = sid + 4
        wordseqlist = []
        for ids in range(sid, eid):
            word = sent.xpath("./tokens/token[@id='%s']/lemma/text()" %ids)
            if word != []:
                wordseqlist.append(word[0])
        wssize = len(wordseqlist)

        paratpllst = []
        if wssize == 2:
            wseq = "_".join(wordseqlist)
            if wseq in phrasedict[gv.lemma]:
                ###
                wseqtpl = (1,) + (wseql[0],) + (wseq,) # datatype = phrasal verb
                # paratpllst = []
                for para in phrasedict[gv.lemma][wseq]:
                    paratpl = (2, para, wseq)
                    paratpllst += [paratpl] # datatype = paraphrase
                ###
                # paraphraselist = [wseq] + phrasedict[gv.lemma][wseq]

        elif wssize == 3:
            for wseql in [wordseqlist, wordseqlist[:-1], [wordseqlist[0]]+[wordseqlist[2]]]:
                wseq = "_".join(wseql)
                if wseq in phrasedict[gv.lemma]:
                    ###
                    wseqtpl = (1,) + (wseql[0],) + (wseq,) # datatype = phrasal verb
                    # paratpllst = []
                    for para in phrasedict[gv.lemma][wseq]:
                        paratpl = (2, para, wseq)
                        paratpllst += [paratpl] # datatype = paraphrase
                    ###
                    # paraphraselist = [wseq] + phrasedict[gv.lemma][wseq]
                    break
        elif wssize == 4:
            for wseql in [wordseqlist, wordseqlist[:-1], wordseqlist[:2]+[wordseqlist[3]], [wordseqlist[0]]+wordseqlist[2:], wordseqlist[:2], [wordseqlist[0]]+[wordseqlist[2]], [wordseqlist[0]]+[wordseqlist[3]]]:
                wseq = "_".join(wseql)
                if wseq in phrasedict[gv.lemma]:
                    ###
                    wseqtpl = (1,) + (wseql[0],) + (wseq,) # datatype = phrasal verb
                    # paratpllst = []
                    for para in phrasedict[gv.lemma][wseq]:
                        paratpl = (2, para, wseq)
                        paratpllst += [paratpl] # datatype = paraphrase
                    ###
                    # paraphraselist = [wseq] + phrasedict[gv.lemma][wseq]
                    break
        ###
        if paratpllst != []:
            ret = ret + [wseqtpl] + paratpllst
            # print >>sys.stderr, "ret = %s" % (ret)
            return scn.governor_t(gv.rel, gv.token, ret, gv.POS)
        ###

        # if paraphraselist != []:
        #     # print >>sys.stderr, "\n\n(paraphraselist = %s)\n\n" % (paraphraselist)
        #     return scn.governor_t(gv.rel, gv.token, paraphraselist, gv.POS)
        else:
            return gv
            
        # newgv = scn.getPhrasal(sent, gv, phrasedict[gv.lemma])
        # return newgv
    else:
        return gv

def calcnewConsim(csim, freq, center):
    # return math.log(1 + csim ** (freq / 1000.0))
    tfreq = min(freq, 900000)
    # return math.log(1 + csim ** (tfreq / 900000.0))
    steep  = 20

    a = (tfreq / 900000.0) ** 0.7
    b = 1.0/(1 + math.exp(-steep*(-center+csim)))
    c = csim ** 0.2
    return (a*b*csim) + (1-a)*c*csim

def calcnewConsimthre(csim, freq, thresh):
    steep  = 20
    center = 0.7

    # a = (tfreq / 900000.0) ** 0.7
    b = 1.0/(1 + math.exp(-steep*(-center+csim)))
    c = csim ** 0.2

    if freq > thresh:
        return b*csim
    else:
        return c*csim    
    

    
class ranker_t:
    def __init__(self, ff, ana, candidates, sent, pa):
        self.NNexamples = []
        self.NN = collections.defaultdict(list)
        self.rankingsRv = collections.defaultdict(list)
        self.statistics = collections.defaultdict(list)
        self.pa	= pa
        self.bitturn = []

        # if pa.simw2v: ff.libiri.setW2VSimilaritySearch(True)
        # if pa.simwn:  ff.libiri.setWNSimilaritySearch(True)
        # if pa.simwn:  ff.libiri.setWNSimilaritySearch(False)

        negcontext = tuple("d:neg:not-r d:neg:no-d d:neg:never-r d:advmod:seldom-r d:advmod:rarely-r d:advmod:hardly-r d:advmod:scarcely-r".split())
        negcontext2 = tuple("d:advmod:however-r d:advmod:nevertheless-r d:advmod:nonetheless-r d:mark:while-i d:mark:unless-i d:mark:although-i d:mark:though-i".split())
        negconjcol1 = tuple(["conj_but"])
        
        # For REAL-VALUED FEATURES, WE FIRST CALCULATE THE RANKING VALUES
        # FOR EACH CANDIDATE.
        for can in candidates:
                
            wPrn, wCan	 = scn.getLemma(ana), scn.getLemma(can)
            vCan				 = can.attrib["id"]
            gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa), scn.getPrimaryPredicativeGovernor(sent, can, pa)
            pathline = scn.getPath(sent, ana, can, pa)
                        
            self.rankingsRv["position"] += [(vCan, -int(can.attrib["id"]))]

            if None != gvAna and None != gvCan:

                # # For ncnaive0pmi
                # clineAna = scn.getFirstOrderContext(sent, gvAna.token).split()
                # clineCan = scn.getFirstOrderContext(sent, gvCan.token).split()
                # # bit = [0,0,0]

                # for c1e in clineAna:
                #     if c1e in negcontext + negcontext2:
                #         bit[0] += 1
                # for c2e in clineCan:
                #     if c2e in negcontext + negcontext2:
                #         bit[1] += 1
                # for pathe in pathline.split():
                #     if pathe == "":
                #         continue
                #     # print >>sys.stderr, pathe
                #     # if pathe in negconj:
                #     #     bit[2] += 1
                #     pathcol1 = pathe.split(":")[1]
                #     if pathcol1 in negconjcol1:
                #         bit[2] += 1
                        
                # print >>sys.stderr, "for PMI = %s ~ %s ~ %s ~ %s" %(clineCan, clineAna, pathline, tuple(bit)) 

                # if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                # else: gvanalemmas = gvAna.lemma[0].split("_")[:1] + gvAna.lemma[1:]
                # if not isinstance(gvCan.lemma, list): gvcanlemmas = [gvCan.lemma]
                # else: gvcanlemmas = gvCan.lemma[0].split("_")[:1] + gvCan.lemma[1:]

                if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                else: gvanalemmas = [x[1] for x in gvAna.lemma]
                if not isinstance(gvCan.lemma, list): gvcanlemmas = [gvCan.lemma]
                else: gvcanlemmas = [x[1] for x in gvCan.lemma]
                
                for (gvanalemma, gvcanlemma) in itertools.product(gvanalemmas, gvcanlemmas):

                    # SELECTIONAL PREFERENCE
                    if "O" == scn.getNEtype(can):
                        ret = ff.sp.calc("%s-%s" % (gvanalemma, gvAna.POS[0].lower()), gvAna.rel, "%s-n-%s" % (wCan, scn.getNEtype(can)))
                        self.rankingsRv["selpref"] += [(vCan, ret[0])]
                        self.rankingsRv["selprefCnt"] += [(vCan, ret[1])]
                                        
                    # NARRATIVE CHAIN FEATURE (C&J08'S OUTPUT)
                    self.rankingsRv["NCCJ08"] += [(vCan, 1 if 1 <= len(ff.nc.getChains(
                        ff.nc.createQuery(gvanalemma, gvAna.rel),
                        ff.nc.createQuery(gvcanlemma, gvCan.rel))) else 0)]
                    self.statistics["NCCJ08"] += [(vCan, "%s ~ %s" % (ff.nc.createQuery(gvanalemma, gvAna.rel), ff.nc.createQuery(gvcanlemma, gvCan.rel)))]
                                
                    # NARRATIVE CHAIN FEATURE
                    if len(ff.ncnaive) > 0:
                        # bit = tuple(bit)
                        for i in xrange(0, 1):
                            # self.rankingsRv["NCNAIVE%sFREQ" % i] += [(vCan, ff.ncnaive[i].getFreqbit("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), bit))]
                            # self.rankingsRv["NCNAIVE%sPMI" % i] += [(vCan, ff.ncnaive[i].getPMIbit("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), bit, discount=1.0/(2**i)))]
                            # self.rankingsRv["NCNAIVE%sNPMI" % i] += [(vCan, ff.ncnaive[i].getNPMIbit("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), bit, discount=1.0/(2**i)))]
                            self.rankingsRv["NCNAIVE%sFREQ" % i] += [(vCan, ff.ncnaive[i].getFreq("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel)))]
                            self.rankingsRv["NCNAIVE%sPMI" % i] += [(vCan, ff.ncnaive[i].getPMI("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), discount=1.0/(2**i)))]
                            self.rankingsRv["NCNAIVE%sNPMI" % i] += [(vCan, ff.ncnaive[i].getNPMI("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), discount=1.0/(2**i)))]
                            
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
                    print >>sys.stderr, "anaphra govornor and candidate govornor are phrasal verb"
                    for anaph in gvAna.lemma:
                        for canph in gvCan.lemma:
                            p1 = anaph[1]
                            p2 = canph[1]
                            ff.iri(self.NN,
                                   vCan,
                                   p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                                   p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph,
                                   pathline,
                                   pa,
                                   ff,
                                   self.bitturn,
                                   self.statistics["iriInstances"],
                                   self.NNexamples,
                            )
                            if p1 == p2:                            
                                ff.iri(self.NN,
                                       vCan,
                                       p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph,
                                       p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                                       pathline,
                                       pa,
                                       ff,
                                       self.bitturn,
                                       self.statistics["iriInstances"],
                                       self.NNexamples,
                                   )

                    
                    # p1 = gvAna.lemma[0].split("_")[0]
                    # p2 = gvCan.lemma[0].split("_")[0]
                    # ff.iri(self.NN,
                    #        vCan,
                    #        p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext4phrasal(sent, gvAna.token), wPrn,
                    #        p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext4phrasal(sent, gvCan.token), wCan,
                    #        pathline,
                    #        pa,
                    #        self.statistics["iriInstances"],
                    #        self.NNexamples,
                    #    )
                    
                    # if "nsubj" == gvAna.rel: gvanarel = "nsubj"
                    # else: gvanarel = "dobj"
                    # if "nsubj" == gvCan.rel: gvcanrel = "nsubj"
                    # else: gvcanrel = "dobj"
                                    
                    # for p1 in gvAna.lemma[1:]:
                    #     for p2 in gvCan.lemma[1:]:
                    #         ff.iri(self.NN,
                    #                vCan,
                    #                p1, gvanarel, gvAna.POS, scn.getFirstOrderContext4phrasal(sent, gvAna.token), wPrn,
                    #                p2, gvcanrel, gvCan.POS, scn.getFirstOrderContext4phrasal(sent, gvCan.token), wCan,
                    #                pathline,
                    #                pa,
                    #                self.statistics["iriInstances"],
                    #                self.NNexamples,
                    #            )
                    
                elif isinstance(gvAna.lemma, list):
                    print >>sys.stderr, "anaphra govornor is phrasal verb"
                    canph = None
                    for anaph in gvAna.lemma:
                        p1 = anaph[1]                            
                        ff.iri(self.NN,
                            vCan,
                            p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                            gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph,
                            pathline,
                            pa,
                            ff,
                            self.bitturn,
                            self.statistics["iriInstances"],
                            self.NNexamples,
                        )
                        
                        if p1 == gvCan.lemma:
                            ff.iri(self.NN,
                                   vCan,
                                   gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph,
                                   p1, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                                   pathline,
                                   pa,
                                   ff,
                                   self.bitturn,
                                   self.statistics["iriInstances"],
                                   self.NNexamples,
                               )
                            


                elif isinstance(gvCan.lemma, list):
                    print >>sys.stderr, "candidate govornor is phrasal verb"
                    anaph = None
                    for canph in gvCan.lemma:
                        p2 = canph[1]
                        ff.iri(self.NN,
                           vCan,
                           gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                           p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph,
                           pathline,
                           pa,
                           ff,
                           self.bitturn,
                           self.statistics["iriInstances"],
                           self.NNexamples,
                        )

                        if p2 == gvAna.lemma:
                            ff.iri(self.NN,
                                   vCan,
                                   p2, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph,
                                   gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                                   pathline,
                                   pa,
                                   ff,
                                   self.bitturn,
                                   self.statistics["iriInstances"],
                                   self.NNexamples,
                               )                            
                                        
                else:
                    anaph = None
                    canph = None
                    ff.iri(self.NN,
                           vCan,
                           gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                           gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan if "O" == scn.getNEtype(can) else scn.getNEtype(can).lower(), canph, 
                           pathline,
                           pa,
                           ff,
                           self.bitturn,
                           self.statistics["iriInstances"],
                           self.NNexamples,
                       )
                    if gvAna.lemma == gvCan.lemma:
                        ff.iri(self.NN,
                               vCan,
                               gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan if "O" == scn.getNEtype(can) else scn.getNEtype(can).lower(), canph,
                               gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph,
                               pathline,
                               pa,
                               ff,
                               self.bitturn,
                               self.statistics["iriInstances"],
                               self.NNexamples,
                           )
                        
                    # ff.iriEnumerate(self.NNexamples,
                    #        vCan,
                    #        gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                    #        gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                    # )
                        

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

    def sort(self):
        for fk in self.NN.keys():
            random.shuffle(self.NN[fk])
			
            self.NN[fk].sort(key=lambda y: y[1], reverse=True)
		
    def getKNNRank(self, x, t, K=20):
        votes = collections.defaultdict(int)

        if 100 < len(self.NN[t]):
            tmpNNt = self.NN[t][:100]
        else:
            tmpNNt = self.NN[t]
        if K < len(self.NN[t]):
            # K = len(self.NN[t])-1
            if len(set([v[0] for v in tmpNNt if v[1] == tmpNNt[K-1][1]])) >= 2 and tmpNNt[K-1][1] == tmpNNt[K][1]:
                return 0
        # if len(set([v[0] for v in tmpNNt if v[1] == tmpNNt[K-1][1]])) >= 2 and tmpNNt[K-1][1] == tmpNNt[K][1]:
            # return 0

        for votedCan, votedScore, bittype in self.NN[t][:K]:
            votes[votedCan] += votedScore

        if len(votes) >= 2 and votes.values()[0] == votes.values()[1]:
            return 0 if self.NN[t][:K][-1][0] != x else 1

        for i, xc in enumerate(sorted(votes.iteritems(), key=lambda y: y[1], reverse=True)):
            if x == xc[0]: return i

        return len(votes)
	
    def getKNNRankValue(self, x, t, K=20, score=False, de=0):
        votes = collections.defaultdict(int)
        if 100 < len(self.NN[t]):
            tmpNNt = self.NN[t][:100]
        else:
            tmpNNt = self.NN[t]
        if K < len(self.NN[t]):
            if len(set([v[0] for v in tmpNNt if v[1] == tmpNNt[K-1][1]])) >= 2 and tmpNNt[K-1][1] == tmpNNt[K][1]:
                return 0
        
        for votedCan, votedScore, bittype in self.NN[t][:K]:
            votes[votedCan] += 1 if not score else votedScore
            
        for i, xc in enumerate(votes.iteritems()):
            if x == xc[0]: return xc[1]

        return de

    def getKNNRankValue4bit(self, x, t, candidates, K=20, score=False, de=0):
        
        votes = collections.defaultdict(int)
        
        if 100 < len(self.NN[t]):
            tmpNNt = self.NN[t][:100]
        else:
            tmpNNt = self.NN[t]
        if K < len(self.NN[t]):
            if len(set([v[0] for v in tmpNNt if v[1] == tmpNNt[K-1][1]])) >= 2 and tmpNNt[K-1][1] == tmpNNt[K][1]:
                return 0

        cand1, cand2 = candidates
        id1 = cand1.attrib["id"]
        id2 = cand2.attrib["id"]
        
                
        for votedCan, votedScore, bittype in self.NN[t][:K]:
            # print >>sys.stderr, "AAA = %s %s" % (votedCan, bittype)
            if bittype == -1:
                voteid = id2 if votedCan == id1 else id1
            else:
                voteid = id1 if votedCan == id1 else id2

            votes[voteid] += 1 if not score else votedScore
                
        for i, xc in enumerate(votes.iteritems()):
            if x == xc[0]: return xc[1]

        return de

# LOAD THE KEY-VALUE STORE.
class feature_function_t:
	def __init__(self, pa, dirExtKb):
		self.pa							 = pa

		self.libiri = None

                if pa.kbsmall:
                    coreftsv = "corefevents.0909small.tsv"
                elif pa.kb4:
                    coreftsv = "corefevents.0126.1.tsv"
                    ncnaivecdb = "corefevents.0126.1.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0126.1.cdblist.tuples.cdb"
                elif pa.kb4e:
                    coreftsv = "corefevents.0212.tsv"
                    ncnaivecdb = "corefevents.0212.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0212.cdblist.tuples.cdb"
                elif pa.kb4e2:
                    coreftsv = "corefevents.0218e2.tsv"
                    ncnaivecdb = "corefevents.0218e2.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0218e2.cdblist.tuples.cdb"
                    # ncnaivecdbbit = "corefevents.0218e2bit.cdblist.ncnaive.0.cdb"
                    # tuplescdbbit = "corefevents.0218e2bit.cdblist.tuples.cdb"
                elif pa.kb87ei:
                    coreftsv = "corefevents.0909inter.tsv"
                    ncnaivecdb = "corefevents.0909inter.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0909inter.cdblist.tuples.cdb"
                elif pa.kb100:
                    coreftsv = "corefevents.100.%s.tsv" % pa.kb100
                    ncnaivecdb = "corefevents.100.%s.cdblist.ncnaive.0.cdb" % pa.kb100
                    tuplescdb = "corefevents.100.%s.cdblist.tuples.cdb" % pa.kb100
                elif pa.kb10:
                    coreftsv = "corefevents.10.%s.tsv" % pa.kb10
                    ncnaivecdb = "corefevents.10.%s.cdblist.ncnaive.0.cdb" % pa.kb10
                    tuplescdb = "corefevents.10.%s.cdblist.tuples.cdb" % pa.kb10
                elif pa.oldkb:
                    coreftsv = "corefevents.tsv"
                else:
                    coreftsv = "corefevents.0909.tsv"
                    ncnaivecdb = "ncnaive0909.0.cdb"
                    tuplescdb = "tuples.0909.tuples.cdb"
		self.libiri    = iri.iri_t(
                        os.path.join(dirExtKb, coreftsv),
                        # os.path.join(dirExtKb, "corefevents.tsv"),
			os.path.join(os.path.dirname(sys.argv[0]), "../bin"),
			dirExtKb,
                        pa,
			os.path.join(dirExtKb, "corefevents.com.lsh"),
			fUseMemoryMap=pa.quicktest,
			)


		self.ncnaive = {}

                # if pa.oldkb == True:
                #     for i in xrange(0, 8):
                #         p                = 1.0/(2**i)
                #         self.ncnaive[i] = ncnaive.ncnaive_t(os.path.join(_getPathKB(), "ncnaive.ds.%s.cdb" % p), os.path.join(_getPathKB(), "tuples.cdb"))
                # else:
                for i in xrange(0, 1):
                    p                = 1.0/(2**i)
                    if pa.oldkb:
                        self.ncnaive[i] = ncnaive.ncnaive_t(os.path.join(_getPathKB(), "ncnaive.ds.%s.cdb" % p), os.path.join(_getPathKB(), "tuples.cdb"))
                    else:
                        self.ncnaive[i] = ncnaive.ncnaive_t(os.path.join(_getPathKB(), ncnaivecdb), os.path.join(_getPathKB(), tuplescdb))
                    # else:
                    #     self.ncnaive[i] = ncnaive.ncnaive_t(os.path.join(_getPathKB(), ncnaivecdbbit), os.path.join(_getPathKB(), tuplescdbbit))
                        
		self.nc        = nccj08.nccj08_t(os.path.join(_getPathKB(), "schemas-size12"), os.path.join(_getPathKB(), "verb-pair-orders"))
		self.sp        = selpref.selpref_t(pathKB=_getPathKB())
                if pa.newpol:
                    self.sentpol   = sentimentpolarity.sentimentpolarity_t(os.path.join(_getPathKB(), "subjclueslen1-HLTEMNLP05_SentiWNlen1.txt"))

                else:
                    self.sentpol   = sentimentpolarity.sentimentpolarity_t(os.path.join(_getPathKB(), "wilson05_subj/subjclueslen1-HLTEMNLP05.tff"))

                    
		# GOOGLE NGRAMS
		self.gn        = googlengram.googlengram_t(os.path.join(_getPathKB(), "ngrams"))
		# self.deptypes  = map(lambda x: "d:%s" % x.strip(), open(os.path.join(dirExtKb, "stanfordDepTypes.txt"))) +\
		# 								 map(lambda x: "g:%s" % x.strip(), open(os.path.join(dirExtKb, "stanfordDepTypes.txt"))) +\
		# 								 ["UNIFORM"]
		self.deptypes = ["UNIFORM"]

	def generateFeatureSet(self, ana, can, sent, ranker, candidates, pa):
		vCan = can.attrib["id"]		
		basicFeature = map(None, self.generateFeature(ana, can, sent, ranker, candidates, pa))
		numVectors = 0
		
		for vote, vector in ranker.NNexamples:
			if vote == vCan:
				numVectors += 1
				yield basicFeature + vector

		if 0 == numVectors:
			yield basicFeature

	def generateFeature(self, ana, can, sent, ranker, candidates, pa):
		conn				 = scn.getConn(sent)
		position		 = "left" if "R1" == ranker.getRank(can.attrib["id"], "position") else "right"
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa), scn.getPrimaryPredicativeGovernor(sent, can, pa)

		# kNN FEATURES.
		ranker.sort()
                flag_ScoreKnn = pa.sknn
                # if pa.sknn:
                #     ScoreKnn = True
                # else:
                #     ScoreKnn = False
		for K in xrange(10):
                        K = K+1
			for fk, fnn in ranker.NN.iteritems():
				r = ranker.getKNNRank(can.attrib["id"], fk, K)
                                # print ranker.bitturn

				#if 0 == r:
				yield "KNN%d_%s_%s" % (K, fk, r), 1
				yield "SKNN%d_%s_%s" % (K, fk, r), ranker.getKNNRankValue(can.attrib["id"], fk, K, flag_ScoreKnn)
				yield "SKNNTURN%d_%s_%s" % (K, fk, r), ranker.getKNNRankValue4bit(can.attrib["id"], fk, candidates, K, flag_ScoreKnn)
					
		# RANKING FEATURES.
		for fk, fr in ranker.rankingsRv.iteritems():
			if "position" == fk: continue
			
			r	=ranker.getRank(can.attrib["id"], fk)

			if "selpref" == fk:
				yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)

			if "NCNAIVE0NPMI" == fk:
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
			if isinstance(gvAna.lemma, list):
				yield "%s_LEX_ADHC1VA_%s,%s" % (position, scn.getLemma(can), gvAna.lemma[0][1]), 1
			else:
				yield "%s_LEX_ADHC1VA_%s,%s" % (position, scn.getLemma(can), gvAna.lemma), 1

		if None != gvCan:
			if isinstance(gvCan.lemma, list):
				yield "%s_LEX_ADHC1VC1_%s,%s" % (position, scn.getLemma(can), gvCan.lemma[0][1]), 1
			else:
				yield "%s_LEX_ADHC1VC1_%s,%s" % (position, scn.getLemma(can), gvCan.lemma), 1
				
		# HEURISTIC POLARITY.
                fhpoldic = collections.defaultdict(int)
		for fHPOL in self.heuristicPolarity(ana, can, sent, ranker, candidates, pa):
                        # print >>sys.stderr, fHPOL
                        fhpoldic[fHPOL[0]] += 1
                for k, v in fhpoldic.iteritems():
                        itemleft = "%s-%d" % (k, v)
                        yield (itemleft, 1)
                        # yield "(%s-%d, 1)" % (k, v)
                        # print >>sys.stderr, "(%s-%d, 1)" % (k, v)

		# NC VERB ORDER.
		# if None != gvAna and None != gvCan:
		# 	diff = self.nc.getVerbPairOrder(gvCan.lemma, gvAna.lemma) - self.nc.getVerbPairOrder(gvAna.lemma, gvCan.lemma)
			
		# 	if diff > 25: yield "NCCJ08_VO_SAME_ORDER", 1
		# 	elif diff < -25: yield "NCCJ08_VO_REVERSE_ORDER", 1

	def heuristicPolarity(self, ana, can, sent, ranker, candidates, pa):
		conn				 = scn.getConn(sent)
		gvCan1, gvCan2 = scn.getPrimaryPredicativeGovernor(sent, candidates[0], pa), scn.getPrimaryPredicativeGovernor(sent, candidates[1], pa)
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa), scn.getPrimaryPredicativeGovernor(sent, can, pa)
		polAna, polCan1, polCan2 = 0, 0, 0
		position		 = "left" if "R1" == ranker.getRank(can.attrib["id"], "position") else "right"

                # print >>sys.stderr, "### gvCan1 = %s, gvCan2 = %s, gvAna = %s" % (gvCan1, gvCan2, gvAna)
		if None == gvAna or None == gvCan1 or None == gvCan2: return

                # if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                # else: gvanalemmas = gvAna.lemma[0].split("_")[:1] + gvAna.lemma[1:]
                # if not isinstance(gvCan1.lemma, list): gvcan1lemmas = [gvCan1.lemma]
                # else: gvcan1lemmas = gvCan1.lemma[0].split("_")[:1] + gvCan1.lemma[1:]
                # if not isinstance(gvCan2.lemma, list): gvcan2lemmas = [gvCan2.lemma]
                # else: gvcan2lemmas = gvCan2.lemma[0].split("_")[:1] + gvCan2.lemma[1:]

                if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                else: gvanalemmas = [x[1] for x in gvAna.lemma]
                if not isinstance(gvCan1.lemma, list): gvcan1lemmas = [gvCan1.lemma]
                else: gvcan1lemmas = [x[1] for x in gvCan1.lemma]
                if not isinstance(gvCan2.lemma, list): gvcan2lemmas = [gvCan2.lemma]
                else: gvcan2lemmas = [x[1] for x in gvCan2.lemma]

                
                for gvanalemma in gvanalemmas:
                
                    for (gvcan1lemma, gvcan2lemma) in itertools.product(gvcan1lemmas, gvcan2lemmas):
                        
                        if None != gvAna:
                            polAna = self.sentpol.getPolarity(gvanalemma) if gvAna.rel == "nsubj" or scn.getDeepSubject(sent, gvAna.token) == ana.attrib["id"] else None
                            # FLIPPING
                            if None != polAna and (scn.getNeg(sent, gvAna.token) or (None != conn and scn.getLemma(conn) in "but although though however".split())): polAna *= -1

                        if None != gvCan1:
                            polCan1 = self.sentpol.getPolarity(gvcan1lemma) if gvCan1.rel == "nsubj" or scn.getDeepSubject(sent, gvCan1.token) == candidates[0].attrib["id"] else None
                            
                            # FLIPPING
                            if None != polCan1 and scn.getNeg(sent, gvCan1.token): polCan1 *= -1
			
                        if None != gvCan2:
                            polCan2 = self.sentpol.getPolarity(gvcan2lemma) if gvCan2.rel == "nsubj" or scn.getDeepSubject(sent, gvCan2.token) == candidates[1].attrib["id"] else None

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

	def iriEnumerate(self, outExamples, NNvoted, p1, r1, ps1, c1, a1, p2, r2, ps2, c2, a2):
		if None == self.libiri: return 0

		for vector in self.libiri.predict(
				"%s-%s" % (p1, ps1[0].lower()), c1, r1, a1, "%s-%s" % (p2, ps2[0].lower()), c2, r2, a2,
				threshold = 1, pos1=ps1, pos2=ps2, limit=1000, fVectorMode=True):
			
			outExamples += [(NNvoted, vector)]

                        
	def iri(self, outNN, NNvoted, p1, r1, ps1, c1, a1, ph1, p2, r2, ps2, c2, a2, ph2, pathline, pa, ff, bitcached, cached = None, outExamples = None):
		if None == self.libiri: return 0
                if pa.noknn == True: return 0
                phnopara = False

                if pa.ph and ph1:
                    if ph1[0] == 0:
                        c1 = _rmphrasalctx(c1, ph1)
                    elif ph1[0] == 2:
                        if phnopara == True: return 0
                        c1 = _rmphrasalctx(c1, ph1)
                        r1 = _setphrel(r1, ph1)
                        
                if pa.ph and ph2:
                    if ph2[0] == 0:
                        c2 = _rmphrasalctx(c2, ph2)
                    elif ph2[0] == 2:
                        if phnopara == True: return 0
                        c2 = _rmphrasalctx(c2, ph2)
                        r2 = _setphrel(r2, ph2)
                        
                # freq_evp = ff.ncnaive[0].getFreq("%s-%s:%s" % (p1, ps1[0].lower(), r1), "%s-%s:%s" % (p2, ps2[0].lower(), r2))
                freq_p1 = ff.ncnaive[0].getFreqPred("%s-%s:%s" % (p1, ps1[0].lower(), r1))
                freq_p2 = ff.ncnaive[0].getFreqPred("%s-%s:%s" % (p2, ps2[0].lower(), r2))
		# ELIMINATE THE ELEMENT WITH THE SAME ROLE AS ROLE.
                
		c1 = " ".join(filter(lambda x: x.split(":")[1] != r1, c1.strip().split(" "))) if "" != c1.strip() else c1
		c2 = " ".join(filter(lambda x: x.split(":")[1] != r2, c2.strip().split(" "))) if "" != c2.strip() else c2

                # print "c1 = %s, c2 = %s" %(c1, c2)

                if pa.bitsim == True:
                    pbit = [0,0,0]
                    paths = pathline.split("|")                
                    negcontext = tuple("d:neg:not-r d:neg:never-r d:advmod:seldom-r d:advmod:rarely-r d:advmod:hardly-r d:advmod:scarcely-r".split())
                    negcontext2 = tuple("d:advmod:however-r d:advmod:nevertheless-r d:advmod:nonetheless-r d:mark:unless-i d:mark:although-i d:mark:though-i".split())
                    negcatenative = tuple("g:xcomp:forbid g:xcomp:miss g:xcomp:quit g:xcomp:dislike g:xcomp:stop g:xcomp:deny g:xcomp:forget g:xcomp:resist g:xcomp:escape g:xcomp:fail g:xcomp:hesitate g:xcomp:avoid g:xcomp:detest g:xcomp:refuse g:xcomp:neglect".split())
                    negconjcol1 = tuple(["conj_but"])

                    for c1e in c1.split(" "):
                        if c1e in negcontext + negcatenative:
                            pbit[0] += 1
                        if c1e in negcontext2:
                            pbit[2] += 1
                            # match += [c1e]
                    for c2e in c2.split(" "):
                        if c2e in negcontext + negcatenative:
                            pbit[1] += 1
                        if c2e in negcontext2:
                            pbit[2] += 1
                            # match += [c2e]
                    pbit[2] += get_conjbit(pathline, negconjcol1)
                    pbit = tuple(pbit)
                
		nnVectors = []
                requiredlist = ["d:conj_", "g:conj_", "d:mark:"]

                # if pa.pathsim1 == True:
                #     conjpath = False
                #     for pppp in paths:
                #         for ppp in pppp.split(" "):
                #             for required in requiredlist:
                #                 if ppp.startswith(required): conjpath = True
                #     print "conjpath = %s" %(conjpath)
                #     print paths

                simretry = False
                if pa.simwn == True:
                    # print >>sys.stderr, "SET SIMWN OFF"
                    self.libiri.setWNSimilaritySearch(False)
                    simretry = True

                # nnn = self.libiri.getNumRules("%s-%s" % (p1, ps1[0].lower()), c1, r1, a1, "%s-%s" % (p2, ps2[0].lower()), c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2, limit=100000)
                # print >>sys.stderr, "NumRules = %d" % (nnn)
                
                # if pa.simwn and nnn == 0:
                #     print >>sys.stderr, "\nCHANGE SIMWN ON\n"
                #     ff.libiri.setWNSimilaritySearch(True)
                classifier = CG.train_classifier()
                
                #for ret, raw in self.libiri.predict(p1, c1, r1, a1, p2, c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2):
                for ret, raw, vec in self.libiri.predict("%s-%s" % (p1, ps1[0].lower()), c1, r1, a1, simretry, "%s-%s" % (p2, ps2[0].lower()), c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2, limit=100000):
                    
                        # print >>sys.stderr, "vec = %s" %(vec)
                        # print >>sys.stderr, "raw = %s" %(raw)
                        # if pa.gensent == True:
                        #     instid = raw[-1].lstrip("# ").strip()
                        #     # instid = "1008wb-40:724:1:12"
                        #     # print >>sys.stderr, "instid = %s" %(instid)
                        #     generality = CG.classify_sent(classifier, instid)
                        #     # print >>sys.stderr, "generality = %d" %(generality)
                            
                        # penaltyscore = 1.0
                        penalty_ph = 1.0
                        # penalty_path = 1.0
                        penalty_bit = 1.0
                        # penalty_insent = 1.0
                        flag_continue_bit = 0
                        flag_continue_ph = 0
                        # print >>sys.stderr, "ph1 = %s" %(repr(ph1))                        
                        # print >>sys.stderr, "ph2 = %s" %(repr(ph2))
                        
                        if pa.bitsim == True:
                            icl, icr, ipath = raw[4], raw[5], raw[6]                        
                            ibit = [0,0,0]
                            match = []


                            predl = raw[0].split("-")[0]
                            predr = raw[1].split("-")[0]

                            # print >>sys.stderr, "predl, predr = %s, %s" %(predl, predr)
                            # print >>sys.stderr, "p1, p2 = %s, %s" %(p1, p2)
                            # print >>sys.stderr, "raw0, raw1 = %s, %s" %(raw[0], raw[1])
                            # print >>sys.stderr, "p1+ps1,r1, p2+ps2,r2 = %s-%s:%s, %s-%s:%s" %(p1, ps1[0].lower(), r1, p2, ps2[0].lower(), r2)

                            psr1 = "%s-%s:%s" %(p1, ps1[0].lower(), r1)
                            psr2 = "%s-%s:%s" %(p2, ps2[0].lower(), r2)
                            
                            if psr1 == raw[0] or psr2 == raw[1]:
                                ic1 = icl
                                ic2 = icr
                            else:
                                ic1 = icr
                                ic2 = icl
                                
                            for ic1e in ic1.split(" "):
                                if ic1e in negcontext + negcatenative:
                                    ibit[0] += 1
                                    match += [ic1e]
                                if ic1e in negcontext2:
                                    ibit[2] += 1
                                    match += [ic1e]
                            for ic2e in ic2.split(" "):
                                if ic2e in negcontext + negcatenative:
                                    ibit[1] += 1
                                    match += [ic2e]
                                if ic1e in negcontext2:
                                    ibit[2] += 1
                                    match += [ic2e]
                            ibit[2] += get_conjbit(ipath, negconjcol1)
                            ibit = tuple(ibit)

                            penalty_bit, bittype = calc_bitsim(pbit, ibit)
                            if bittype == 0 or bittype == -1:
                                flag_continue_bit = 1
                            # else:
                                # print >>sys.stderr, pbit, ibit, bittype, bitsim
                        
                        if ph1 != None or ph2 != None:
                            ctxlinel = raw[4].strip()
                            ctxliner = raw[5].strip()
                            predl = raw[0].split("-")[0]
                            predr = raw[1].split("-")[0]
                            rell = raw[0].split(":")[1]
                            relr = raw[1].split(":")[1]

                            if predl == p1 or predr == p2:
                                # assert(predr == p2)
                                ctxline1 = ctxlinel
                                ctxline2 = ctxliner
                                rel1 = rell
                                rel2 = relr
                            elif predr == p1 or predl == p2:
                                # assert(predl == p2)
                                ctxline1 = ctxliner
                                ctxline2 = ctxlinel
                                rel1 = relr
                                rel2 = rell
                                
                            if ph1 != None:
                                penalty_ph = _calphpenalty(ph1, ctxline1, rel1, penalty_ph, pa)
                                if pa.reqph == True:
                                    if penalty_ph == 0.2 or penalty_ph == 0.5:
                                        flag_continue_ph = 1
                            if ph2  != None:
                                penalty_ph = _calphpenalty(ph2, ctxline2, rel2, penalty_ph, pa)
                                if pa.reqph == True:
                                    # print >>sys.stderr, "ph2 = %s" %(repr(ph2))
                                    if penalty_ph == 0.2 or penalty_ph == 0.5:
                                        flag_continue_ph = 1
                            # print >>sys.stderr, "raw = %s" %(raw)

                        kbpaths = raw[6].split("|")
                        
                        if pa.insent == True: # USE INSTANCES FROM INTER-SENTENTIAL COREFERENCE
                            if "1" == raw[3]:
                                continue

                        if pa.insent2 == True: # SET PENALTY_INSENT=0.5  TO USE INSTANCES FROM NOT INTER-SENTENTIAL COREFERENCE
                            if "1" == raw[3]:
                                penalty_insent = penalty_insent * 0.5

                        # print >>sys.stderr, "raw = %s" % (raw)
                        # print >>sys.stderr, "c1 = %s, c2 = %s" % (c1, c2)

                        # if pa.req == True: # CONTINUE INSTANCES IF NOT CONTAIN REQUIED CONTEXT

                        #     reqc1 = []
                        #     reqc2 = []
                        #     for reqele in requiredlist:
                        #         for matchreq in [x for x in c1.split(" ") if x.startswith(reqele)]:
                        #             reqc1.append(matchreq)
                        #         for matchreq in [x for x in c2.split(" ") if x.startswith(reqele)]:
                        #             reqc2.append(matchreq)
                        #     if raw[0].startswith(p1):
                        #         assert(raw[1].startswith(p2))
                        #         if reqc1 != []:
                        #             if set(reqc1) != set(reqc1) & set(raw[4].strip().split(" ")):
                        #                 continue                                
                        #         if reqc2 != []:
                        #             if set(reqc2) != set(reqc2) & set(raw[5].strip().split(" ")):
                        #                 continue
                        #     else:
                        #         assert(raw[0].startswith(p2))
                        #         assert(raw[1].startswith(p1))
                        #         if reqc1 != []:
                        #             if set(reqc1) != set(reqc1) & set(raw[5].strip().split(" ")):
                        #                 continue                                
                        #         if reqc2 != []:
                        #             if set(reqc2) != set(reqc2) & set(raw[4].strip().split(" ")):
                        #                 continue


                        # if pa.pathsim1 == True or pa.pathsim2 == True:
                        #     if pa.pathsim1: pathsimilarity = 0.5
                        #     elif pa.pathsim2: pathsimilarity = 0
                        #     pathsimilarity = _getpathsim(kbpaths, paths, pathsimilarity, pa)
                        #     if pathsimilarity == 0: continue
                            # print "path similarity = %s" % (pathsimilarity)
                                
                        if pa.simpred1 == True: # SET PRED SIMILARITY = 1 
                            sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sRuleAssoc # * penaltyscore
                        else:
                            sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred*ret.sRuleAssoc # * penaltyscore
                        sp_original = sp

                        centers = [0.6, 0.7, 0.8]
                        threshs = [200000, 500000, 800000]
                        newCsimc = {}
                        newCsimt = {}

                        psr1 = "%s-%s:%s" %(p1, ps1[0].lower(), r1)
                        psr2 = "%s-%s:%s" %(p2, ps2[0].lower(), r2)
                        
                        if psr1 == raw[0] or psr2 == raw[1]:
                            freq_pi = freq_p1
                            freq_pp = freq_p2
                        else:
                            freq_pi = freq_p2
                            freq_pp = freq_p1

                        for center in centers:
                            newCsim1c = calcnewConsim(ret.sIndexContext[ret.iIndexed], freq_pi, center)
                            newCsim2c = calcnewConsim(ret.sPredictedContext, freq_pp, center)
                            newCsimc[center] = newCsim1c * newCsim2c
                        for thresh in threshs:
                            newCsim1t = calcnewConsimthre(ret.sIndexContext[ret.iIndexed], freq_pi, thresh)
                            newCsim2t = calcnewConsimthre(ret.sPredictedContext, freq_pp, thresh)
                            newCsimt[thresh] = newCsim1t * newCsim2t

                        # print >>sys.stderr, ret.sIndexContext[ret.iIndexed], newCsim1,freq_p1 , ret.sPredictedContext, newCsim2, freq_p2, newCsim
                        
                        # if pa.pathsim1 == True:
                        #     sp = sp * pathsimilarity
                        bitcached += [bittype]
                        
                        for settingname in "OFF bitON phON ON".split():
                            sp = sp_original
                            
                            if pa.bitsim == True and settingname in ("bitON", "ON"):                                
                                sp = sp_original * penalty_bit
                                if flag_continue_bit == 1:
                                    continue
                            if pa.ph == True and settingname in ("phON", "ON"):
                                sp = sp_original * penalty_ph
                                if flag_continue_ph == 1:
                                    continue                                

                            spa = sp * ret.sPredictedArg
                            spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            
                            sfinal = s_final(sp, spa, spc, spac)
                            nret = ret._replace(s_final = sfinal)
                            if None != cached: cached += [(NNvoted, nret)]
                            # if None != cached: cached += [(NNvoted, ret)]

                            elif pa.bitsim == True and settingname == bitON:
                                assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/bitsim - ret.score) < 0.1)
                            else:
                                assert(abs(spac/penaltyscore - ret.score) < 0.1)
                        
                            # if pa.simpred1 == True and pa.pathsim1 == True and pa.bitsim == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * pathsimilarity * bitsim) - ret.score) < 0.1)
                            # elif pa.simpred1 == True and pa.bitsim == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * bitsim) - ret.score) < 0.1)
                            # elif pa.pathsim1 == True and pa.bitsim == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * pathsimilarity * bitsim) - ret.score) < 0.1)
                            # elif pa.simpred1 == True and pa.pathsim1 == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * pathsimilarity) - ret.score) < 0.1)
                            # elif pa.simpred1 == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore) - ret.score) < 0.1)
                            # elif pa.pathsim1 == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * pathsimilarity) - ret.score) < 0.1)
                            # elif pa.bitsim == True:
                            #     assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * bitsim) - ret.score) < 0.1)
                            # else:
                            #     assert(abs(spac/penaltyscore - ret.score) < 0.1)
                            
                            outNN["iriPred%s" %(settingname)] += [(NNvoted, sp, bittype)]
                            outNN["iriPredArg%s" %(settingname)] += [(NNvoted, spa, bittype)]
                            outNN["iriPredCon%s" %(settingname)] += [(NNvoted, spc, bittype)]
                            outNN["iriPredArgCon%s" %(settingname)] += [(NNvoted, spac, bittype)]
                            outNN["iriArg%s" %(settingname)] += [(NNvoted, ret.sPredictedArg, bittype)]
                            outNN["iriCon%s" %(settingname)] += [(NNvoted, ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext, bittype)]
                            outNN["iriArgCon%s" %(settingname)] += [(NNvoted, ret.sPredictedArg*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext, bittype)]

                            for settingnameNCon, newCsim in newCsimc.items():
                                outNN["iriPredNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, sp * newCsim, bittype)]
                                outNN["iriPredArgNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, spa * newCsim, bittype)]
                                outNN["iriNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, newCsim, bittype)]
                                outNN["iriArgNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, ret.sPredictedArg*newCsim, bittype)]
                            for settingnameNCon, newCsim in newCsimt.items():
                                outNN["iriPredNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, sp * newCsim, bittype)]
                                outNN["iriPredArgNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, spa * newCsim, bittype)]
                                outNN["iriNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, newCsim, bittype)]
                                outNN["iriArgNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, ret.sPredictedArg*newCsim, bittype)]

                            # outNN["iriAddPredCon%s" %(settingname)] += [(NNvoted, sp + 0.5*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
                            # outNN["iriAddPredArgCon%s" %(settingname)] += [(NNvoted, sp + 0.2*ret.sPredictedArg + 0.5*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
                            # outNN["iriAddPredArg%s" %(settingname)] += [(NNvoted, sp + 0.2*ret.sPredictedArg)]
                            

                            # print >>sys.stderr, bitcached
                            nnVectors += [(spac, vec)]                            
                            # CONTEX TYPE-WISE EVAL.
                            def _calcConSim(_c, typelist):
				scw, scZw = 0.0, 0.0
				scd, scZd = 0.0, 0.0

				for _t, _v in _c:
                                    isfind = 0
                                    for atype in typelist:
                                        if _t.find(atype) != -1:
                                            isfind = 1
                                            # sc  += 0.01 * float(_v)
                                            # scZ += 0.01
                                        #     continue
                                        # else:
                                    if isfind == 1:
                                        scw  += 1.0 * float(_v)
                                        scZw += 1.0
                                        scd  += 1.0 * float(_v)
                                        scZd += 1.0
                                    else:
                                        scw  += 0.1 * float(_v)
                                        scZw += 0.1
                                # print >>sys.stderr, "==="
                                # print >>sys.stderr, scw, scZw
                                # print >>sys.stderr, scd, scZd
                                if scZw == 0:
                                    scZw, scw = 1.0, 1.0
                                if scZd == 0:
                                    scZd, scd = 1.0, 1.0
				return scw/scZw, scd/scZd


                            # tmp = [["nsubj", "dobj", "prep_"]]
                            deptypedic = {}
                            deptypedic["Min"] = ["obj", "prep_"]
                            deptypedic["Min+subj"] = ["nsubj", "obj", "prep_"]
                            deptypedic["Min+xcomp"] = ["xcomp", "obj", "prep_"]
                            deptypedic["Min+xcomp+nsubj"] = ["nsubj", "xcomp", "obj", "prep_"]
                            
                            for typename, typelist in deptypedic.items():
				# funcWeight = lambda x: 100.0 if None != re.match("^%s$" % weightedType, x) else 1.0
				# funcWeight = lambda x: 100.0 if weightedType in x else 1.0
				# funcWeight = lambda x: 0.1 if weightedType in x else 1.0

				try:
					sc_iw, sc_id = _calcConSim(vec[ret.iIndexed], typelist)
                                        sc_pw, sc_pd = _calcConSim(vec[2], typelist)
				except IndexError:
					continue

                                # print >>sys.stderr, sc_iw, sc_pw
                                # print >>sys.stderr, sc_id, sc_pd
                                
				outNN["iriPredArgConW_%s_%s" % (typename, settingname)] += [(NNvoted, spa * sc_iw * sc_pw, bittype)]
                                outNN["iriPredArgConD_%s_%s" % (typename, settingname)] += [(NNvoted, spa * sc_id * sc_pd, bittype)]
                                outNN["iriPredConW_%s_%s" % (typename, settingname)] += [(NNvoted, sp * sc_iw * sc_pw, bittype)]
                                outNN["iriPredConD_%s_%s" % (typename, settingname)] += [(NNvoted, sp * sc_id * sc_pd, bittype)]
                                outNN["iriConW_%s_%s" %(typename, settingname)] += [(NNvoted, sc_iw * sc_pw, bittype)]
                                outNN["iriConD_%s_%s" %(typename, settingname)] += [(NNvoted, sc_id * sc_pd, bittype)]
                                outNN["iriArgConW_%s_%s" %(typename, settingname)] += [(NNvoted, ret.sPredictedArg * sc_iw * sc_pw, bittype)]
                                outNN["iriArgConD_%s_%s" %(typename, settingname)] += [(NNvoted, ret.sPredictedArg * sc_id * sc_pd, bittype)]

                                newCsimcw = {}
                                newCsimcd = {}
                                newCsimtw = {}
                                newCsimtd = {}
                                for center in centers:
                                    newCsim1cw = calcnewConsim(sc_iw, freq_pi, center)
                                    newCsim2cw = calcnewConsim(sc_pw, freq_pp, center)
                                    newCsimcw[center] = newCsim1cw * newCsim2cw
                                    newCsim1cd = calcnewConsim(sc_id, freq_pi, center)
                                    newCsim2cd = calcnewConsim(sc_pd, freq_pp, center)
                                    newCsimcd[center] = newCsim1cd * newCsim2cd


                                for thresh in threshs:
                                    newCsim1tw = calcnewConsimthre(sc_iw, freq_pi, thresh)
                                    newCsim2tw = calcnewConsimthre(sc_pw, freq_pp, thresh)
                                    newCsimtw[thresh] = newCsim1tw * newCsim2tw
                                    newCsim1td = calcnewConsimthre(sc_id, freq_pi, thresh)
                                    newCsim2td = calcnewConsimthre(sc_pd, freq_pp, thresh)
                                    newCsimtd[thresh] = newCsim1td * newCsim2td

                                # newCsimiw = calcnewConsim(sc_iw, freq_p1)
                                # newCsimpw = calcnewConsim(sc_pw, freq_p2)
                                # newCsimw = newCsimiw * newCsimpw
                                # newCsimid = calcnewConsim(sc_id, freq_p1)
                                # newCsimpd = calcnewConsim(sc_pd, freq_p2)
                                # newCsimd = newCsimid * newCsimpd

                                # for Ncon center
                                for settingnameNCon, newCsim in newCsimcw.items():
                                    outNN["iriPredArgNConW_center%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, spa * newCsim, bittype)]
                                    outNN["iriPredNConW_center%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, sp * newCsim, bittype)]
                                    outNN["iriNConW_center%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, newCsim, bittype)]
                                    outNN["iriArgNConW_center%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, ret.sPredictedArg * newCsim, bittype)]
                                for settingnameNCon, newCsim in newCsimcd.items():
                                    outNN["iriPredArgNConD_center%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, spa * newCsim, bittype)]
                                    outNN["iriPredNConD_center%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, sp * newCsim, bittype)]
                                    outNN["iriNConD_center%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, newCsim, bittype)]
                                    outNN["iriArgNConD_center%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, ret.sPredictedArg * newCsim, bittype)]
                                # for Ncon thresh
                                for settingnameNCon, newCsim in newCsimtw.items():
                                    outNN["iriPredArgNConW_thresh%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, spa * newCsim, bittype)]
                                    outNN["iriPredNConW_thresh%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, sp * newCsim, bittype)]
                                    outNN["iriNConW_thresh%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, newCsim, bittype)]
                                    outNN["iriArgNConW_thresh%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, ret.sPredictedArg * newCsim, bittype)]
                                for settingnameNCon, newCsim in newCsimtd.items():
                                    outNN["iriPredArgNConD_thresh%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, spa * newCsim, bittype)]
                                    outNN["iriPredNConD_thresh%s_%s_%s" % (settingnameNCon, typename, settingname)] += [(NNvoted, sp * newCsim, bittype)]
                                    outNN["iriNConD_thresh%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, newCsim, bittype)]
                                    outNN["iriArgNConD_thresh%s_%s_%s" %(settingnameNCon, typename, settingname)] += [(NNvoted, ret.sPredictedArg * newCsim, bittype)]

                                # print >>sys.stderr, "*****"
                                # print >>sys.stderr, raw
                                # print >>sys.stderr, freq_pi, freq_pp
                                # # print >>sys.stderr, calcnewConsim(0.9, freq_p1), calcnewConsim(0.9, freq_p2)
                                
                                # print >>sys.stderr, calcnewConsim(0.8, freq_pi, 0.7), calcnewConsim(0.8, freq_pp, 0.7)
                                # print >>sys.stderr, calcnewConsim(0.5, freq_pi, 0.7), calcnewConsim(0.5, freq_pp, 0.7)
                                # print >>sys.stderr, calcnewConsimthre(0.8, freq_pi, 500000), calcnewConsimthre(0.8, freq_pp, 500000)
                                # print >>sys.stderr, calcnewConsimthre(0.5, freq_pi, 500000), calcnewConsimthre(0.5, freq_pp, 500000)
                                                                
                                # print >>sys.stderr, newCsimiw, newCsimpw
                                # print >>sys.stderr, newCsimid, newCsimpd
		# for score, goodVec in sorted(nnVectors, key=lambda x: x[0], reverse=True)[:5]:
		# 	outExamples += [(NNvoted, goodVec)]

		return 0
