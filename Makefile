all:
	rsync -av --exclude "pathKB.txt" --exclude "bin" --exclude "local" . 13IAM511@io-t2.g.gsic.titech.ac.jp:~/wsc/
	rsync -av ~/bin/xpath 13IAM511@io-t2.g.gsic.titech.ac.jp:~/bin/

tools: hash hashTuples similaritySearch reducer 

unittest:
	g++ -o ./bin/unittest ./src/unittest.cpp /home/naoya-i/src/tinycdb-0.78/libcdb.a

hash:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/hash ./src/hash.cpp

hashTuples:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/hashTuples ./src/hashTuples.cpp

similaritySearch:
	g++ -O2 -msse4.2 -fopenmp -D GLIBCXX -o ./bin/similaritySearch ./src/similaritySearch.cpp $$HOME/src/tinycdb-0.78/libcdb.a

reducer:
	g++ -O2 -D GLIBCXX -o ./bin/compress ./src/compress.cpp
