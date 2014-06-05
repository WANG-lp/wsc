
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include <fstream>
#include <string>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <fcntl.h>

#include <tr1/unordered_map>

using namespace std;
using namespace tr1;

class google_word2vec_t {
public:
  typedef unordered_map<string, pair<size_t, uint16_t> > dict_t;
  
private:
  struct stat m_fStatW2VDB;
  int         m_fdW2VDB;
  
  char   *m_pW2VDB;
  dict_t  m_dict;

public:  
  static const size_t FILE_SIZE = 3644258522;
  static const int DIMENSION = 300;

 google_word2vec_t(const string &fnBin, const string &fnIndex, bool fUseMemoryMap = false) : m_pW2VDB(NULL), m_fdW2VDB(-1) {
    //
    // LOAD THE INDEX.
    cerr << "Loading " << fnIndex << "..." << endl;
    
    ifstream ifsIndex(fnIndex.c_str(), ios::in|ios::binary);
    string   entry;
    
    while(getline(ifsIndex, entry, '\t')) {
      size_t offset; uint16_t size;
      ifsIndex.read((char*)&offset, sizeof(size_t));
      ifsIndex.read((char*)&size, sizeof(uint16_t));
      
      m_dict[entry] = make_pair(offset, size);
    }

    ifsIndex.close();

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
  }

  inline const dict_t &getDictionary() const { return m_dict; }
  
  inline bool getWordVector(float *pOut, const string &word) const {
    dict_t::const_iterator iterEntry = m_dict.find(word);
    if(m_dict.end() == iterEntry) return false;

    memcpy(pOut, m_pW2VDB+iterEntry->second.first+word.length()+1, sizeof(float)*DIMENSION);

    return true;
  }

  inline bool getWordVector(const float **pOut, const string &word) const {
    dict_t::const_iterator iterEntry = m_dict.find(word);
    if(m_dict.end() == iterEntry) return false;

    *pOut = (const float*)(m_pW2VDB+iterEntry->second.first+word.length()+1);

    return true;
  }
  
};
