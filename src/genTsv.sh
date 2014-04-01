#!/bin/zsh

k=10

xpath work1/wsc/testset.features.thin.xml \
    problem @id \
    @anaphor governors/@anaphor contexts/@anaphor \
    @antecedent governors/@antecedent contexts/@antecedent \
    @falseAntecedent governors/@falseAntecedent contexts/@falseAntecedent \
    "statistics[@type='cirNumRules']/@correct:0" "statistics[@type='cirNumRules']/@wrong:0" \
    "feature[@type='cirPMIMatch']/@correct:0" "feature[@type='cirPMIMatch']/@wrong:0" \
    "feature[@type='kNN_score_cirPMICon,K=$k']/@correct:0" "feature[@type='kNN_score_cirPMICon,K=$k']/@wrong:0" \
    "feature[@type='kNN_score_cirArgPMI,K=$k']/@correct:0" "feature[@type='kNN_score_cirArgPMI,K=$k']/@wrong:0" \
    "feature[@type='kNN_score_cirArgConPMI,K=$k']/@correct:0" "feature[@type='kNN_score_cirArgConPMI,K=$k']/@wrong:0" \
    "feature[@type='selpref']/@correct:0" "feature[@type='selpref']/@wrong:0" \
    @text
