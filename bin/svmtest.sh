#!/bin/zsh

# 'KNN7_iriPredArg[^C]' 'KNN4_iriPredCon' 'KNN3_iriPredArgCon'
# 'HPOL' 'NCCJ08' 'google' 'selpref' 'LEX' \
#    'google|selpref|LEX|HPOL|settings' \

settings=('google' 'selpref' 'LEX' 'HPOL' 'NCCJ08' 'NCNAIVE0PMI' 'NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' 'google|selpref|LEX|HPOL' 'google|selpref|LEX|HPOL|NCCJ08' 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ')
settings=('google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ' 'google|selpref|LEX|HPOL|NCNAIVE0PMI|NCNAIVE0NPMI|NCNAIVE0FREQ|KNN[1-5]_iriAddPredArgCon')

echo '' > testedFeatures.list.tmp

foreach setting ($settings)
echo ${setting//|/-} >> testedFeatures.list.tmp
end

#
# FEATURE GENERATION.
foreach setting ($settings)

cat local/train.sv | python src/filterFeature.py inc $setting | \
    python src/indexify.py - local/train.${setting//|/-}.isv.vocab > local/train.${setting//|/-}.isv

cat local/test.sv | python src/filterFeature.py inc $setting | \
    python src/indexify.py local/train.${setting//|/-}.isv.vocab - > local/test.${setting//|/-}.isv

end

#
# PARALLEL TRAINING.
cat testedFeatures.list.tmp | parallel -j $argv[1] \
    '/home/naoya-i/src/svm_rank/svm_rank_learn -c 100.0 -# 100 local/train.{}.isv local/train.{}.model.svmrank;'\
'/home/naoya-i/src/svm_rank/svm_rank_classify local/test.{}.isv local/train.{}.model.svmrank local/test.{}.svmrank.predictions;'\
'python ./src/checkWrongOrNodec.py {} local/test.{}.svmrank.predictions > local/result.{}.txt'

#
# CLASSIFICATION
echo ''
echo ''

cat local/result.*.txt
