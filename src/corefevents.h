
#include <sstream>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <fcntl.h>

#include "vectorize.h"

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
    string          line;
    float           score;
    float           spm1, sam1, sm1, scm1;
    float           spm2, sam2, sm2, scm2;
    float           spm, sam, sm, scm;
    uint16_t        iIndexed, iPredicted;
    uint16_t        length;
    sparse_vector_t vcon1, vcon2, vcon;
  };

  struct proposition_t {
    string predicate, context, slot, focusedArgument;
    string src, text;

    string toString() const { return predicate + ":" + slot + "\t" + focusedArgument + "\t" + context; }
    string predSlotToString() const { return predicate + ":" + slot; }
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

  string _getWord(const string &wr) const {
    return wr.substr(0, wr.find("-"));
  }
  
  string _getPOS(const string &wr) const {
    return wr.substr(wr.find("-")+1);
  }

  void getEventPair(proposition_t *pOut1, proposition_t *pOut2, uint64_t offset, string *pOutLine = NULL) {
    char buffer[1024*16];

    for(uint64_t i=offset; '\n'!=m_pCorefEvents[i]; i++) {
      buffer[i-offset] = m_pCorefEvents[i]; buffer[i-offset+1] = 0;
    }
    
    if(NULL != pOutLine)
      *pOutLine = buffer;

    string        sentdist, text;
    istringstream ssRule(buffer);
    
    getline(ssRule, pOut1->predicate, ':'); pOut1->predicate = _getWord(pOut1->predicate); getline(ssRule, pOut1->slot, '\t');
    getline(ssRule, pOut2->predicate, ':'); pOut2->predicate = _getWord(pOut2->predicate); getline(ssRule, pOut2->slot, '\t');
    getline(ssRule, pOut1->focusedArgument, ','); getline(ssRule, pOut2->focusedArgument, '\t');
    getline(ssRule, sentdist, '\t');
    getline(ssRule, pOut1->context, '\t'); getline(ssRule, pOut2->context, '\t');
    getline(ssRule, pOut1->text, '\t'); getline(ssRule, pOut2->text, '\t');
    getline(ssRule, pOut1->src, '\t');

    pOut2->src = pOut1->src;
  }

  void generateVector(string *pOut, uint64_t offset, const proposition_t &ie1, const proposition_t &ie2, google_word2vec_t &gw2v) {
    proposition_t e1, e2;
    this->getEventPair(&e1, &e2, offset, NULL);

    if(e1.predicate != ie1.predicate && e2.predicate != ie2.predicate) swap(e1, e2);

    sparse_vector_t fv;
    _fvArgSim(&fv, e1, ie1, e2, ie2, gw2v);
    _fvConSim(&fv, e1, ie1, e2, ie2, gw2v);

    *pOut = toString(fv);
  }
  
  bool calcScore(result_t *pOut, uint64_t offset, int length, const proposition_t &prpIndexed, const proposition_t &prpPredicted, char whichArg, const unordered_map<string, float> &weightMap, google_word2vec_t &gw2v) {
    proposition_t e1, e2;
    this->getEventPair(&e1, &e2, offset, &pOut->line);
    
    pOut->length = pOut->line.length();

    if(0 == whichArg)      e2.focusedArgument = e1.focusedArgument;
    else if(1 == whichArg) e1.focusedArgument = e2.focusedArgument;

    pOut->spm1 = calcWordSimilarity(e1.predicate, _getWord(prpIndexed.predicate), gw2v);
    pOut->scm1 = calcContextualSimilarity(e1.context, prpIndexed.context, weightMap, gw2v, &pOut->vcon1);
    pOut->sm1  = calcSlotSimilarity(e1.slot, prpIndexed.slot);
    pOut->sam1 = 1; //calcWordSimilarity(a1, prpIndexed.focusedArgument, gw2v);
    
    pOut->spm2 = calcWordSimilarity(e2.predicate, _getWord(prpIndexed.predicate), gw2v);
    pOut->scm2 = calcContextualSimilarity(e2.context, prpIndexed.context, weightMap, gw2v, &pOut->vcon2);
    pOut->sm2  = calcSlotSimilarity(e2.slot, prpIndexed.slot);
    pOut->sam2 = 1; //calcWordSimilarity(a2, prpIndexed.focusedArgument, gw2v);
      
    proposition_t *pe;
    
    if(pOut->spm1*pOut->sm1 > pOut->spm2*pOut->sm2) {
      pe = &e2;
      pOut->iIndexed = 0;
      pOut->iPredicted = 1;
    } else {
      pe = &e1;
      pOut->iIndexed = 1;
      pOut->iPredicted = 0;
    }

    if("" != prpPredicted.predicate) {
      pOut->spm = calcWordSimilarity(pe->predicate, _getWord(prpPredicted.predicate), gw2v);
      pOut->scm = calcContextualSimilarity(pe->context, prpPredicted.context, weightMap, gw2v, &pOut->vcon);
      pOut->sm  = calcSlotSimilarity(pe->slot, prpPredicted.slot);
      pOut->sam = calcWordSimilarity(_getWord(pe->focusedArgument), _getWord(prpPredicted.focusedArgument), gw2v);

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

  void _fvArgSim(sparse_vector_t *pOut, const proposition_t &e1, const proposition_t &ie1, const proposition_t &e2, const proposition_t &ie2, google_word2vec_t &gw2v) {
    float
      sim1 = calcWordSimilarity(_getWord(e1.focusedArgument), _getWord(ie1.focusedArgument), gw2v),
      sim2 = calcWordSimilarity(_getWord(e2.focusedArgument), _getWord(ie2.focusedArgument), gw2v);
    
    (*pOut)["ARGMATCH_MIN_SIM"] = min(sim1, sim2);
    (*pOut)["ARGMATCH_MAX_SIM"]  = max(sim1, sim2);
    
    (*pOut)["ARGMATCH_MIN_INPUT_POS_" + (sim1 == min(sim1, sim2) ? _getPOS(ie1.focusedArgument) : _getPOS(ie2.focusedArgument))] = 1;
    (*pOut)["ARGMATCH_MIN_TARGET_POS_" + (sim1 == min(sim1, sim2) ? _getPOS(e1.focusedArgument) : _getPOS(e2.focusedArgument))]  = 1;
    (*pOut)["ARGMATCH_MAX_INPUT_POS_" + (sim1 == max(sim1, sim2) ? _getPOS(ie1.focusedArgument) : _getPOS(ie2.focusedArgument))] = 1;
    (*pOut)["ARGMATCH_MAX_TARGET_POS_" + (sim1 == max(sim1, sim2) ? _getPOS(e1.focusedArgument) : _getPOS(e2.focusedArgument))]  = 1;
  }

  void _fvConSim(sparse_vector_t *pOut, const proposition_t &e1, const proposition_t &ie1, const proposition_t &e2, const proposition_t &ie2, google_word2vec_t &gw2v) {
    float sum = 0.0;
    
    for(int which=0; which<2; which++) {
      unordered_set<string> keys;
      unordered_map<string, vector<string> > ce, cie;
        
      breakDownContext(&keys, &ce, 0 == which ? e1.context : e2.context);
      breakDownContext(&keys, &cie, 0 == which ? ie1.context : ie2.context);

      for(unordered_set<string>::iterator iter_k=keys.begin(); keys.end()!=iter_k; ++iter_k) {
        float  eMax = -9999.0;
        string wordmax_e, wordmax_ie;
    
        for(int i=0; i<ce[*iter_k].size(); i++) {
          for(int j=0; j<cie[*iter_k].size(); j++) {
            float sim = calcWordSimilarity(_getWord(ce[*iter_k][i]),
                                           _getWord(cie[*iter_k][j]),
                                           gw2v);
            if(eMax < sim) {
              eMax = sim;
              wordmax_e = ce[*iter_k][i];
              wordmax_ie = cie[*iter_k][j];
            }
          } }
        
        if(-9999 != eMax) {          
          sum += eMax;
          (*pOut)["CONMATCH_TYPE_" + *iter_k] += eMax;
          (*pOut)["CONMATCH_LEX_"  + wordmax_ie] += eMax;
          (*pOut)["CONMATCH_POS_"  + _getPOS(wordmax_ie)] += eMax;
        } else {
          sum += 1;
          (*pOut)["CONMATCH_MISS_TYPE_" + *iter_k] += 1;
        }
      }
    }

    // NORMALIZE THEM.
    for(sparse_vector_t::iterator i=pOut->begin(); pOut->end()!=i; ++i) {
      if("CONMATCH" == i->first.substr(0, 8)) i->second /= sum;
    }
  }
  
  static float calcDistance(const proposition_t &p1, const proposition_t &p2, google_word2vec_t &gw2v) {
    unordered_map<string, float> weightMap;
    
    return 
      calcWordSimilarity(p1.predicate, p2.predicate, gw2v) *
      calcSlotSimilarity(p1.slot, p2.slot) *
      calcWordSimilarity(p1.focusedArgument, p2.focusedArgument, gw2v) *
      calcContextualSimilarity(p1.context, p2.context, weightMap, gw2v);
  }

};
