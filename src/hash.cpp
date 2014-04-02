
#include <omp.h>

#include <ctime>

#include <iostream>
#include <fstream>
#include <sstream>

#include <list>

#include "google-word2vec.h"
#include "lsh.h"
#include "optparse.h"
#include "vectorize.h"
#include "corefevents.h"

using namespace std;

#define ARGV_EXTKB   argv[1]
#define ARGV_IN      argv[2]
#define ARGV_OUT     argv[3]
#define ARGV_NUMPARA argv[4]

static size_t writeHash(lsh_t::entry128b_t *pOut, size_t *pOutCnt, size_t *pNumWritten, const float *pVecHash, size_t offset, uint16_t length, const lsh_t &lsh) {
  if(0.0 == pVecHash[0]) return 0;

  size_t cnt;
  
#pragma omp critical
  {
    cnt = *pOutCnt;
    (*pOutCnt)++;
    (*pNumWritten)++;
  }
  
  lsh.hashing(&pOut[cnt], pVecHash);
  pOut[cnt].offset = offset;

  return cnt;
}

static void process(unordered_map<uint64_t, unordered_map<uint64_t, vector<size_t> > > *pOut, lsh_t::entry128b_t *ompResult, uint64_t *pNumWritten, const vector<pair<size_t, string> > &poolLines, const google_word2vec_t& gw2v, lsh_t *pLsh, int nThreads, bool fPrint) {
  uint64_t ompResultCnt = 0;
  
#pragma omp parallel for shared(gw2v, pOut, ompResultCnt, pNumWritten, pLsh) num_threads(nThreads)
  for(size_t data=0; data<poolLines.size(); data++) {
    istringstream ssLine(poolLines[data].second);
    string        p1, p2, arg, sentdist, c1, c2;
    getline(ssLine, p1, '\t'); getline(ssLine, p2, '\t');
    getline(ssLine, arg, '\t');
    getline(ssLine, sentdist, '\t');
    getline(ssLine, c1, '\t'); getline(ssLine, c2, '\t');

    // CONSTRUCT THE VECTOR OF INSTANCE.        
    float vecHash[google_word2vec_t::DIMENSION];
    size_t cnt;
          
    for(int i=0;i<2;i++) {
      string        &c = 0 == i ? c1 : c2, &p = 0 == i ? p1 : p2;
      istringstream  ssContext(c);
      string         element;

      // INDEX BY PREDICATE.
      initVector(vecHash, google_word2vec_t::DIMENSION);
      addWordVector(vecHash, p.substr(0, p.find(":")-2), gw2v);
      cnt = writeHash(ompResult, &ompResultCnt, pNumWritten, vecHash, poolLines[data].first, poolLines[data].second.length(), *pLsh);

      if(fPrint && 0 != cnt)
        cerr << poolLines[data].second << endl
             << "  hash("<< p <<") = " << ompResult[cnt].hv1 << "," << ompResult[cnt].hv2 << endl;
            
      // INDEX BY CONTEXT.
      while(ssContext >> element) {
        if(string::npos != element.find("dobj")  || string::npos != element.find("iobj") ||
           string::npos != element.find("nsubj") || string::npos != element.find("prep_") ||
           string::npos != element.find("acomp")
           ) {
          initVector(vecHash, google_word2vec_t::DIMENSION);
          addWordVector(vecHash, element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1), gw2v);
          writeHash(ompResult, &ompResultCnt, pNumWritten, vecHash, poolLines[data].first, poolLines[data].second.length(), *pLsh);
        }
      }
    }
  }

  cerr << "Aggregating..." << " " << flush;

  for(int i=0; i<(int)ompResultCnt; i++)
    (*pOut)[ompResult[i].hv1][ompResult[i].hv2].push_back(ompResult[i].offset);
  
}

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  hash"
                  " -k <PATH TO KNOWLEDGE BASE>"
                  " -i <INPUT EVENT PAIRS>"
                  " -o <OUTPUT BIN>"
                  " -m <PARALLELS>"
                  " [-h <HASH TYPE:p|pc|pcjoin|pp|ppcc>]"
                  " [-p]"
                  ,
                  "k:i:o:m:h:p", "kiom", argc, argv);
  if(!opts.isGood()) return 0;

  opts.defset('h', "pc");
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.bin");

  ofstream ofsOut(opts.of('o').c_str(), ios::out|ios::binary);
  
  string   line(0, 1024*1024);
  size_t   bytesProcessed = 0, numProcessed = 0, numWritten = 0;
  ifstream ifsInstances(opts.of('i').c_str(), ios::in);
  char     typeHash[8]; strcpy(typeHash, opts.of('h').c_str());
  
  vector<pair<size_t, string> > poolLines;

  lsh_t  lsh300(128, false, google_word2vec_t::DIMENSION), lsh600(128, false, google_word2vec_t::DIMENSION*2);
  lsh_t *pLsh = &lsh300;

  if("pcjoin" == opts.of('h') || "pceachjoin" == opts.of('h')) pLsh = &lsh600;

  // WRITE THE BASIC INFO AND RANDOM HYPER PLANES.
  int nBits = pLsh->getBits(), nDim = pLsh->getDim();
  ofsOut.write((const char*)&nBits, sizeof(int));
  ofsOut.write((const char*)&nDim, sizeof(int));
  ofsOut.write((const char*)typeHash, sizeof(char)*8);
  ofsOut.write((const char*)&numWritten, sizeof(size_t)); // STILL IT IS DUMMY.

  for(int i=0; i<pLsh->getBits(); i++) {
    for(int j=0; j<pLsh->getDim(); j++) {
      ofsOut.write((const char*)&(pLsh->getRandomHyperPlane(i)[j]), sizeof(float));
    }
  }

  unordered_map<uint64_t, unordered_map<uint64_t, vector<size_t> > > hashTable;
  lsh_t::entry128b_t                        *ompResult = new lsh_t::entry128b_t[10000000*10];
  
  do {
    string line;
    getline(ifsInstances, line);

    if(0 == numProcessed % 10000000) {
      time_t timer; time(&timer);
      cerr << string(ctime(&timer)).substr(0, string(ctime(&timer)).length()-1) << " ";
    }

    numProcessed++;
    poolLines.push_back(make_pair(bytesProcessed, line));
    bytesProcessed += line.length()+1;
    
    if(0 == numProcessed % 500000) cerr << ".";
    if(0 == numProcessed % 10000000 || ifsInstances.eof()) {
      cerr << " " << (numProcessed) << " " << flush;
      process(&hashTable, ompResult, &numWritten, poolLines, gw2v, pLsh, atoi(opts.of('m').c_str()), opts.hasKey('p'));
      cerr << numWritten << endl;
      poolLines.clear();
    }
  } while(!ifsInstances.eof());
  
  delete[] ompResult;
  
  cerr << "Writing..." << endl;

  // WRITE THE HASH TABLE.
  size_t numKeys = 0;
  
  for(unordered_map<uint64_t, unordered_map<uint64_t, vector<size_t> > >::iterator
        i=hashTable.begin(); hashTable.end()!=i; ++i) {
    for(unordered_map<uint64_t, vector<size_t> >::iterator
          j=i->second.begin(); i->second.end()!=j; ++j) {
      
      // WRITE THE HASH KEY.
      numKeys++;
      ofsOut.write((const char*)&i->first, sizeof(uint64_t));
      ofsOut.write((const char*)&j->first, sizeof(uint64_t));

      uint32_t numOffsets = j->second.size();
      ofsOut.write((const char*)&numOffsets, sizeof(uint32_t));

      // WRITE THE LIST OF OFFSETS.
      for(int k=0; k<(int)j->second.size(); k++) {
        ofsOut.write((const char*)&j->second[k], sizeof(size_t));
      }
    } }

  // REWRITE THE SIZE.
  ofsOut.seekp(sizeof(int) + sizeof(int) + sizeof(char)*8);
  ofsOut.write((const char*)&numKeys, sizeof(size_t));
  
  ofsOut.close();
  
  return 0;
  
}   

