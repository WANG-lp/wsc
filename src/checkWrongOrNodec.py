
import sys, re
import collections

freq			= collections.defaultdict(int)
instances	= collections.defaultdict(list)
dp_id			= 0

for score_c1, score_c2 in re.findall("([0-9.-]+)\n([0-9.-]+)", open(sys.argv[2]).read()):
	score_c1, score_c2 = float(score_c1), float(score_c2)
	
	if score_c1 == score_c2:
		freq["NO_DECISION"] += 1
		instances["NO_DECISION"] += [dp_id]		
	elif score_c1 < score_c2:
		freq["CORRECT"] += 1
		instances["CORRECT"] += [dp_id]		
	else:
		freq["WRONG"] += 1
		instances["WRONG"] += [dp_id]

	dp_id += 1

rows = []

for t in "CORRECT WRONG NO_DECISION".split():
	rows += ["%.1f\\%% (%3d/%3d)" % (
		100.0 * freq[t] / sum(freq.values()), freq[t],
		sum(freq.values()) )]

print " & ".join(map(lambda x: x.replace("_", "\\_").replace("|", "+"), [sys.argv[1]] + rows)), "\\\\"

# for t in "CORRECT WRONG NO_DECISION".split():
# 	print "%s\t%s" % (t, " ".join([str(x) for x in instances[t]]))
	
