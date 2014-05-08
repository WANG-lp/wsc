
#include <tr1/unordered_set>
#include <tr1/unordered_map>

#include <sstream>
#include <vector>

#include <math.h>

using namespace std;

static inline float _weight(const string &k) {
  /* if(string::npos != k.find("dobj")  || string::npos != k.find("iobj") || */
  /*    string::npos != k.find("nsubj") || string::npos != k.find("prep_") || */
  /*    string::npos != k.find("acomp")) return 1.0; */
  if(string::npos != k.find("dobj")  || string::npos != k.find("iobj") ||
     string::npos != k.find("nsubj") || string::npos != k.find("advcl")) return 1.0;
  return 0.2;
}

static inline float calcWordSimilarity(const string &w1, const string &w2, const google_word2vec_t &gw2v) {
  if(w1 == w2) return 1.0; // WELL, IT'S OBVIOUS.
  
  const float *pWordVec1, *pWordVec2;
  float dot = 0, vLen1 = 0, vLen2 = 0;
  
  if(gw2v.getWordVector(&pWordVec1, w1) && gw2v.getWordVector(&pWordVec2, w2))
    for(int i=0; i<google_word2vec_t::DIMENSION; i++) {
      dot   += pWordVec1[i] * pWordVec2[i];
      vLen1 += pWordVec1[i] * pWordVec1[i];
      vLen2 += pWordVec2[i] * pWordVec2[i];
    }

  vLen1 = sqrt(vLen1); vLen2 = sqrt(vLen2);
  vLen1 *= vLen2;
    
  return 0.0 == vLen1 ? 0.0 : 0.5*(1+(dot/vLen1));
}

static inline float calcContextualSimilarity(const string &c1, const string &c2, const google_word2vec_t &gw2v) {
  
  istringstream ssContext1(c1), ssContext2(c2);
  string        element;
  unordered_set<string> keys;
  unordered_map<string, vector<string> > c1e, c2e;
  
  while(ssContext1 >> element) {
    c1e[element.substr(0, element.find(":", 2))].push_back(element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1));
    keys.insert(element.substr(0, element.find(":", 2)));
  }
  
  while(ssContext2 >> element) {
    c2e[element.substr(0, element.find(":", 2))].push_back(element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1));
    keys.insert(element.substr(0, element.find(":", 2)));
  }

  float dot = 0, numContext = 0;
  
  for(unordered_set<string>::iterator iter_k=keys.begin(); keys.end()!=iter_k; ++iter_k) {
    float eMax = -9999.0;
    
    for(int i=0; i<c1e[*iter_k].size(); i++) {
      for(int j=0; j<c2e[*iter_k].size(); j++) {
        eMax = max(eMax, calcWordSimilarity(c1e[*iter_k][i], c2e[*iter_k][j], gw2v));
      } }

    if(-9999 != eMax)
      dot += _weight(*iter_k) * eMax;

    numContext++;
  }

  return (1.0+(0.0 == numContext ? 0.0 : dot / numContext));
}

static inline float calcSlotSimilarity(const string &s1, const string &s2) {
  if(s1 == s2) return 1.0;
  return 0.1;
}

static inline void initVector(float *pOutInVector, int nDim) {
  for(int i=0; i<nDim; i++) pOutInVector[i] = 0.0;  
}

static inline void addWordVector(float *pOut, const string &p, const google_word2vec_t &gw2v) {
  const float *pWordVec;
  
  if(gw2v.getWordVector(&pWordVec, p))
    for(int i=0; i<google_word2vec_t::DIMENSION; i++) pOut[i] += pWordVec[i];
}

static inline void addContextVector(float *pOut, const string &c, const google_word2vec_t &gw2v) {
  istringstream ssContext(c);
  string        element;

  while(ssContext >> element) {
    if(string::npos != element.find("dobj")  || string::npos != element.find("iobj") ||
       string::npos != element.find("nsubj") || string::npos != element.find("prep_") ||
       string::npos != element.find("acomp")
       ) {

      // cerr << "addContextVector(): added: " << element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1) << " in " << element << endl;
      
      addWordVector(pOut, element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1), gw2v);
    }
  }
}

static inline void extractContextWords(vector<string> *pOut, const string &c) {
  istringstream ssContext(c);
  string        element;

  while(ssContext >> element) {
    if(string::npos != element.find("dobj")  || string::npos != element.find("iobj") ||
       string::npos != element.find("nsubj") || string::npos != element.find("prep_") ||
       string::npos != element.find("acomp")
       ) {

      // cerr << "addContextVector(): added: " << element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1) << " in " << element << endl;
      pOut->push_back(element.substr(element.find(":", 2)+1, element.find("-")-element.find(":", 2)-1));
    }
  }
}

