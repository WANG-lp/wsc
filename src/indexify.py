
import sys

# ARGS: <IN_VOCAB> <OUT_VOCAB> < <SPARSE_VECTOR>

q     = 2
vocab	= {}
	
if "-" != sys.argv[1]:
	vocab				 = dict([tuple(reversed(x.strip().split("\t", 1))) for x in open(sys.argv[1]).readlines()])
	
	print >>sys.stderr, len(vocab), "vocab entries are loaded."
	
fs_out_vocab = open(sys.argv[2], "w") if "-" != sys.argv[2] else None

for ln in sys.stdin:
	es			 = ln.strip().split(" ")
	features = []

	print " ".join(es[:q]),

	for e in es[q:]:
		e = e.rsplit(":", 1)
		
		vocab_id = int(vocab.get(e[0], -1))

		if -1 == vocab_id:
			if "-" == sys.argv[1]:
				vocab_id    = 1+len(vocab)
				vocab[e[0]] = 1+len(vocab)

				if None != fs_out_vocab:
					print >>fs_out_vocab, "%s\t%s" % (vocab[e[0]], e[0])
					
			else:
				continue
			
		try:
			if int(float(e[1])) == float(e[1]):
				e[1] = str(int(float(e[1])))

			if "0" != e[1]:
				features += [(vocab_id, e[1])]
			
		except IndexError:
			print >>sys.stderr, "?", ln.strip()

	features = list(set(features))
	features.sort(key=lambda x: x[0])
	
	print " ".join(["%d:%s" % x for x in features])

if None != fs_out_vocab:
	fs_out_vocab.close()
