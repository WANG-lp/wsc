#include <omp.h>

#include <ctime>

#include <iostream>
#include <fstream>
#include <sstream>

#include <list>
#include <algorithm>

#include "google-word2vec.h"
#include "optparse.h"
#include "vectorize.h"
#include "corefevents.h"

using namespace std;

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n simsearch"
                  "-k <PATH TO KB>"
                  "[-w <PATH TO LIST OF WN PREDICATES>]"
                  "[-m <NUM OF CPUS>]"
                  ,
                  "k:m:w:", "k", argc, argv);
  if(!opts.isGood()) return 0;

  opts.defset('m', "1");
  opts.defset('w', "");
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.cdb",
                         true);
  
  string                           line;
  vector<string>                   vocab;
  uint                             numCpus = atoi(opts.of('m').c_str()), K = 10;
  unordered_set<string>            wnpredicates;

  gw2v.readVocab(&vocab, opts.of('k') + "/GoogleNews-vectors-negative300.vocab.txt", opts.of('w'));

  cerr << vocab.size() << " words." << endl;
  cout << "200 OK" << endl;
  
  while(getline(cin, line)) {
    if(line.length() >= 2) {
      if("K " == line.substr(0, 2)) {
        K = atoi(line.substr(2).c_str());
        continue;
      }
    }

    google_word2vec_t::kbest_t kbest;
    gw2v.getSimilarEntiries(&kbest, line, vocab, K, numCpus);

    cout << kbest.size() << endl;
    
    for(uint i=0; i<kbest.size(); i++)
      cout << (1+i) << "\t" << kbest[i].second << "\t" << vocab[kbest[i].first] << endl;
  }
  
  return 1;
}
