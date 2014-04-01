#!/bin/zsh

pc12dir=$HOME/parsing_clueweb12
wdir=/work1/t2g-13IAM/13IAM511
queue=$argv[1]
dt=`date +%Y%m%d-%H%M%S`
groupparam="-W group_list=t2g-13IAM"
 
mkdir -p $wdir/wsc/log_$argv[5]_$dt
cd $wdir/wsc/log_$argv[5]_$dt

if [ "TEST" = "$argv[7]" ]; then
    groupparam=""
fi

eval /work0/GSIC/apps/t2sub_a/t2sub_a \
    -J $argv[5] \
    -n 1 \
    -m $pc12dir/src/t2sub_a.mk \
    $groupparam \
    -q $queue \
    -l select=$argv[2]:ncpus=$argv[3]:mem=$argv[4] \
    -l place=scatter \
    -l walltime=$argv[6] \
    -N PC12W2T \
    $HOME/wsc/job/generateTrainingSet.sh

#   
#    -l select=8:mpiprocs=1:ncpus=1:mem=32gb \

