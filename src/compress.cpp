
#include <ctime>

#include "stdint.h"

#include <stdlib.h>

#include <fstream>
#include <sstream>
#include <iostream>

#include <vector>

#include <tr1/unordered_map>

#include "optparse.h"

using namespace std;
using namespace tr1;

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  compress"
                  " -i <INPUT EVENT PAIRS>"
                  " -o <OUTPUT EVENT PAIRS>"
                  ,
                  "o:i:", "io", argc, argv);
  if(!opts.isGood()) return 0;
  
  string   line;
  ofstream ofsOut(opts.of('o').c_str(), ios::out);
  ifstream ifsCorefEvents(opts.of('i').c_str(), ios::in);
  uint64_t numProcessed = 0, numBytesProcessed = 0;
  
  while(getline(ifsCorefEvents, line)) {
    if(0 == numProcessed % 10000000) {
      time_t timer; time(&timer);
      cerr << string(ctime(&timer)).substr(0, string(ctime(&timer)).length()-1) << " ";
    }
    
    numProcessed++;
    
    if(0 == numProcessed % 500000) cerr << ".";
    if(0 == numProcessed % 10000000 || ifsCorefEvents.eof()) {
      cerr << " " << (numProcessed) << endl;
    }
    
    string p1, p2, a1, a2, sentdist, c1, c2, s1, s2, off;
    istringstream ss(line);
    
    getline(ss, p1, '\t'); getline(ss, p2, '\t');
    getline(ss, a1, ',');  getline(ss, a2, '\t');
    getline(ss, sentdist, '\t');
    getline(ss, c1, '\t'); getline(ss, c2, '\t');
    getline(ss, s1, '\t'); getline(ss, s2, '\t');
    getline(ss, off);

    ofsOut << p1 << "\t" << p2 << "\t"
           << a1 << "," << a2 << "\t"
           << sentdist << "\t"
           << c1 << "\t" << c2 << "\t"
           << off.substr(2)
           << endl;
      
    numBytesProcessed += line.length()+1;
  }

  cerr << endl;

  ofsOut.close();
}
