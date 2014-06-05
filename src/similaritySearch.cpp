
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
#include "exactsearch.h"
#include "optparse.h"
#include "vectorize.h"
#include "corefevents.h"

using namespace std;
using namespace tr1;

static int myrandom (int i) { return std::rand()%i; }

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  similaritySearch"
                  " -i <INPUT LSH>"
                  " -k <PATH TO KNOWLEDGE BASE>"
                  " -d <COREF EVENTS TSV>"
                  " -m <PARALLELS>"
                  " [-w <WEIGHT MAP>]"
                  " [-q] "
                  ,
                  "k:i:m:d:qw:", "kimd", argc, argv);
  if(!opts.isGood()) return 0;
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.bin",
                         opts.hasKey('q'));
  exactsearch_t  es(opts.of('k') + "/corefevents.cdblist");
  string         line;
  bool           fSimilaritySearchOn = false, fVectorGeneration = false;
  int            th                  = 0;
  size_t         maxRules            = 10000;
  
  corefevents_t                libce(opts.of('d'), true);
  corefevents_t::proposition_t prpIndexed, prpPredicted;
  unordered_map<string, float> weightMap;

  if(opts.hasKey('w')) {
    ifstream ifsWeightMap(opts.of('w').c_str());
    string   nameWeight;
    float    value;
    
    while(ifsWeightMap >> nameWeight >> value)
      weightMap[nameWeight] = value;
  }
  
  cout << "200 OK" << endl;
  
  while(getline(cin, line)) {
    if('p' == line[0]) prpIndexed.predicate = line.substr(2);
    if('c' == line[0]) prpIndexed.context = line.substr(2);
    if('a' == line[0]) prpIndexed.focusedArgument = line.substr(2);
    if('s' == line[0]) prpIndexed.slot = line.substr(2);

    if('~' == line[0]) {
      if('p' == line[1]) prpPredicted.predicate = line.substr(3);
      if('c' == line[1]) prpPredicted.context = line.substr(3);
      if('a' == line[1]) prpPredicted.focusedArgument = line.substr(3);
      if('s' == line[1]) prpPredicted.slot = line.substr(3);
    }
    
    if('+' == line[0]) fSimilaritySearchOn = line.substr(2) == "y";
    if('t' == line[0]) th = atoi(line.substr(2).c_str());
    if('m' == line[0]) maxRules = atoi(line.substr(2).c_str());
    if('v' == line[0]) fVectorGeneration = line.substr(2) == "y";
    
    if("" != line) continue;
    
    int timeElapsed;
    timeval t1, t2;
    size_t numExactMatches;
    gettimeofday(&t1, NULL);

    cerr << "Searching... " << endl;
    cerr << "(query: " << prpIndexed.predicate + ":" + prpIndexed.slot + "@" + prpIndexed.context
         << ", " << prpPredicted.predicate + ":" + prpPredicted.slot + "@" + prpPredicted.context << endl;
    vector<exactsearch_t::result_t> ret;
    es.search(&ret, prpIndexed.predicate + ":" + prpIndexed.slot, prpPredicted.predicate + ":" + prpPredicted.slot);
    numExactMatches = ret.size();
    
    gettimeofday(&t2, NULL);

    timeElapsed = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;
  
    // <-- FILTERING: RANDOM SAMPLING
    std::srand(0);
    std::random_shuffle(ret.begin(), ret.end(), myrandom);

    if(ret.size() > maxRules) {
      ret.resize(maxRules);
      cerr << "Truncated." << endl;
    }
    // <-- FILTERING ENDS
      
    cerr << "Done!" << endl;
    cerr << ret.size() << " entries (original: " << numExactMatches << ") have been found. (took " << float(timeElapsed)/1000.0 << " sec)." << endl;

    cout << numExactMatches << endl;
    cout << (fVectorGeneration ? ret.size() : 2*ret.size()) << endl;
    
    // IDENTIFY THE COMMON IDS.
    for(size_t i=0; i<ret.size(); i++) {
      if(fVectorGeneration) {
        string vector;
        libce.generateVector(&vector, ret[i].offset, prpIndexed, prpPredicted, gw2v);

        cout << vector << endl;
        continue;
      }
      
      for(int j=0; j<2; j++) {
        corefevents_t::result_t retScore;
        libce.calcScore(&retScore, ret[i].offset, ret[i].length, prpIndexed, prpPredicted, j, weightMap, gw2v);

        cout.write((const char*)&retScore.iIndexed, sizeof(uint16_t));
        cout.write((const char*)&retScore.iPredicted, sizeof(uint16_t));
      
        cout.write((const char*)&ret[i].offset, sizeof(uint64_t));
        cout.write((const char*)&retScore.length, sizeof(uint16_t));
      
        cout.write((const char*)&retScore.score, sizeof(float));
      
        cout.write((const char*)&retScore.spm1, sizeof(float));
        cout.write((const char*)&retScore.scm1, sizeof(float));
        cout.write((const char*)&retScore.sm1, sizeof(float));
        cout.write((const char*)&retScore.sam1, sizeof(float));

        cout.write((const char*)&retScore.spm2, sizeof(float));
        cout.write((const char*)&retScore.scm2, sizeof(float));
        cout.write((const char*)&retScore.sm2, sizeof(float));
        cout.write((const char*)&retScore.sam2, sizeof(float));

        cout.write((const char*)&retScore.spm, sizeof(float));
        cout.write((const char*)&retScore.scm, sizeof(float));
        cout.write((const char*)&retScore.sm, sizeof(float));
        cout.write((const char*)&retScore.sam, sizeof(float));

        string vector;
        libce.generateVector(&vector, ret[i].offset, prpIndexed, prpPredicted, gw2v);
        cout << toString(retScore.vcon1) << "\t"
             << toString(retScore.vcon2) << "\t"
             << toString(retScore.vcon) << endl;
        //cout << retScore.line << endl;
      }
    }

    cerr << ret.size() << " entries have been listed (took " << float(timeElapsed)/1000.0 << " sec)." << endl;
  }
 
  return 0;
  
}

