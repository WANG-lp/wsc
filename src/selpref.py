
import sys
import math
import os
import cdb

def _npmi(pxy, px, py):
    return math.log(pxy / (px*py), 2)

class selpref_t:
    def __init__(self, pathKB="/work1/t2g-13IAM/13IAM511/extkb"):
        self.cdbTuples  = cdb.init(os.path.join(pathKB, "tuples.cdb"))
        self.totalFreq = int(open(os.path.join(pathKB, "tuples.totalfreq.txt")).read())

    def calc(self, p, r, a):
        try:
            pxy  = float(self.cdbTuples.get("%s:%s,%s" % (p, r, a)))
            px   = float(self.cdbTuples.get("%s:%s" % (p, r)))
            py   = float(self.cdbTuples.get("%s" % (a)))
            d    = (1.0 * pxy / (pxy+1)) * (1.0 * min(px, py) / (min(px, py)+1))
        except TypeError:
            return 0
        
        print pxy, px, py, d, self.totalFreq, _npmi(pxy/self.totalFreq, px/self.totalFreq, py/self.totalFreq)

        return d * _npmi(pxy/self.totalFreq, px/self.totalFreq, py/self.totalFreq)


if "__main__" == __name__:
    sp = selpref_t()
    print sp.calc(*sys.argv[1:])
