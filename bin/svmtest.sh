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

settings=( \
    'HPOL' \
    # 'LEX' \
    # 'LEX|HPOL' \
    #
    # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ'
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArg[^W]'
    # #'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|[^S]KNN[1-5]_iriPredArgConW_UNIFORM'
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArgConW_UNIFORM'
    # # '[^S]KNN0_iriArg[^C]'
    # # 'SKNN1_iriArg[^C]'
    # # 'NCNAIVE0NPMI'
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|[^S]KNN[1-5]_iriArg'
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1_iriPred'
    # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN1_iriPred'
    # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN1_iriPredArgConW_UNIFORM'
    # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgConW_UNIFORM'
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|[^S]KNN[1-5]_iriPredArgCon[^W]'
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|SKNN[1-5]_iriPredArgCon[^W]' \
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|CONMATCH_|ARGMATCH_' \
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriPredArgCon' \
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredArgCon' \
    # # 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' \
    # 'google|selpref|LEX|HPOL|Rank_NCCJ08' \
    'google|selpref|HPOL' \
    # 'google|selpref|LEX|HPOL' \
) #CONMATCH_|ARGMATCH_')
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
