
import hashlib

import re
import sys


for guys in re.findall("(.*?)\n(.*?)\n(.*?)\n(.*?)\n\n", open(sys.argv[1]).read()):
	print tuple([hashlib.sha1(repr(guys)).hexdigest()[:8]] + [x.strip() for x in guys])
