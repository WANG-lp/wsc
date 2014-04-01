import mmap
import sys

f = open(sys.argv[1], "rb")
m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

ret = []

for q in sys.argv[2:]:
	offset, length = map(lambda x: int(x), q.split(":"))

	ret += [m[offset:offset+length]]

if len(ret) > 0:
	print "\n".join(sorted(ret))
