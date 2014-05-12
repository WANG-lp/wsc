#!/bin/zsh

cat /work/naoya-i/kb/tuples.pra.tsv /work/naoya-i/kb/tuples.pr.tsv /work/naoya-i/kb/tuples.a.tsv | cdbsrc | cdbmake /work/naoya-i/kb/tuples.simple.cdb /work/naoya-i/kb/tuples.simple.cdb.tmp
