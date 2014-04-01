#!/usr/bin/zsh

s=`zgrep -n '<<XML_BEGIN' /home/work/data/ClueWeb12/clueweb12_parsed/stanford/$argv[1].warc.gz.xmls.gz | awk -F":" '{docid++;} '$argv[2]' == docid {print $1; exit 1;}'`
e=`zgrep -n '<<XML_END' /home/work/data/ClueWeb12/clueweb12_parsed/stanford/$argv[1].warc.gz.xmls.gz | awk -F":" '{docid++;} '$argv[2]' == docid {print $1; exit 1;}'`

s=`expr $s + 1`
e=`expr $e - 1`

zcat /home/work/data/ClueWeb12/clueweb12_parsed/stanford/$argv[1].warc.gz.xmls.gz | sed -n "$s,$e""p"

