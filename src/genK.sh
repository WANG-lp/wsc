#!/bin/zsh

seq 1 49 | parallel -k -j16 "/home/naoya-i/bin/xpath $argv[1] problem @id \
    \"statistics[@type='iriNumRules']/@correct:0\" \"statistics[@type='iriNumRules']/@wrong:0\" \
    \"feature[@type='cirPMIMatch']/@correct:None\" \"feature[@type='cirPMIMatch']/@wrong:None\" \
    \"feature[@type='NCNAIVE0NPMI']/@correct:None\" \"feature[@type='NCNAIVE0NPMI']/@wrong:None\" \
    \"feature[@type='kNN_score_iriPredArg,K={}']/@correct:None\" \"feature[@type='kNN_score_iriPredArg,K={}']/@wrong:None\" \
    \"feature[@type='kNN_score_iriPredArgCon,K={}']/@correct:None\" \"feature[@type='kNN_score_iriPredArgCon,K={}']/@wrong:None\" \
    \"feature[@type='kNN_score_iriPredCon,K={}']/@correct:None\" \"feature[@type='kNN_score_iriPredCon,K={}']/@wrong:None\" \
    \"feature[@type='kNN_score_iriPred,K={}']/@correct:None\" \"feature[@type='kNN_score_iriPred,K={}']/@wrong:None\" \
    \"feature[@type='kNN_score_iriAddPredArg,K={}']/@correct:None\" \"feature[@type='kNN_score_iriAddPredArg,K={}']/@wrong:None\" \
    \"feature[@type='kNN_score_iriAddPredCon,K={}']/@correct:None\" \"feature[@type='kNN_score_iriAddPredCon,K={}']/@wrong:None\" \
    \"feature[@type='kNN_score_iriAddPredArgCon,K={}']/@correct:None\" \"feature[@type='kNN_score_iriAddPredArgCon,K={}']/@wrong:None\" \
    | python ./src/performance.py {}"

