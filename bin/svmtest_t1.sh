#!/bin/zsh

# settings=('google' 'selpref' 'LEX' 'HPOL' 'NCNAIVE0NPMI' 'google|selpref|LEX|HPOL' 'google|selpref|LEX|HPOL|NCNAIVE0NPMI')
    # 'selpref|LEX|HPOL' \
    # )
    # 'selpref|LEX|HPOL|NCCJ08' \
	# 'selpref|LEX|HPOL|NCNAIVE0NPMI' \
    # 'google|selpref|HPOL|LEX|svocount')

settings=($argv[3])
nsettings=(`echo $settings[@]`)

echo -n '' > testedFeatures.rawlist.tmp

foreach setting ($nsettings)
echo $setting >> testedFeatures.rawlist.tmp
end

# # PARALLEL TRAINING.
# cat testedFeatures.rawlist.tmp | parallel -j $argv[1] \
#     'f={}; fs=${f//|/-};'\
# 'cat local/train.sv | python src/filterFeature.py inc $f | python src/indexify.py - local/train.$fs.isv.vocab > local/train.$fs.isv;'\
# 'cat local/test.sv | python src/filterFeature.py inc $f | python src/indexify.py local/train.$fs.isv.vocab - > local/test.$fs.isv;'\
# '/home/naoya-i/src/svm_rank/svm_rank_learn -c $argv[2] -# 100 local/train.$fs.isv local/train.$fs.model.svmrank;'\
# '/home/naoya-i/src/svm_rank/svm_rank_classify local/test.$fs.isv local/train.$fs.model.svmrank local/test.$fs.svmrank.predictions;'\
# 'python ./src/checkWrongOrNodec4SvmRanktmp.py $fs local/test.$fs.isv local/test.$fs.svmrank.predictions > local/result.$fs.txt'

# PARALLEL TRAINING.
cat testedFeatures.rawlist.tmp | parallel -j $argv[1] -u \
    'f={}; fs=${f//|/-};'\
'echo -- Start training and classification with $fs features...;'\
'cat local/train.sv | python src/filterFeature.py inc $f | python src/indexify.py - local/train.$fs.isv.vocab > local/train.$fs.isv;'\
'cat local/test.sv | python src/filterFeature.py inc $f | python src/indexify.py local/train.$fs.isv.vocab - > local/test.$fs.isv;'\
'echo ;'\
'echo -- Training on local/train.$fs.isv;'\
'echo /home/naoya-i/src/svm_rank/svm_rank_learn -c '$argv[2]' -# 100 local/train.$fs.isv local/train.$fs.model.svmrank;'\
'/home/naoya-i/src/svm_rank/svm_rank_learn -c '$argv[2]' -# 100 local/train.$fs.isv local/train.$fs.model.svmrank;'\
'echo ;'\
'echo -- Classifying on local/test.$fs.isv;'\
'echo /home/naoya-i/src/svm_rank/svm_rank_classify local/test.$fs.isv local/train.$fs.model.svmrank local/test.$fs.svmrank.predictions;'\
'/home/naoya-i/src/svm_rank/svm_rank_classify local/test.$fs.isv local/train.$fs.model.svmrank local/test.$fs.svmrank.predictions;'\
'python ./src/checkWrongOrNodec4SvmRanktmp.py $fs local/test.$fs.isv local/test.$fs.svmrank.predictions > local/result.$fs.txt'

#'python ./src/checkWrongOrNodec4SvmRank.py {} local/test.{}.isv local/test.{}.svmrank.predictions > local/result.{}.txt'

#
# CLASSIFICATION
echo ''
echo ''

foreach setting ($nsettings)
cat local/result.${setting//|/-}.txt
end
