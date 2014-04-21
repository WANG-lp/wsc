all:
	rsync -av --exclude "bin" --exclude "local" . 13IAM511@io-t2.g.gsic.titech.ac.jp:~/wsc/
	rsync -av ~/bin/xpath 13IAM511@io-t2.g.gsic.titech.ac.jp:~/bin/

tools: hash hashTuples similaritySearch reducer 

hash:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/hash ./src/hash.cpp

hashTuples:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/hashTuples ./src/hashTuples.cpp

similaritySearch:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/similaritySearch ./src/similaritySearch.cpp

reducer:
	g++ -O2 -D GLIBCXX -o ./bin/compress ./src/compress.cpp
