
#include <iostream>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include <tr1/unordered_map>
#include <string>

#include <cdb.h>

#include <string.h>
#include <stdlib.h>

using namespace std;
using namespace tr1;

class exactsearch_t {
private:
  unordered_map<char, struct cdb> m_cdb;
  unordered_map<char, int>        m_fd;
  string                          m_pathDB;
  
public:
  struct result_t {
    size_t offset, length;

    result_t(size_t _offset, size_t _length) : offset(_offset), length(_length) {};
    result_t() : offset(0), length(0) {};
  };
  
  exactsearch_t(const string &pathDB) : m_pathDB(pathDB) {
    
  }

  ~exactsearch_t() {
    for(unordered_map<char, int>::iterator i=m_fd.begin(); m_fd.end()!=i; ++i) {
      close(i->second);
    }
    
    for(unordered_map<char, struct cdb>::iterator i=m_cdb.begin(); m_cdb.end()!=i; ++i) {
      cdb_free(&i->second);
    }
  }

  char _getIndex(const string &k) {
    return 'a' <= k[0] && k[0] <= 'z' ? k[0] :
      ('A' <= k[0] && k[0] <= 'Z' ? ('a' + (k[0] - 'A')) : '0');
  }
  
  void search(vector<result_t> *pOut, const string &pr1, const string &pr2) {
    string key = pr1 < pr2 ? (pr1 + "," + pr2) : (pr2 + "," + pr1);
    char   cdbindex = _getIndex(key);

    if(m_cdb.count(cdbindex) == 0) {
      m_fd[cdbindex]  = open((m_pathDB + "/corefevents.index." + cdbindex + ".cdb").c_str(), O_RDONLY);
      cdb_init(&m_cdb[cdbindex], m_fd[cdbindex]);
    }

    struct cdb_find cdbf;
    cdb_findinit(&cdbf, &m_cdb[cdbindex], key.c_str(), key.length());
    
    while(cdb_findnext(&cdbf) > 0) {
      size_t
        vpos = cdb_datapos(&m_cdb[cdbindex]),
        vlen = cdb_datalen(&m_cdb[cdbindex]);
      char
        *pBuffer = new char[vlen];
      
      cdb_read(&m_cdb[cdbindex], pBuffer, vlen, vpos);

      char *pTab = strchr(pBuffer, '\t')+1;
      char *err;
      
      string nOffset(pBuffer, pTab-pBuffer), nLength(pTab);
      pOut->push_back(result_t(strtoul(nOffset.c_str(), &err, 10), strtoul(nLength.c_str(), &err, 10)));
      
      delete[] pBuffer;
    }
    
  }
};
