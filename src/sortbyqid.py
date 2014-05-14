
import sys

sys.stdout.write("".join(sorted(sys.stdin.readlines(), key=lambda x: int(x.split(" ", 2)[1][4:]))))
