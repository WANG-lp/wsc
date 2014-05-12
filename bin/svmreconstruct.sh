#!/bin/zsh

python src/extractXML.py /work/naoya-i/tmp/train.xml > /work/naoya-i/tmp/train.full.xml
python src/extractXML.py /work/naoya-i/tmp/test.xml > /work/naoya-i/tmp/test.full.xml

xpath --linejoin /work/naoya-i/tmp/train.full.xml problem 'feature-vector' > local/train.sv
xpath --linejoin /work/naoya-i/tmp/test.full.xml problem 'feature-vector' > local/test.sv
