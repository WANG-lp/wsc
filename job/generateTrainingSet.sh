#!/bin/zsh

idx=$PBS_ARRAY_INDEX

cd $HOME/wsc

PYTHONPATH=$HOME/lib64/python2.6/site-packages python $HOME/wsc/src/generateTrainingSet.py \
    --input $HOME/wsc/data/dp-train.tuples \
    --problemno $idx \
    --quicktest --cat \
    --extkb $HOME/work1/extkb > $HOME/work1/wsc/trainingset.result.$idx.xml
