import sys
import subprocess
import optparse
import os

def getpnum(setname):
    cmd = 'wc -l data/dp-%s.tuples' %setname
    ret = subprocess.check_output(cmd, shell=True)
    return int(ret.split(" ")[0])

def getprocerr(errfilename):
    cmd = 'fgrep "Processing No" %s |wc -l' % errfilename
    pnum = subprocess.check_output(cmd, shell=True)
    cmd = 'fgrep "Error" %s |wc -l' % errfilename
    enum = subprocess.check_output(cmd, shell=True)
    return int(pnum), int(enum)
    
cmdparser		= optparse.OptionParser(description="Feature generator.")
cmdparser.add_option("--targetset", help = "target set")
cmdparser.add_option("--genoptions", help = "options for feature generate")
cmdparser.add_option("--date", help = ".", default="0000")

options, args = cmdparser.parse_args()
# settings
defaultgenoptions = "--quicktest --extkb /share01/jun-s/kb"
myoptions = "--" + " --".join(options.genoptions.split())
lightfnlst = []

problemindex = os.environ['BKP_INDEX']


for setname in options.targetset.split():
    pnum = getpnum(setname) -1
    print setname, pnum

    xmlfn = "/share01/jun-s/tmp/%s.%s.%s%s.xml" % (options.date, "-".join(options.genoptions.split()), setname, problemindex)
    errfn = "/share01/jun-s/tmp/%s%serr" % (setname, problemindex)

    generatecmd = "python src/generateTrainingSet.py --input data/dp-%s.tuples %s --problemno %s %s > %s 2> %s" %(setname, defaultgenoptions, problemindex, myoptions, xmlfn, errfn)
    print generatecmd
    # subprocess.call(generatecmd, shell=True)

    # procnum, errnum = getprocerr(errfn)

    # print "Finish %s" %(setname)
    # print "Processing = %d  Error = %d" %(procnum, errnum)

    # lightfn = xmlfn.replace(".xml", ".light.xml")
    # lightcmd = 'python src/extractXMLlight.py %s > %s' %(xmlfn, lightfn)
    # print lightcmd
    # subprocess.call(lightcmd, shell=True)

    # lightfnlst += [lightfn]

# reconstruct
# ./bin/svmreconstruct.sh /work/jun-s/tmp/0630kb4e2.testrain2all.fullsknn-ph.light.xml /work/jun-s/tmp/0630kb4e2.dev2all.fullsknn-ph.light.xml
# reconcmd = './bin/svmreconstruct.sh %s %s' %(lightfnlst[0], lightfnlst[1])
# subprocess.call(reconcmd, shell=True)
# print reconcmd
# print "Finish Reconstruct"







# seq 0 563 | /home/jun-s/bin/parallel -j12 'python src2/generateTrainingSet.py --input data/dp-test.tuples --quicktest --extkb /work/jun-s/kb --problemno {} --kb4e2 --noknn --pfilter' > /work/jun-s/tmp/0807kb4e2.testall.large.test.xml 2> /work/jun-s/tmp/testerr
