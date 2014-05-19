
#include <sstream>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <fcntl.h>

using namespace std;

class corefevents_t {
public:
  typedef unordered_map<uint32_t,string> vocab_t;
  typedef unordered_map<uint16_t,string> vocabct_t;
  
private:
  int          m_fd;
  struct stat  m_fs;
  char        *m_pCorefEvents;

public:
  struct result_t {
    string   line;
    float    score;
    float    spm1, sam1, sm1, scm1;
    float    spm2, sam2, sm2, scm2;
    float    spm, sam, sm, scm;
    uint16_t iIndexed, iPredicted;
    uint16_t length;
  };

  struct proposition_t {
    string predicate, context, slot, focusedArgument;
  };

  corefevents_t(const string &fnCorefEventsTsv, bool fMemoryMapped = false) : m_fd(-1) {
    
    // READ THE COREF EVENT PAIRS.
    cerr << "Loading " << fnCorefEventsTsv << "..." << endl;
    
    m_fd = open(fnCorefEventsTsv.c_str(), O_RDONLY);
    fstat(m_fd, &m_fs);
    
    if(fMemoryMapped)
      m_pCorefEvents = (char*)mmap(0, m_fs.st_size, PROT_READ, MAP_SHARED, m_fd, 0);
    
    else {
      close(m_fd); m_fd = -1;
      
      ifstream ifsCorefEvents(fnCorefEventsTsv.c_str(), ios::in|ios::binary);
      m_pCorefEvents = new char[m_fs.st_size];
      ifsCorefEvents.read((char*)m_pCorefEvents, m_fs.st_size);
      ifsCorefEvents.close();
    }
  }

  ~corefevents_t() {
    if(-1 != m_fd) {
      munmap(m_pCorefEvents, m_fs.st_size);
      close(m_fd);
    } else
      delete[] m_pCorefEvents;
  }

  void getPredicates(string *pOut1, string *pOut2, uint64_t offset) {
    char buffer[1024*16];
    for(uint64_t i=offset; '\t'!=m_pCorefEvents[i]; i++) {
      buffer[i-offset] = m_pCorefEvents[i]; buffer[i-offset+1] = 0;
    }

    (*pOut1) = buffer;
    offset += strlen(buffer)+1;
    
    for(uint64_t i=offset; '\t'!=m_pCorefEvents[i]; i++) {
      buffer[i-offset] = m_pCorefEvents[i]; buffer[i-offset+1] = 0;
    }

    (*pOut2) = buffer;
  }

  string _getWord(const string &wr) {
    return wr.substr(0, wr.find("-"));
  }
  
  bool calcScore(result_t *pOut, uint64_t offset, int length, const proposition_t &prpIndexed, const proposition_t &prpPredicted, char whichArg, const google_word2vec_t &gw2v) {
    char     buffer[1024*16];

    for(uint64_t i=offset; '\n'!=m_pCorefEvents[i]; i++) {
      buffer[i-offset] = m_pCorefEvents[i]; buffer[i-offset+1] = 0;
    }
    
    pOut->line   = buffer;
    pOut->length = strlen(buffer);
    
    string   p1, s1, p2, s2, a1, a2, c1, c2, sentdist;
    istringstream ssRule(pOut->line);
    
    getline(ssRule, p1, ':'); p1 = _getWord(p1); getline(ssRule, s1, '\t');
    getline(ssRule, p2, ':'); p2 = _getWord(p2); getline(ssRule, s2, '\t');
    getline(ssRule, a1, ','); a1 = a1.substr(0, a1.find("-"));
    getline(ssRule, a2, '\t'); a2 = a2.substr(0, a2.find("-"));
    getline(ssRule, sentdist, '\t');
    getline(ssRule, c1, '\t'); getline(ssRule, c2, '\t');

    if(0 == whichArg)      a2 = a1;
    else if(1 == whichArg) a1 = a2;

    pOut->spm1 = calcWordSimilarity(p1, _getWord(prpIndexed.predicate), gw2v);
    pOut->scm1 = calcContextualSimilarity(c1, prpIndexed.context, gw2v);
    pOut->sm1  = calcSlotSimilarity(s1, prpIndexed.slot);
    pOut->sam1 = 1; //calcWordSimilarity(a1, prpIndexed.focusedArgument, gw2v);
    
    pOut->spm2 = calcWordSimilarity(p2, _getWord(prpIndexed.predicate), gw2v);
    pOut->scm2 = calcContextualSimilarity(c2, prpIndexed.context, gw2v);
    pOut->sm2  = calcSlotSimilarity(s2, prpIndexed.slot);
    pOut->sam2 = 1; //calcWordSimilarity(a2, prpIndexed.focusedArgument, gw2v);
      
    string *pp, *ps, *pa, *pc;
    
    if(pOut->spm1*pOut->sm1 > pOut->spm2*pOut->sm2) {
      pp = &p2; pc = &c2; ps = &s2; pa = &a2; pOut->iIndexed = 0; pOut->iPredicted = 1;
    } else {
      pp = &p1; pc = &c1; ps = &s1; pa = &a1; pOut->iIndexed = 1; pOut->iPredicted = 0;
    }

    if("" != prpPredicted.predicate) {
      pOut->spm = calcWordSimilarity(*pp, _getWord(prpPredicted.predicate), gw2v);
      pOut->scm = calcContextualSimilarity(*pc, prpPredicted.context, gw2v);
      pOut->sm  = calcSlotSimilarity(*ps, prpPredicted.slot);
      pOut->sam = calcWordSimilarity(*pa, prpPredicted.focusedArgument, gw2v);

      pOut->score = 0 == pOut->iIndexed ?
        pOut->spm1*pOut->scm1*pOut->sm1*pOut->sam1*pOut->spm*pOut->scm*pOut->sm*pOut->sam :
        pOut->spm2*pOut->scm2*pOut->sm2*pOut->sam2*pOut->spm*pOut->scm*pOut->sm*pOut->sam;
    } else {
      pOut->score = 0 == pOut->iIndexed ?
        pOut->spm1*pOut->scm1*pOut->sm1*pOut->sam1 :
        pOut->spm2*pOut->scm2*pOut->sm2*pOut->sam2;
    }
    
    return true;
  }

  static float calcDistance(const proposition_t &p1, const proposition_t &p2, const google_word2vec_t &gw2v) {
    return 
      calcWordSimilarity(p1.predicate, p2.predicate, gw2v) *
      calcSlotSimilarity(p1.slot, p2.slot) *
      calcWordSimilarity(p1.focusedArgument, p2.focusedArgument, gw2v) *
      calcContextualSimilarity(p1.context, p2.context, gw2v);
  }

};
