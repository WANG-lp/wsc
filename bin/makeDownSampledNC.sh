#!/bin/zsh

kb=/work/naoya-i/kb/corefevents.tsv

python -c 'import sys; [sys.stdout.write("%s\n" % (1.0/(2**i))) for i in xrange(1,8)]' | \
    parallel -j 8 './bin/ncdownsampler -p {} -s 20140522 -i /work/naoya-i/kb/corefevents.tsv -o /work/naoya-i/kb/corefevents.ds/corefevents.{}.tsv -O /work/naoya-i/kb/corefevents.ds/corefevents.{}.predicate-pairs.tsv'

python -c 'import sys; [sys.stdout.write("%s\n" % (1.0/(2**i))) for i in xrange(1,8)]' | \
    parallel -j 1 'sort --parallel=8 /work/naoya-i/kb/corefevents.ds/corefevents.{}.predicate-pairs.tsv | uniq -c > /work/naoya-i/kb/corefevents.ds/corefevents.{}.predicate-pairs.sorteduniqc.tsv'

foreach k (`python -c 'import sys; [sys.stdout.write("%s\n" % (1.0/(2**i))) for i in xrange(1,8)]'`)
awk '{print $2 " ~ " $3 "\t" $1}' /work/naoya-i/kb/corefevents.ds/corefevents.$k.predicate-pairs.sorteduniqc.tsv | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive.ds.$k.cdb /work/naoya-i/kb/ncnaive.ds.$k.cdb.tmp &
end
