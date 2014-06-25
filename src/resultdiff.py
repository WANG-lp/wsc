#-*- coding: utf-8 -*-

import sys
import popen2
from collections import defaultdict

options = sys.argv[1:]
in1 = options[0]
in2 = options[3]

target1 = options[1]
target2 = options[4]

k1 = options[2]
k2 = options[5]

def mappingtarget(target):
    mappingdict = {
			"p": "kNN_score_iriPred",
			"pa": "kNN_score_iriPredArg",
			"pac": "kNN_score_iriPredArgCon",
			"pc": "kNN_score_iriPredCon",
			"p+c": "kNN_score_iriAddPredCon",
			"p+a+c": "kNN_score_iriAddPredArgCon",
			"pol": "POL",        
			"n": "iriPredNumRules"
		}
    return mappingdict[target]

def _getClass(xk, yk, x, y, fInvertPolarity = False):
    if "None" == xk: xk = "0"
    if "None" == yk: yk = "0"
    if "None" == x: x = "0"
    if "None" == y: y = "0"
    
    x, y = float(x), float(y)
    xk, yk = float(xk), float(yk)
    
    if fInvertPolarity: x, y = -x, -y
    
    return xk != 0, yk != 0, x > y

def _getClassPol(c1, w1, c2, w2):
    lc1, rc1 = c1.split(",")
    lw1, rw1 = w1.split(",")
    lc2, rc2 = c2.split(",")
    lw2, rw2 = w2.split(",")

    lcrc1 = _isSamePol(lc1, rc1)
    lwrw1 = _isSamePol(lw1, rw1)
    lcrc2 = _isSamePol(lc2, rc2)
    lwrw2 = _isSamePol(lw2, rw2)

    return lcrc1, lwrw1, lcrc2, lwrw2
    
def _isSamePol(l, r):
    if (l, r) in [('1','1'), ('-1','-1'), ('0','0')]:
        return True
    elif (l, r) in [('1','-1'), ('-1','1'), ('1','0'), ('0','1'), ('-1','0'), ('0','-1')]:
        return False
    else:
        return None    


def _getResultDict(cmd1, cmd2):
    stdout1, stdin1, stderr1 = popen2.popen3(cmd1)
    ret1 = {}
    for l in stdout1:
        ret1[l.split("\t")[0]] = l.strip()

    stdout2, stdin2, stderr2 = popen2.popen3(cmd2)
    ret2 = {}
    for l in stdout2:
        ret2[l.split("\t")[0]] = l.strip()    
    return ret1, ret2

    
t1 = mappingtarget(target1)
t2 = mappingtarget(target2)
    
print in1, t1, k1, in2, t2, k2   

if t1 == 'POL' and t2 == 'POL':
    print "POL!!!"
    cmd1 = ("/home/naoya-i/bin/xpath %s problem @id \
    \"statistics[@type='%s']/@correct:0\" \"statistics[@type='%s']/@wrong:0\" " %(in1, t1, t1))
    cmd2 = ("/home/naoya-i/bin/xpath %s problem @id \
    \"statistics[@type='%s']/@correct:0\" \"statistics[@type='%s']/@wrong:0\" " %(in2, t2, t2))

    tmp1, tmp2 = _getResultDict(cmd1, cmd2)
    countcNone1 = 0
    countcNone2 = 0
    countwNone1 = 0
    countwNone2 = 0

    changedictc = defaultdict(int)
    changedictw = defaultdict(int)
    
    print len(tmp1), len(tmp2)
    # print tmp1, tmp2
    for problemno in sorted(set(tmp1.keys()) & set(tmp2.keys()), key=lambda x: int(x)):
        ln1 = tmp1[problemno].strip().split("\t")
        ln2 = tmp2[problemno].strip().split("\t")
        print ln1, ln2
        lcrc1, lwrw1, lcrc2, lwrw2 = _getClassPol(ln1[1], ln1[2], ln2[1], ln2[2])

        changedictc["%s -> %s" % (lcrc1, lcrc2)] += 1
        changedictw["%s -> %s" % (lwrw1, lwrw2)] += 1

        
        # polarity辞書カバレッジ
        # countNone1 += [lcrc1, lwrw1].count(None)
        # countNone2 += [lcrc2, lwrw2].count(None)
        if lcrc1 == None: countcNone1 += 1 
        if lcrc2 == None: countcNone2 += 1
        if lwrw1 == None: countwNone1 += 1 
        if lwrw2 == None: countwNone2 += 1 
    # print 2*len(tmp1) - countNone1, 2*len(tmp2) - countNone2
    sys.stdout.write("#correctNone = %d -> %d\t#wrongNone = %d -> %d\n" % (countcNone1, countcNone2, countwNone1, countwNone2))

    print "change of Correct"
    for k,v in changedictc.iteritems():
        print k,v
    print

    print "change of Wrong"
    for k,v in changedictw.iteritems():
        print k,v
    print
        # tf2 = _getClassPol(ln2[1], ln2[2])
    
else:
    cmd1 = ("/home/naoya-i/bin/xpath %s problem @id \
\"statistics[@type='iriNumRules']/@correct:0\" \"statistics[@type='iriNumRules']/@wrong:0\" \
\"feature[@type='%s,K=%s']/@correct:None\" \"feature[@type='%s,K=%s']/@wrong:None\" " %(in1, t1, k1, t1, k1))
    cmd2 = ("/home/naoya-i/bin/xpath %s problem @id \
\"statistics[@type='iriNumRules']/@correct:0\" \"statistics[@type='iriNumRules']/@wrong:0\" \
\"feature[@type='%s,K=%s']/@correct:None\" \"feature[@type='%s,K=%s']/@wrong:None\" " %(in2, t2, k2, t2, k2))

    tmp1, tmp2 = _getResultDict(cmd1, cmd2)
    print len(tmp1), len(tmp2)

    for problemno in sorted(set(tmp1.keys()) & set(tmp2.keys()), key=lambda x: int(x)):
        # print ln1, ln2
        ln1 = tmp1[problemno].strip().split("\t")
        ln2 = tmp2[problemno].strip().split("\t")
        lRules1, rRules1, tf1 = _getClass(ln1[1], ln1[2], ln1[3], ln1[4])
        lRules2, rRules2, tf2 = _getClass(ln2[1], ln2[2], ln2[3], ln2[4])

        if (lRules1, rRules1) != (True, True) or (lRules2, rRules2) != (True, True):
            continue

        sdiff1, sdiff2 = float(ln1[3])-float(ln1[4]), float(ln2[3])-float(ln2[4])

        ln1 = [(x if "." not in x else "%.4f" % float(x)).rjust(6) for x in ln1]
        ln2 = [(x if "." not in x else "%.4f" % float(x)).rjust(6) for x in ln2]
    
        if (tf1, tf2) == (True, True):
            print "\t".join([ln1[0], "Correct", "Correct", ln1[1], ln1[2], "|", ln1[3], ln1[4], "|", ln2[1], ln2[2],  "|",ln2[3], ln2[4], str(sdiff2)])
        
        elif (tf1, tf2) == (True, False):
            print "\t".join([ln1[0], "Correct", "Wrong", ln1[1], ln1[2],  "|", ln1[3], ln1[4], "|", ln2[1], ln2[2],  "|",ln2[3], ln2[4], str(sdiff2), "### -"])
        
        elif (tf1, tf2) == (False, True):
            print "\t".join([ln1[0], "Wrong", "Correct", ln1[1], ln1[2],  "|",ln1[3], ln1[4], "|", ln2[1], ln2[2],  "|",ln2[3], ln2[4], str(sdiff2), "### +"])
        
        elif (tf1, tf2) == (False, False):
            print "\t".join([ln1[0], "Wrong", "Wrong", ln1[1], ln1[2],  "|",ln1[3], ln1[4], "|", ln2[1], ln2[2],  "|",ln2[3], ln2[4], str(sdiff2)])

