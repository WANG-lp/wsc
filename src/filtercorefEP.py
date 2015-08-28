import sys

epf = open(sys.argv[1])

epset = set()
for epln in epf.readlines():
    epset.add(epln.strip())


    
for corefln in sys.stdin:
    target1 = corefln.split("\t")[0:2]
    key1 = "\t".join(target1)
    target2 = corefln.strip().split("\t")[-2:]
    key2 = "\t".join(target2)

    if key1 in epset:
        print corefln,
    elif key2 in epset:
        print corefln,
