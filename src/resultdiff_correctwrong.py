#-*- coding: utf-8 -*-

"""
python resultdiff_correctworng.py INPUT1 INPUT2
INPUT e.g. /work/jun-s/tmp/correctwrong/iriPred.0106.best+simwn+ph.tsv
"""

import sys
from mcnemartest import mcnemar_t

lfile = open(sys.argv[1])
rfile = open(sys.argv[2])

ldic = {}
rdic = {}

for lline in lfile.readlines():
    ldic[int(lline.split("\t")[0])] = lline.split("\t")[1].strip()

for rline in rfile.readlines():
    rdic[int(rline.split("\t")[0])] = rline.split("\t")[1].strip()

# print ldic
# print rdic
ret = []
numchangeC = 0
numchangeW = 0
numnochangeC = 0
numnochangeW = 0
numnochangeN = 0
numchangeNC = 0
numchangeNW = 0
numchangeCN = 0
numchangeWN = 0


for (lid, lresult) in sorted(ldic.items()):
    rresult = rdic[lid]
    # if rresult == "NoDec":
    #     rresult = lresult
    # if rresult == "NoDec":
    #     rresult = "WRONG"
    # if lresult == "NoDec":
    #     lresult = "WRONG"
    if lresult == "CORRECT" and rresult == "WRONG":
        change = "xxx"
        numchangeW += 1
    elif lresult == "WRONG" and rresult == "CORRECT":
        change = "+++"
        numchangeC += 1
    elif lresult == "WRONG" and rresult == "WRONG":
        change = ""
        numnochangeW += 1
    elif lresult == "CORRECT" and rresult == "CORRECT":
        change = ""
        numnochangeC += 1
    elif lresult == "NO DEC" and rresult == "WRONG":
        change = "x"
        numchangeNW += 1
    elif lresult == "NO DEC" and rresult == "CORRECT":
        change = "+"
        numchangeNC += 1
    elif lresult == "WRONG" and rresult == "NO DEC":
        change = "+?"
        numchangeWN += 1
    elif lresult == "CORRECT" and rresult == "NO DEC":
        change = "x?"
        numchangeCN += 1        
    elif lresult == "NO DEC" and rresult == "NO DEC":
        change = ""
        numnochangeN += 1
    else:
        change = ""
    
    ret = [str(lid), lresult, rresult, change]
    # print ret
    print "\t".join(ret)
    ret = []
    preC = numnochangeC + numchangeW + numchangeCN
    preW = numchangeC + numnochangeW + numchangeWN
    preN = numchangeNC + numchangeNW + numnochangeN
    newC = numnochangeC + numchangeC + numchangeNC
    newW = numchangeW + numnochangeW + numchangeNW
    newN = numchangeCN + numchangeWN + numnochangeN

print
print "\t\tnewC\tnewW\tnewN\n\t\t%s\t%s\t%s\n\t\t---\t---" %(newC, newW, newN)
print "oldC  %s |\t%s\t%s\t%s" %(preC, numnochangeC, numchangeW, numchangeCN)
print "oldW  %s |\t%s\t%s\t%s" %(preW, numchangeC, numnochangeW, numchangeWN)
print "oldN  %s |\t%s\t%s\t%s" %(preN, numchangeNC, numchangeNW, numnochangeN)
print "New Prec %s" %(1.0*newC/(newC+newW))
print "Old Prec %s" %(1.0*preC/(preC+preW))

print "McnemarTest = %s" % (mcnemar_t(numnochangeC, numchangeW, numchangeC, numnochangeW))
print "numnochangeC = %s" % (numnochangeC)
print "numchangeW = %s" % (numchangeW)
print "numchangeC = %s" % (numchangeC)
print "numnochangeW = %s" % (numnochangeW)
