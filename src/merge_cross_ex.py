import sys
import commands

basename = sys.argv[1]
tailname = sys.argv[2]
numlines = -1 * int(sys.argv[3])
results = {}
rows = []

for i in xrange(10):
    filename = "%s%d%s" %(basename, i, tailname)
    # print filename
    f = open(filename)
    for line in f.readlines()[numlines:]:
        # print >>sys.stderr, line.strip()
        key, prec, recall, F = line.split("&")
        key, prec, recall, F = key.strip(), prec.strip(), recall.strip(), F.strip()
        # print >>sys.stderr, key, prec, recall
        precl, precr = prec.split(" (")[-1].strip("()").split("/")
        recalll, recallr = recall.split(" (")[-1].strip("()").split("/")
        # print col, cor, wrl, wrr
        if key not in results:
            results[key] = [0,0,0,0]

        tmp1, tmp2, tmp3, tmp4 = results[key]
        results[key] = [tmp1+int(precl), tmp2+int(precr), tmp3+int(recalll), tmp4+int(recallr)]


# print "RESULTS = "
for k, v in sorted(results.items()):
    rows = []
    rows += ["%.1f\\%% (%4d/%4d)" % (100.0 * v[0] / v[1], v[0], v[1] )]
    rows += ["%.1f\\%% (%4d/%4d)" % (100.0 * v[2] / (v[3]), v[2], (v[3]) )]
    rows += ["%.3f" %((2.0*(1.0*v[0]/v[1])*(1.0*v[2]/(v[3]))) / ((1.0* v[0]/v[1]) + (1.0* v[2]/(v[3]))))]
    rows += [k]
    print " ".join(rows)
