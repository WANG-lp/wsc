#!/bin/zsh

awk '$1 > 5' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive5.cdb /work/naoya-i/kb/ncnaive5.cdb.tmp &

awk '$1 > 10' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive10.cdb /work/naoya-i/kb/ncnaive10.cdb.tmp &

awk '$1 > 25' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive25.cdb /work/naoya-i/kb/ncnaive25.cdb.tmp &

awk '$1 > 50' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive50.cdb /work/naoya-i/kb/ncnaive50.cdb.tmp &

awk '$1 > 100' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive100.cdb /work/naoya-i/kb/ncnaive100.cdb.tmp &

awk '$1 > 200' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive200.cdb /work/naoya-i/kb/ncnaive200.cdb.tmp &

awk '$1 > 400' /work/naoya-i/kb/corefevents.predicate-pairs.sorteduniqc.tsv | \
    awk '{print $2 " ~ " $3 "\t" $1}' | cdbsrc | \
    cdbmake /work/naoya-i/kb/ncnaive400.cdb /work/naoya-i/kb/ncnaive400.cdb.tmp
