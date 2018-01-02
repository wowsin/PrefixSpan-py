#! /usr/bin/env python3

"""
Usage:
    prefixspan.py (frequent | top-k) <threshold> [--minlen=1] [--maxlen=maxint] [<file>]
"""

# Uncomment for static type checking
# from typing import *
# Matches = List[Tuple[int, int]]
# Pattern = List[int]
# Results = List[Tuple[int, Pattern]]

import sys
from collections import defaultdict
from heapq import heappop, heappush

from docopt import docopt

__minlen, __maxlen = 1, sys.maxsize

results = [] # type: Results

def __scan(matches):
    # type: (Matches) -> DefaultDict[int, Matches]
    alloccurs = defaultdict(list) # type: DefaultDict[int, Matches]

    for (i, pos) in matches:
        seq = db[i]

        occurs = set() # type: Set[int]
        for j in range(pos, len(seq)):
            k = seq[j]
            if k not in occurs:
                occurs.add(k)
                alloccurs[k].append((i, j + 1))

    return alloccurs


def frequent_rec(patt, matches):
    # type: (Pattern, Matches) -> None
    if len(patt) >= __minlen:
        results.append((len(matches), patt))

        if len(patt) == __maxlen:
            return

    for (c, newmatches) in __scan(matches).items():
        if len(newmatches) >= minsup:
            frequent_rec(patt + [c], newmatches)


def topk_rec(patt, matches):
    # type: (Pattern, Matches) -> None
    if len(patt) >= __minlen:
        heappush(results, (len(matches), patt))
        if len(results) > k:
            heappop(results)

        if len(patt) == __maxlen:
            return

    for (c, newmatches) in sorted(
            __scan(matches).items(),
            key=(lambda x: len(x[1])),
            reverse=True
        ):
        if len(results) == k and len(newmatches) <= results[0][0]:
            break

        topk_rec(patt + [c], newmatches)


if __name__ == "__main__":
    def checkArg(arg, cond):
        # type: (str, Callable[[int], bool]) -> int
        try:
            threshold = int(argv[arg])
            if not cond(threshold):
                raise ValueError
        except ValueError:
            print("ERROR: Cannot parse {}.".format(arg), file=sys.stderr)
            print(__doc__, file=sys.stderr)
            sys.exit(1)

        return threshold


    argv = docopt(__doc__)

    db = [
        [int(v) for v in line.rstrip().split(' ')]
        for line in (open(argv["<file>"]) if argv["<file>"] else sys.stdin)
    ]

    if argv["frequent"]:
        minsup = checkArg("<threshold>", lambda v: 0 < v <= len(db))
        func = frequent_rec
    elif argv["top-k"]:
        k = checkArg("<threshold>", lambda v: v > 0)
        func = topk_rec

    if argv["--minlen"]:
        __minlen = checkArg("--minlen", lambda v: v > 0)
    if argv["--maxlen"]:
        __maxlen = checkArg("--maxlen", lambda v: v >= __minlen)

    func([], [(i, 0) for i in range(len(db))])

    if argv["top-k"]:
        results.sort(key=(lambda x: -x[0]))
    for (freq, patt) in results:
        print("{} : {}".format(' '.join(str(v) for v in patt), freq))
