
#include <stdint.h>
#include <stdlib.h>
#include <math.h>

#include <string>
#include <vector>
#include <smmintrin.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <fcntl.h>

#include <tr1/unordered_map>

using namespace std;
using namespace tr1;

// PORTED FROM: Naoaki Okazaki
static inline int _getHammingDistance(const uint64_t x64, const uint64_t y64) {
  return _mm_popcnt_u64(x64 ^ y64);
}

static inline uint64_t _binstr2uint64(const string &binstr, int start = 0) {
  uint64_t ret = 0;
  for(int i=start; i<start+64; i++)
    if('1' == binstr[i]) ret += (2^i);
  return ret;
}

// PORTED FROM: http://c-faq.com/lib/gaussian.html
static inline double gaussrand() {
  static double V1, V2, S;
  static int phase = 0;
  double X;

  if(phase == 0) {
    do {
      double U1 = (double)rand() / RAND_MAX;
      double U2 = (double)rand() / RAND_MAX;

      V1 = 2 * U1 - 1;
      V2 = 2 * U2 - 1;
      S = V1 * V1 + V2 * V2;
    } while(S >= 1 || S == 0);

    X = V1 * sqrt(-2 * log(S) / S);
  } else
    X = V2 * sqrt(-2 * log(S) / S);

  phase = 1 - phase;

  return X;
}

class lsh_t {
public:
  struct entry128b_t {
    uint64_t hv1, hv2;
    uint64_t offset;

    inline int getHammingDistance(uint64_t hvQ1, uint64_t hvQ2) {
      return _getHammingDistance(this->hv1, hvQ1) +
        _getHammingDistance(this->hv2, hvQ2);
    }

    entry128b_t() : hv1(0), hv2(0), offset(0) {}
    entry128b_t(uint64_t _hv1, uint64_t _hv2, uint64_t _offset) : hv1(_hv1), hv2(_hv2), offset(_offset) {}
  };

private:  
  vector<vector<float> > m_randomHyperplanes;

  int    m_nBits, m_nDim;
  size_t m_numKeys;
  string m_typeHash;
  
  unordered_map<uint64_t, unordered_map<uint64_t, vector<uint64_t> > > *m_pHashTable;
  size_t       m_offsetData;

  struct stat m_fStatData;
  int         m_fdData;
  bool        m_fLoaded;
  
public:
  static const int MAX_POOL_SEARCH_RESULT = 1000000;

 lsh_t(int nBits = 32, bool fUseMemoryMap = false, int nDim = 300) : m_pHashTable(NULL), m_nBits(nBits), m_nDim(nDim), m_fdData(-1), m_fLoaded(false) {
    
    // GENERATE THE RANDOM HYPER PLANES.
    srand(1);
    
    for(int i=0; i<m_nBits; i++) {
      m_randomHyperplanes.push_back(vector<float>());
      
      for(int j=0; j<m_nDim; j++) m_randomHyperplanes[i].push_back(gaussrand());
    }
  }

  lsh_t(const string &fnBin, bool fUseMemoryMap = false) : m_pHashTable(NULL), m_fdData(-1) {
    ifstream ifsBin(fnBin.c_str(), ios::in|ios::binary);
    char     typeHash[8];
    
    ifsBin.read((char*)&m_nBits, sizeof(int));
    ifsBin.read((char*)&m_nDim, sizeof(int));
    ifsBin.read((char*)typeHash, sizeof(char)*8);    m_typeHash = string(typeHash);
    ifsBin.read((char*)&m_numKeys, sizeof(size_t));

    // LOAD THE RANDOMIZED HYPER PLANE.
    cerr << "Loading hyper-planes..." << endl;
    
    for(int i=0; i<m_nBits; i++) {
      m_randomHyperplanes.push_back(vector<float>());
      
      for(int j=0; j<m_nDim; j++) {
        float e;
        ifsBin.read((char*)&e, sizeof(float));

        m_randomHyperplanes[i].push_back(e);
      }
    }

    // LOAD HASH VALUE AND OFFSETS.
    cerr << "Loading hash table..." << endl;

    if(!fUseMemoryMap) {
      m_pHashTable = new unordered_map<uint64_t, unordered_map<uint64_t, vector<uint64_t> > >[m_numKeys];
      
      for(int i=0; i<m_numKeys; i++) {
        uint64_t hv1, hv2;
        ifsBin.read((char*)&hv1, sizeof(uint64_t));
        ifsBin.read((char*)&hv2, sizeof(uint64_t));

        uint32_t numOffsets;
        ifsBin.read((char*)&numOffsets, sizeof(uint32_t));

        char *buffer = new char[sizeof(uint64_t)*numOffsets];
        ifsBin.read(buffer, sizeof(uint64_t)*numOffsets);
        
        for(int j=0; j<numOffsets; j++)
          (*m_pHashTable)[hv1][hv2].push_back(*((uint64_t*)&buffer[j*sizeof(uint64_t)]));

        delete[] buffer;
      }

      cerr << m_numKeys << " entries have been loaded." << endl;
      cerr << "Hash type: " << m_typeHash << endl;
      cerr << "Bits: " << m_nBits << endl;
      cerr << "Dimension: " << m_nDim << endl;
    
      ifsBin.close();
    
      cerr << "Done!" << endl;
    }

    m_fLoaded = true;
  }

  ~lsh_t() {
    if(NULL != m_pHashTable) delete[] m_pHashTable;
  }

  inline bool isLoaded() const { return m_fLoaded; }
  inline int getBits() const { return m_nBits; }
  inline int getDim() const { return m_nDim; }
  inline const string &getHashType() const { return m_typeHash; }
  inline vector<float> &getRandomHyperPlane(int bit) { return m_randomHyperplanes[bit]; }
  
  inline void hashing(entry128b_t *pOut, const float *pVector) const {
    pOut->hv1 = 0; pOut->hv2 = 0;
    
    for(int i=0; i<m_nBits; i++) {
      // CALCULATE THE DOT PRODUCT
      float dot = 0.0;
      
      for(int j=0; j<m_nDim; j++)
        dot += pVector[j] * m_randomHyperplanes[i][j];

      if(dot >= 0.0) {
        if(i < 64) pOut->hv1 += (2^i);
        else       pOut->hv2 += (2^i);
      }
    }
  }

  inline void search(vector<uint64_t> *pOut, const float *pVector, int threshold, int nThreads) const {
    entry128b_t e;
    hashing(&e, pVector);

    // LINEAR SEARCH.
    for(unordered_map<uint64_t, unordered_map<uint64_t, vector<uint64_t> > >::iterator
          i=m_pHashTable->begin(); m_pHashTable->end()!=i; ++i) {
      for(unordered_map<uint64_t, vector<uint64_t> >::iterator
            j=i->second.begin(); i->second.end()!=j; ++j) {
        int d =
          _getHammingDistance(i->first, e.hv1) +
          _getHammingDistance(j->first, e.hv2);

        if(d <= threshold) {
          for(size_t k=0; k<j->second.size(); k++)
            pOut->push_back(j->second[k]);
        }
      } }
  }
};
