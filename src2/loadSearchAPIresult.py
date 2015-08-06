# -*- coding: utf-8 -*-

### dev2_pid=8_CVW_qw.json ###

import json
import glob
import sys

# targethead = sys.argv[1]
qtypes = ["CV", "CVW", "JC", "MA"]

def loadresult(targetname):
    
    f = open(targetname, "r")
    data = f.read()
    f.close()
    
    if data == "None":
        return 0.0
    
    data = json.loads(data)

    return data["searchInformation"]["totalResults"]

if "__main__" == __name__:
    resultdic = {}
    if sys.argv[1] == "all":
        filenamelist = glob.glob("/home/jun-s/work/wsc/data/google/*.json")
    for targetfilename in filenamelist:
        targetname = targetfilename.split("/")[-1]
        totalresult = loadresult(targetfilename)
        
        resultdic[targetname] = totalresult

    # if sys.argv[1] == "all":
    for tn, value in sorted(resultdic.items()):
        print tn, value

    
            
    # for qtype in qtypes:
    #     targetnameC = "/home/jun-s/work/wsc/data/google/%s_%s_qc" %(targethead, qtype)
    #     targetnameW = "/home/jun-s/work/wsc/data/google/%s_%s_qw" %(targethead, qtype)
    #     loadresult(targetnameC)
