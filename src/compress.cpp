
#include <ctime>

#include "stdint.h"

#include <fstream>
#include <sstream>
#include <iostream>

#include <tr1/unordered_map>

using namespace std;
using namespace tr1;

static uint16_t g_newIdCT = 0;
static uint32_t g_newId = 0;

static inline uint32_t getId(unordered_map<string, uint32_t> *pDict, ofstream &ofsOutVocab, uint32_t *pNewId, const string &k) {
  unordered_map<string, uint32_t>::const_iterator i = pDict->find(k);

  if(pDict->end() == i) {
    ofsOutVocab << k << "\t";
    ofsOutVocab.write((const char*)pNewId, sizeof(uint32_t));
    (*pDict)[k] = (*pNewId)++;
  }

  return (*pDict)[k];
}

static inline uint16_t getId(unordered_map<string, uint16_t> *pDict, ofstream &ofsOutVocab, uint16_t *pNewId, const string &k) {
  unordered_map<string, uint16_t>::const_iterator i = pDict->find(k);

  if(pDict->end() == i) {
    ofsOutVocab << k << "\t";
    ofsOutVocab.write((const char*)pNewId, sizeof(uint16_t));
    (*pDict)[k] = (*pNewId)++;
  }

  return (*pDict)[k];
}

static inline void writeContext(ofstream &ofsOut, ofstream &ofsOutVocab, ofstream &ofsOutVocabCT, const string &c, unordered_map<string, uint32_t> *pVocab, unordered_map<string, uint16_t> *pVocabCT) {
  istringstream ssContext(c), ssContextForCnt(c);
  string        element;

#ifdef UNITTEST
  cerr << c << endl;
#endif

  char numElements = 0;
  
  while(ssContextForCnt >> element) numElements++;

  ofsOut.write((const char*)&numElements, sizeof(char));

  while(ssContext >> element) {
    string type = element.substr(0, element.find(":", 2)), value = element.substr(element.find(":", 2)+1);
    
#ifdef UNITTEST
    cerr << type << "\t" << value << endl;
#endif

    uint16_t idCT = getId(pVocabCT, ofsOutVocabCT, &g_newIdCT, type);
    uint32_t id   = getId(pVocab, ofsOutVocab, &g_newId, value);

    ofsOut.write((const char*)&idCT, sizeof(uint16_t));
    ofsOut.write((const char*)&id, sizeof(uint32_t));
  }
}

int main(int argc, char **argv) {
  string                          line;
  ofstream                        ofsOut(argv[1], ios::out), ofsVocab(argv[2], ios::out), ofsVocabCT(argv[3], ios::out);
  unordered_map<string, uint32_t> vocab;
  unordered_map<string, uint16_t> vocabContextType;
  uint64_t                        numProcessed = 0;
  
  while(getline(cin, line)) {
    if(0 == numProcessed % 10000000) {
      time_t timer; time(&timer);
      cerr << string(ctime(&timer)).substr(0, string(ctime(&timer)).length()-1) << " ";
    }
    
    numProcessed++;
    
    if(0 == numProcessed % 500000) cerr << ".";
    if(0 == numProcessed % 10000000 || cin.eof()) {
      cerr << " " << (numProcessed) << endl;
    }
    
    string p1, p2, a1, a2, sentdist, c1, c2;
    istringstream ss(line);
    
    getline(ss, p1, '\t'); getline(ss, p2, '\t');
    getline(ss, a1, ',');  getline(ss, a2, '\t');
    getline(ss, sentdist, '\t');
    getline(ss, c1, '\t'); getline(ss, c2, '\t');

    uint32_t
      idP1 = getId(&vocab, ofsVocab, &g_newId, p1),
      idP2 = getId(&vocab, ofsVocab, &g_newId, p2),
      idA1 = getId(&vocab, ofsVocab, &g_newId, a1),
      idA2 = getId(&vocab, ofsVocab, &g_newId, a2);
    
    ofsOut.write((const char*)&idP1, sizeof(uint32_t));
    ofsOut.write((const char*)&idP2, sizeof(uint32_t));
    ofsOut.write((const char*)&idA1, sizeof(uint32_t));
    ofsOut.write((const char*)&idA2, sizeof(uint32_t));
    ofsOut.write((const char*)&(sentdist.c_str()[0]), sizeof(char));
    writeContext(ofsOut, ofsVocab, ofsVocabCT, c1, &vocab, &vocabContextType);
    writeContext(ofsOut, ofsVocab, ofsVocabCT, c2, &vocab, &vocabContextType);
  }

  ofsOut.close();
  ofsVocab.close();
  ofsVocabCT.close();
}
