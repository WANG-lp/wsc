import sys
import subprocess
import optparse
import os

cmdparser		= optparse.OptionParser(description="Feature generator.")
cmdparser.add_option("--mpiopt", help = "options for mpirun")
cmdparser.add_option("--targetset", help = "target set")
cmdparser.add_option("--genoptions", help = "options for feature generate")
cmdparser.add_option("--date", help = ".", default="0000")
options, args = cmdparser.parse_args()

def getpnum(setname):
    cmd = 'wc -l data/dp-%s.tuples' %setname
    ret = subprocess.check_output(cmd, shell=True)
    return int(ret.split(" ")[0])

for setname in options.targetset.split():
    pnum = getpnum(setname) -1
    print setname, pnum

    generatecmd = "mpirun -np %s /home/jun-s/src/bkp/bin/bkp %s python bin/generatef_nict.py --targetset '%s' --date %s --genoptions '%s'" %(options.mpiopt, pnum, setname, options.date, options.genoptions)
    print generatecmd
    subprocess.call(generatecmd, shell=True)
