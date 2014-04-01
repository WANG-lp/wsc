
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

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  probHashiInstances -k <PATH TO KNOWLEDGE BASE>"
                  " -i <INPUT EVENT PAIRS>"
                  " -v <INPUT VOCAB OF EVENT PAIRS>"
                  " -c <INPUT VOCAB OF CONTEXT TYPES>"
                  " -o <OUTPUT BIN>"
                  " -m <PARALLELS>"
                  " [-h <HASH TYPE:p|pc|pcjoin|pp|ppcc>]"
                  " [-p]"
                  ,
                  "k:v:c:i:o:m:h:p", "kivomc", argc, argv);
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

  // READ THE VOCAB.
  cerr << "Loading vocab..." << endl;
  corefevents_t::vocab_t vocab; 
  corefevents_t::vocabct_t vocabCT;
  corefevents_t::readVocab(&vocab, opts.of('v'));
  corefevents_t::readVocab(&vocabCT, opts.of('c'));
  
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
  size_t                                    ompResultCnt;
  
  do {
    uint32_t ip1, ip2, ia1, ia2;
    char     sentdist, numC1, numC2;
    char     rawc1[1024], rawc2[1024];
    
    ifsInstances.read((char*)&ip1, sizeof(uint32_t));
    ifsInstances.read((char*)&ip2, sizeof(uint32_t));
    ifsInstances.read((char*)&ia1, sizeof(uint32_t));
    ifsInstances.read((char*)&ia2, sizeof(uint32_t));
    ifsInstances.read((char*)&sentdist, sizeof(char));
    ifsInstances.read((char*)&numC1, sizeof(char));
    ifsInstances.read((char*)rawc1, sizeof(char)*numC1*(2+4));
    ifsInstances.read((char*)&numC2, sizeof(char));
    ifsInstances.read((char*)rawc2, sizeof(char)*numC2*(2+4));

    line = vocab[ip1] + "\t" + vocab[ip2] + "\t" + vocab[ia1] + "," + vocab[ia2] + "\t" + sentdist + "\t";
    corefevents_t::addContext(&line, rawc1, numC1*(2+4), vocab, vocabCT);
    line += "\t";
    corefevents_t::addContext(&line, rawc2, numC2*(2+4), vocab, vocabCT);

    if(0 == numProcessed % 10000000) {
      time_t timer; time(&timer);
      cerr << string(ctime(&timer)).substr(0, string(ctime(&timer)).length()-1) << " ";
    }

    numProcessed++;
    poolLines.push_back(make_pair(bytesProcessed, line));
    bytesProcessed += sizeof(uint32_t)*4 + sizeof(char)*3 + sizeof(char)*(numC1+numC2)*(2+4);
    
    if(0 == numProcessed % 500000) cerr << ".";
    if(0 == numProcessed % 10000000 || ifsInstances.eof()) {
      cerr << " " << (numProcessed) << " " << flush;

      int nThreads = atoi(opts.of('m').c_str());

      ompResultCnt = 0;
  
#pragma omp parallel for shared(gw2v, ofsOut, ompResult, ompResultCnt, numWritten, pLsh) num_threads(nThreads)
      for(size_t data=0; data<poolLines.size(); data++) {
        istringstream ssLine(poolLines[data].second);
        string        p1, p2, arg, sentdist, c1, c2;
        getline(ssLine, p1, '\t'); getline(ssLine, p2, '\t');
        getline(ssLine, arg, '\t');
        getline(ssLine, sentdist, '\t');
        getline(ssLine, c1, '\t'); getline(ssLine, c2, '\t');

        // CONSTRUCT THE VECTOR OF INSTANCE.        
        if("pc" == opts.of('h')) {
          // float vecHash[google_word2vec_t::DIMENSION];
          // lsh_t::entry128b_t hashValue;
          
          // initVector(vecHash, google_word2vec_t::DIMENSION);
          // addWordVector(vecHash, p1.substr(0, p1.find(":")-2), gw2v);
          // addContextVector(vecHash, c1, gw2v);
          // writeHash(&ofsOut, &hashValue, &numWritten, vecHash, poolLines[data].first, poolLines[data].second.length(), *pLsh);

          // initVector(vecHash, google_word2vec_t::DIMENSION);
          // addWordVector(vecHash, p2.substr(0, p2.find(":")-2), gw2v);
          // addContextVector(vecHash, c2, gw2v);
          // writeHash(&ofsOut, &hashValue, &numWritten, vecHash, poolLines[data].first, poolLines[data].second.length(), *pLsh);

        } else if("pceach" == opts.of('h')) {
          float vecHash[google_word2vec_t::DIMENSION];
          size_t cnt;
          
          for(int i=0;i<2;i++) {
            string        &c = 0 == i ? c1 : c2, &p = 0 == i ? p1 : p2;
            istringstream  ssContext(c);
            string         element;

            // INDEX BY PREDICATE.
            initVector(vecHash, google_word2vec_t::DIMENSION);
            addWordVector(vecHash, p.substr(0, p.find(":")-2), gw2v);
            cnt = writeHash(ompResult, &ompResultCnt, &numWritten, vecHash, poolLines[data].first, poolLines[data].second.length(), *pLsh);

            if(opts.hasKey('p') && 0 != cnt)
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
                writeHash(ompResult, &ompResultCnt, &numWritten, vecHash, poolLines[data].first, poolLines[data].second.length(), *pLsh);
              }
            }
          }
          
        } else
          cerr << "Not supported hash type: " << opts.of('h') << endl;
            
      }

      cerr << "Aggregating..." << " " << flush;

      for(int i=0; i<(int)ompResultCnt; i++)
        hashTable[ompResult[i].hv1][ompResult[i].hv2].push_back(ompResult[i].offset);
        
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

