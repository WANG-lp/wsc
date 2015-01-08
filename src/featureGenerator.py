
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

        
class ranker_t:
    def __init__(self, ff, ana, candidates, sent, pa):
        self.NNexamples = []
        self.NN = collections.defaultdict(list)
        self.rankingsRv = collections.defaultdict(list)
        self.statistics = collections.defaultdict(list)
        self.pa	= pa

        # if pa.simw2v: ff.libiri.setW2VSimilaritySearch(True)
        # if pa.simwn:  ff.libiri.setWNSimilaritySearch(True)
        # if pa.simwn:  ff.libiri.setWNSimilaritySearch(False)
			
        # For REAL-VALUED FEATURES, WE FIRST CALCULATE THE RANKING VALUES
        # FOR EACH CANDIDATE.
        for can in candidates:
                
            wPrn, wCan	 = scn.getLemma(ana), scn.getLemma(can)
            vCan				 = can.attrib["id"]
            gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa), scn.getPrimaryPredicativeGovernor(sent, can, pa)
            pathline = scn.getPath(sent, ana, can, pa)
                        
            self.rankingsRv["position"] += [(vCan, -int(can.attrib["id"]))]

            if None != gvAna and None != gvCan:

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
                        for i in xrange(0, 1):
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

        for votedCan, votedScore in self.NN[t][:K]:
            votes[votedCan] += votedScore

        if len(votes) >= 2 and votes.values()[0] == votes.values()[1]:
            return 0 if self.NN[t][:K][-1][0] != x else 1

        for i, xc in enumerate(sorted(votes.iteritems(), key=lambda y: y[1], reverse=True)):
            if x == xc[0]: return i

        return len(votes)
	
    def getKNNRankValue(self, x, t, K=20, score=False, de=0):
        votes = collections.defaultdict(int)

        # print >>sys.stderr, "$$$$$ = %s" % self.NN[t]
        # print >>sys.stderr, "$$$$$ = %s" % len(set([v for v in self.NN[t] if v[1] == self.NN[t][K][1]]))
        if 100 < len(self.NN[t]):
            tmpNNt = self.NN[t][:100]
        else:
            tmpNNt = self.NN[t]
        if K < len(self.NN[t]):
            # K2 = len(self.NN[t])-1
            if len(set([v[0] for v in tmpNNt if v[1] == tmpNNt[K-1][1]])) >= 2 and tmpNNt[K-1][1] == tmpNNt[K][1]:
            # print >>sys.stderr, "!!!!! = %s" % len(set([v for v in self.NN[t] if v[1] == self.NN[t][K][1]]))
            # print >>sys.stderr, "##### = %s, K = %s" % ([v for v in self.NN[t] if v[1] == self.NN[t][K][1]], K)
                return 0
        
        for votedCan, votedScore in self.NN[t][:K]:
            votes[votedCan] += 1 if not score else votedScore
            
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
                elif pa.kb100:
                    coreftsv = "corefevents.100.%s.tsv" % pa.kb100
                    ncnaivecdb = "corefevents.100.%s.cdblist.ncnaive.0.cdb" % pa.kb100
                    tuplescdb = "corefevents.100.%s.cdblist.tuples.cdb" % pa.kb100
                elif pa.kb10:
                    coreftsv = "corefevents.10.%s.tsv" % pa.kb10
                    ncnaivecdb = "corefevents.10.%s.cdblist.ncnaive.0.cdb" % pa.kb10
                    tuplescdb = "corefevents.10.%s.cdblist.tuples.cdb" % pa.kb10
                    print >>sys.stderr, "coreftsv = %s" % coreftsv
                    print >>sys.stderr, "ncnaivecdb = %s" % ncnaivecdb
                    print >>sys.stderr, "tuplescdb = %s" % tuplescdb
                                       
                elif pa.oldkb:
                    coreftsv = "corefevents.tsv"
                else:
                    coreftsv = "corefevents.0909.tsv"
                    ncnaivecdb = "ncnaive0909.0.cdb"
                    tuplescdb = "tuples.0909.cdb"
		self.libiri    = iri.iri_t(
                        os.path.join(dirExtKb, coreftsv),
                        # os.path.join(dirExtKb, "corefevents.tsv"),
			os.path.join(os.path.dirname(sys.argv[0]), "../bin"),
			dirExtKb,
                        pa,
			os.path.join(dirExtKb, "corefevents.com.lsh"),
			fUseMemoryMap=pa.quicktest
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
                ScoreKnn = True
                
		for K in xrange(10):
                        K = K+1
			for fk, fnn in ranker.NN.iteritems():
				r = ranker.getKNNRank(can.attrib["id"], fk, K)

				#if 0 == r:
				yield "KNN%d_%s_%s" % (K, fk, r), 1
				yield "SKNN%d_%s_%s" % (K, fk, r), ranker.getKNNRankValue(can.attrib["id"], fk, K, ScoreKnn)
					
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
				
	def iri(self, outNN, NNvoted, p1, r1, ps1, c1, a1, ph1, p2, r2, ps2, c2, a2, ph2, pathline, pa, ff, cached = None, outExamples = None):
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


		# ELIMINATE THE ELEMENT WITH THE SAME ROLE AS ROLE.
                
		c1 = " ".join(filter(lambda x: x.split(":")[1] != r1, c1.strip().split(" "))) if "" != c1.strip() else c1
		c2 = " ".join(filter(lambda x: x.split(":")[1] != r2, c2.strip().split(" "))) if "" != c2.strip() else c2

                # print "c1 = %s, c2 = %s" %(c1, c2)
                
		nnVectors = []
                requiredlist = ["d:conj_", "g:conj_", "d:mark:"]
                paths = pathline.split("|")
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
                
                #for ret, raw in self.libiri.predict(p1, c1, r1, a1, p2, c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2):
                for ret, raw, vec in self.libiri.predict("%s-%s" % (p1, ps1[0].lower()), c1, r1, a1, simretry, "%s-%s" % (p2, ps2[0].lower()), c2, r2, a2, threshold = 1, pos1=ps1, pos2=ps2, limit=100000):
                        # print >>sys.stderr, "ret = %s" %(ret)
                            
                        penaltyscore = 1.0
                        if ph1 == True or ph2 == True:
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
                                
                            if ph1:
                                penaltyscore = _calphpenalty(ph1, ctxline1, rel1, penaltyscore, pa)
                                if pa.reqph == True:
                                    if penaltyscore == 0.2 or penaltyscore == 0.5:
                                        continue
                            if ph2:
                                penaltyscore = _calphpenalty(ph2, ctxline2, rel2, penaltyscore, pa)
                                if pa.reqph == True:
                                    if penaltyscore == 0.2 or penaltyscore == 0.5:
                                        continue
                            # print >>sys.stderr, "raw = %s" %(raw)

                        kbpaths = raw[6].split("|")
                        
                        if pa.insent == True: # USE INSTANCES FROM INTER-SENTENTIAL COREFERENCE
                            if "1" == raw[3]:
                                continue

                        if pa.insent2 == True: # SET PENALTYSCORE=0.5  TO USE INSTANCES FROM NOT INTER-SENTENTIAL COREFERENCE
                            if "1" == raw[3]:
                                penaltyscore = penaltyscore * 0.5

                        # print >>sys.stderr, "raw = %s" % (raw)
                        # print >>sys.stderr, "c1 = %s, c2 = %s" % (c1, c2)

                        if pa.req == True: # CONTINUE INSTANCES IF NOT CONTAIN REQUIED CONTEXT

                            reqc1 = []
                            reqc2 = []
                            for reqele in requiredlist:
                                for matchreq in [x for x in c1.split(" ") if x.startswith(reqele)]:
                                    reqc1.append(matchreq)
                                for matchreq in [x for x in c2.split(" ") if x.startswith(reqele)]:
                                    reqc2.append(matchreq)
                            if raw[0].startswith(p1):
                                assert(raw[1].startswith(p2))
                                if reqc1 != []:
                                    if set(reqc1) != set(reqc1) & set(raw[4].strip().split(" ")):
                                        continue                                
                                if reqc2 != []:
                                    if set(reqc2) != set(reqc2) & set(raw[5].strip().split(" ")):
                                        continue
                            else:
                                assert(raw[0].startswith(p2))
                                assert(raw[1].startswith(p1))
                                if reqc1 != []:
                                    if set(reqc1) != set(reqc1) & set(raw[5].strip().split(" ")):
                                        continue                                
                                if reqc2 != []:
                                    if set(reqc2) != set(reqc2) & set(raw[4].strip().split(" ")):
                                        continue


                        if pa.pathsim1 == True or pa.pathsim2 == True:
                            if pa.pathsim1: pathsimilarity = 0.5
                            elif pa.pathsim2: pathsimilarity = 0
                            pathsimilarity = _getpathsim(kbpaths, paths, pathsimilarity, pa)
                            if pathsimilarity == 0: continue
                            # print "path similarity = %s" % (pathsimilarity)
                                
                        if pa.simpred1 == True: # SET PRED SIMILARITY = 1 
                            sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sRuleAssoc*penaltyscore
                        else:
                            sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred*ret.sRuleAssoc*penaltyscore

                        if pa.pathsim1 == True:
                            sp = sp * pathsimilarity

                        spa = sp * ret.sPredictedArg
			spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
			spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext

                        sfinal = s_final(sp, spa, spc, spac)
                        nret = ret._replace(s_final = sfinal)
                        if None != cached: cached += [(NNvoted, nret)]
                        # if None != cached: cached += [(NNvoted, ret)]

                        if pa.simpred1 == True and pa.pathsim1 == True:
                            assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * pathsimilarity) - ret.score) < 0.1)
                        elif pa.simpred1 == True:
                            assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore) - ret.score) < 0.1)
                        elif pa.pathsim1 == True:
                            assert(abs(spac*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred/(penaltyscore * pathsimilarity) - ret.score) < 0.1)
                        else:
                            assert(abs(spac/penaltyscore - ret.score) < 0.1)

			outNN["iriPred"] += [(NNvoted, sp)]
			outNN["iriPredArg"] += [(NNvoted, spa)]
			outNN["iriPredCon"] += [(NNvoted, spc)]
			outNN["iriPredArgCon"] += [(NNvoted, spac)]
			outNN["iriArg"] += [(NNvoted, ret.sPredictedArg)]
			outNN["iriCon"] += [(NNvoted, ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
			outNN["iriArgCon"] += [(NNvoted, ret.sPredictedArg*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
			outNN["iriAddPredCon"] += [(NNvoted, sp + 0.5*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
			outNN["iriAddPredArgCon"] += [(NNvoted, sp + 0.2*ret.sPredictedArg + 0.5*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext)]
			outNN["iriAddPredArg"] += [(NNvoted, sp + 0.2*ret.sPredictedArg)]

			# CONTEX TYPE-WISE EVAL.
			def _calcConSim(_c, _funcWeight):
				sc, scZ = 0.0, 0.0

				for _t, _v in _c:
					sc  += _funcWeight(_t)*float(_v)
					scZ += _funcWeight(_t)

				return sc/scZ

			for weightedType in self.deptypes:
				# funcWeight = lambda x: 100.0 if None != re.match("^%s$" % weightedType, x) else 1.0
				# funcWeight = lambda x: 100.0 if weightedType in x else 1.0
				funcWeight = lambda x: 0.1 if weightedType in x else 1.0

				try:
					sc_i, sc_p = _calcConSim(vec[ret.iIndexed], funcWeight), _calcConSim(vec[2], funcWeight)
				except IndexError:
					continue
					
				outNN["iriPredArgConW_%s" % weightedType] += [(NNvoted, spa * sc_i * sc_p)]
				
			nnVectors += [(spac, vec)]

		# for score, goodVec in sorted(nnVectors, key=lambda x: x[0], reverse=True)[:5]:
		# 	outExamples += [(NNvoted, goodVec)]

		return 0
