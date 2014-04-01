#!/bin/zsh

$HOME/wsc/bin/reduceCorefevents \
    ~/work1/extkb/corefevents.reduced.tsv \
    ~/work1/extkb/corefevents.reduced.vocab.bin \
    ~/work1/extkb/corefevents.reduced.vocabct.bin \
    < ~/work1/extkb/corefevents.tsv \
    2> $HOME/reduce.stderr

