#!/bin/zsh

# 'KNN7_iriPredArg[^C]' 'KNN4_iriPredCon' 'KNN3_iriPredArgCon'
# 'HPOL' 'NCCJ08' 'google' 'selpref' 'LEX' \
#    'google|selpref|LEX|HPOL|settings' \

settings=('google' 'selpref' 'LEX' 'HPOL' 'NCCJ08' 'NCNAIVE0PMI' 'NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' 'google|selpref|LEX|HPOL' 'google|selpref|LEX|HPOL|NCCJ08' 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ')
settings=('google|selpref|LEX|HPOL' 'google|selpref|LEX|HPOL|Rank_NCCJ08' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredCon' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredArg[^C]' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredArgCon' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredArg[^C]|KNN[1-5]_iriAddPredCon' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArgCon' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArg[^C]' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredCon' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArg[^C]|KNN[1-5]_iriPredCon' \
)

settings=('google|selpref|LEX|HPOL' 'google|selpref|LEX|HPOL|Rank_NCCJ08' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredNConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgNConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriNConOFF' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgNConOFF' \
    
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredNConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgNConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriNConON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgNConON' \
	
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredNConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgNConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriNConbitON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgNConbitON' \

    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredNConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgNConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriNConphON' \
    'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriArgNConphON' \
    
    # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArg[^C]|SKNN[1-5]_iriPredCon' \
    'SKNN[1-5]_iriPredOFF' \
    'SKNN[1-5]_iriPredArgConOFF' \
    'SKNN[1-5]_iriPredArgOFF' \
    'SKNN[1-5]_iriPredConOFF' \
    'SKNN[1-5]_iriArgOFF' \
    'SKNN[1-5]_iriConOFF' \
    'SKNN[1-5]_iriArgConOFF' \
    'SKNN[1-5]_iriPredNConOFF' \
    'SKNN[1-5]_iriPredArgNConOFF' \
    'SKNN[1-5]_iriNConOFF' \
    'SKNN[1-5]_iriArgNConOFF' \

    'SKNN[1-5]_iriPredON' \
    'SKNN[1-5]_iriPredArgConON' \
    'SKNN[1-5]_iriPredArgON' \
    'SKNN[1-5]_iriPredConON' \
    'SKNN[1-5]_iriArgON' \
    'SKNN[1-5]_iriConON' \
    'SKNN[1-5]_iriArgConON' \
    'SKNN[1-5]_iriPredNConON' \
    'SKNN[1-5]_iriPredArgNConON' \
    'SKNN[1-5]_iriNConON' \
    'SKNN[1-5]_iriArgNConON' \

    'SKNN[1-5]_iriPredbitON' \
    'SKNN[1-5]_iriPredArgConbitON' \
    'SKNN[1-5]_iriPredArgbitON' \
    'SKNN[1-5]_iriPredConbitON' \
    'SKNN[1-5]_iriArgbitON' \
    'SKNN[1-5]_iriConbitON' \
    'SKNN[1-5]_iriArgConbitON' \
    'SKNN[1-5]_iriPredNConbitON' \
    'SKNN[1-5]_iriPredArgNConbitON' \
    'SKNN[1-5]_iriNConbitON' \
    'SKNN[1-5]_iriArgNConbitON' \

    'SKNN[1-5]_iriPredphON' \
    'SKNN[1-5]_iriPredArgConphON' \
    'SKNN[1-5]_iriPredArgphON' \
    'SKNN[1-5]_iriPredConphON' \
    'SKNN[1-5]_iriArgphON' \
    'SKNN[1-5]_iriConphON' \
    'SKNN[1-5]_iriArgConphON' \
    'SKNN[1-5]_iriPredNConphON' \
    'SKNN[1-5]_iriPredArgNConphON' \
    'SKNN[1-5]_iriNConphON' \
    'SKNN[1-5]_iriArgNConphON' \
)
# settings=( \
#     'HPOL' \
#     # 'LEX' \
#     # 'LEX|HPOL' \
#     #
#     # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ'
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArg[^W]'
#     # #'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|[^S]KNN[1-5]_iriPredArgConW_UNIFORM'
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArgConW_UNIFORM'
#     # # '[^S]KNN0_iriArg[^C]'
#     # # 'SKNN1_iriArg[^C]'
#     # # 'NCNAIVE0NPMI'
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|[^S]KNN[1-5]_iriArg'
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1_iriPred'
#     # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN1_iriPred'
#     # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN1_iriPredArgConW_UNIFORM'
#     # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgConW_UNIFORM'
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|[^S]KNN[1-5]_iriPredArgCon[^W]'
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgCon[^W]' \
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|CONMATCH_|ARGMATCH_' \
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArgCon' \
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredArgCon' \
#     # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' \
#     # 'google|selpref|LEX|HPOL|Rank_NCCJ08' \
#     'google|selpref|HPOL' \
#     # 'google|selpref|LEX|HPOL' \
# )
#CONMATCH_|ARGMATCH_')
#settings=('google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|CONMATCH_|ARGMATCH_')

#settings=`python src/hey.py ./data/stanfordDepTypes.txt`

#settings=('Rank_NCCJ08' 'NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ')
# settings=('google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' 'google|selpref|LEX|HPOL|NCNAIVE1PMI|NCNAIVE1NPMI|NCNAIVE1FREQ' \
#     'google|selpref|LEX|HPOL|NCNAIVE2PMI|NCNAIVE2NPMI|NCNAIVE2FREQ' 'google|selpref|LEX|HPOL|NCNAIVE3PMI|NCNAIVE3NPMI|NCNAIVE3FREQ' \
#     'google|selpref|LEX|HPOL|NCNAIVE4PMI|NCNAIVE4NPMI|NCNAIVE4FREQ' 'google|selpref|LEX|HPOL|NCNAIVE5PMI|NCNAIVE5NPMI|NCNAIVE5FREQ' \
#     'google|selpref|LEX|HPOL|NCNAIVE6PMI|NCNAIVE6NPMI|NCNAIVE6FREQ' 'google|selpref|LEX|HPOL|NCNAIVE7PMI|NCNAIVE7NPMI|NCNAIVE7FREQ')

echo -n '' > testedFeatures.rawlist.tmp

foreach setting ($settings)
echo $setting >> testedFeatures.rawlist.tmp
end

#
# PARALLEL TRAINING.
cat testedFeatures.rawlist.tmp | parallel -j $argv[1] \
    'f={}; fs=${f//|/-};'\
'cat local/train.sv | python src/filterFeature.py inc $f | python src/indexify.py - local/train.$fs.isv.vocab > local/train.$fs.isv;'\
'cat local/test.sv | python src/filterFeature.py inc $f | python src/indexify.py local/train.$fs.isv.vocab - > local/test.$fs.isv;'\
'/home/naoya-i/src/svm_rank/svm_rank_learn -c '$argv[2]' -# 100 local/train.$fs.isv local/train.$fs.model.svmrank;'\
'/home/naoya-i/src/svm_rank/svm_rank_classify local/test.$fs.isv local/train.$fs.model.svmrank local/test.$fs.svmrank.predictions;'\
'python ./src/checkWrongOrNodec4SvmRank.py $fs local/test.$fs.isv local/test.$fs.svmrank.predictions > local/result.$fs.txt'

#'python ./src/checkWrongOrNodec4SvmRank.py {} local/test.{}.isv local/test.{}.svmrank.predictions > local/result.{}.txt'

#
# CLASSIFICATION
echo ''
echo ''

foreach setting ($settings)
cat local/result.${setting//|/-}.txt
end
