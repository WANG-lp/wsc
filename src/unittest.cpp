
#include <vector>

#include "exactsearch.h"

using namespace std;


int main(int argc, char **argv) {
  exactsearch_t es("/work/naoya-i/kb/corefevents.cdblist");
  vector<size_t> out;
  
  es.search(&out, "kill-v:dobj", "die-v:nsubj")
}
