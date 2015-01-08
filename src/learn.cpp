
#include <omp.h>

#include <sys/time.h>
#include <sys/stat.h>

#include <ctime>

#include <iostream>
#include <fstream>
#include <sstream>

#include <algorithm>
#include <vector>
#include <cstdlib>

#include <readline/readline.h>
#include <readline/history.h>

#include <tr1/unordered_set>

#include "optparse.h"

using namespace std;
using namespace tr1;

typedef unordered_map<string, float> vector_t;
typedef unordered_map<string, float> rule_t;

static float _distance(const vector_t &weight, const vector_t &fv) {
  float ret = 0;
  
  for(vector_t::const_iterator i=fv.begin(); fv.end()!=i; ++i)
    ret += weight.find(i->first)->second * i->second;
  
  return ret;
}

static bool _fileExists(const string& name) {
  struct stat buffer;
  return (stat (name.c_str(), &buffer) == 0);
}

// VECTOR OPERATION.
static void _addVector(vector_t *pInOut, const vector_t &src) {
  for(vector_t::const_iterator i=src.begin(); src.end()!=i; ++i)
    (*pInOut)[i->first] += i->second;
}

static void _subVector(vector_t *pInOut, const vector_t &src) {
  for(vector_t::const_iterator i=src.begin(); src.end()!=i; ++i)
    (*pInOut)[i->first] -= i->second;
}

vector_t _vectorizeRule(const rule_t &rule) {
  vector_t ret;
  ret["pred"] =
    rule.find("sRuleAssoc")->second *
    (0 == rule.find("iIndexed")->second ? rule.find("sIndexPred0")->second : rule.find("sIndexPred1")->second) * rule.find("sPredictedPred")->second *
    (0 == rule.find("iIndexed")->second ? rule.find("sIndexSlot0")->second : rule.find("sIndexSlot1")->second) * rule.find("sPredictedSlot")->second;
  ret["arg"] =
    rule.find("sPredictedArg")->second;
  ret["context"] =
    (0 == rule.find("iIndexed")->second ? rule.find("sIndexContext0")->second : rule.find("sIndexContext1")->second) * rule.find("sPredictedContext")->second;
  return ret;
}


// COMPARATOR FOR rule_t.
class _compMoreRuleT {
private:
  const vector_t &m_weight;

public:
  _compMoreRuleT(const vector_t &weight) : m_weight(weight) {}
  
  bool operator()(const rule_t &rLeft, const rule_t rRight) const {
    return _distance(this->m_weight, _vectorizeRule(rLeft)) > _distance(this->m_weight, _vectorizeRule(rRight));
  }
};

class learner_t {
private:
  vector_t   m_weight;
  string     m_fnCache;

public:
  learner_t(const string &fnCache) : m_fnCache(fnCache) {
    m_weight["pred"] = 0.001;
    m_weight["arg"] = 0.001;
    m_weight["context"] = 0.001;
  };

  string getCacheFileName(int problemno) const {
    char buffer[1024];
    sprintf(buffer, "%s%d%s",
            m_fnCache.substr(0, m_fnCache.find("{")).c_str(),
            problemno,
            m_fnCache.substr(m_fnCache.find("}")+1).c_str()
            );
    return string(buffer);
  }
  
  bool iterate(vector_t *pOut, uint problemno, uint K) {
    vector<rule_t> rules;
    vector_t       fvUpdate;

    if(!_fileExists(this->getCacheFileName(problemno))) return false;

    ifstream ifsCache(this->getCacheFileName(problemno).c_str(), ios::in);
    string   line;
    
    while(getline(ifsCache, line)) {
      if(string::npos != line.find("type=\"iriInstances\"")) {
        rule_t rule;
        string text = line.substr(line.find("\">")+2, line.find("</statis")-(line.find("\">")+2));
        
        rule["Label"] = string::npos != line.find("label=\"Correct\"") ? 1 : 0;

        sscanf(text.c_str(), "%f\t%f\t%f\t%f\t(%f, %f)\t(%f, %f)\t(%f, %f)\t(%f, %f)\t%f\t%f\t%f\t%f",
               &rule["score"], &rule["iPredicted"], &rule["iIndexed"], &rule["sRuleAssoc"],
               &rule["sIndexPred0"], &rule["sIndexPred1"],
               &rule["sIndexArg0"], &rule["sIndexArg1"],
               &rule["sIndexContext0"], &rule["sIndexContext1"],
               &rule["sIndexSlot0"], &rule["sIndexSlot1"],
               &rule["sPredictedPred"], &rule["sPredictedArg"], &rule["sPredictedContext"], &rule["sPredictedSlot"]
               );
        rules.push_back(rule);
        
        if(10000 < rules.size())
          return false;
      }
    }

    sort(rules.begin(), rules.end(), _compMoreRuleT(this->m_weight));

    float    scoreCorrect = 0, scoreWrong = 0;
    vector_t fvCorrect, fvWrong;
    
    for(uint i=0; i<min((size_t)K, rules.size()); i++) {
      vector_t fv = _vectorizeRule(rules[i]);
      
      if(1 == rules[i]["Label"]) {
        scoreCorrect += _distance(this->m_weight, fv);
        _addVector(&fvCorrect, fv);
      } else if(0 == rules[i]["Label"]) {
        scoreWrong += _distance(this->m_weight, fv);
        _addVector(&fvWrong, fv);
      }
    }

    cerr << "SCORE: " << problemno << ":" << scoreCorrect << " vs " << scoreWrong << endl;
    
    // IMPLIES WRONG PREDICTION (y^ != y*)?
    if(scoreCorrect < scoreWrong) {
      cerr << "WRONG PREDICTION: " << problemno << endl;
      *pOut = fvCorrect;
      _subVector(pOut, fvWrong);
      return true;
    }

    return false;
  }
  
  void learn(float learningRate, uint maxIter, uint K) {
    float currentLearningRate = 1.0;
    
    for(uint i=0; i<maxIter; i++) {      
      cerr << "=== Iteration:" << 1+i << endl;

      //currentLearningRate *= learningRate;
      currentLearningRate = learningRate;
      
      vector<vector_t> fvUpdates;
      vector_t         fvAveragedUpdate;

      #pragma omp parallel for
      for(uint j=0; j<2000; j++) {
        vector_t fv;
        
        if(this->iterate(&fv, j, K)) {
          #pragma omp critical
          {
            fvUpdates.push_back(fv);
          }
        }
      }

      cerr << fvUpdates.size() << " updates." << endl;
      cerr << "Learning rate: " << currentLearningRate << endl;

      for(uint j=0; j<fvUpdates.size(); j++)
        _addVector(&fvAveragedUpdate, fvUpdates[j]);

      for(vector_t::const_iterator j=fvAveragedUpdate.begin(); fvAveragedUpdate.end()!=j; ++j)
        this->m_weight[j->first] += currentLearningRate * j->second / fvUpdates.size();

      for(vector_t::const_iterator j=this->m_weight.begin(); this->m_weight.end()!=j; ++j)
        cerr << j->first << "\t" << j->second << endl;
    }

  }
};

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  learn"
                  " -i <CACHE FILE>"
                  " [-K <K-BEST=5>]"
                  " [-r <LEARNING RATE=0.2>]"
                  " [-n <MAX ITERATIONS=30>]"
                  " [-m <# OF PARALLEL PROCESSOR=4>]"
                  ,
                  "i:K:r:n:m:", "i", argc, argv);
  if(!opts.isGood()) return 0;
  opts.defset('K', "5");
  opts.defset('r', "0.2");
  opts.defset('n', "30");
  opts.defset('m', "4");

  omp_set_num_threads(atoi(opts.of('m').c_str()));
  
  learner_t learner(opts.of('i'));
  learner.learn(atof(opts.of('r').c_str()), atoi(opts.of('n').c_str()), atoi(opts.of('K').c_str()));
  
}
