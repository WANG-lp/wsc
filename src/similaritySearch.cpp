
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

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  similaritySearch"
                  " -i <INPUT LSH>"
                  " -k <PATH TO KNOWLEDGE BASE>"
                  " -d <COREF EVENTS TSV>"
                  " -m <PARALLELS>"
                  ,
                  "k:i:m:d:", "kimd", argc, argv);
  if(!opts.isGood()) return 0;
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.bin");
  lsh_t   lsh(opts.of('i'));
  string  line;
  int     th       = 0;
  size_t  maxRules = 1000;
  float  *pQuery   = new float[lsh.getDim()];
  
  corefevents_t                libce(opts.of('d'), true);
  corefevents_t::proposition_t prpIndexed, prpPredicted;
  
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
    
    if('t' == line[0]) th = atoi(line.substr(2).c_str());
    if('m' == line[0]) maxRules = atoi(line.substr(2).c_str());
    
    if("" != line) continue;
    
    if("pceach" != lsh.getHashType()) {
      cerr << "SORRY..." << endl;
      cerr << "Idk the hash type: " << lsh.getHashType() << endl;
      continue;
    }
    
    vector<uint64_t> offsets;
    vector<string> keys;

    // PREPARE THE KEYS.
    keys.push_back(prpIndexed.predicate);
    extractContextWords(&keys, prpIndexed.context);
    
    timeval t1, t2;
    gettimeofday(&t1, NULL);
    
    for(size_t i=0; i<keys.size(); i++) {
      cerr << "Searching... " << flush;
    
      initVector(pQuery, lsh.getDim());
      addWordVector(pQuery, keys[i], gw2v);

      vector<uint64_t> ret(1024*1024, 0);
      lsh.search(&ret, pQuery, th, atoi(opts.of('m').c_str()));

      unordered_set<uint64_t> setRet(ret.begin(), ret.end());
      for(unordered_set<uint64_t>::iterator j=setRet.begin(); setRet.end()!=j; ++j)
        offsets.push_back(*j);
      
      cerr << "Cool. " << ret.size() << " entries found." << endl;
    }
    
    gettimeofday(&t2, NULL);

    int timeElapsed = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;
    vector<uint64_t> ret;

    sort(offsets.begin(), offsets.end());

    size_t counter = 0;
    for(size_t i=0; i<offsets.size();) {
      for(counter=0; i+counter<offsets.size(); counter++)
        if(offsets[i]!=offsets[i+counter]) break;
      
      if(counter >= keys.size()) ret.push_back(offsets[i]);
      
      i += counter;
    }
    
    std::srand(0);
    std::random_shuffle(ret.begin(), ret.end(), myrandom);

    if(ret.size() > maxRules) {
      ret.resize(maxRules);
      cerr << "Truncated." << endl;
    }
      
    cerr << "Done!" << endl;
    cerr << ret.size() << " entries have been found. (took " << float(timeElapsed)/1000.0 << " sec)." << endl;

    cout << ret.size() << endl;
    
    // IDENTIFY THE COMMON IDS.
    for(size_t i=0; i<ret.size(); i++) {
      corefevents_t::result_t retScore;
      libce.calcScore(&retScore, ret[i], 0, prpIndexed, prpPredicted, gw2v);

      cout.write((const char*)&retScore.iIndexed, sizeof(uint16_t));
      cout.write((const char*)&retScore.iPredicted, sizeof(uint16_t));
      
      cout.write((const char*)&ret[i], sizeof(uint64_t));
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

      cout << retScore.line << endl;
    }

    cerr << ret.size() << " entries have been listed (took " << float(timeElapsed)/1000.0 << " sec)." << endl;
  }
 
  delete[] pQuery;
  
  return 0;
  
}

