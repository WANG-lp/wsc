#!/bin/zsh

echo '' > result

# 'KNN7_iriPredArg[^C]' 'KNN4_iriPredCon' 'KNN3_iriPredArgCon'
# 'HPOL' 'NCCJ08' 'google' 'selpref' 'LEX' \
#    'google|selpref|LEX|HPOL|NCCJ08' \

foreach setting (
    'NCNAIVE10'  \
    'NCNAIVE0'  \
    'google|selpref|LEX|HPOL|NCCJ08|NCNAIVE0' \
    'google|selpref|LEX|HPOL|NCCJ08|KNN5_iriPredArg[^C]' \
    'google|selpref|LEX|HPOL|NCCJ08|KNN3_iriPredCon' \
    'google|selpref|LEX|HPOL|NCCJ08|KNN2_iriPredArgCon' \
    )
cat local/train.sv | python src/filterFeature.py inc $setting | \
    python src/indexify.py - local/train.isv.vocab > local/train.isv

cat local/test.sv | python src/filterFeature.py inc $setting | \
    python src/indexify.py local/train.isv.vocab - > local/test.isv

/home/naoya-i/src/svm_rank/svm_rank_learn -c 100.0 -# 100 local/train.isv local/train.model.svmrank
/home/naoya-i/src/svm_rank/svm_rank_classify local/test.isv local/train.model.svmrank local/test.svmrank.predictions

python ./src/checkWrongOrNodec.py $setting local/test.svmrank.predictions >> result
echo '' >> result

end

echo ''
echo ''

cat result
