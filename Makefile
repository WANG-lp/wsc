all:
	rsync -av --exclude "reduceCorefevents" --exclude "local" --exclude "bin/similaritySearch" --exclude "bin/probHashInstances" . 13IAM511@io-t2.g.gsic.titech.ac.jp:~/wsc/
	rsync -av ~/bin/xpath 13IAM511@io-t2.g.gsic.titech.ac.jp:~/bin/

tools: probHashInstances similaritySearch reducer translate

probHashInstances:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/probHashInstances ./src/probHashInstances.cpp

similaritySearch:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/similaritySearch ./src/similaritySearch.cpp

reducer:
	g++ -O2 -D GLIBCXX -o ./bin/reduceCorefevents ./src/reduceCorefevents.cpp

translate:
	g++ -O2 -D GLIBCXX -o ./bin/translate ./src/translate.cpp

