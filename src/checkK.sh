#!/bin/zsh

foreach k (`seq 1 99`)
xpath work1/wsc/testset.features.xml \
    /root/problem @id \
    "statistics[@type='cirNumRules']/@correct:0" "statistics[@type='cirNumRules']/@wrong:0" \
    "feature[@type='cirPMIMatch']/@correct:None" "feature[@type='cirPMIMatch']/@wrong:None" \
    "feature[@type='kNN_rank_cirArg,K=$k']/@correct:None" "feature[@type='kNN_rank_cirArg,K=$k']/@wrong:None" \
    "feature[@type='kNN_rank_cirPMICon,K=$k']/@correct:None" "feature[@type='kNN_rank_cirPMICon,K=$k']/@wrong:None" \
    "feature[@type='kNN_rank_cirArgPMI,K=$k']/@correct:None" "feature[@type='kNN_rank_cirArgPMI,K=$k']/@wrong:None" \
    "feature[@type='kNN_rank_cirArgCon,K=$k']/@correct:None" "feature[@type='kNN_rank_cirArgCon,K=$k']/@wrong:None" \
    "feature[@type='kNN_rank_cirArgConPMI,K=$k']/@correct:None" "feature[@type='kNN_rank_cirArgConPMI,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_cirArg,K=$k']/@correct:None" "feature[@type='kNN_score_cirArg,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_cirPMICon,K=$k']/@correct:None" "feature[@type='kNN_score_cirPMICon,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_cirArgPMI,K=$k']/@correct:None" "feature[@type='kNN_score_cirArgPMI,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_cirArgCon,K=$k']/@correct:None" "feature[@type='kNN_score_cirArgCon,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_cirArgConPMI,K=$k']/@correct:None" "feature[@type='kNN_score_cirArgConPMI,K=$k']/@wrong:None" | python $HOME/wsc/bin/performance.py $k
end

