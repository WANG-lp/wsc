
#include <getopt.h>
#include <tr1/unordered_map>
#include <tr1/unordered_set>

using namespace std;
using namespace tr1;

typedef unordered_map<int, string> command_option_t;

class optparse_t {
private:
  command_option_t m_parsedopts;
  bool             m_good;
  
public:
  optparse_t(const string &help, const string &acceptable, const string &required, int argc, char **argv ) : m_good(true) {
    int                 option;
    unordered_set<char> assigned;

    /* Hmm... let me see. */
    while( -1 != (option = getopt(argc, argv, acceptable.c_str())) ) {
      if('?' == option) { m_good = false; return; }
      if( NULL == optarg ) m_parsedopts[option] = "";
      else                 m_parsedopts[option] = optarg;

      if(string::npos != required.find(option))
        assigned.insert(option);
    }

    // CHECK IF THE REQUIRED ARGUMENTS ARE ALL THERE.
    bool fShowUsage = false;
    
    for(int i=0; i<required.length(); i++)
      if(0 == assigned.count(required[i])) {
        cerr << "Missing required argument: -" << required[i] << endl;
        fShowUsage = true;
        m_good     = false;
      }

    if(fShowUsage) cerr << endl << help << endl;
  }

  inline string of(const char c) const {
    command_option_t::const_iterator iter = m_parsedopts.find(c);
    return m_parsedopts.end() == iter ? "" : iter->second;
  }

  inline string of(const char c, const string &from, const string &to) const {
    string val = of(c);
    
    size_t start_pos = 0;
    while((start_pos = val.find(from, start_pos)) != string::npos) {
      val.replace(start_pos, from.length(), to);
      start_pos += to.length();
    }

    return val;
  }
  
  inline bool hasKey(const char c) const {
    command_option_t::const_iterator iter = m_parsedopts.find(c);
    return m_parsedopts.end() != iter;
  }
  
  inline bool isGood() const { return m_good; }

  inline void defset(const char c, const string &def) {
    if("" == this->of(c)) m_parsedopts[c] = def;
  }
};

