#
# Usage: python identifyTempoRels.py data/dp-train.tuples

import sys
import re

# Define heuristic rules.
list_prn_ant = "because|since| if |when| although | though | as | after"
list_ant_prn = "When| so | but | and | before"


def _estimateTempoRel(x):
	if re.search(list_prn_ant, x): return "PRN -> ANT"
	if re.search(list_ant_prn, x): return "ANT -> PRN"

	return "?"


def main():
	for ln in sys.stdin:
		t = eval(ln)

		print "\t".join([t[1], _estimateTempoRel(t[1])])


if "__main__" == __name__:
	main()
