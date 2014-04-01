
#include <omp.h>
#include <sys/time.h>

#include <ctime>

#include <iostream>
#include <fstream>
#include <sstream>

#include <algorithm>
#include <cstdlib>

#include <readline/readline.h>
#include <readline/history.h>

#include <tr1/unordered_set>

#include "google-word2vec.h"
#include "optparse.h"
#include "vectorize.h"
#include "corefevents.h"

using namespace std;
using namespace tr1;

static int myrandom (int i) { return std::rand()%i; }

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  translate "
                  " -v <VOCAB OF COREF EVENT PAIRS>"
                  " -c <VOCAB OF CONTEXT TYPES>"
                  ,
                  "v:c:", "vc", argc, argv);
  if(!opts.isGood()) return 0;
  
  cerr << "Loading vocab..." << endl;
  corefevents_t::vocab_t vocab; 
  corefevents_t::vocabct_t vocabCT;
  corefevents_t::readVocab(&vocab, opts.of('v'));
  corefevents_t::readVocab(&vocabCT, opts.of('c'));
  
  cout << "200 OK" << endl;

  string line;
  int input;
  
  while(getline(cin, line)) {
    if('c' == line[0] && 't' == line[1]) {
      int input = atoi(line.substr(3).c_str());
      cout << vocabCT[input] << endl;
    } else {
      int input = atoi(line.c_str());
      cout << vocab[input] << endl;
    }
  }
  
  return 0;
  
}

