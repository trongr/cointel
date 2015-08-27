#!/usr/bin/env python
import prefs
import numpy

# Throws an error if a1 and a2 are not equal. pearsonCoeff is between
# -1 and 1, negatively and positively correlated resp.
def pearsonCoeff(a1, a2):
    if not a1 or not a2:
        return 0 # not similar
    return numpy.corrcoef(a1, a2)[0, 1]

def pearsonDist(a1, a2):
    # 1 - pc because pc --> 1 means a1 and a2 are very similar,
    # i.e. they're very close, i.e. dist --> 0:
    return 1 - pearsonCoeff(a1, a2)

def prefSimilarity(prefs, user1, user2):
    scores1 = []
    scores2 = []
    for movie in prefs[user1]:
        if movie in prefs[user2]:
            scores1.append(prefs[user1][movie])
            scores2.append(prefs[user2][movie])
    return pearsonCoeff(scores1, scores2)

# Returns the top n users with prefs similar to user, as a list of
# pairs: [(score, user),...].
#
# If you reverse prefs to become ratings
# this method will return the top n movies with ratings similar to to
# movie.
def rankedUsers(prefs, user, n=5):
    matches = []
    for user2 in prefs:
        matches.append((prefSimilarity(prefs, user, user2), user2))
    matches.sort()
    matches.reverse()
    return matches[0:n]

# Finds the top n critics similar to user, and ranks their rated
# movies by how similar the critics' preferences were to you. Returns
# the list of movies in pairs: [(score, movie),...]
#
# If you reverse prefs to become ratings this method will find the top
# n movies similar to movie, and rank their critics by how similar the
# movies' ratings were to the input movie. That'd be useful e.g. to
# find critics that liked the input movie
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
    scores = []
    for movie in movies:
        totalScore = sum([score for (score, userRank) in movies[movie]])
        totalSim = sum([userRank for (score, userRank) in movies[movie]])
        scores.append((totalScore / totalSim, movie))
    scores.sort()
    scores.reverse()
    return scores

def prefsToRatings(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result

def main():
    # print rankedUsers(prefs.prefs, "Toby", 10)
    # print rankedMovies(prefs.prefs, "Toby", 10)

    movieRatings = prefsToRatings(prefs.prefs)
    # print rankedUsers(movieRatings, "Superman Returns", 10)
    print rankedMovies(movieRatings, "Just My Luck", 10)

if __name__ == "__main__":
    main()
