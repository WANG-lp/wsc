import sys
import subprocess
import optparse
import os

def getpnum(setname):
    cmd = 'wc -l data/dp-%s.tuples' %setname
    print cmd
    ret = subprocess.check_output(cmd, shell=True)
    return int(ret.split(" ")[0])

cmdparser		= optparse.OptionParser(description="Feature generator.")
cmdparser.add_option("--mpiopt", help = "options for mpirun")
cmdparser.add_option("--targetset", help = "target set")
cmdparser.add_option("--genoptions", help = "options for feature generate")
cmdparser.add_option("--date", help = ".", default="0000")
options, args = cmdparser.parse_args()

for setname in options.targetset.split():
    pnum = getpnum(setname) -1
    print setname, pnum

    generatecmd = "mpirun -np %s /home/jun-s/src/bkp/bin/bkp %s /opt/PYTHON/python-2.7.5/bin/python bin/generatef_nict.py --targetset '%s' --date %s --genoptions '%s'" %(options.mpiopt, pnum, setname, options.date, options.genoptions)
    print generatecmd
    subprocess.call(generatecmd, shell=True)
