#!/bin/zsh

# python src/extractXML.py /work/naoya-i/tmp/train.xml > /work/naoya-i/tmp/train.full.xml
# python src/extractXML.py /work/naoya-i/tmp/test.xml > /work/naoya-i/tmp/test.full.xml

xpath --linejoin $argv[1] problem 'feature-vector' | python src/rsbyqid.py 1 | python src/sortbyqid.py > local/train.sv &
xpath --linejoin $argv[2] problem 'feature-vector' | python src/rsbyqid.py 1 | python src/sortbyqid.py > local/test.sv
wait
