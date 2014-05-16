
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
#include "lsh.h"
#include "optparse.h"
#include "vectorize.h"
#include "corefevents.h"

using namespace std;
using namespace tr1;

static int myrandom (int i) { return std::rand()%i; }

void _readProposition(istringstream &iss, corefevents_t::proposition_t *pOut) {
  getline(iss, pOut->predicate, '\t');
  getline(iss, pOut->context, '\t');
  getline(iss, pOut->slot, '\t');
  getline(iss, pOut->focusedArgument, '\t');
}

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  distance"
                  " -k <PATH TO KNOWLEDGE BASE>"
                  " [-q] "
                  ,
                  "k:q", "k", argc, argv);
  if(!opts.isGood()) return 0;
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.bin",
                         opts.hasKey('q'));
  string        line;
  corefevents_t::proposition_t p1, p2;
  
  cout << "200 OK" << endl;
  
  while(getline(cin, line)) {
    istringstream issLine(line);
    
    _readProposition(issLine, &p1);
    _readProposition(issLine, &p2);
    
    cout << corefevents_t::calcDistance(p1, p2, gw2v) << endl;
  }
 
  return 0;
  
}

