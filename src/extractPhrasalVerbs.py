
import sys

from nltk.corpus import wordnet as wn

def _printHypernyms(s):
	for sh in s.hypernyms():
		
		# FIND A SINGLE WORD PARAPHRASES AND PRINT THEM OUT.
		for lh in sh.lemmas:
			print "\t".join([l.name, lh.name])


for s in wn.all_synsets():
	for l in s.lemmas:
		if ("_" in l.name) and (".v." in str(l)):
			_printHypernyms(s)
			
