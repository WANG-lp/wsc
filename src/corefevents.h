
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
  vocab_t      m_vocab;
  vocabct_t    m_vocabct;

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

  corefevents_t(const string &fnCorefEventsTsv, const string &fnCorefEventsVocab, const string &fnCorefEventsVocabCT, bool fMemoryMapped = false) : m_fd(-1) {
    
    // READ THE VOCAB.
    cerr << "Loading vocab..." << endl;
    readVocab(&m_vocab, fnCorefEventsVocab);
    readVocab(&m_vocabct, fnCorefEventsVocabCT);
    
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

  bool calcScore(result_t *pOut, size_t offset, int length, const proposition_t &prpIndexed, const proposition_t &prpPredicted, const google_word2vec_t &gw2v) {
    char     buffer[1024*16];
    uint32_t ip1, ip2, ia1, ia2;
    char     csentdist, numC1, numC2;
    char     rawc1[1024], rawc2[1024];

    ip1      = *((uint32_t*)&m_pCorefEvents[offset]);
    ip2      = *((uint32_t*)&m_pCorefEvents[offset+sizeof(uint32_t)*1]);
    ia1      = *((uint32_t*)&m_pCorefEvents[offset+sizeof(uint32_t)*2]);
    ia2      = *((uint32_t*)&m_pCorefEvents[offset+sizeof(uint32_t)*3]);
    csentdist = *((char*)&m_pCorefEvents[offset+sizeof(uint32_t)*4]);
    numC1    = *((char*)&m_pCorefEvents[offset+sizeof(uint32_t)*4+sizeof(char)]);
    memcpy(rawc1, (char*)&m_pCorefEvents[offset+sizeof(uint32_t)*4+sizeof(char)*2], numC1*(2+4));
    
    numC2    = *((char*)&m_pCorefEvents[offset+sizeof(uint32_t)*4+sizeof(char)*2+sizeof(char)*numC1*(2+4)]);
    memcpy(rawc2, (char*)&m_pCorefEvents[offset+sizeof(uint32_t)*4+sizeof(char)*2+sizeof(char)*numC1*(2+4)+sizeof(char)], numC2*(2+4));

    pOut->line = m_vocab[ip1] + "\t" + m_vocab[ip2] + "\t" + m_vocab[ia1] + "," + m_vocab[ia2] + "\t" + csentdist + "\t";
    addContext(&pOut->line, rawc1, numC1*(2+4), m_vocab, m_vocabct);
    pOut->line += "\t";
    addContext(&pOut->line, rawc2, numC2*(2+4), m_vocab, m_vocabct);

    pOut->length = sizeof(uint32_t)*4 + sizeof(char)*3 + sizeof(char)*(numC1+numC2)*(2+4);
    
    string   p1, s1, p2, s2, a1, a2, c1, c2, sentdist;
    istringstream ssRule(pOut->line);
    
    getline(ssRule, p1, ':'); p1 = p1.substr(0, p1.find("-")); getline(ssRule, s1, '\t');
    getline(ssRule, p2, ':'); p2 = p2.substr(0, p2.find("-")); getline(ssRule, s2, '\t');
    getline(ssRule, a1, ','); a1 = a1.substr(0, a1.find("-"));
    getline(ssRule, a2, '\t'); a2 = a2.substr(0, a2.find("-"));
    getline(ssRule, sentdist, '\t');
    getline(ssRule, c1, '\t'); getline(ssRule, c2, '\t');

    pOut->spm1 = calcWordSimilarity(p1, prpIndexed.predicate, gw2v);
    pOut->scm1 = calcContextualSimilarity(c1, prpIndexed.context, gw2v);
    pOut->sm1  = calcSlotSimilarity(s1, prpIndexed.slot);
    pOut->sam1 = calcWordSimilarity(a1, prpIndexed.focusedArgument, gw2v);
    
    pOut->spm2 = calcWordSimilarity(p2, prpIndexed.predicate, gw2v);
    pOut->scm2 = calcContextualSimilarity(c2, prpIndexed.context, gw2v);
    pOut->sm2  = calcSlotSimilarity(s2, prpIndexed.slot);
    pOut->sam2 = calcWordSimilarity(a2, prpIndexed.focusedArgument, gw2v);
      
    string *pp, *ps, *pa, *pc;
    
    if(pOut->spm1*pOut->sam1*pOut->sm1*pOut->scm1 > pOut->spm2*pOut->sam2*pOut->sm2*pOut->scm2) {
      pp = &p2; pc = &c2; ps = &s2; pa = &a2; pOut->iIndexed = 0; pOut->iPredicted = 1;
    } else {
      pp = &p1; pc = &c1; ps = &s1; pa = &a1; pOut->iIndexed = 1; pOut->iPredicted = 0;
    }

    if("" != prpPredicted.predicate) {
      pOut->spm = calcWordSimilarity(*pp, prpPredicted.predicate, gw2v);
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

  static void addContext(string *pOut, const char *rawc, int length, const vocab_t &vocab, const vocabct_t &vocabCT) {
    for(int i=0; i<length; i+=2+4) {
      uint16_t idType  = *((uint16_t*)&rawc[i]);
      uint32_t idValue = *((uint32_t*)&rawc[i+2]);

      if(0 != i) *pOut += " ";

      *pOut += vocabCT.find(idType)->second + ":" + vocab.find(idValue)->second;
    }
  }

  static void readVocab(vocab_t *pOut, const string &fnVocab) {
    ifstream ifsVocab(fnVocab.c_str(), ios::in);
    string line;
    
    while(!ifsVocab.eof()) {
      uint32_t id;
      getline(ifsVocab, line, '\t');
      ifsVocab.read((char*)&id, sizeof(uint32_t));
      (*pOut)[id] = line;
    }

    ifsVocab.close();
  }
  
  static void readVocab(vocabct_t *pOut, const string &fnVocab) {
    ifstream ifsVocab(fnVocab.c_str(), ios::in);
    string line;
  
    while(!ifsVocab.eof()) {
      uint16_t id;
      getline(ifsVocab, line, '\t');
      ifsVocab.read((char*)&id, sizeof(uint16_t));
      (*pOut)[id] = line;
    }

    ifsVocab.close();
  }
  
};
