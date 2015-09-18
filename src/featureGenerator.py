
import random

import iri
import selpref
import googlengram
import nccj08
import ncnaive
import sentimentpolarity

import stanfordHelper as scn
import loadSearchAPIresult as lSAPI

import sys
import itertools
import re
import collections
import math
import os
import cdb
import marshal
import glob
# from kyotocabinet import *

sys.path += ["./subrepo/knowledgeacquisition/bin"]
import flagging
import sdreader
import karesource

import classify_gen.classify_gensent as CG

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
                  'able', 'unable', 'tend', 'delay', 'advise', 'make', 'begin', 'finish',
                  'intend', 'resume', 'detest', 'let', 'plan', 'imagine', 'ask',
                  'come', 'wait', 'regret', 'refuse', 'undertake', 'attempt',
                  'remember', 'disdain', 'try', 'request', 'keep', 'admit', 'swear',
                  'stand', 'allow', 'permit', 'strive', 'neglect', 'struggle', 'manage']
negcatenativelist = "forbit miss quit dislike stop deny forget resist escape fail hesitate avoid detest refuse neglect unable".split()



#
# s_final = collections.namedtuple('s_final', 'sp spa spc spac')

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
            return 0.8, 1
        elif abs(psum - isum) % 2 == 0:
            return 0.8, 1
        elif abs(psum - isum) % 2 == 1:
            return 0.8, -1
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

def _getnphrasal(gv, sent):
    if gv == None:
        return "-", "-", "-"
    ret = []
    ret += [gv.lemma]
    phrasedict = marshal.load( open("/home/jun-s/work/wsc/data/phrasedict.msl") )

    prepret = None
    if gv.rel.startswith("prep_"):
        prepret = [gv.lemma, gv.rel.replace("prep_", "")]

    c = scn.getFirstOrderContext(sent, gv.token)
    dependent_items = sent.xpath("./dependencies[@type='basic-dependencies']/dep[not(@type='conj_and')]/governor[@idx='%s']" % gv.token.attrib["id"])

    prtret = None
    for depitem in dependent_items:
        idx = depitem.xpath("../dependent")[0].attrib["idx"]
        tp  = depitem.xpath("..")[0].attrib["type"]
        lm = sent.xpath("./tokens/token[@id='%s']/lemma/text()" % idx)
        if 0 == len(lm): lm = ["?"]
        if tp in ["prt"]:
            prtret = [gv.lemma] + lm

    dicret = None

    if gv.lemma in phrasedict:
        # print >>sys.stderr, gv.lemma
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
                dicret = wordseqlist

        elif wssize == 3:
            for wseql in [wordseqlist, wordseqlist[:-1], [wordseqlist[0]]+[wordseqlist[2]]]:
                wseq = "_".join(wseql)
                if wseq in phrasedict[gv.lemma]:
                    dicret = wseql
                    break
        elif wssize == 4:
            for wseql in [wordseqlist, wordseqlist[:-1], wordseqlist[:2]+[wordseqlist[3]], [wordseqlist[0]]+wordseqlist[2:], wordseqlist[:2], [wordseqlist[0]]+[wordseqlist[2]], [wordseqlist[0]]+[wordseqlist[3]]]:
                wseq = "_".join(wseql)
                if wseq in phrasedict[gv.lemma]:
                    dicret = wseql
                    break

    prepret = "-" if prepret == None else "_".join(prepret)
    prtret = "-"  if prtret == None else "_".join(prtret)
    dicret = "-" if dicret == None else "_".join(dicret)
    return prepret, prtret, dicret

def _phrasalget(gv, sent, dirPhDic="/home/jun-s/work/wsc/data/phrasedict.msl"):
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
            return scn.governor_t(gv.rel, gv.token, ret, gv.POS)
        ###

        # if paraphraselist != []:
        #     # print >>sys.stderr, "\n\n(paraphraselist = %s)\n\n" % (paraphraselist)
        #     return scn.governor_t(gv.rel, gv.token, paraphraselist, gv.POS)
        else:
            # print >>sys.stderr, "ret = %s" % (ret)
            return gv

        # newgv = scn.getPhrasal(sent, gv, phrasedict[gv.lemma])
        # return newgv
    else:
        return gv

def calcnewConsim(csim, freq, center):
    # if csim == 0.0:
    #     csim = 0.1
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

def _isPronoun(x):
    return x in "I|we|you|he|she|it|they".split("|")

def _getsofromctx(ctx):
    s1 = ""
    o1 = ""
    for cline in ctx.strip().split(" "):
        if "obj" in cline.split(":")[1] or "nsubj_pass" in cline.split(":")[1]:
            o1 = cline.split(":")[2]
        elif "subj" in cline.split(":")[1]:
            s1 = cline.split(":")[2]
    return s1, o1

POS_PREDICATE = "VB VBD VBG VBN VBP VBZ JJ JJR JJS".split()
POS_VB = "VB VBD VBG VBN VBP VBZ".split()
POS_NOUN = "NN NNS NNP NNPS PRP PRPS".split()
POS_ADJ = "JJ JJR JJS".split()

def get_VPpengfromctx(v, rel, ctx, ps):
    ret = [v]
    nrel = rel
    tctx = []
    if "::" in ctx or "--" in ctx:
        return ret, nrel

    for x in ctx.strip().split(" "):
        if x.startswith("d:"):
            tctx += [x]

    if ps == "j":
        if "cop" in [x.split(":")[1] for x in tctx]:
            ret = ["be"] + ret
            if rel.startswith("prep_"):
                ret += [rel.split("_")[1]]
                nrel = "dobj"
            else:
                for tlm, tps in [x.split(":", 2)[2].split("-", 1) for x in tctx]:
                    if tps in ["i", "t"]:
                        ret += [tlm]
    if ps == "v":
        if rel.startswith("prep_"):
            ret += [rel.split("_")[1]]
            nrel = "dobj"
        else:
            for tlm, tps in [x.split(":", 2)[2].split("-", 1) for x in tctx]:
                if tps in ["i", "t"]:
                    ret += [tlm]
                elif tps == "j":
                    ret += [tlm]

    return ret, nrel

def get_VPpeng(sent, tk, rel):
    ret = [scn.getLemma(tk)]
    retsurf = [scn.getSurf(tk)]

    vptype = None
    nrel = rel
    tkprev = scn.getPreviousToken(sent, tk)
    tknext = scn.getNextToken(sent, tk)
    tknext2 = scn.getNextToken(sent, tknext)
    # tknext3 = scn.getNextToken(sent, tknext2)

    # print >>sys.stderr, "BBBBB"
    # print >>sys.stderr, scn.getLemma(tkprev), scn.getLemma(tk), scn.getLemma(tknext), scn.getLemma(tknext2),
    # print >>sys.stderr, scn.getPOS(tkprev), scn.getPOS(tk), scn.getPOS(tknext), scn.getPOS(tknext2),

    if scn.getPOS(tk) in POS_VB and scn.getPOS(tknext)[0] in ("TO") and scn.getPOS(tknext2) in POS_VB:
        for tpx, tkx in scn.getGovernors(sent, tknext2):
            if "g:cop:" in tpx[:6]:
                return get_VPpeng(sent, tkx, rel)
        return get_VPpeng(sent, tknext2, rel)

    if scn.getPOS(tk) in POS_ADJ:
        # print >>sys.stderr, [x[0] for x in scn.getDependents(sent, tk)]
        # print >>sys.stderr, rel
        # if "cop" in [x[0] for x in scn.getDependents(sent, tk)]:
        for dep, deptk in scn.getDependents(sent, tk):
            if "cop" in dep:
                ret = ["be"] + ret
                retsurf = [scn.getSurf(deptk)] + retsurf
                vptype = ["BE", "ADJ"]

                if rel.startswith("prep_"):
                    ret += [rel.split("_")[1]]
                    retsurf += [rel.split("_")[1]]
                    vptype = ["BE", "ADJ", "IN"]
                    nrel = "dobj"
                elif scn.getPOS(tknext) in ("IN", "TO"):
                    ret += [scn.getLemma(tknext)]
                    retsurf += [scn.getSurf(tknext)]
                    vptype = ["BE", "ADJ", "IN"]
    elif scn.getPOS(tk) in POS_VB:
        if rel.startswith("prep_"):
            ret += [rel.split("_")[1]]
            retsurf += [rel.split("_")[1]]
            vptype = ["VB", "IN"]
            nrel = "dobj"
        elif scn.getPOS(tknext) in ("IN", "TO"):
            ret += [scn.getLemma(tknext)]
            retsurf += [scn.getSurf(tknext)]
            vptype = ["VB", "IN"]
        elif scn.getPOS(tknext) in POS_ADJ:
            ret += [scn.getLemma(tknext)]
            retsurf += [scn.getSurf(tknext)]
            vptype = ["VB", "ADJ"]
        elif scn.getPOS(tknext) in POS_VB:
            ret += [scn.getLemma(tknext)]
            retsurf += [scn.getSurf(tknext)]
            vptype = ["VB", "VB"]
    return ret, retsurf, vptype, nrel

def getsowdet(sent, tk):
    s1 = ""
    o1 = ""
    for tpdep, tkdep in scn.getDependents(sent, tk):
        depdeplst = []
        if "obj" in tpdep or "nsubj_pass" in tpdep:
            o1 = scn.getLemma(tkdep)
            for tpdepdep, tkdepdep in scn.getDependents(sent, tkdep):
                # if tpdepdep in ["det", "nn"]:
                if tpdepdep in ["nn"]:
                    depdeplst.append(scn.getLemma(tkdepdep))
            if depdeplst != []:
                o1 = "%s %s" %(" ".join(depdeplst), o1)
        elif "subj" in tpdep:
            s1 = scn.getLemma(tkdep)
            for tpdepdep, tkdepdep in scn.getDependents(sent, tkdep):
                # if tpdepdep in ["det", "nn"]:
                if tpdepdep in ["nn"]:
                    depdeplst.append(scn.getLemma(tkdepdep))
            if depdeplst != []:
                s1 = "%s %s" %(" ".join(depdeplst), s1)

    if o1 == "":
        for tpdep, tkdep in scn.getDependents(sent, tk):
            depdeplst = []
            if "prep_" in tpdep:
                o1 = scn.getLemma(tkdep)
                for tpdepdep, tkdepdep in scn.getDependents(sent, tkdep):
                    # if tpdepdep in ["det", "nn"]:
                    if tpdepdep in ["nn"]:
                        depdeplst.append(scn.getLemma(tkdepdep))
                if depdeplst != []:
                    o1 = "%s %s" %(" ".join(depdeplst), o1)

    return s1, o1

def getsowdet4google(sent, tk):
    s1 = ""
    o1 = ""
    for tpdep, tkdep in scn.getDependents(sent, tk):
        depdeplst = []
        if "obj" in tpdep or "nsubj_pass" in tpdep:
            o1 = scn.getSurf(tkdep)
            for tpdepdep, tkdepdep in scn.getDependents(sent, tkdep):
                if tpdepdep in ["det", "nn"]:
                # if tpdepdep in ["nn"]:
                    depdeplst.append(scn.getSurf(tkdepdep))
            if depdeplst != []:
                o1 = "%s %s" %(" ".join(depdeplst), o1)
        elif "subj" in tpdep:
            s1 = scn.getSurf(tkdep)
            for tpdepdep, tkdepdep in scn.getDependents(sent, tkdep):
                if tpdepdep in ["det", "nn"]:
                # if tpdepdep in ["nn"]:
                    depdeplst.append(scn.getSurf(tkdepdep))
            if depdeplst != []:
                s1 = "%s %s" %(" ".join(depdeplst), s1)

    if o1 == "":
        for tpdep, tkdep in scn.getDependents(sent, tk):
            depdeplst = []
            if "prep_" in tpdep:
                o1 = scn.getSurf(tkdep)
                for tpdepdep, tkdepdep in scn.getDependents(sent, tkdep):
                    if tpdepdep in ["det", "nn"]:
                    # if tpdepdep in ["nn"]:
                        depdeplst.append(scn.getSurf(tkdepdep))
                if depdeplst != []:
                    o1 = "%s %s" %(" ".join(depdeplst), o1)

    return s1, o1

def getsvpo(p1, c1, a1, r1, ps1, p2, c2, a2, r2, ps2):
    svosvotype = None
    # svol = None
    # svor = None
    svo1 = None
    svo2 = None
    vp1, nr1 = get_VPpengfromctx(p1, r1, c1, ps1)
    vp2, nr2 = get_VPpengfromctx(p2, r2, c2, ps2)

    s1, o1 = _getsofromctx(c1)
    s2, o2 = _getsofromctx(c2)

    s1, o1 = s1.split("-")[0], o1.split("-")[0]
    s2, o2 = s2.split("-")[0], o2.split("-")[0]

    if "obj" in r2 or "nsubj_pass" in r2 or "prep_" in r2:
           # o2 = o1 if "obj" in r1 or "nsubj_pass" in r1 or "prep_" in r1 else s1
        o2 = a1.split("-")[0]
        svosvotype = "svmsvm" if "obj" in r2 or "nsubj_pass" in r1 or "prep_" in r1 else "mvosvm"
    elif "subj" in r2:
           # s2 = o1 if "obj" in r1 or "nsubj_pass" in r1 or "prep_" in r1 else s1
        s2 = a1.split("-")[0]
        svosvotype = "svmmvo" if "obj" in r2 or "nsubj_pass" in r1 or "prep_" in r1 else "mvomvo"
        # svor = [s2, p2, o2]
        # svol = [s1, p1, o1]
    svo1 = [s1, "%s:%s" % ("_".join(vp1), nr1), o1]
    svo2 = [s2, "%s:%s" % ("_".join(vp2), nr2), o2]

    return svo1, svo2, svosvotype

def getsvo(p1, c1, a1, r1, p2, c2, a2, r2):
    svosvotype = None
    # svol = None
    # svor = None
    svo1 = None
    svo2 = None

    s1, o1 = _getsofromctx(c1)
    s2, o2 = _getsofromctx(c2)

    # if _isPronoun(a1):
    #     if "obj" in r1 or "nsubj_pass" in r1 or "prep_" in r1:
    #        # o1 = o2 if "obj" in r2 or "nsubj_pass" in r2 or "prep_" in r2 else s2
    #        o1 = "%s-n" %a2
    #        svosvotype = "svmsvm" if "obj" in r2 or "nsubj_pass" in r2 else "svmmvo"
    #     elif "subj" in r1:
    #        # s1 = o2 if "obj" in r2 or "nsubj_pass" in r2 or "prep_" in r2 else s2
    #        s1 = "%s-n" %a2
    #        svosvotype = "mvosvm" if "obj" in r2 or "nsubj_pass" in r2 or "prep_" in r2 else "mvomvo"
    #     # svol = [s2, p2, o2]
    #     # svor = [s1, p1, o1]
    # if _isPronoun(a2):
    if "obj" in r2 or "nsubj_pass" in r2 or "prep_" in r2:
           # o2 = o1 if "obj" in r1 or "nsubj_pass" in r1 or "prep_" in r1 else s1
        o2 = "%s-n" %a1
        svosvotype = "svmsvm" if "obj" in r2 or "nsubj_pass" in r1 or "prep_" in r1 else "mvosvm"
    elif "subj" in r2:
           # s2 = o1 if "obj" in r1 or "nsubj_pass" in r1 or "prep_" in r1 else s1
        s2 = "%s-n" %a1
        svosvotype = "svmmvo" if "obj" in r2 or "nsubj_pass" in r1 or "prep_" in r1 else "mvomvo"
        # svor = [s2, p2, o2]
        # svol = [s1, p1, o1]
    svo1 = [s1, p1, o1]
    svo2 = [s2, p2, o2]

    return svo1, svo2, svosvotype
    # return svol, svor, svosvotype

def check_svosvomatch_giga(psvosvo, pairdb):
    lsvo, rsvo = (psvosvo[0], psvosvo[1]) if psvosvo[0][1] <= psvosvo[1][1] else (psvosvo[1], psvosvo[0])
    # print >>sys.stderr, "AAA"
    # print >>sys.stderr, lsvo
    # print >>sys.stderr, rsvo
    # print >>sys.stderr, pairdb.get("~have:nsubj~~~land:nsubj~~0")
    # print >>sys.stderr, pairdb.get("~have:nsubj~~~land:prep_on~~0")
    # print >>sys.stderr, pairdb.get("bee~have:nsubj~~~land:nsubj~~0")

    ret = {}
    ret["VV"] = int(pairdb.get("~%s~~~%s~~%s" %(lsvo[1], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("~%s~~~%s~~%s" %(lsvo[1], rsvo[1], str(psvosvo[2]))) else 0.0

    ret["SVV"] = int(pairdb.get("%s~%s~~~%s~~%s" %(lsvo[0], lsvo[1], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("%s~%s~~~%s~~%s" %(lsvo[0], lsvo[1], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["VOV"] = int(pairdb.get("~%s~%s~~%s~~%s" %(lsvo[1], lsvo[2], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("~%s~%s~~%s~~%s" %(lsvo[1], lsvo[2], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["VSV"] = int(pairdb.get("~%s~~%s~%s~~%s" %(lsvo[1], rsvo[0], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("~%s~~%s~%s~~%s" %(lsvo[1], rsvo[0], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["VVO"] = int(pairdb.get("~%s~~~%s~%s~%s" %(lsvo[1], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("~%s~~~%s~%s~%s" %(lsvo[1], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0

    ret["SVOV"] = int(pairdb.get("%s~%s~%s~~%s~~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("%s~%s~%s~~%s~~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["SVSV"] = int(pairdb.get("%s~%s~~%s~%s~~%s" %(lsvo[0], lsvo[1], rsvo[0], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("%s~%s~~%s~%s~~%s" %(lsvo[0], lsvo[1], rsvo[0], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["SVVO"] = int(pairdb.get("%s~%s~~~%s~%s~%s" %(lsvo[0], lsvo[1], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("%s~%s~~~%s~%s~%s" %(lsvo[0], lsvo[1], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0
    ret["VOSV"] = int(pairdb.get("~%s~%s~%s~%s~~%s" %(lsvo[1], lsvo[2], rsvo[0], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("~%s~%s~%s~%s~~%s" %(lsvo[1], lsvo[2], rsvo[0], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["VOVO"] = int(pairdb.get("~%s~%s~~%s~%s~%s" %(lsvo[1], lsvo[2], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("~%s~%s~~%s~%s~%s" %(lsvo[1], lsvo[2], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0
    ret["VSVO"] = int(pairdb.get("~%s~~%s~%s~%s~%s" %(lsvo[1], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("~%s~~%s~%s~%s~%s" %(lsvo[1], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0

    ret["SVOSV"] = int(pairdb.get("%s~%s~%s~%s~%s~~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[0], rsvo[1], str(psvosvo[2])))) if None != pairdb.get("%s~%s~%s~%s~%s~~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[0], rsvo[1], str(psvosvo[2]))) else 0.0
    ret["SVOVO"] = int(pairdb.get("%s~%s~%s~~%s~%s~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("%s~%s~%s~~%s~%s~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0
    ret["SVSVO"] = int(pairdb.get("%s~%s~~%s~%s~%s~%s" %(lsvo[0], lsvo[1], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("%s~%s~~%s~%s~%s~%s" %(lsvo[0], lsvo[1], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0
    ret["VOSVO"] = int(pairdb.get("~%s~%s~%s~%s~%s~%s" %(lsvo[1], lsvo[2], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("~%s~%s~%s~%s~%s~%s" %(lsvo[1], lsvo[2], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0

    ret["SVOSVO"] = int(pairdb.get("%s~%s~%s~%s~%s~%s~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2])))) if None != pairdb.get("%s~%s~%s~%s~%s~%s~%s" %(lsvo[0], lsvo[1], lsvo[2], rsvo[0], rsvo[1], rsvo[2], str(psvosvo[2]))) else 0.0

    # print sys.stderr, ret

    return ret

def check_svosvomatch(psvosvo, isvosvo, svosvocount):
    #svosvo = [svo1, svo2, conjbit]

    if psvosvo[2] != isvosvo[2]: # conjunction match
        return svosvocount

    # only v-v match
    svosvocount["VV"] += 1

    cache = 0
    # for VV+1
    if psvosvo[0][0] == isvosvo[0][0] != "":
        svosvocount["SVV"] += 1
        cache += 1
    if psvosvo[0][2] == isvosvo[0][2] != "":
        svosvocount["VOV"] += 1
        cache += 1
    if psvosvo[1][0] == isvosvo[1][0] != "":
        svosvocount["VSV"] += 1
        cache += 1
    if psvosvo[1][2] == isvosvo[1][2] != "":
        svosvocount["VVO"] += 1
        cache += 1

    if cache <= 1:
        return svosvocount

    # for VV+2
    if psvosvo[0][0] == isvosvo[0][0] != "" and psvosvo[0][2] == isvosvo[0][2] != "":
        svosvocount["SVOV"] += 1
    if psvosvo[0][0] == isvosvo[0][0] != "" and psvosvo[1][0] == isvosvo[0][0] != "":
        svosvocount["SVSV"] += 1
    if psvosvo[0][0] == isvosvo[0][0] != "" and psvosvo[1][2] == isvosvo[1][2] != "":
        svosvocount["SVVO"] += 1
    if psvosvo[0][2] == isvosvo[0][2] != "" and psvosvo[1][0] == isvosvo[1][0] != "":
        svosvocount["VOOV"] += 1
    if psvosvo[0][2] == isvosvo[0][2] != "" and psvosvo[1][2] == isvosvo[1][2] != "":
        svosvocount["VOVO"] += 1
    if psvosvo[1][0] == isvosvo[1][0] != "" and psvosvo[1][2] == isvosvo[1][2] != "":
        svosvocount["VSVO"] += 1

    if cache == 2:
        return svosvocount

    # for VV+3
    if psvosvo[0][0] != isvosvo[0][0]:
        svosvocount["VOSVO"] += 1
    if psvosvo[0][2] != isvosvo[0][2]:
        svosvocount["SVSVO"] += 1
    if psvosvo[1][0] != isvosvo[1][0]:
        svosvocount["SVOVO"] += 1
    if psvosvo[1][2] != isvosvo[1][2]:
        svosvocount["SVOSV"] += 1

    if cache == 3:
        return svosvocount

    else:
        # for SVOSVO
        svosvocount["SVOSVO"] += 1

    return svosvocount



class ranker_t:
    def __init__(self, ff, ana, candidates, sent, pa, mentions, db, pairdb):

        self.doc = sdreader.createDocFromLXML(sent)
        dbbase = "./subrepo/knowledgeacquisition"

        opt = karesource.option_t(
            pa.verbose,
            os.path.join(dbbase, "./data/catenative-verbs.tsv"),
            os.path.join(dbbase, "./data/ergative-verbs.tsv"),
            os.path.join(dbbase, "./data/linking-verbs.tsv"),
            os.path.join(dbbase, "./data/phrases.ec+wn.txt"),
        )
        self.res = karesource.res_t(opt)        
        
        self.doc.rels += list(self.res.comp.prt(self.doc, self.res))
        ff.setProblemDoc(self.doc, self.res)

        self.NNexamples = []
        self.NN = collections.defaultdict(list)
        self.rankingsRv = collections.defaultdict(list)
        self.statistics = collections.defaultdict(list)
        self.pa	= pa
        # self.numsvosvo = collections.defaultdict(list)
        self.db = db

        # if pa.simw2v: ff.libiri.setW2VSimilaritySearch(True)
        # if pa.simwn:  ff.libiri.setWNSimilaritySearch(True)
        # if pa.simwn:  ff.libiri.setWNSimilaritySearch(False)

        negcontext = set("d:neg:not-r d:neg:no-d d:neg:never-r d:advmod:seldom-r d:advmod:rarely-r d:advmod:hardly-r d:advmod:scarcely-r d:advmod:less-r".split())
        negcontext2 = set("d:advmod:however-r d:advmod:nevertheless-r d:advmod:nonetheless-r d:mark:while-i d:mark:unless-i d:mark:although-i d:mark:though-i".split())
        negconjcol1 = set(["conj_but"])


        
        # For REAL-VALUED FEATURES, WE FIRST CALCULATE THE RANKING VALUES
        # FOR EACH CANDIDATE.
        for can in candidates:
            wPrn, wCan	 = scn.getLemma(ana), scn.getLemma(can)
            # print >>sys.stderr, wPrn, wCan
            vCan				 = can.attrib["id"]
            gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa, ff.doc), scn.getPrimaryPredicativeGovernor(sent, can, pa, ff.doc)

            gvAnaCat = scn.checkCatenativeNeg(sent, ana, gvAna, pa, negcontext, negcontext2, catenativelist)
            gvCanCat = scn.checkCatenativeNeg(sent, can, gvCan, pa, negcontext, negcontext2, catenativelist)
            # print >>sys.stderr, "ana = %s" % ana
            # print >>sys.stderr, "gvAna = %s" % gvAna.token
            # print >>sys.stderr, "gvCan = %s" % gvCan.token

            print >>sys.stderr, "gvAnaCat = %s" % repr(gvAnaCat)
            print >>sys.stderr, "gvCanCat = %s" % repr(gvCanCat)

            if pa.nph == True:
                print >>sys.stderr, "NewPhrasal Start"
                nphAprep, nphAprt, nphAdic = _getnphrasal(gvAna, sent)
                nphCprep, nphCprt, nphCdic = _getnphrasal(gvCan, sent)

                print >>sys.stderr, "nphraseA", nphAprep, nphAprt, nphAdic
                print >>sys.stderr, "nphraseC", nphCprep, nphCprt, nphCdic
                print >>sys.stderr, "NewPhrasal End"

            self.rankingsRv["position"] += [(vCan, -int(can.attrib["id"]))]

            if None != gvAna:
                if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                else: gvanalemmas = [x[1] for x in gvAna.lemma]

                # for gvanalemma in gvanalemmas:

                #     # SELECTIONAL PREFERENCE
                #     if "O" == scn.getNEtype(can):
                #         ret = ff.sp.calc("%s-%s" % (gvanalemma, gvAna.POS[0].lower()), gvAna.rel, "%s-n-%s" % (wCan, scn.getNEtype(can)))
                #         self.rankingsRv["selpref"] += [(vCan, ret[0])]
                #         self.rankingsRv["selprefCnt"] += [(vCan, ret[1])]

                # GOOGLE HIT COUNT

                googleS, googleO = getsowdet4google(sent, gvAna.token)
                svoV = gvAna.lemma
                svoVPlms, svoVPsurfs, vptype, vprel = get_VPpeng(sent, gvAna.token, gvAna.rel)

                # Q1, 2: CV
                # ## USING GOOGLE NGRAM
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

                # ============
                # ## USING GOOGLE SEARCH API

                # # tkNextAna = scn.getNextPredicateToken(sent, ana)
                # if "JJ" in gvAna.POS or "NN" in gvAna.POS:
                #     tkNextAna = scn.getNextPredicateToken(sent, ana)
                # else:
                #     tkNextAna = gvAna.token

                # print >>sys.stderr, "tkNextAna.rel = %s" % gvAna.rel

                # if "dobj" == gvAna.rel:
                #     qC = googleS.split(" ")
                #     self.statistics["subject"] += [(vCan, " ".join(qC))]
                # else:
                #     qC = [scn.getSurf(can)]
                #     # idqC = can.attrib["id"]
                #     # lmqC = [scn.getLemma(can)]

                # if qC[0] in mentions[1].split() and qC[0] in mentions[2].split():
                #     print >>sys.stderr, "EACH MENTION MATCH!"
                #     # WHICH MENTION = CAN?

                #     m1, m2 = mentions[1].split(), mentions[2].split()
                #     lenm1, lenm2 = len(m1), len(m2)

                #     startid1 = int(vCan) - m1.index(qC[0])
                #     startid2 = int(vCan) - m2.index(qC[0])
                #     endid1 = startid1 + lenm1
                #     endid2 = startid2 + lenm2

                #     if startid1 > 0:
                #         surfs1 = [scn.getSurf(scn.getTokenById(sent, x)) for x in range(startid1, endid1)]
                #     else: surfs1 = ""
                #     if startid2 > 0:
                #         surfs2 = [scn.getSurf(scn.getTokenById(sent, x)) for x in range(startid2, endid2)]
                #     else: surfs2 = ""

                #     if " ".join(surfs1) == mentions[1] or " ".join(surfs2) == mentions[1]:
                #         print >>sys.stderr, "%s = %s" %(qC[0], mentions[1])
                #         qC = mentions[1].split()
                #     elif " ".join(surfs1) == mentions[2] or " ".join(surfs2) == mentions[2]:
                #         print >>sys.stderr, "%s = %s" %(qC[0], mentions[2])
                #         qC = mentions[2].split()
                #     else:
                #         print >>sys.stderr, "%s = %s" %(qC[0], mentions[0])
                #         qC = mentions[0].split()

                # else:
                #     if qC[0] in mentions[1].split():
                #         print >>sys.stderr, "%s = %s" %(qC[0], mentions[1])
                #         qC = mentions[1].split()

                #     elif qC[0] in mentions[2].split():
                #         print >>sys.stderr, "%s = %s" %(qC[0], mentions[2])
                #         qC = mentions[2].split()
                #     else:
                #         print >>sys.stderr, "%s = %s" %(qC[0], mentions[0])
                #         qC = mentions[0].split()

                # # lmqC = [scn.getLemma(scn.getTokenById(sent, x)) for x in range(int(idqC) - len(qC)+1, int(idqC)+1)]
                # # print >>sys.stderr, "lmqC = %s" %lmqC
                # labelC = "+".join(qC)


                # qCV = [scn.getSurf(can), scn.getSurf(tkNextAna)]
                # if "nsubj_pass" == gvAna.rel and "JJ" not in gvAna.POS and "NN" not in gvAna.POS:
                #     # print >>sys.stderr, scn.getSurf(gvAna.token)
                #     tktmpqV = scn.getTarget(sent, gvAna.token, "auxpass")
                #     if tktmpqV == []:
                #         print >>sys.stderr, "Cannot find auxpass"
                #         qV = [scn.getSurf(tkNextAna)]
                #         lmqV = [scn.getLemma(tkNextAna)]
                #     else:
                #         qV = [scn.getSurf(tktmpqV), scn.getSurf(tkNextAna)]
                #         lmqV = [scn.getLemma(tktmpqV), scn.getLemma(tkNextAna)]
                # else:
                #     qV = [scn.getSurf(tkNextAna)]
                #     lmqV = [scn.getLemma(tkNextAna)]
                # labelV = "+".join(qV)


                # # ret = ff.gn.search(qC+qV)

                # labelcv = "+".join([labelC, labelV])
                # filename = glob.glob("/home/jun-s/work/wsc/data/google/*_%s.json" %(labelcv))
                # if filename == []:
                #     ret = 0.0
                # else:
                #     ret = int(lSAPI.loadresult(filename[0]))

                # self.statistics["CV"] += [(vCan, " ".join(qC+qV))]
                # self.statistics["governor"] += [(vCan, "%s:%s" % (" ".join(qV),gvAna.rel))]
                # self.rankingsRv["googleCV"] += [(vCan, ret)]
                # self.rankingsRv["ggllogedCV"] += [(vCan, math.log(1+ret))]

                # # Q3, Q4: CVW
                # tkNeighbor = scn.getNextToken(sent, tkNextAna)
                # if None != tkNeighbor:
                #     if scn.getPOS(tkNeighbor) == "DT":
                #         tkNeighborGovs = scn.getGovernors(sent, tkNeighbor)
                #         # print >>sys.stderr, tkNeighborGovs
                #         # print >>sys.stderr, "tkNeighborGovs"
                #         if tkNeighborGovs != None and len(tkNeighborGovs) == 1:
                #             qCV = [scn.getSurf(can), scn.getSurf(tkNextAna)]
                #             qW = [scn.getSurf(tkNeighbor), scn.getSurf(tkNeighborGovs[0][1])]
                #             lmqW = [scn.getLemma(tkNeighbor), scn.getLemma(tkNeighborGovs[0][1])]
                #         else:
                #             qCV = [scn.getSurf(can), scn.getSurf(tkNextAna)]
                #             qW = [scn.getSurf(tkNeighbor)]
                #             lmqW = [scn.getLemma(tkNeighbor)]
                #     else:
                #         # print >>sys.stderr, "POS="
                #         # print >>sys.stderr, scn.getPOS(tkNeighbor)
                #         qCV = [scn.getSurf(can), scn.getSurf(tkNextAna)]
                #         if "JJ" in gvAna.POS or "NN" in gvAna.POS and "RB" in scn.getPOS(tkNeighbor):
                #             qW = [scn.getSurf(gvAna.token)]
                #             lmqW = [scn.getLemma(gvAna.token)]
                #         else:
                #             qW = [scn.getSurf(tkNeighbor)]
                #             lmqW = [scn.getLemma(tkNeighbor)]

                #     labelW = "+".join(qW)
                #     labelcvw = "+".join([labelC, labelV, labelW])
                #     labelma = "+".join([labelC, labelW])
                #     # print >>sys.stderr, "labelcvw = %s" %(labelcvw)
                #     filename = glob.glob("/home/jun-s/work/wsc/data/google/*_%s.json" %(labelcvw))
                #     # print >>sys.stderr, filename
                #     if filename == []:
                #         ret = 0.0
                #     else:
                #         ret = int(lSAPI.loadresult(filename[0]))

                #     # if len(qC+qV+qW) > 4:
                #     #     ret = 0.0
                #     # else:
                #     #     ret = ff.gn.search(qC+qV+qW)
                #     self.statistics["CVW"] += [(vCan, " ".join(qC+qV+qW))]
                #     self.statistics["argument"] += [(vCan, " ".join(qW))]
                #     self.rankingsRv["googleCVW"] += [(vCan, ret)]
                #     self.rankingsRv["ggllogedCVW"] += [(vCan, math.log(1+ret))]

                #     filename = glob.glob("/home/jun-s/work/wsc/data/google2/*_%s.json" %(labelma))
                #     if filename == []:
                #         ret = 0.0
                #     else:
                #         ret = int(lSAPI.loadresult(filename[0]))

                #     self.statistics["MA"] += [(vCan, " ".join(qC+qW))]
                #     self.rankingsRv["googleMA"] += [(vCan, ret)]
                #     self.rankingsRv["ggllogedMA"] += [(vCan, math.log(1+ret))]


                # if "JJ" in gvAna.POS:
                #     # Q5, Q6: JC
                #     qCV = [scn.getSurf(gvAna.token), scn.getSurf(can)]
                #     qJ = [scn.getSurf(gvAna.token)]

                #     labelJ = "+".join(qJ)
                #     labeljc = "+".join([labelJ, labelC])
                #     print >>sys.stderr, "labeljc = %s" %(labeljc)
                #     filename = glob.glob("/home/jun-s/work/wsc/data/google/*_%s.json" %(labeljc))
                #     print >>sys.stderr, filename
                #     if filename == []:
                #         ret = 0.0
                #     else:
                #         ret = int(lSAPI.loadresult(filename[0]))

                #     self.statistics["JC"] += [(vCan, " ".join(qCV))]
                #     self.statistics["adjective"] += [(vCan, " ".join(qJ))]
                #     self.rankingsRv["googleJC"] += [(vCan, ret)]
                #     self.rankingsRv["ggllogedJC"] += [(vCan, math.log(1+ret))]
                # ==============

                svoana = None
                svocan = None
                
                # # SVO COUNT
                # # cAna = scn.getFirstOrderContext(sent, gvAna.token)
                # svoS, svoO = getsowdet(sent, gvAna.token)
                # svoV = gvAna.lemma
                # svoVPlms, svoVPsurfs, vptype, vprel = get_VPpeng(sent, gvAna.token, gvAna.rel)
                # svoVP = "_".join(svoVPlms)
                # svoVPrel = "%s:%s" %(svoVP, vprel)

                # if "obj" in gvAna.rel or "prep_" in gvAna.rel or "nsubj_pass" in gvAna.rel:
                #     # svoO = " ".join(lmqW)
                #     svoO = wCan
                # elif "subj" in gvAna.rel:
                #     # svoS = " ".join(lmqC)
                #     svoS = wCan

                # if svoS != "":
                #     if "NN" in gvAna.POS:
                #         ret = int(db.get("%s~%s~" %(svoS, svoV))) if None != db.get("%s~%s~" %(svoS, svoV)) else 0.0
                #         self.statistics["svocount_svo"] += [(vCan, " ".join([svoS, "be", svoV]))]
                #         ret = math.log(1+ret)
                #         self.rankingsRv["svocountSVO"] += [(vCan, ret)]
                #     elif svoO != "":
                #         ret = int(db.get("%s~%s~%s" %(svoS, svoVP, svoO))) if None != db.get("%s~%s~%s" %(svoS, svoVP, svoO)) else 0.0
                #         self.statistics["svocount_svo"] += [(vCan, " ".join([svoS, svoVP, svoO]))]
                #         ret = math.log(1+ret)
                #         self.rankingsRv["svocountSVO"] += [(vCan, ret)]

                # if "subj" in gvAna.rel and "nsubj_pass" not in gvAna.rel:
                #     # SV
                #     if "NN" in gvAna.POS:
                #         ret = 0.0
                #     else:
                #         ret = int(db.get("%s~%s~" %(svoS, svoVP))) if None != db.get("%s~%s~" %(svoS, svoVP)) else 0.0
                #         self.statistics["svocount_svvo"] += [(vCan, " ".join([svoS, svoVP]))]
                # else:
                #     # VO
                #     ret = int(db.get("~%s~%s" %(svoVP, svoO))) if None != db.get("~%s~%s" %(svoVP, svoO)) else 0.0
                #     self.statistics["svocount_svvo"] += [(vCan, " ".join([svoVP, svoO]))]

                # ret = math.log(1+ret)
                # self.rankingsRv["svocountSVVO"] += [(vCan, ret)]
                # # print >>sys.stderr, "ret = %s" %ret

            if None != gvAna and None != gvCan:
                # pathline = scn.getPath(sent, gvAna.token, gvCan.token, pa)
                pathline = scn.getPath(sent, ana, can, pa)
                # print >>sys.stderr, pathline

                # cansvoS, cansvoO = getsowdet(sent, gvCan.token)
                # cansvoVPlms, cansvoVPsurfs, canvptype, canvprel = get_VPpeng(sent, gvCan.token, gvCan.rel)
                # cansvoVP = "_".join(cansvoVPlms)

                # print >>sys.stderr, "canVP=%s" %(cansvoVP)

                # cansvoV = gvCan.lemma
                # if "obj" in gvCan.rel or "prep_" in gvCan.rel or "nsubj_pass" in gvCan.rel:
                #     # svoO = " ".join(lmqW)
                #     cansvoO = wCan
                # elif "subj" in gvCan.rel:
                #     # svoS = " ".join(lmqC)
                #     cansvoS = wCan

                # cansvoVPrel = "%s:%s" %(cansvoVP, canvprel)
                # svocan = [cansvoS, cansvoVPrel, cansvoO]
                # svoana = [svoS, svoVPrel, svoO]
                pnegconjbit = 0

                for cAnae in scn.getFirstOrderContext(sent, gvAna.token).strip().split():
                    if cAnae in negcontext2:
                        pnegconjbit = 1
                for cCane in scn.getFirstOrderContext(sent, gvCan.token).strip().split():
                    if cCane in negcontext2:
                        pnegconjbit = 1
                pnegconjbit = max(get_conjbit(pathline, negconjcol1), pnegconjbit)

                # svosvocount_giga = check_svosvomatch_giga([svoana, svocan, pnegconjbit], pairdb)

                # for svosvoname, svosvovalue in svosvocount_giga.iteritems():
                #     svosvotype = 1 if svosvoname == "VV" else 2
                #     self.statistics["svopair%d_%s" % (svosvotype, svosvoname)] += [(vCan, svosvovalue)]
                #     self.statistics["svoploged%d_%s" % (svosvotype, svosvoname)] += [(vCan, math.log(1+svosvovalue))]
                #     self.rankingsRv["svopair%d_%s" % (svosvotype, svosvoname)] += [(vCan, svosvovalue)]
                #     self.rankingsRv["svoploged%d_%s" % (svosvotype, svosvoname)] += [(vCan, math.log(1+svosvovalue))]
                # self.statistics["svopair_q"] += [(vCan, "%s==%s==%d" %("~".join(svocan), "~".join(svoana), pnegconjbit))]

                # if cansvoS != "":
                #     if "JJ" in gvCan.POS or "NN" in gvCan.POS:
                #         ret = int(db.get("%s~%s~" %(svoS, svoV))) if None != db.get("%s~%s~" %(svoS, svoV)) else 0.0
                #         self.statistics["svocount_svo"] += [(vCan, " ".join([svoS, "be", svoV]))]
                #         ret = math.log(1+ret)
                #         self.rankingsRv["svocountSVO"] += [(vCan, ret)]
                #     elif cansvoO != "":
                #         ret = int(db.get("%s~%s~%s" %(svoS, svoV, svoO))) if None != db.get("%s~%s~%s" %(svoS, svoV, svoO)) else 0.0
                #         self.statistics["svocount_svo"] += [(vCan, " ".join([svoS, svoV, svoO]))]
                #         ret = math.log(1+ret)
                #         self.rankingsRv["svocountSVO"] += [(vCan, ret)]

                # if psr1 == raw[0] or psr2 == raw[1]:
                #         # matching [svocan svoana pnegconjbit] and [isvol isvor inegconjbit]
                #         svosvocount = check_svosvomatch([svocan, svoana, pnegconjbit], [isvol, isvor, inegconjbit], svosvocount)
                # else:
                #         # matching [svoana svocan pnegconjbit] and [isvol isvor inegconjbit]
                #         svosvocount = check_svosvomatch([svoana, svocan, pnegconjbit], [isvol, isvor, inegconjbit], svosvocount)

                # # for ncnaivepmi
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

                # if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                # else: gvanalemmas = [x[1] for x in gvAna.lemma]
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
                            eAna = sdreader.createTokenFromLXML(gvAna.token)
                            eCan = sdreader.createTokenFromLXML(gvCan.token)
                            e1i, e2i = ff.doc.getEventIndex(eAna, ff.res.lv), ff.doc.getEventIndex(eCan, ff.res.lv)
                            
                            if pa.kbflag == True:
                                self.rankingsRv["NCNAIVE%sFREQ" % i] += [(vCan, ff.ncnaive[i].getFreq("%s-%s:%s" % (e1i, gvAna.POS[0].lower(), ff.doc.getRelationIndex(gvAna.rel, eAna)), "%s-%s:%s" % (e2i, gvCan.POS[0].lower(), ff.doc.getRelationIndex(gvCan.rel, eCan))))]
                                self.rankingsRv["NCNAIVE%sPMI" % i] += [(vCan, ff.ncnaive[i].getPMI("%s-%s:%s" % (e1i, gvAna.POS[0].lower(), ff.doc.getRelationIndex(gvAna.rel, eAna)), "%s-%s:%s" % (e2i, gvCan.POS[0].lower(), ff.doc.getRelationIndex(gvCan.rel, eCan)), discount=1.0/(2**i)))]
                                self.rankingsRv["NCNAIVE%sNPMI" % i] += [(vCan, ff.ncnaive[i].getNPMI("%s-%s:%s" % (e1i, gvAna.POS[0].lower(), ff.doc.getRelationIndex(gvAna.rel, eAna)), "%s-%s:%s" % (e2i, gvCan.POS[0].lower(), ff.doc.getRelationIndex(gvCan.rel, eCan)), discount=1.0/(2**i)))]

                                print >>sys.stderr, "KEYsPH ="
                                print >>sys.stderr, "%s-%s:%s" % (e1i, gvAna.POS[0].lower(), ff.doc.getRelationIndex(gvAna.rel, eAna))
                                print >>sys.stderr, "%s-%s:%s" % (e2i, gvCan.POS[0].lower(), ff.doc.getRelationIndex(gvCan.rel, eCan))

                            else:                                
                                self.rankingsRv["NCNAIVE%sFREQ" % i] += [(vCan, ff.ncnaive[i].getFreq("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel)))]
                                self.rankingsRv["NCNAIVE%sPMI" % i] += [(vCan, ff.ncnaive[i].getPMI("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), discount=1.0/(2**i)))]
                                self.rankingsRv["NCNAIVE%sNPMI" % i] += [(vCan, ff.ncnaive[i].getNPMI("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), discount=1.0/(2**i)))]
                                                                        
                                print >>sys.stderr, "KEYs ="
                                print >>sys.stderr, "%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel)
                                print >>sys.stderr, "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel)


                            print >>sys.stderr, "rankingsRv NCNAIVE = "
                            print >>sys.stderr, [(vCan, ff.ncnaive[i].getFreq("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel)))]
                            print >>sys.stderr, [(vCan, ff.ncnaive[i].getPMI("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), discount=1.0/(2**i)))]                         
                            print >>sys.stderr, [(vCan, ff.ncnaive[i].getNPMI("%s-%s:%s" % (gvanalemma, gvAna.POS[0].lower(), gvAna.rel), "%s-%s:%s" % (gvcanlemma, gvCan.POS[0].lower(), gvCan.rel), discount=1.0/(2**i)))]

                            
                if isinstance(gvAna.lemma, list) and isinstance(gvCan.lemma, list):
                    # print >>sys.stderr, "anaphra govornor and candidate govornor are phrasal verb"
                    for anaph in gvAna.lemma:
                        for canph in gvCan.lemma:
                            p1 = anaph[1]
                            p2 = canph[1]
                            ff.iri(self.NN,
                                   vCan, wCan,
                                   p1, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                                   p2, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan, canph, gvCanCat,
                                   pathline,
                                   pa,
                                   ff,
                                   [svoana, svocan, pnegconjbit],
                                   self.statistics,
                                   self.statistics["iriInstances"],
                                   self.NNexamples,
                                   False
                            )
                            if p1 == p2:
                                ff.iri(self.NN,
                                       vCan, wCan,
                                       p2, gvAna.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan, canph, gvCanCat,
                                       p1, gvCan.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                                       pathline,
                                       pa,
                                       ff,
                                       [svocan, svoana, pnegconjbit],
                                       self.statistics,
                                       self.statistics["iriInstances"],
                                       self.NNexamples,
                                       True
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
                    # print >>sys.stderr, "anaphra govornor is phrasal verb"
                    canph = None
                    for anaph in gvAna.lemma:
                        p1 = anaph[1]
                        ff.iri(self.NN,
                            vCan, wCan,
                            p1, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                            gvCan.lemma, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan, canph, gvCanCat,
                            pathline,
                            pa,
                            ff,
                            [svoana, svocan, pnegconjbit],
                            self.statistics,
                            self.statistics["iriInstances"],
                            self.NNexamples,
                            False
                        )

                        if p1 == gvCan.lemma:
                            ff.iri(self.NN,
                                   vCan, wCan,
                                   gvCan.lemma, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan, canph, gvCanCat,
                                   p1, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                                   pathline,
                                   pa,
                                   ff,
                                   [svocan, svoana, pnegconjbit],
                                   self.statistics,
                                   self.statistics["iriInstances"],
                                   self.NNexamples,
                                   True
                               )



                elif isinstance(gvCan.lemma, list):
                    # print >>sys.stderr, "candidate govornor is phrasal verb"
                    anaph = None
                    for canph in gvCan.lemma:
                        p2 = canph[1]
                        ff.iri(self.NN,
                            vCan, wCan,
                            gvAna.lemma, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                            p2, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan, canph, gvCanCat,
                            pathline,
                            pa,
                            ff,
                            [svoana, svocan, pnegconjbit],
                            self.statistics,
                            self.statistics["iriInstances"],
                            self.NNexamples,
                            False
                        )

                        if p2 == gvAna.lemma:
                            ff.iri(self.NN,
                                   vCan, wCan,
                                   p2, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan, canph, gvCanCat,
                                   gvAna.lemma, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                                   pathline,
                                   pa,
                                   ff,
                                   [svocan, svoana, pnegconjbit],
                                   self.statistics,
                                   self.statistics["iriInstances"],
                                   self.NNexamples,
                                   True
                               )

                else:
                    anaph = None
                    canph = None


                    ff.iri(self.NN,
                           vCan, wCan,
                           gvAna.lemma, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                           gvCan.lemma, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan if "O" == scn.getNEtype(can) else scn.getNEtype(can).lower(), canph, gvCanCat,
                           pathline,
                           pa,
                           ff,
                           [svoana, svocan, pnegconjbit],
                           self.statistics,
                           self.statistics["iriInstances"],
                           self.NNexamples,
                           False
                       )
                    if gvAna.lemma == gvCan.lemma:
                        ff.iri(self.NN,
                               vCan, wCan,
                               gvCan.lemma, gvCan.token, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), can, wCan if "O" == scn.getNEtype(can) else scn.getNEtype(can).lower(), canph, gvCanCat,
                               gvAna.lemma, gvAna.token, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), ana, wPrn, anaph, gvAnaCat,
                               pathline,
                               pa,
                               ff,
                               [svocan, svoana, pnegconjbit],
                               self.statistics,
                               self.statistics["iriInstances"],
                               self.NNexamples,
                               True
                           )
                    # ff.iri(self.NN,
                    #        vCan,
                    #        gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph, gvAnaCat,
                    #        gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph, gvCanCat,
                    #        pathline,
                    #        pa,
                    #        ff,
                    #        self.numsvosvo,
                    #        self.statistics,
                    #        self.statistics["iriInstances"],
                    #        self.NNexamples,
                    #    )
                    # if gvAna.lemma == gvCan.lemma:
                    #     ff.iri(self.NN,
                    #            vCan,
                    #            gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan, canph, gvCanCat,
                    #            gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn, anaph, gvAnaCat,
                    #            pathline,
                    #            pa,
                    #            ff,
                    #            self.numsvosvo,
                    #            self.statistics,
                    #            self.statistics["iriInstances"],
                    #            self.NNexamples,
                    #        )

                    # ff.iriEnumerate(self.NNexamples,
                    #        vCan,
                    #        gvAna.lemma, gvAna.rel, gvAna.POS, scn.getFirstOrderContext(sent, gvAna.token), wPrn,
                    #        gvCan.lemma, gvCan.rel, gvCan.POS, scn.getFirstOrderContext(sent, gvCan.token), wCan,
                    # )


        for rank in self.rankingsRv.values():
            rank.sort(key=lambda x: x[1], reverse=True)

    def getSVOpairRankValue(self, x, t, de = 0.0, src = None):
        for xc in src[t] if None != src else self.numsvosvo[t]:
            # print >>sys.stderr, xc
            if x == xc[0]: return xc[1]

        return de

    def getRankValueOrigin(self, x, t, de = 0.0, src = None):
        for xc in src[t] if None != src else self.rankingsRv[t]:
            if x == xc[0]: return xc[1]

        return de

    def getRankValue(self, x, t, de = 0.0, src = None):
        for xc in src[t] if None != src else self.rankingsRv[t]:
            if (t == "NCNAIVE0NPMI" or t == "selpref") and  1 >= len(self.rankingsRv[t]): return 0.0
            if x == xc[0]: return xc[1]

        return de

    def getRank(self, x, t):
        if 1 >= len(self.rankingsRv[t]) or self.rankingsRv[t][0][1] == self.rankingsRv[t][1][1]:
            return None

        for i, xc in enumerate(self.rankingsRv[t]):
            if x == xc[0]:
                return "R1" if 0 == i else "R2"

    def sort(self):
        for fk in self.NN.keys():
            random.shuffle(self.NN[fk])

            self.NN[fk].sort(key=lambda y: y[1], reverse=True)

    # def getSumVScores(self, x, t, V):
    #     upper = 10000
    #     votes = collections.defaultdict(int)
    #     votesnum = collections.defaultdict(int)
    #     tmp = []

    #     if upper < len(self.NN[t]):
    #         tmpNNt = self.NN[t][:upper]
    #     else:
    #         tmpNNt = self.NN[t]
    #     for votedCan, votedScore, bittype in tmpNNt:
    #         if votesnum[votedCan] == V:
    #             continue
    #         tmp.append([votedCan, votedScore])
    #         votes[votedCan] += votedScore
    #         votesnum[votedCan] += 1

    #     for i, xc in enumerate(votes.iteritems()):
    #         if x == xc[0]: return xc[1], tmp

    #     return 0

    def getSumVScores(self, x, t, candidates, V, revote=False ):
        upper = 10000
        votes = collections.defaultdict(int)
        votesnum = collections.defaultdict(int)
        tmp = []
        num = 1

        if upper < len(self.NN[t]):
            tmpNNt = self.NN[t][:upper]
        else:
            tmpNNt = self.NN[t]

        cand1, cand2 = candidates
        id1 = cand1.attrib["id"]
        id2 = cand2.attrib["id"]

        for votedCan, votedScore, bittype in tmpNNt:

            if revote == False:
                voteid = votedCan
            elif bittype == -1:
                voteid = id2 if votedCan == id1 else id1
            else:
                voteid = id1 if votedCan == id1 else id2

            if votesnum[voteid] == V:
            # if votesnum[votedCan] == 5:
                continue
            tmp.append([voteid, votedScore, bittype])
            votes[voteid] += votedScore
            votesnum[voteid] += 1

        for i, xcn in enumerate(votesnum.iteritems()):
            if x == xcn[0]:
                num = xcn[1]
                if num == 0: num = 1

        for i, xc in enumerate(votes.iteritems()):
            if x == xc[0]: return (1.0 * xc[1] / num), tmp

        return 0, tmp

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
		self.ann = flagging.annotator_t()

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
                elif pa.kbflag:
                    coreftsv = "corefevents.0901.exact.assoc.filtered2.tsv"
                    ncnaivecdb = "corefevents.0901.exact.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0901.exact.cdblist.tuples.cdb"
                elif pa.kbflagsmall:
                    coreftsv = "corefevents.0826small.fixed.tsv"
                    ncnaivecdb = "corefevents.0826small.fixed.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0826small.fixed.cdblist.tuples.cdb"
                elif pa.kbflagnoph:
                    coreftsv = "corefevents.0826.fixed.noph.exact.tsv"
                    ncnaivecdb = "corefevents.0826.fixed.noph.exact.cdblist.ncnaive.0.cdb"
                    tuplescdb = "corefevents.0826.fixed.noph.exact.cdblist.tuples.cdb"
                # elif pa.kbflagnoph:
                #     coreftsv = "corefevents.0826.fixed.filtered.noph.tsv"
                #     ncnaivecdb = "corefevents.0826.fixed.filtered.noph.cdblist.ncnaive.0.cdb"
                #     tuplescdb = "corefevents.0826.fixed.filtered.noph.cdblist.tuples.cdb"
                elif pa.kb4e2down:
                    coreftsv = "corefevents.0218e2down%s.tsv" % pa.kb4e2down
                    ncnaivecdb = "corefevents.0218e2down%s.cdblist.ncnaive.0.cdb" % pa.kb4e2down
                    tuplescdb = "corefevents.0218e2down%s.cdblist.tuples.cdb" % pa.kb4e2down
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
                elif pa.kb0909:
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

	def setProblemDoc(self, doc, res):
		self.doc = doc
                self.res = res

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
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa, self.doc), scn.getPrimaryPredicativeGovernor(sent, can, pa, self.doc)

                EPupperfreq = 2000
                numncnaive = 0
                numncnaiveop = 0
                # print >>sys.stderr, "numncnaive"
                # print >>sys.stderr, ranker.rankingsRv["NCNAIVE0FREQ"]
                for tmp, numnc in ranker.rankingsRv["NCNAIVE0FREQ"]:
                    if tmp == can.attrib["id"]:
                        numncnaive += numnc
                    else:
                        numncnaiveop += numnc
                # print >>sys.stderr, can.attrib["id"]
                # print >>sys.stderr, numncnaive


		# kNN FEATURES.
		ranker.sort()
                flag_ScoreKnn = True
                # if pa.sknn:
                #     ScoreKnn = True
                # else:
                #     ScoreKnn = False
                if not pa.noprknn:
                        for K in xrange(10):
                                K = K+1
                                for fk, fnn in ranker.NN.iteritems():
                                        r = ranker.getKNNRank(can.attrib["id"], fk, K)
                                        # print ranker.numsvosvo

                                        #if 0 == r:
                                        yield "KNN%d_%s_%s" % (K, fk, r), 1
                                        yield "SKNN%d_%s_%s" % (K, fk, r), ranker.getKNNRankValue(can.attrib["id"], fk, K, flag_ScoreKnn)
                                        yield "KNNTURN%d_%s_%s" % (K, fk, r), ranker.getKNNRankValue4bit(can.attrib["id"], fk, candidates, K)
                                        yield "SKNNTURN%d_%s_%s" % (K, fk, r), ranker.getKNNRankValue4bit(can.attrib["id"], fk, candidates, K, flag_ScoreKnn)

                # for fk, fnn in ranker.NN.iteritems():
                #     # V = 5
                #     for V in xrange(1,6):
                #         # print >>sys.stderr, "testing...sumVscore"
                #         # print >>sys.stderr, fk
                #         if fk != "iriPredArgNConW_center0.7_Min+subj_ON": continue
                #         sumVscores, elementlst = ranker.getSumVScores(can.attrib["id"], fk, candidates, V, False)
                #         print >>sys.stderr, "sumVscores = %s" % (sumVscores)
                #         # for ele in elementlst:
                #         #     print >>sys.stderr, "%s" % (ele)
                #         # print >>sys.stderr, "%s" % ("\n".join(elementlst))
                #         # print >>sys.stderr, "sumVscores = %s, %s" % (sumVscores, elementlst)
                #         sumVscoresRevote, elementlstRevote = ranker.getSumVScores(can.attrib["id"], fk, candidates, V, True)
                #         print >>sys.stderr, "sumVscoresRevote = %s" % (sumVscoresRevote)
                #         # for ele in elementlstRevote:
                #         #     print >>sys.stderr, "%s" % (ele)

                #         # self.rankingsRv["SUM%d" % V] += ([gvCan, sumVscores])
                #         # self.rankingsRv["SUMTURN%d" % V] += ([gvCan, sumVscoresRevote])
                #         # self.rankingsRv["googleJC"] += [(vCan, ret)]
                #         # yield "%s_Rank_SUM%d_%s" %("x", V, fk), sumVscores
                #         # yield "%s_SUMTURN%d_%s" %("x", V, fk), sumVscoresRevote
                #         yield "%s_Rank_SUM%d" %("x", V), sumVscores
                #         yield "%s_Rank_SUMTURN%d" %("x", V), sumVscoresRevote

                    # print >>sys.stderr, "sumVscoresRevote = %s, %s" % (sumVscoresRevote, elementlstRevote)
		# RANKING FEATURES.
                # G1, G2, G3 = {}, {}, {}

                # for c in candidates:
                #     G1[c.attrib["id"]] = 0
                #     G2[c.attrib["id"]] = 0
                #     G3[c.attrib["id"]] = 0

                # def _target(x):
                #     if "googleCV" == x: return G1
                #     if "googleCVW" == x: return G2
                #     if "googleJC" == x: return G3

                # for fk, fr in ranker.numsvosvo.iteritems():
                #     print >>sys.stderr, "numsvosvo"
                #     print >>sys.stderr, fk, fr

                #     if "svopair" in fk:
                #         ranker.statistics[fk] += [(can.attrib["id"], fr)]
                #         yield "%s_Rank_%s" % ("x", fk), ranker.getSVOpairRankValue(can.attrib["id"], fk)
                #     if "svoploged" in fk:
                #         yield "%s_Rank_%s" % ("x", fk), ranker.getSVOpairRankValue(can.attrib["id"], fk)


		for fk, fr in ranker.rankingsRv.iteritems():
			if "position" == fk: continue

			r	=ranker.getRank(can.attrib["id"], fk)

			if "selpref" == fk:
				yield "%s_Rank_%sVN" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                                yield "%s_Rank_%sVO" % ("x", fk), ranker.getRankValueOrigin(can.attrib["id"], fk)

                        if "svocount" in fk:
                                yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                        if "svopair" in fk:
                            yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                                # if fk == "svopair_VV":
                                #     if numncnaive < EPupperfreq and numncnaiveop < EPupperfreq: # filter out EP feature of freq > EPupperfreq
                                #         yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                                # else:
                                #     yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                        if "svoploged" in fk:
                            yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                                # if fk == "svoploged_VV":
                                #     if numncnaive < EPupperfreq and numncnaiveop < EPupperfreq: # filter out EP feature of freq > EPupperfreq
                                #         yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                                # else:
                                #     yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)


                        if "NCNAIVE0NPMI" == fk:
                            yield "%s_Rank_%sVN" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                            yield "%s_Rank_%sVO" % ("x", fk), ranker.getRankValueOrigin(can.attrib["id"], fk)
                                # if numncnaive < EPupperfreq and numncnaiveop < EPupperfreq: # filter out EP feature of freq > EPupperfreq
                                #     yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                        # if "google" in fk:
                        #         yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)
                        if "gglloged" in fk:
                                yield "%s_Rank_%s" % ("x", fk), ranker.getRankValue(can.attrib["id"], fk)

                        # if "google" in fk:
                        #     # min(fr[1][1], fr[0][1]) > 0 and
                        #     if max(fr[1][1], fr[0][1]) > 0 and \
                        #        float(abs(fr[1][1] - fr[0][1])) / max(fr[1][1], fr[0][1]) > 0.2:

                        #         if ranker.getRank(can.attrib["id"], fk) ==
                        #         # _target(fk)[can.attrib["id"]] = 1

			if "R1" == r:
				if "google" in fk:
                                        # min(fr[1][1], fr[0][1]) > 0 and
					if max(fr[1][1], fr[0][1]) > 0 and \
								 float(abs(fr[1][1] - fr[0][1])) / max(fr[1][1], fr[0][1]) > 0.2:
                                #         # if max(fr[1][1], fr[0][1]) > 0 and \
                                #         #    float(min(fr[1][1], fr[0][1])) / max(fr[1][1], fr[0][1]) < 0.8:
                                #             # _target(fk)[can.attrib["id"]] = 1

                                            yield "%s_Rank_%s_%s" % ("x", fk, r), 1

				elif "NCCJ08" == fk:
					if 2 > fr[0][1] + fr[1][1]:
						yield "%s_Rank_%s_%s" % ("x", fk, r), 1

				elif "NCCJ08_VO" == fk:
					if abs(fr[0][1] - fr[1][1])>25:
						yield "%s_Rank_%s_%s" % ("x", fk, r), 1
				elif "NCNAIVE0NPMI" == fk:
                                        yield "%s_Rank_%s1_%s" % ("x", fk, r), 1
                                elif "selpref" == fk:
                                        yield "%s_Rank_%s1_%s" % ("x", fk, r), 1
				else:
					yield "%s_Rank_%s_%s" % ("x", fk, r), 1

                # c1n, c2n = can.attrib["id"], candidates[0] if candidates[1] == can.attrib["id"] else candidates[1]

                # if G1[c1n] == 1 or G1[c2n] == 1: yield "G4", G1[c1n]
                # elif G2[c1n] == 1 or G2[c2n] == 1: yield "G4", G2[c1n]
                # elif G3[c1n] == 1 or G3[c2n] == 1: yield "G4", G3[c1n]

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
		gvCan1, gvCan2 = scn.getPrimaryPredicativeGovernor(sent, candidates[0], pa, self.doc), scn.getPrimaryPredicativeGovernor(sent, candidates[1], pa, self.doc)
		gvAna, gvCan = scn.getPrimaryPredicativeGovernor(sent, ana, pa, self.doc), scn.getPrimaryPredicativeGovernor(sent, can, pa, self.doc)
		polAna, polCan1, polCan2 = 0, 0, 0
		position		 = "left" if "R1" == ranker.getRank(can.attrib["id"], "position") else "right"

                # print >>sys.stderr, "### gvCan1 = %s, gvCan2 = %s, gvAna = %s" % (gvCan1, gvCan2, gvAna)
		if None == gvAna or None == gvCan1 or None == gvCan2: return

                if not isinstance(gvAna.lemma, list): gvanalemmas = [gvAna.lemma]
                else: gvanalemmas = [x[1] for x in gvAna.lemma]
                if not isinstance(gvCan1.lemma, list): gvcan1lemmas = [gvCan1.lemma]
                else: gvcan1lemmas = [x[1] for x in gvCan1.lemma]
                if not isinstance(gvCan2.lemma, list): gvcan2lemmas = [gvCan2.lemma]
                else: gvcan2lemmas = [x[1] for x in gvCan2.lemma]


                for gvanalemma in gvanalemmas:

                    for (gvcan1lemma, gvcan2lemma) in itertools.product(gvcan1lemmas, gvcan2lemmas):
                        # if None != gvAna:
                        #     if gvAna.rel == "nsubj" or scn.getDeepSubject(sent, gvAna.token) == ana.attrib["id"]:
                        #         polAna = self.sentpol.getPolarity(gvanalemma)
                        #     if "obj" in gvAna.rel or gvAna.rel == "nsubj_pass":
                        #         polAna = None if self.sentpol.getPolarity(gvanalemma) == None else self.sentpol.getPolarity(gvanalemma) * -1
                        #     else:
                        #         polAna = None
                        #     # polAna = self.sentpol.getPolarity(gvanalemma) if gvAna.rel == "nsubj" or scn.getDeepSubject(sent, gvAna.token) == ana.attrib["id"] else None
                        #     # FLIPPING
                        #     if None != polAna and (scn.getNeg(sent, gvAna.token) or (None != conn and scn.getLemma(conn) in "but although though however".split())): polAna *= -1


                        # if None != gvCan1:
                        #     if gvCan1.rel == "nsubj" or scn.getDeepSubject(sent, gvCan1.token) == candidates[0].attrib["id"]:
                        #         polCan1 = self.sentpol.getPolarity(gvcan1lemma)
                        #     elif "obj" in gvCan1.rel or gvCan1.rel == "nsubj_pass":
                        #         polCan1 = None if self.sentpol.getPolarity(gvcan1lemma) == None else self.sentpol.getPolarity(gvcan1lemma) * -1
                        #     else:
                        #         polCan1 = None
                        #     # polCan1 = self.sentpol.getPolarity(gvcan1lemma) if gvCan1.rel == "nsubj" or scn.getDeepSubject(sent, gvCan1.token) == candidates[0].attrib["id"] else None
                        #     # FLIPPING
                        #     if None != polCan1 and scn.getNeg(sent, gvCan1.token): polCan1 *= -1

                        # if None != gvCan2:
                        #     if gvCan2.rel == "nsubj" or scn.getDeepSubject(sent, gvCan2.token) == candidates[0].attrib["id"]:
                        #         polCan2 = self.sentpol.getPolarity(gvcan2lemma)
                        #     elif "obj" in gvCan2.rel or gvCan2.rel == "nsubj_pass":
                        #         polCan2 = None if self.sentpol.getPolarity(gvcan2lemma) == None else self.sentpol.getPolarity(gvcan2lemma) * -1
                        #     else:
                        #         polCan2 = None
                        #     # polCan2 = self.sentpol.getPolarity(gvcan2lemma) if gvCan2.rel == "nsubj" or scn.getDeepSubject(sent, gvCan2.token) == candidates[1].attrib["id"] else None
                        #     # FLIPPING
                        #     if None != polCan2 and scn.getNeg(sent, gvCan2.token): polCan2 *= -1


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

                            # HPOL ACCORDING TO RAHMAN
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

                            # # HPOL ACCORDING TO PENG
                            # if None != polAna and None != polCan1 and 0 != polAna*polCan1:
                            #     if can == candidates[0] and polCan1 == polAna: yield "%s_HPOL_MATCH" % position, 1
                            #     if can == candidates[0] and polCan1 == polAna == 1: yield "%s_HPOL_POSMATCH" % position, 1
                            #     if can == candidates[0] and polCan1 == polAna == -1: yield "%s_HPOL_NEGMATCH" % position, 1

                            # if None != polAna and None != polCan2 and 0 != polAna*polCan2:
                            #     if can == candidates[1] and polCan2 == polAna: yield "%s_HPOL_MATCH" % position, 1
                            #     if can == candidates[1] and polCan2 == polAna == 1: yield "%s_HPOL_POSMATCH" % position, 1
                            #     if can == candidates[1] and polCan2 == polAna == -1: yield "%s_HPOL_NEGMATCH" % position, 1


	def iriEnumerate(self, outExamples, NNvoted, p1, r1, ps1, c1, a1, p2, r2, ps2, c2, a2):
		if None == self.libiri: return 0

		for vector in self.libiri.predict(
				"%s-%s" % (p1, ps1[0].lower()), c1, r1, a1, "%s-%s" % (p2, ps2[0].lower()), c2, r2, a2,
				threshold = 1, pos1=ps1, pos2=ps2, limit=1000, fVectorMode=True):

			outExamples += [(NNvoted, vector)]

        def flagsimTemp(self, pflags, iflags):
            # F14: temporal relation b/w e1 and e2. T:U or T:12 or T:21.
            isskip = False
            if pflags[13] == "T:U" or iflags[13] == "T:U":
                return 0.75, isskip
            elif pflags[13] == iflags[13]:
                return 1.0, isskip
            else:
                return 0.5, isskip

        def flagsimPol(self, pflags, iflags):
            # F1,2: polarity. A (affirmative) or N (negative).
            isskip = False
            if pflags[0:2] == iflags[0:2]:
                return 1.0, isskip
            else:
                return 0.75, isskip

        def flagsimBit(self, pflags, iflags):
            # F1,2: polarity. A (affirmative) or N (negative).
            # F5,6: expectation field. E (expects) or C (contra-expects).
            isskip = False
            isrevote = False
            TFlst = [pflags[0]==iflags[0], pflags[1]==iflags[1], pflags[4]==iflags[4], pflags[5]==iflags[5]]
            if TFlst == [True, True, True, True]:
                return 1.0, isskip, isrevote
            elif TFlst == [True, True, False, True] or TFlst == [True, True, True, False]:                
                isrevote = True
                return 0.75, isskip, isrevote
            elif TFlst.count(False) == 2: # "strong and win" & "strong but not win" & "not strong and not win"
                return 0.75, isskip, isrevote
            else:
                return 0.5, isskip, isrevote

        def flagsimGrammatical(self, pflags, iflags):
            # F13: grammatical relation b/w e1 and e2. U, A12, A21, C12, C21, X12, X21.
            isskip = False
            if pflags[12] == "G:U" or iflags[12] == "G:U":
                return 0.75, isskip
            elif pflags[12] == iflags[12]:
                return 1.0, isskip
            else:
                return 0.5, isskip
            
	def iri(self, outNN, NNvoted, lmvcan, p1, tp1, r1, ps1, c1, ta1, a1, ph1, cat1, p2, tp2, r2, ps2, c2, ta2, a2, ph2, cat2, pathline, pa, ff, svoplst, statistics, cached = None, outExamples = None, trade = False):
                if None == self.libiri: return 0

                # How to use annotator_t.
                pflags = self.ann.annotate(
                sdreader.createTokenFromLXML(tp1),
                sdreader.createTokenFromLXML(ta1),
                sdreader.rel_t(r1, -1, -1),
                sdreader.createTokenFromLXML(tp2),
                sdreader.createTokenFromLXML(ta2),
                sdreader.rel_t(r2, -1, -1),
                self.doc,
                self.res
                ).split(",")
                print >>sys.stderr, pflags
                
                # if pa.noknn == True: return 0
                phnopara = False

                if pa.ph and ph1:
                    if ph1[0] == 0:
                        c1 = _rmphrasalctx(c1, ph1)
                    elif ph1[0] == 2:
                        if phnopara == True: return 0
                        c1 = _rmphrasalctx(c1, ph1)
                        r1 = _setphrel(r1, ph1)

                print >>sys.stderr, "AAA"
                print >>sys.stderr, p1, c1, a1, r1
                print >>sys.stderr, p2, c2, a2, r2
                print >>sys.stderr, lmvcan

                print >>sys.stderr, "KEYs2 ="
                print >>sys.stderr, "%s-%s:%s" % (p1, ps1[0].lower(), r1)
                print >>sys.stderr, "%s-%s:%s" % (p2, ps2[0].lower(), r2)

                e1 = sdreader.createTokenFromLXML(tp1)
                e2 = sdreader.createTokenFromLXML(tp2)
                e1i, e2i = ff.doc.getEventIndex(e1, ff.res.lv), ff.doc.getEventIndex(e2, ff.res.lv)

                print >>sys.stderr, "KEYs2PH ="
                print >>sys.stderr, "%s-%s:%s" % (e1i, ps1[0].lower(), ff.doc.getRelationIndex(r1, e1))
                print >>sys.stderr, "%s-%s:%s" % (e2i, ps2[0].lower(), ff.doc.getRelationIndex(r2, e2))

                if pa.noknn == True: return 0

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

                if "agent" == r1:
                    print >>sys.stderr, "replace agent2nsubj r1"
                    r1 = "nsubj"
                if "agent" == r2:
                    print >>sys.stderr, "replace agent2nsubj r2"
                    r2 = "nsubj"

                # if pa.bitsim == True:
                pbit = [0,0,0]
                paths = pathline.split("|")
                negcontext = set("d:neg:not-r d:neg:never-r d:advmod:seldom-r d:advmod:rarely-r d:advmod:hardly-r d:advmod:scarcely-r d:advmod:less-r d:amod:less-j".split())
                # "d:advmod:less-r d:amod:less-j"
                negcontext2 = set("d:advmod:however-r d:advmod:nevertheless-r d:advmod:nonetheless-r d:mark:unless-i d:mark:although-i d:mark:though-i".split())
                negcatenative = set("g:xcomp:forbid-v g:xcomp:miss-v g:xcomp:quit-v g:xcomp:dislike-v g:xcomp:stop-v g:xcomp:deny-v g:xcomp:forget-v g:xcomp:resist-v g:xcomp:escape-v g:xcomp:fail-v g:xcomp:hesitate-v g:xcomp:avoid-v g:xcomp:detest-v g:xcomp:refuse-v g:xcomp:neglect-v g:xcomp:unable-j".split())
                negconjcol1 = tuple(["conj_but"])

                match = []
                if cat1[1] == True:
                        pbit[0] += 1
                if cat2[1] == True:
                        pbit[1] += 1
                if cat1[2] == True or cat2[2] == True:
                        pbit[2] += 1
                for c1e in c1.split(" "):
                        if c1e in negcontext|negcatenative:
                                pbit[0] += 1
                                match += [c1e]
                        if c1e in negcontext2:
                                pbit[2] += 1
                                match += [c1e]
                for c2e in c2.split(" "):
                        if c2e in negcontext|negcatenative:
                                pbit[1] += 1
                                match += [c2e]
                        if c2e in negcontext2:
                                pbit[2] += 1
                                match += [c2e]
                pbit[2] += get_conjbit(pathline, negconjcol1)
                # print >>sys.stderr, match, pbit, pathline
                if pa.onlybit:
                        sys.stderr.write("problembit=\t%s\t" % pbit)
                        return
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

                instancecache = []
                svosvocount = collections.defaultdict(int)

                for ret, raw, vec in self.libiri.predict("%s-%s" % (e1i, ps1[0].lower()), c1, ff.doc.getRelationIndex(r1, e1), a1, simretry, "%s-%s" % (e2i, ps2[0].lower()), c2, ff.doc.getRelationIndex(r2, e2), a2, threshold = 1, pos1=ps1, pos2=ps2, limit=100000):

                        # print >>sys.stderr, "raw = "
                        # print >>sys.stderr, raw
                        
                        if pa.nodupli == True: # COTINUE DUPLICATE INSTANCES
                            if str(raw[:7]) in set(instancecache): # SAME without IDs
                                # print >>sys.stderr, "is Duplication"
                                continue
                            # print >>sys.stderr, "ret = %s" % repr(ret)
                            # print >>sys.stderr, "raw[:-2] = %s" % str(raw[:-2])

                        # F1,2: polarity. A (affirmative) or N (negative).
                        # F3,4: transitive verb or not. T-* (transitive) or I (intransitive).
                        # F5,6: expectation field. E (expects) or C (contra-expects).
                        # F7, 8: role sources. A (propadvcl), C (propcoord), P (propxcomp), or - (pure).
                        # F9, 10: auxiliary-like verb. A (yes) or - (no).
                        # F11, 12: gomi verb. Y (yes) or N (no).
                        # F13: grammatical relation b/w e1 and e2. U, A12, A21, C12, C21, X12, X21.
                        #      (basically, clausal complement or adverbial modifier or xcomp)
                        # F14: temporal relation b/w e1 and e2. U or 12 or 21.
                        # F15: heuristic coref rule is satisfied or not. Y or N.
                            
                        iflags = raw[9].split(",")
                        # print >>sys.stderr, iflags

                        # SKIP gomi verb
                        if iflags[10] == "Y" or iflags[11] == "Y":
                            continue

                        # Calculate temporal similarity and skip flag
                        temporalsim, temporalskip = ff.flagsimTemp(pflags, iflags)
                        # print >>sys.stderr, temporalsim, temporalskip

                        # Calculate polarity similarity and skip flag
                        polaritysim, polarityskip = ff.flagsimPol(pflags, iflags)
                        # print >>sys.stderr, polaritysim, polarityskip
                        
                        # Calculate bit similarity and skip flag and revoteflag
                        bitsim, bitskip, bitrevote = ff.flagsimBit(pflags, iflags)
                        # print >>sys.stderr, bitsim, bitskip, bitrevote

                        # Calculate temporal similarity and skip flag
                        grammaticalsim, grammaticalskip = ff.flagsimGrammatical(pflags, iflags)
                        # print >>sys.stderr, temporalsim, temporalskip

                        psr1 = "%s-%s:%s" %(p1, ps1[0].lower(), r1)
                        psr2 = "%s-%s:%s" %(p2, ps2[0].lower(), r2)

                        icl, icr, ipath = raw[4], raw[5], raw[6]
                        imention = "-".join(raw[2].split("-")[:2])
                        irl = raw[0].split(":")[-1]
                        irr = raw[1].split(":")[-1]
                        ipl = raw[0].split("-")[0]
                        ipr = raw[1].split("-")[0]
                        ipsl = raw[0].split(":")[0].split("-")[1]
                        ipsr = raw[1].split(":")[0].split("-")[1]
                        pnegconjbit = pbit[2]

                        addicl = "d:%s:%s %s" %(irl, imention, icl)
                        addicr = "d:%s:%s %s" %(irr, imention, icr)

                        isvol = None
                        isvor = None
                        s1l, o1l = _getsofromctx(addicl)
                        s2r, o2r = _getsofromctx(addicr)

                        isvol = [s1l, ipl, o1l]
                        isvor = [s2r, ipr, o2r]

                        isvpol, isvpor, isvosvotype = getsvpo(ipl, addicl, imention, irl, ipsl,  ipr, addicr, imention, irr, ipsr)
                        # print >>sys.stderr, "isvpol, isvpor = %s, %s" % (repr(isvpol), repr(isvpor))
                        # print >>sys.stderr, "psvoplist = %s\n" % (repr(svoplst))

                        # # phrase check
                        # pphs = set([svoplst[0][1], svoplst[1][1]])
                        # iphs = set([isvpol[1], isvpor[1]])
                        # # print >>sys.stderr, "pph, iph = %s, %s\n" % (repr(pphs), repr(iphs))
                        # if pa.phpeng == True and pphs != iphs:
                        #         continue

                        if psr1 == raw[0] or psr2 == raw[1]:
                            ic1, ic2, isvpo1, isvpo2 = icl, icr, isvpol, isvpor
                        else:
                            ic1, ic2, isvpo1, isvpo2 = icr, icl, isvpor, isvpol

                        inegconjbit = 0
                        for ic1e in ic1.split(" "):
                            if ic1e in negcontext2:
                                inegconjbit = 1
                        for ic2e in ic2.split(" "):
                            if ic2e in negcontext2:
                                inegconjbit = 1
                        inegconjbit +=get_conjbit(ipath, negconjcol1)

                        # # peng check
                        # pengcount = 0
                        # if svoplst[0][0] == isvpo1[0]:
                        #     pengcount += 1
                        # if svoplst[0][2] == isvpo1[2]:
                        #     pengcount += 1
                        # if svoplst[1][0] == isvpo2[0]:
                        #     pengcount += 1
                        # if svoplst[1][2] == isvpo2[2]:
                        #     pengcount += 1

                        # pengconjpenalty = 0.8 if svoplst[2] != inegconjbit else 1.0

                        # if pengcount >= 3:
                        #         penalty_peng = 1.0*pengconjpenalty
                        # elif pengcount <= 2:
                        #         penalty_peng = 1.0*(0.8**(3-pengcount))*pengconjpenalty

                        # pargs = set([svoplst[0][0], svoplst[0][2], svoplst[1][0], svoplst[1][2]])
                        # iargs = set([isvpol[0], isvpol[2], isvpor[0], isvpor[2]])


                        # svoS, svoO = getsowdet(sent, gvAna.token)
                        # svoV = gvAna.lemma
                        # svoVPlms, svoVPsurfs, vptype, vprel =
                        # get_VPpengfromctx(gvAna.token, gvAna.rel)

                        # print >>sys.stderr, svoVPlms

                        # svoVP = "_".join(svoVPlms)
                        # print >>sys.stderr, "anaVP=%s" %(svoVP)

                        # svoVPrel = "%s:%s" %(svoVP, vprel)

                        # # # svoS, svoO = svoS.split("-")[0], svoO.split("-")[0]
                        # if "obj" in gvAna.rel or "prep_" in gvAna.rel or "nsubj_pass" in gvAna.rel:
                        #     # svoO = " ".join(lmqW)
                        #     svoO = wCan
                        # elif "subj" in gvAna.rel:
                        #     # svoS = " ".join(lmqC)
                        #     svoS = wCan



                        # # SVO-SVO-CONJ MATCH
                        # if psr1 == raw[0] or psr2 == raw[1]:
                        #     # matching [svocan svoana pnegconjbit] and [isvol isvor inegconjbit]
                        #     svosvocount = check_svosvomatch([svocan, svoana, pnegconjbit], [isvol, isvor, inegconjbit], svosvocount)
                        # else:
                        #     # matching [svoana svocan pnegconjbit] and [isvol isvor inegconjbit]
                        #     svosvocount = check_svosvomatch([svoana, svocan, pnegconjbit], [isvol, isvor, inegconjbit], svosvocount)

                        # if svosvotype == "svmsvm":
                        #     insvl = raw[0].split("-")[0]
                        #     insvr = raw[1].split("-")[0]
                        #     print >>sys.stderr, svosvotype
                        # elif svosvotype == "svmmvo":
                        #     print >>sys.stderr, svosvotype
                        # elif svosvotype == "mvosvm":
                        #     print >>sys.stderr, svosvotype
                        # elif svosvotype == "mvomvo":
                        #     print >>sys.stderr, svosvotype

                        # print >>sys.stderr, raw

                        ibit = [None]
                        penalty_ph = 1.0
                        penalty_bit = 1.0

                        penaltyscore = 1.0
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

                            # psr1 = "%s-%s:%s" %(p1, ps1[0].lower(), r1)
                            # psr2 = "%s-%s:%s" %(p2, ps2[0].lower(), r2)

                            if psr1 == raw[0] or psr2 == raw[1]:
                                ic1 = icl
                                ic2 = icr
                            else:
                                ic1 = icr
                                ic2 = icl

                            for ic1e in ic1.split(" "):
                                if ic1e in negcontext|negcatenative:
                                    ibit[0] += 1
                                    match += [ic1e]
                                if ic1e in negcontext2:
                                    ibit[2] += 1
                                    match += [ic1e]
                            for ic2e in ic2.split(" "):
                                if ic2e in negcontext|negcatenative:
                                    ibit[1] += 1
                                    match += [ic2e]
                                if ic2e in negcontext2:
                                    ibit[2] += 1
                                    match += [ic2e]
                            ibit[2] += get_conjbit(ipath, negconjcol1)
                            ibit = tuple(ibit)

                            penalty_bit, bittype = calc_bitsim(pbit, ibit)
                            # if bittype == 0 or bittype == -1:

                            if bittype == 0:
                                flag_continue_bit = 1
                            # else:
                            #     print >>sys.stderr, pbit, ibit, bittype
                        else:
                            bittype = None

                        if bitrevote == True:
                            bittype = -1
                        else:
                            bittype = 1
                            
                        # print >>sys.stderr, pbit, ibit, bittype

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

                        if pa.simpred1 == True: # SET PRED SIMILARITY = 1
                            sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sRuleAssoc # * penaltyscore
                        else:
                            sp = ret.sIndexSlot[ret.iIndexed]*ret.sPredictedSlot*ret.sIndexPred[ret.iIndexed]*ret.sPredictedPred*ret.sRuleAssoc # * penaltyscore
                        sp_original = sp

                        # centers = [0.6, 0.7, 0.8]
                        # threshs = [200000, 500000, 800000]
                        centers = [0.6, 0.7]
                        threshs = [500000]

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

                        # for center in centers:
                        #     newCsim1c = calcnewConsim(ret.sIndexContext[ret.iIndexed], freq_pi, center)
                        #     newCsim2c = calcnewConsim(ret.sPredictedContext, freq_pp, center)
                        #     newCsimc[center] = [newCsim1c, newCsim2c]
                        # for thresh in threshs:
                        #     newCsim1t = calcnewConsimthre(ret.sIndexContext[ret.iIndexed], freq_pi, thresh)
                        #     newCsim2t = calcnewConsimthre(ret.sPredictedContext, freq_pp, thresh)
                        #     newCsimt[thresh] = [newCsim1t, newCsim2t]

                        # print >>sys.stderr, ret.sIndexContext[ret.iIndexed], newCsim1,freq_p1 , ret.sPredictedContext, newCsim2, freq_p2, newCsim

                        # if pa.pathsim1 == True:
                        #     sp = sp * pathsimilarity
                        # bitcached += [bittype]

                        spa = sp * ret.sPredictedArg
                        spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                        spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                        spa_original = spa
                        spc_original = spc
                        spac_original = spac

                        sfinal = {}
                        sfinal = {"sp": sp,"spa": spa,"spc": spc, "spac": spac, "scIndexed": ret.sIndexContext[ret.iIndexed], "scPredicted": ret.sPredictedContext, "bittype": bittype}
                        # sfinal = s_final(sp, spa, spc, spac)
                        nret = ret._replace(s_final = sfinal)

                        # print >>sys.stderr, "bit == %s == %s" % (penalty_bit, flag_continue_bit)
                        # print >>sys.stderr, "ph == %s == %s" % (penalty_ph, flag_continue_ph)

                        for settingname in "OFF BitON TempON GramON ON".split():
                        # for settingname in "OFF bitON pengON ON".split():
                            sp = sp_original
                            spa = spa_original
                            spc = spc_original
                            spac = spac_original
                            penaltyscore = 1.0

                            if pa.bitsim == True and settingname == "bitON":
                                sp = sp_original * penalty_bit
                                spa = sp * ret.sPredictedArg
                                spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                penaltyscore = penalty_bit
                                if flag_continue_bit == 1:
                                    continue
                            if pa.ph == True and settingname == "phON":
                                sp = sp_original * penalty_ph
                                spa = sp * ret.sPredictedArg
                                spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                penaltyscore = penalty_ph
                                if flag_continue_ph == 1:
                                    continue
                                    
                            if settingname == "TempON":
                                sp = sp_original * temporalsim
                                spa = sp * ret.sPredictedArg
                                spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                penaltyscore = temporalsim
                                if temporalskip == True:
                                    continue
                            if settingname == "BitON":
                                sp = sp_original * bitsim
                                spa = sp * ret.sPredictedArg
                                spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                penaltyscore = bitsim
                                if bitskip == True:
                                    continue
                            if settingname == "GramON":
                                sp = sp_original * grammaticalsim
                                spa = sp * ret.sPredictedArg
                                spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                penaltyscore = grammaticalsim
                                if grammaticalskip == True:
                                    continue
                            if settingname == "ON":
                                sp = sp_original * temporalsim * bitsim * grammaticalsim
                                spa = sp * ret.sPredictedArg
                                spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                                penaltyscore = temporalsim * bitsim * grammaticalsim
                                if temporalskip == True or bitskip == True or grammaticalskip == True:
                                    continue
                                
                            # if pa.peng == True and settingname == "pengON":
                            #     sp = sp_original * penalty_peng
                            #     spa = sp * ret.sPredictedArg
                            #     spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            #     spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            #     penaltyscore = penalty_peng

                            # if pa.bitsim == True and pa.peng == True and settingname == "ON":
                            #     sp = sp_original * penalty_bit * penalty_peng
                            #     spa = sp * ret.sPredictedArg
                            #     spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            #     spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            #     penaltyscore = penalty_bit * penalty_peng
                            #     if flag_continue_bit == 1:
                            #         continue

                            # if pa.bitsim == True and pa.ph == True and settingname == "ON":
                            #     sp = sp_original * penalty_bit * penalty_ph
                            #     spa = sp * ret.sPredictedArg
                            #     spc = sp * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            #     spac = spa * ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext
                            #     penaltyscore = penalty_bit * penalty_ph
                            #     if flag_continue_bit == 1 or flag_continue_ph == 1:
                            #         continue

                            # if None != cached: cached += [(NNvoted, nret)]
                            # if None != cached: cached += [(NNvoted, ret)]

                            if None == cached:
                                if pa.bitsim == True and settingname == bitON:
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
                            outNN["iriArg%s" %(settingname)] += [(NNvoted, ret.sPredictedArg*penaltyscore, bittype)]
                            outNN["iriCon%s" %(settingname)] += [(NNvoted, ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext*penaltyscore, bittype)]
                            outNN["iriArgCon%s" %(settingname)] += [(NNvoted, ret.sPredictedArg*ret.sIndexContext[ret.iIndexed]*ret.sPredictedContext*penaltyscore, bittype)]

                            if settingname != "OFF":
                                sfinal["iriPred%s" % (settingname)] =  sp
                                sfinal["iriPredArg%s" % (settingname)] =  spa
                                sfinal["iriPredCon%s" % (settingname)] =  spc
                                sfinal["iriPredArgCon%s" % (settingname)] =  spac
                                sfinal["iriPredArgCon%s.bit" % (settingname)] = ibit
                                nret = ret._replace(s_final = sfinal)

                            # for settingnameNCon, newCsim in newCsimc.items():
                            #     outNN["iriPredNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, sp * newCsim[0]*newCsim[1], bittype)]
                            #     outNN["iriPredArgNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, spa * newCsim[0]*newCsim[1], bittype)]
                            #     outNN["iriNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, newCsim[0]*newCsim[1]*penaltyscore, bittype)]
                            #     outNN["iriArgNCon_center%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, ret.sPredictedArg*newCsim[0]*newCsim[1]*penaltyscore, bittype)]

                                # if settingnameNCon == 0.7 and settingname == "OFF":
                                #     sfinal["iriPredArgNCon_center%s_%s" % (settingnameNCon, settingname)] =  spa * newCsim[0]*newCsim[1]
                                #     sfinal["iriPredArgNCon_center%s_%s.scIndexed" % (settingnameNCon, settingname)] = newCsim[0]
                                #     sfinal["iriPredArgNCon_center%s_%s.scPredicted" % (settingnameNCon, settingname)] = newCsim[1]
                                #     sfinal["iriPredArgNCon_center%s_%s.bit" % (settingnameNCon, settingname)] = ibit
                                #     nret = ret._replace(s_final = sfinal)


                            # for settingnameNCon, newCsim in newCsimt.items():
                            #     outNN["iriPredNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, sp * newCsim[0]*newCsim[1], bittype)]
                            #     outNN["iriPredArgNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, spa * newCsim[0]*newCsim[1], bittype)]
                            #     outNN["iriNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, newCsim[0]*newCsim[1]*penaltyscore, bittype)]
                            #     outNN["iriArgNCon_thresh%s_%s" %(settingnameNCon, settingname)] += [(NNvoted, ret.sPredictedArg*newCsim[0]*newCsim[1]*penaltyscore, bittype)]

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
                                            # print >>sys.stderr, scw, scZw
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
                            # deptypedic["Min"] = ["obj", "prep_"]
                            deptypedic["Min+subj"] = ["nsubj", "obj", "prep_"]
                            # deptypedic["Min+xcomp"] = ["xcomp", "obj", "prep_"]
                            # deptypedic["Min+xcomp+nsubj"] = ["nsubj", "xcomp", "obj", "prep_"]

                        # for allsettingname, v in outNN.items():
                        #     # scoreofsetting = v[0][1]
                        #     sfinal[allsettingname] = v[0][1]
                        # nret = ret._replace(s_final = sfinal)

                        if None != cached: cached += [(NNvoted, nret)]
                        if pa.nodupli == True:
                            instancecache += [str(raw[:7])]

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

                # print >>sys.stderr, "svosvocount"
                # print >>sys.stderr, svosvocount

                # for svosvoname, svosvovalue in svosvocount.iteritems():
                #     numsvosvo["svopair_%s" % (svosvoname)] += [(NNvoted, svosvovalue)]
                #     numsvosvo["svoploged_%s" % (svosvoname)] += [(NNvoted, math.log(1+svosvovalue))]


		return 0
