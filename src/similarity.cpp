
#include <math.h>
#include <sys/time.h>

#include <ctime>

#include <iostream>
#include <fstream>
#include <sstream>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <fcntl.h>

#include "google-word2vec.h"
#include "optparse.h"
#include "vectorize.h"

using namespace std;

int main(int argc, char **argv) {
  optparse_t opts("Usage:\n  similarity -k <PATH TO KNOWLEDGE BASE>"
                  " -m <PARALLELS>",
                  "k:m:", "km", argc, argv);
  if(!opts.isGood()) return 0;
  
  google_word2vec_t gw2v(opts.of('k') + "/GoogleNews-vectors-negative300.bin",
                         opts.of('k') + "/GoogleNews-vectors-negative300.index.bin");
  string   line, typeCalc, p1, c1, p2, c2, a1, a2, p3, c3, a3;

  cout << "200 OK" << endl;
  
  while(getline(cin, line)) {
    istringstream ss(line);
    getline(ss, typeCalc, '\t');

    if('0' == typeCalc[0]) {
      getline(ss, p1, '\t'); getline(ss, c1, '\t'); getline(ss, a1, '\t');
      getline(ss, p2, '\t'); getline(ss, c2, '\t'); getline(ss, a2, '\t');
      getline(ss, p3, '\t'); getline(ss, c3, '\t'); getline(ss, a3, '\t');

      float
        spm13 = calcWordSimilarity(p1, p3, gw2v), sam13 = calcWordSimilarity(a1, a3, gw2v), scm13 = calcContextualSimilarity(c1, c3, gw2v),
        spm23 = calcWordSimilarity(p2, p3, gw2v), sam23 = calcWordSimilarity(a2, a3, gw2v), scm23 = calcContextualSimilarity(c2, c3, gw2v);
      cout.write((const char*)&spm13, sizeof(float)); cout.write((const char*)&sam13, sizeof(float)); cout.write((const char*)&scm13, sizeof(float));
      cout.write((const char*)&spm23, sizeof(float)); cout.write((const char*)&sam23, sizeof(float)); cout.write((const char*)&scm23, sizeof(float));
      
    } else if('1' == typeCalc[0]) {
      getline(ss, p1, '\t'); getline(ss, c1, '\t'); getline(ss, a1, '\t');
      getline(ss, p2, '\t'); getline(ss, c2, '\t'); getline(ss, a2, '\t');

      float
        spm12 = calcWordSimilarity(p1, p2, gw2v), sam12 = calcWordSimilarity(a1, a2, gw2v), scm12 = calcContextualSimilarity(c1, c2, gw2v);
      
      cout.write((const char*)&spm12, sizeof(float)); cout.write((const char*)&sam12, sizeof(float)); cout.write((const char*)&scm12, sizeof(float));
    }
  }
  
  return 0;
  
}

