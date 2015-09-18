# -*- coding: utf-8 -*-

import sys
import random

random.seed(int(sys.argv[2]))

NUM_TESTRAIN = 1686
NUM_DEV = 200
outd = {}
twinid = 0
checknum = 0
bid = 1
tmpid = 0
tmp = []
divrange = 10
divsize = 10
# divsizes = (84, 84, 84, 84, 84, 84, 84, 85, 85, 85)
divsizes = (84, 84, 84, 84, 84, 84, 84, 84, 85, 85)
# divsizes = (10, 10, 10, 10, 9, 9, 9, 11, 11, 11)
outfn = sys.argv[3]

def mkcross(keys, divsizes):
    ret = []
    bi = 0
    for i in divsizes:
        tmp = keys[bi:bi+i]
        print len(tmp)
        bi = bi + i
        ret.append(tuple(tmp))
    # print len(ret)
    return ret

for ln in open(sys.argv[1]):
    # print >>sys.stderr, ln
    qid = int(ln.split(" ", 2)[1].split(":", 2)[1])
    # print >>sys.stderr, qid
    if qid % 2 == 1 and bid % 2 == 0:
        twinid += 1
        # if qid == 1373: twinid += 1
        sys.stdout.write("qid = %s\t%s\n" %((qid) // 2, twinid))
        assert qid // 2 == twinid 

        outd[twinid] = tmp
        # print len(tmp)
        tmpid += 1
        tmp = []

        tmp.append(ln)
        bid = qid
    else:
        tmpid += 1
        tmp.append(ln)
        bid = qid
    # print len(tmp), len(outd)
else:
    twinid += 1
    # sys.stdout.write("qid = %s\t%s\n" %((qid) // 2, twinid))
    outd[twinid] = tmp
    # print len(tmp)

# print len(outd)
keys = outd.keys()
random.shuffle(keys)
# print keys


# crosstpl = zip(*[iter(keys)]*divrange)
crosstpl = mkcross(keys, divsizes)
# print crosstpl
# for l in crosstpl:
#     print l
#     print len(l)

# print outd[100]
# print outd[200]
# print outd[400]


for cid, ctpl in enumerate(crosstpl):
    with open("%s%d.sv" %(outfn, cid), "w") as f:
        for ctplid in ctpl:
            for line in outd[ctplid]:
                # print line
                f.write(line)

# print crosstpl
# print len(crosstpl)
# for ki in keys:
#     for twins in outd[ki]:

        
# for i in random.shuffle(outd.keys()):
#     print i
    # if twinid % 2 == 0:
    #     outd[twinid].append(ln)
    #     twinid += 1
        
    # for twinid in xrange(1, NUM_TESTRAIN+1):
        
