#!/usr/bin/zsh

# s=`zgrep -n '<<XML_BEGIN' /home/work/data/ClueWeb12/clueweb12_parsed/stanford/$argv[1].warc.gz.xmls.gz | awk -F":" '{docid++;} '$argv[2]' == docid {print $1; exit 1;}'`
# e=`zgrep -n '<<XML_END' /home/work/data/ClueWeb12/clueweb12_parsed/stanford/$argv[1].warc.gz.xmls.gz | awk -F":" '{docid++;} '$argv[2]' == docid {print $1; exit 1;}'`

s=`sed -n $argv[2]p /home/work/data/ClueWeb12/clueweb12_parsed/stanford2/$argv[1].warc.gz.txt.gz.forparse.index | awk '{print $2}'`

s=`expr $s - 5`
e=`expr $s + 10`

# zcat /home/work/data/ClueWeb12/clueweb12_parsed/stanford/$argv[1].warc.gz.xmls.gz | sed -n "$s,$e""p"
zcat /home/work/data/ClueWeb12/clueweb12_parsed/text2/$argv[1].warc.gz.txt.gz | sed -n "$s,$e""p"
