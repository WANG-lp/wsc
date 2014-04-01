#!/bin/zsh


$HOME/wsc/bin/probHashInstances \
    -k ~/work1/extkb/ \
    -i ~/work1/extkb/corefevents.reduced.tsv \
    -v ~/work1/extkb/corefevents.reduced.vocab.bin \
    -c ~/work1/extkb/corefevents.reduced.vocabct.bin \
    -o ~/work1/extkb/corefevents.b128.pceach.bin \
    -m 24 -h pceach \
    2> $HOME/hashing.stderr
