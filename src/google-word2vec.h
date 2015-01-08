
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include <fstream>
#include <string>
#include <vector>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <fcntl.h>

#include <tr1/unordered_map>

#include "cdb.h"

using namespace std;
using namespace tr1;

struct _google_word2vec_kbest_sort_pred {
  bool operator()(const std::pair<int,float> &left, const std::pair<int,float> &right) {
    return left.second > right.second;
  }
};

class google_word2vec_t {
public:
  typedef unordered_map<string, pair<uint64_t, uint16_t> > dict_t;
  typedef vector<pair<int, float> > kbest_t;
  typedef vector<string>            vocab_t;

private:
  struct stat m_fStatW2VDB;
  int         m_fdW2VDB;

  struct cdb  m_cdbW2VIndex;
  int         m_fdW2VIndex;

  char   *m_pW2VDB;
  dict_t  m_dict;

  unordered_set<string> m_posfilter;
  unordered_map<string, string> m_posmap;

public:
  static const size_t FILE_SIZE = 3644258522;
  static const int DIMENSION = 300;

  google_word2vec_t(const string &fnBin, const string &fnIndex, bool fUseMemoryMap = false) :
    m_pW2VDB(NULL), m_fdW2VDB(-1), m_fdW2VIndex(-1) {
    //
    // LOAD THE INDEX.
    cerr << "Loading " << fnIndex << "..." << endl;

    if(fnIndex.substr(fnIndex.length()-3) == "cdb") {
      m_fdW2VIndex = open(fnIndex.c_str(), O_RDONLY);
      cerr << "cdb_init(): " << cdb_init(&m_cdbW2VIndex, m_fdW2VIndex) << endl;

    } else {
      ifstream ifsIndex(fnIndex.c_str(), ios::in|ios::binary);
      string   entry;

      while(getline(ifsIndex, entry, '\t')) {
        uint64_t offset; uint16_t size;
        ifsIndex.read((char*)&offset, sizeof(uint64_t));
        ifsIndex.read((char*)&size, sizeof(uint16_t));

        m_dict[entry] = make_pair(offset, size);
      }

      ifsIndex.close();

    }

    //
    // LOAD THE BINARY VECTORS.
    cerr << "Loading " << fnBin << "..." << endl;

    if(!fUseMemoryMap) {
      ifstream ifsBin(fnBin.c_str(), ios::binary|ios::in);

      try {
        m_pW2VDB = new char[FILE_SIZE];
        ifsBin.read(m_pW2VDB, FILE_SIZE);
        ifsBin.close();
      } catch (const std::bad_alloc&) {
        cerr << "Allocation failed. mmap is going to be used." << endl;
        ifsBin.close();

        m_fdW2VDB = open(fnBin.c_str(), O_RDONLY);
        fstat(m_fdW2VDB, &m_fStatW2VDB);
        m_pW2VDB = (char*)mmap(0, m_fStatW2VDB.st_size, PROT_READ, MAP_SHARED, m_fdW2VDB, 0);

      }

    } else {
      m_fdW2VDB = open(fnBin.c_str(), O_RDONLY);
      fstat(m_fdW2VDB, &m_fStatW2VDB);
      m_pW2VDB = (char*)mmap(0, m_fStatW2VDB.st_size, PROT_READ, MAP_SHARED, m_fdW2VDB, 0);

      cerr << "Mapped to memory." << endl;
    }

    cerr << "Done!" << endl;
  }

  ~google_word2vec_t() {
    if(-1 != m_fdW2VDB) {
      munmap(m_pW2VDB, m_fStatW2VDB.st_size);
      close(m_fdW2VDB);
    } else {
      if(NULL != m_pW2VDB)  delete[] m_pW2VDB;
    }

    if(-1 != m_fdW2VIndex)
      close(m_fdW2VIndex);
  }

  inline bool getOffset(uint64_t *pOutOffset, const string &word) {
    if(-1 != m_fdW2VIndex) {
      int ret_cdb_find = -1;

#pragma omp critical
      {
        ret_cdb_find = cdb_find(&m_cdbW2VIndex, word.c_str(), word.length());
      }
      
      if(0 >= ret_cdb_find) return false;

#pragma omp critical
      {
        uint   pos = cdb_datapos(&m_cdbW2VIndex);
        size_t len = cdb_datalen(&m_cdbW2VIndex);

        string tsv;
        char buffer[1024];
        cdb_read(&m_cdbW2VIndex, buffer, len, pos);
        buffer[len] = 0;
        
        tsv = string(buffer);

        *pOutOffset = strtoul(tsv.substr(0, tsv.find("\t")).c_str(), NULL, 10);
      }
      
    } else {
      dict_t::const_iterator iterEntry = m_dict.find(word);
      if(m_dict.end() == iterEntry)
        return false;
      
      *pOutOffset = iterEntry->second.first;
    }

    return true;
  }
  
  inline bool getWordVector(float *pOut, const string &word) {    
    uint64_t offset;
    if(!this->getOffset(&offset, word)) return false;
    
    memcpy(pOut, m_pW2VDB+offset+word.length()+1, sizeof(float)*DIMENSION);
        
    return true;
  }

  inline bool getWordVector(const float **pOut, const string &word) {
    uint64_t offset;
    if(!this->getOffset(&offset, word)) return false;

    *pOut = (const float*)(m_pW2VDB+offset+word.length()+1);

    return true;
  }

  inline void clearSimilaritySearchFilter() {
    m_posfilter.clear();
  }
  
  inline void addSimilaritySearchFilter(const string &pos) {
    m_posfilter.insert(pos);
  }
  
  void getSimilarEntiries(kbest_t *pOut, const string &word, const vector<string> &vocab, uint K = 10, uint numCpus = 8) {
    float vecInput[google_word2vec_t::DIMENSION];
    if(!this->getWordVector(vecInput, word))
      cerr << "No vector found: " << word << endl;
  
#pragma omp parallel for shared(pOut) num_threads(numCpus)
    for(uint i=0; i<vocab.size(); i++) {
      if(0 != m_posfilter.size()) {
        if(0 == m_posfilter.count(this->getPOS(vocab[i]))) continue;
      }
      
      float vec[google_word2vec_t::DIMENSION];
      float dot = 0, len1 = 0, len2 = 0;
      this->getWordVector(vec, vocab[i]);

      for(uint j=0; j<google_word2vec_t::DIMENSION; j++) {
        dot += vecInput[j] * vec[j];
        len1 += vecInput[j] * vecInput[j];
        len2 += vec[j] * vec[j];
      }

      len1 = sqrt(len1);
      len2 = sqrt(len2);

#pragma omp critical
      pOut->push_back(make_pair(i, dot/(len1*len2)));
    }

    sort(pOut->begin(), pOut->end(), _google_word2vec_kbest_sort_pred());
    pOut->resize(K);
  }

  void readVocab(vocab_t *pOut, const string &fnVocab, const string &fnWNFilter = "") {
    if("" != fnWNFilter) {
      ifstream ifsWNpreds(fnWNFilter.c_str());
      string word, pos;
  
      while(ifsWNpreds >> word >> pos)
        m_posmap[word] = pos;
    }

    ifstream ifsVocab(fnVocab.c_str());
    string   word;
    
    while(ifsVocab >> word)
      if(0 == m_posmap.size() || m_posmap.count(word) > 0)        
        pOut->push_back(word);
  }

  inline string getPOS(const string &word) const {
    unordered_map<string, string>::const_iterator i = m_posmap.find(word);
    
    if(m_posmap.end() != i)
      return i->second;
    
    return "?";
  }
  
};
