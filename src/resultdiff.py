import sys
import popen2

options = sys.argv[1:]
in1 = options[0]
in2 = options[3]

target1 = options[1]
target2 = options[4]

k1 = options[2]
k2 = options[5]

def mappingtarget(target):
    mappingdict = {"p": "kNN_score_iriPred", "pa": "kNN_score_iriPredArg", "pac": "kNN_score_iriPredArgCon", "pc": "kNN_score_iriPredCon", "n": "iriPredNumRules"}
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

    
t1 = mappingtarget(target1)
t2 = mappingtarget(target2)
    
print in1, t1, k1, in2, t2, k2
    
cmd1 = ("/home/naoya-i/bin/xpath %s problem @id \
\"statistics[@type='iriNumRules']/@correct:0\" \"statistics[@type='iriNumRules']/@wrong:0\" \
\"feature[@type='%s,K=%s']/@correct:None\" \"feature[@type='%s,K=%s']/@wrong:None\" " %(in1, t1, k1, t1, k1))
cmd2 = ("/home/naoya-i/bin/xpath %s problem @id \
\"statistics[@type='iriNumRules']/@correct:0\" \"statistics[@type='iriNumRules']/@wrong:0\" \
\"feature[@type='%s,K=%s']/@correct:None\" \"feature[@type='%s,K=%s']/@wrong:None\" " %(in2, t2, k2, t2, k2))

stdout1, stdin1, stderr1 = popen2.popen3(cmd1)
tmp1 = []
for l in stdout1:
    tmp1.append(l.strip())

stdout2, stdin2, stderr2 = popen2.popen3(cmd2)
tmp2 = []
for l in stdout2:
    tmp2.append(l.strip())

print len(tmp1), len(tmp2)

if len(tmp1) != len(tmp2):
    print "#Problems Error"

for ln1, ln2 in zip(tmp1, tmp2):
    # print ln1, ln2
    ln1 = ln1.strip().split("\t")
    ln2 = ln2.strip().split("\t")
    lRules1, rRules1, tf1 = _getClass(ln1[1], ln1[2], ln1[3], ln1[4])
    lRules2, rRules2, tf2 = _getClass(ln2[1], ln2[2], ln2[3], ln2[4])

    if (lRules1, rRules1) != (True, True) or (lRules2, rRules2) != (True, True):
        continue
        
    if (tf1, tf2) == (True, True):
        sys.stdout.write("%s\tCorrect\tCorrect\n" %ln1[0])
    elif (tf1, tf2) == (True, False):
        sys.stdout.write("%s\tCorrect\tWrong\t###\n" %ln1[0])
    elif (tf1, tf2) == (False, True):
        sys.stdout.write("%s\tWrong\tCorrect\t###\n" %ln1[0])
    elif (tf1, tf2) == (False, False):
        sys.stdout.write("%s\tWrong\tWrong\n" %ln1[0])
