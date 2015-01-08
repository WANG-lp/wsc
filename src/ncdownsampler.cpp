
#include <omp.h>
#include <sys/time.h>

#include <ctime>

#include <iostream>
#include <fstream>
#include <sstream>

#include <stdint.h>
#include <vector>
#include <algorithm>
#include <cstdlib>

#include <readline/readline.h>
#include <readline/history.h>

#include <tr1/unordered_set>

#include "optparse.h"

using namespace std;
using namespace tr1;

static int myrandom (int i) { return std::rand()%i; }

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  ncdownsampler"
                  " -i <INPUT TSV>"
                  " -s <SEED>"
                  " -p <PROBABILITY OF ACCEPTANCE>"
                  " -o <OUTPUT>"
                  " -O <OUTPUT (PREDICATE PAIRS)>"
                  ,
                  "i:s:p:o:O:", "ispoO", argc, argv);
  if(!opts.isGood()) return 0;

  string   ln;
  float    fProbAccept = atof(opts.of('p').c_str());
  uint64_t numProcessed = 0, numAccepted = 0;

  ifstream ifsTsv(opts.of('i').c_str());
  ofstream
    ofsMain(opts.of('o').c_str()),
    ofsSub(opts.of('O').c_str());
  
  srand(atoi(opts.of('s').c_str()));

  cerr << "P(Acceptance) = " << fProbAccept << endl;
  
  while(getline(ifsTsv, ln)) {
    numProcessed++;

    if(0 == numProcessed % 1000000) cerr << "." << flush;
    if(0 == numProcessed % 10000000) {
      cerr << " " << numProcessed << ", " << numAccepted << endl;
      numAccepted = 0;
    }
    
    float fP = rand() / (float)RAND_MAX;

    if(fP <= fProbAccept) {
      numAccepted++;
      ofsMain << ln << endl;
      ofsSub  << ln.substr(0, ln.find("\t", ln.find("\t")+1)) << endl;
    }
  }

  return 1;
}
