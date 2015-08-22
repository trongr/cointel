#!/usr/bin/env
from prefs import prefs
import numpy

def similarity(a1, a2):
    if not a1 or not a2:
        return 0 # not similar
    return numpy.corrcoef(a1, a2)[0, 1]

def scores(prefs, name1, name2):
    scores1 = []
    scores2 = []
    for movie in prefs[name1]:
        if movie in prefs[name2]:
            scores1.append(prefs[name1][movie])
            scores2.append(prefs[name2][movie])
    return scores1, scores2

def prefSim(prefs, name1, name2):
    scores1, scores2 = scores(prefs, name1, name2)
    print similarity(scores1, scores2)

def main():
    prefSim(prefs, "alice", "bob")

if __name__ == "__main__":
    main()
