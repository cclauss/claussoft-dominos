#!/usr/bin/env python3

import sys
from pathlib import Path

d = {s.split()[4]: s.split()[8] for s in sys.stdin}
print(Path(d[max(d)]).read_text())
