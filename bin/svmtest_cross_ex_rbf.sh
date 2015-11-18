#!/bin/zsh

# settings=('selpref' 'LEX' 'HPOL' 'google' \
#     # 'NCCJ08' \
#     # 'gglloged' \
#     'NCNAIVE0NPMI' \
#     'NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgConbitON' \
# 	'selpref|LEX|HPOL' \
# 	'gglloged|selpref|LEX|HPOL' \
# 	'gglloged|selpref|LEX|HPOL|NCNAIVE0NPMI' \
# 	'selpref|LEX|HPOL|NCNAIVE0NPMI' \
#     'gglloged|selpref|LEX|HPOL|NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgConbitON' \
#     'gglloged|selpref|LEX|HPOL|NCNAIVE0NPMI|SKNN[1-5]_iriPredConOFF' \
#     'gglloged|selpref|LEX|HPOL|NCNAIVE0NPMI|SKNN[1-5]_iriPredArgConOFF' \
#     'selpref|LEX|HPOL|NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgConbitON' \
#     'gglloged|selpref|LEX|HPOL|NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgConOFF' \
#     'gglloged|selpref|LEX|NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgConbitON' \
#     # 'NCNAIVE0NPMI|SKNNTURN1_iriPredArgConbitON|SKNNTURN2_iriPredArgConbitON|SKNNTURN3_iriPredArgConbitON|SKNNTURN4_iriPredArgConbitON|SKNNTURN5_iriPredArgConbitON' \
#     # 'NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgConOFF' \
#     # 'NCNAIVE0NPMI|SKNN[1-5]_iriPredArgConOFF' \
#     # 'NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredArgbitON' \
#     # 'NCNAIVE0NPMI|SKNNTURN[1-5]_iriPredConbitON' \
#     # 'NCNAIVE0NPMI|SKNNTURN[1-5]_iriArgConbitON' \
# )

settings=($argv[5])
nsettings=(`echo $settings[@]`)

echo -n '' > testedFeatures.rawlist.tmp

foreach setting ($nsettings)
echo $setting >> testedFeatures.rawlist.tmp
end

#
# CONSTRUCT CROSS TRAIN-TEST

if test $argv[4] -eq 0 ; then
    echo "cross0"
    cat /home/jun-s/work/wsc/data/$argv[3]{1..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 1; then
	echo "cross1"
    cat /home/jun-s/work/wsc/data/$argv[3]0.sv /home/jun-s/work/wsc/data/$argv[3]{2..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 2; then
	echo "cross2"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..1}.sv /home/jun-s/work/wsc/data/$argv[3]{3..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 3; then
	echo "cross3"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..2}.sv /home/jun-s/work/wsc/data/$argv[3]{4..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 4; then
	echo "cross4"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..3}.sv /home/jun-s/work/wsc/data/$argv[3]{5..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 5; then
	echo "cross5"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..4}.sv /home/jun-s/work/wsc/data/$argv[3]{6..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 6; then
	echo "cross6"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..5}.sv /home/jun-s/work/wsc/data/$argv[3]{7..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 7; then
	echo "cross7"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..6}.sv /home/jun-s/work/wsc/data/$argv[3]{8..9}.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 8; then
	echo "cross8"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..7}.sv /home/jun-s/work/wsc/data/$argv[3]9.sv |python src/sortbyqid.py > local/traincross.sv
elif test $argv[4] -eq 9; then
	echo "cross9"
    cat /home/jun-s/work/wsc/data/$argv[3]{0..8}.sv |python src/sortbyqid.py > local/traincross.sv
fi
cat /home/jun-s/work/wsc/data/$argv[3]$argv[4].sv |python src/sortbyqid.py > local/testcross.sv


#
# PARALLEL TRAINING.
cat testedFeatures.rawlist.tmp | parallel -j $argv[1] -u \
    'f={}; fs=${f//|/-};'\
'echo -- Start training and classification with $fs features...;'\
'cat local/traincross.sv | python src/filterFeature.py inc $f | python src/indexify.py - local/train.$fs.isv.vocab > local/train.$fs.isv;'\
'cat local/testcross.sv | python src/filterFeature.py inc $f | python src/indexify.py local/train.$fs.isv.vocab - > local/test.$fs.isv;'\
'echo ;'\
'echo -- Training on local/train.$fs.isv;'\
'echo ~/src/svm_rank/svm_rank_learn -t 2 -g '$argv[6]' -c '$argv[2]' -# 100 local/train.$fs.isv local/train.$fs.model.svmrank;'\
'~/src/svm_rank/svm_rank_learn -t 2 -g '$argv[6]' -c '$argv[2]' -# 100 local/train.$fs.isv local/train.$fs.model.svmrank;'\
'echo ;'\
'echo -- Classifying on local/test.$fs.isv;'\
'echo ~/src/svm_rank/svm_rank_classify local/test.$fs.isv local/train.$fs.model.svmrank local/test.$fs.svmrank.predictions;'\
'~/src/svm_rank/svm_rank_classify local/test.$fs.isv local/train.$fs.model.svmrank local/test.$fs.svmrank.predictions;'\
'python ./src/checkWrongOrNodec4SvmRanktmp.py $fs local/test.$fs.isv local/test.$fs.svmrank.predictions > local/result.$fs.txt'

#'python ./src/checkWrongOrNodec4SvmRank.py {} local/test.{}.isv local/test.{}.svmrank.predictions > local/result.{}.txt'

# python ./src/checkCorrectWrongNodec_ncnaive0npmi.py "-SKNNTURN[1-5]_iriPredArgConbitON" test > /home/jun-s/work/wsc/result/correctwrong/ncnaive0npmi-iriPredArgConbitON.0630kb4e2.fullsknn5-ph.cross$argv[3].learned.tsv

# python ./src/checkCorrectWrongNodec_base_ncnaive0npmi.py "-SKNNTURN[1-5]_iriPredArgConbitON" test > /home/jun-s/work/wsc/result/correctwrong/base-ncnaive0npmi-iriPredArgConbitON.0630kb4e2.fullsknn5-ph.cross$argv[3].learned.tsv

# python ./src/checkCorrectWrongNodec_base_ncnaive0npmi.py "" test > /home/jun-s/work/wsc/result/correctwrong/base-ncnaive0npmi.0630kb4e2.base.cross$argv[3].learned.tsv

#
# CLASSIFICATION
echo ''
echo ''

foreach setting ($nsettings)
cat local/result.${setting//|/-}.txt
end
