#!/bin/zsh

k=10

xpath work1/wsc/testset.features.xml \
    problem @id \
    @anaphor governors/@anaphor contexts/@anaphor \
    @antecedent governors/@antecedent contexts/@antecedent \
    @falseAntecedent governors/@falseAntecedent contexts/@falseAntecedent \
    "statistics[@type='cirNumRules']/@correct:0" "statistics[@type='cirNumRules']/@wrong:0" \
    'statistics[@type="cirInstances"]' \
    @text

