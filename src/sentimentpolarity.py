
import re
import sys
import os

class sentimentpolarity_t:
	def __init__(self, db):
		# WILSON'S SUBJECTIVITY LEXICON.
		self.subjlex = {}

		for ln in open(db):
			ln = re.findall("word1=([^ ]+).*?priorpolarity=([^ ]+)\n", ln)
			
			if 0 < len(ln):
				self.subjlex[ln[0][0]] = ln[0][1]

	def getPolarity(self, word):
		pol = self.subjlex.get(word, "unknown")
		
		if "negative" == pol: return -1
		elif "positive" == pol: return 1
		elif "neutral" == pol: return 0
		return None
		
if "__main__" == __name__:
	sp = sentimentpolarity_t("/work/naoya-i/kb/wilson05_subj/subjclueslen1-HLTEMNLP05.tff")
	print sp.getPolarity(sys.argv[1])
