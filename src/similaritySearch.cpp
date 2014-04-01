
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
  optparse_t opts("Usage:\n  similaritySearch -k <PATH TO KNOWLEDGE BASE>"
                  " -i <INPUT DATABASE BIN>"
                  " -m <PARALLELS>"
                  " -c <COREF EVENTS TSV>"
                  " -v <VOCAB OF COREF EVENT PAIRS>"
                  " -t <VOCAB OF CONTEXT TYPES>"
                  " [-d]"
                  ,
                  "k:i:m:dc:v:t:", "kimcvt", argc, argv);
  if(!opts.isGood()) return 0;
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.bin",
                         opts.hasKey('d'));
  lsh_t          lsh(opts.of('i'), opts.hasKey('d'));
  string         line;
  int            th     = 0;
  float         *pQuery = new float[lsh.getDim()];
  
  corefevents_t                libce(opts.of('c'), opts.of('v'), opts.of('t'));
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
    
    if("" != line) continue;
    
    if("pceach" != lsh.getHashType()) {
      cerr << "SORRY..." << endl;
      continue;
    } else {
      cerr << "Idk the hash type: " << lsh.getHashType() << endl;
    }
    
    unordered_map<size_t, int> commonOffsets;
    vector<string> keys;

    // PREPARE THE KEYS.
    keys.push_back(prpIndexed.predicate);
    extractContextWords(&keys, prpIndexed.context);
    
    timeval t1, t2;
    gettimeofday(&t1, NULL);
    
    for(int i=0; i<(int)keys.size(); i++) {
      vector<size_t> ret;
      
      cerr << "Searching..." << endl;
    
      initVector(pQuery, lsh.getDim());
      addWordVector(pQuery, keys[i], gw2v);

      lsh.search(&ret, pQuery, th, atoi(opts.of('m').c_str()));

      cerr << "Cool." << endl;

      unordered_map<size_t, bool> localCommonOffsets;
      for(int j=0; j<(int)ret.size(); j++) {
        if(0 != i && 0 == commonOffsets.count(ret[j])) continue;
        
        localCommonOffsets[ret[j]] = true;
      }

      for(unordered_map<size_t, bool>::iterator j=localCommonOffsets.begin(); localCommonOffsets.end()!=j; ++j)
        commonOffsets[j->first]++;
    }
    
    gettimeofday(&t2, NULL);

    int timeElapsed = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;
    vector<size_t> ret;
    
    for(unordered_map<size_t, int>::iterator i=commonOffsets.begin(); commonOffsets.end()!=i; ++i) {
      if((int)keys.size() > i->second) continue;
      ret.push_back(i->first);
    }

    std::srand(0);
    std::random_shuffle(ret.begin(), ret.end(), myrandom);

    if(ret.size() > 1000) {
      ret.resize(1000);
      cerr << "Truncated." << endl;
    }
      
    cerr << "Done!" << endl;
    cerr << ret.size() << " entries have been found. (took " << float(timeElapsed)/1000.0 << " sec)." << endl;

    cout << ret.size() << endl;
    
    // IDENTIFY THE COMMON IDS.
    for(int i=0; i<(int)ret.size(); i++) {
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

