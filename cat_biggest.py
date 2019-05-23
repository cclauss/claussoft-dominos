#!/usr/bin/env python3

import sys

d = {s.split()[4]: s.split()[8] for s in sys.stdin}
with open(d[max(d)]) as in_file:
    print(in_file.read())
