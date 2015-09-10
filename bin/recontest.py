import sys
import subprocess
import optparse

def reconst(fnl, fnr):
    reconcmd = './bin/svmreconstruct.sh %s %s' %(fnl, fnr)
    subprocess.call(reconcmd, shell=True)
    print reconcmd
    print "Finish Reconstruct"

def svmtest(settings, cpara, date, fnl, fnr, options):
    if options.cross == False:
        outfn = fnr.replace("light.xml", "C%s.out%s" %(cpara, date))
        outfn = outfn.split("/")[-1]        
        svmrankcmd = './bin/svmtest_t1.sh 4 %s "%s" > result/%s' %(cpara, settings, outfn)
        print svmrankcmd
        subprocess.call(svmrankcmd, shell=True)
        print "Finish svmtest"

        extract_cwn(options.cwn.split(" "), date)
        print "Finish extract CorrectWrongNodec"

    else:
        # divide to 10
        divideoutfn = fnl.replace("light.xml", "divided.cross%s" %(date))
        divideoutfn = divideoutfn.split("/")[-1]
        # 1022
        dividecmd = 'python src2/divide-10cross.py local/train.sv 1022 /home/jun-s/work/wsc/data/%s' %(divideoutfn)
        print dividecmd
        subprocess.call(dividecmd, shell=True)
        
        for i in xrange(10):
            infn = divideoutfn
            # infn = fnl.replace("light.xml", "divided.cross%s" %(date))
            outfn = fnl.replace("light.xml", "cross%d.C%s.out%s" %(i, cpara, date))
            outfn = outfn.split("/")[-1]

            svmrankcmd = './bin/svmtest_cross_ex.sh 4 %s %s %d "%s" > result/%s' %(cpara, infn, i, settings, outfn)
            print svmrankcmd
            subprocess.call(svmrankcmd, shell=True)

            extract_cwn_cross(options.cwn.split(" "), date, i)
        print "Finish svmtest_cross"
        fnhead = 'result/%scross' %(outfn.split("cross")[0])
        fntail = '.C%s.out%s' %(cpara, date)
        mergedfn = '%s%s' %(fnhead, fntail)
        mergeresultcmd = 'python src/merge_cross_ex.py %s %s %d |sort -r -n -k1 > %s' %(fnhead, fntail, len(settings.split(" ")), mergedfn)
        print mergeresultcmd
        subprocess.call(mergeresultcmd, shell=True)
        print "Finish Merge svmtest result"


        for cwnsetting in options.cwn.split(" "):            
            mergecwncmd = 'cat /home/jun-s/work/wsc/result/correctwrong/cwn.cross[0-9].%s.%s.tsv|sort -n -k1 > /home/jun-s/work/wsc/result/correctwrong/cwn.cross.%s.%s.tsv' % (cwnsetting, date, cwnsetting, date)
            print mergecwncmd
            subprocess.call(mergecwncmd, shell=True)
        print "Finish extract CorrectWrongNodec"

def extract_cwn(cwnsettings, date):
    for cwnsetting in cwnsettings:
        cwnoutfn = '/home/jun-s/work/wsc/result/correctwrong/cwn.%s.%s.tsv' %(cwnsetting, options.date)
        checkcwncmd = 'python ./src/checkCorrectWrongNodec_ex.py %s > %s' %(cwnsetting, cwnoutfn)
        print checkcwncmd
        subprocess.call(checkcwncmd, shell=True)

def extract_cwn_cross(cwnsettings, date, indexi):
    for cwnsetting in cwnsettings:
        cwnoutcrossfn = '/home/jun-s/work/wsc/result/correctwrong/cwn.cross%d.%s.%s.tsv' %(indexi, cwnsetting, options.date)
        checkcwncmd = 'python ./src/checkCorrectWrongNodec_ex.py %s > %s' %(cwnsetting, cwnoutcrossfn)
        print checkcwncmd
        subprocess.call(checkcwncmd, shell=True)
        
if "__main__" == __name__:
    cmdparser		= optparse.OptionParser(description="Feature generator.")
    cmdparser.add_option("--settings", help = "settings.", default="google|selpref|HPOL|LEX google|selpref|HPOL|LEX|NCNAIVE0NPMI")
    cmdparser.add_option("--C", help = "C parameter", default="0.01")
    cmdparser.add_option("--date", help = ".", default="0000")
    cmdparser.add_option("--cwn", help = ".", default="base base-NCNAIVE0NPMI")
    cmdparser.add_option("--cross", help = "cross validation", action="store_true", default=False)
    
    options, args = cmdparser.parse_args()
    fnl, fnr = sys.argv[1], sys.argv[2]
    reconst(fnl, fnr)

    svmtest(options.settings, options.C, options.date, fnl, fnr, options)
    # elif options.cross == True:
    #     svmtest(options.settings, options.C, options.date, outfn)



