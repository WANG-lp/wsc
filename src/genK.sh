#!/bin/zsh

foreach k (`seq 1 49`)
/home/naoya-i/bin/xpath $argv[1] \
    problem @id \
    "statistics[@type='iriNumRules']/@correct:0" "statistics[@type='iriNumRules']/@wrong:0" \
    "feature[@type='cirPMIMatch']/@correct:None" "feature[@type='cirPMIMatch']/@wrong:None" \
    "feature[@type='kNN_score_iriPred,K=$k']/@correct:None" "feature[@type='kNN_score_iriPred,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_iriPredArg,K=$k']/@correct:None" "feature[@type='kNN_score_iriPredArg,K=$k']/@wrong:None" \
    "feature[@type='kNN_score_iriPredArgCon,K=$k']/@correct:None" "feature[@type='kNN_score_iriPredArgCon,K=$k']/@wrong:None" \
    | python ./src/performance.py $k
end

