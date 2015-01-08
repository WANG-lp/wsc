
#include <vector>

#include "exactsearch.h"

using namespace std;

int main(int argc, char **argv) {
  exactsearch_t es("/work/naoya-i/kb/corefevents.cdblist");
  vector<exactsearch_t::result_t> out;
  
  es.search(&out, argv[1], argv[2]);

  for(size_t i=0; i<out.size(); i++)
    cout << out[i].offset << endl;
}
