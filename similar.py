#!/usr/bin/env python
import prefs
import numpy

# Throws an error if a1 and a2 are not equal
def sim(a1, a2):
    if not a1 or not a2:
        return 0 # not similar
    return numpy.corrcoef(a1, a2)[0, 1]

def prefSim(prefs, user1, user2):
    scores1 = []
    scores2 = []
    for movie in prefs[user1]:
        if movie in prefs[user2]:
            scores1.append(prefs[user1][movie])
            scores2.append(prefs[user2][movie])
    return sim(scores1, scores2)

# Returns the top 5 users with prefs similar to user, as a list of
# pairs: [(score, user),...]
def rankedUsers(prefs, user, n=5):
    matches = []
    for user2 in prefs:
        matches.append((prefSim(prefs, user, user2), user2))
    matches.sort()
    matches.reverse()
    return matches[0:n]

def rankedMovies(prefs, user, n=5):
    users = rankedUsers(prefs, user, n)
    movies = {}
    for (userRank, user) in users:
        for movie in prefs[user]:
            rating = prefs[user][movie]
            score = userRank * rating
            if score <= 0:
                continue
            movies.setdefault(movie, list()).append((score, userRank))
    scores = {}
    for movie in movies:
        totalScore = sum([score for (score, userRank) in movies[movie]])
        totalSim = sum([userRank for (score, userRank) in movies[movie]])
        scores[movie] = totalScore / totalSim
    return scores

def main():
    print rankedMovies(prefs.prefs, "Toby", 10)
    # print rankedUsers(prefs.prefs, "Toby", 10)

if __name__ == "__main__":
    main()
