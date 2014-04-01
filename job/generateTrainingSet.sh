#!/bin/zsh

idx=$PBS_ARRAY_INDEX

cd $HOME

PYTHONPATH=$HOME/lib64/python2.6/site-packages python $HOME/wsc/bin/generateTrainingSet.py \
    --output $HOME/work1/wsc/testset \
    --input $HOME/work1/wsc/testset.tuples \
    --problemno $idx \
    --quicktest \
    --extkb ~/work1/extkb/
