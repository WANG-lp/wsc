
import optparse

import sys
import re

def _getPred(x):
	return x.split("-")[0]

def _coloredOutput(x, gvAna, gvAnte, gvFalseAnte):
	return x.replace(
		_getPred(gvAna), "\033[91m%s\033[0m" % _getPred(gvAna)).replace(
			_getPred(gvAnte), "\033[92m%s\033[0m" % _getPred(gvAnte)).replace(
				_getPred(gvFalseAnte), "\033[92m%s\033[0m" % _getPred(gvFalseAnte))

def main(options, args):
	tuples = {}

	for i, ln in enumerate(open(options.tuples)):
		tuples[i] = eval(ln)

	for problemno, gvAnaBefore, gvAnteBefore, gvFalseAnteBefore, gvAnaAfter, gvAnteAfter, gvFalseAnteAfter in \
			re.findall("([0-9]+)\t<governors anaphor=\"(.*?)\" antecedent=\"(.*?)\" falseAntecedent=\"(.*?)\" />\n\t<governors anaphor=\"(.*?)\" antecedent=\"(.*?)\" falseAntecedent=\"(.*?)\" />\n\n", sys.stdin.read(), re.MULTILINE):

		if None != options.problemno and options.problemno != problemno:
			continue
			
		print "\t".join([problemno, "BEFORE", _coloredOutput(tuples[int(problemno)][1], gvAnaBefore, gvAnteBefore, gvFalseAnteBefore)])
		print "\t".join([" ", " ", "%s--%s" % (gvAnteBefore, gvAnaBefore), "%s--%s" % (gvFalseAnteBefore, gvAnaBefore)])
		print "\t".join([problemno, "AFTER", _coloredOutput(tuples[int(problemno)][1], gvAnaAfter, gvAnteAfter, gvFalseAnteAfter)])
		print "\t".join([" ", " ", "%s--%s" % (gvAnteAfter, gvAnaAfter), "%s--%s" % (gvFalseAnteAfter, gvAnaAfter)])
		print
	

if "__main__" == __name__:
	cmdparser		= optparse.OptionParser(description="Feature generator.")
	cmdparser.add_option("--tuples", help			= "The tuples.")
	cmdparser.add_option("--problemno", help			= "The tuples.")
	main(*cmdparser.parse_args())
	
