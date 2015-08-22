#!/usr/bin/env python
import prefs
import numpy

# Throws an error if a1 and a2 are not equal
def similarity(a1, a2):
    if not a1 or not a2:
        return 0 # not similar
    return numpy.corrcoef(a1, a2)[0, 1]

# scores for movies user1 and user2 have in common
def common_scores(prefs, user1, user2):
    scores1 = []
    scores2 = []
    for movie in prefs[user1]:
        if movie in prefs[user2]:
            scores1.append(prefs[user1][movie])
            scores2.append(prefs[user2][movie])
    return scores1, scores2

def prefSimilarity(prefs, user1, user2):
    scores1, scores2 = common_scores(prefs, user1, user2)
    return similarity(scores1, scores2)

# Returns the top 5 users with prefs similar to user, as a list of
# pairs: [(score, user_name),...]
def similarUsers(prefs, user, top_n_users=5):
    matches = []
    for other_user in prefs:
        matches.append((prefSimilarity(prefs, user, other_user), other_user))
    matches.sort()
    matches.reverse()
    return matches[0:top_n_users]

def rankedMovies(prefs, user, top_n_users=5):
    rankedUsers = similarUsers(prefs, user, top_n_users)
    movie_weighted_scores = {}
    for (user_sim_score, username) in rankedUsers:
        for movie in prefs[username]:
            weighted_score = user_sim_score * prefs[username][movie]
            if weighted_score <= 0:
                continue
            movie_weighted_scores.setdefault(movie, list()).append((weighted_score, user_sim_score))
    movie_scores = {}
    for movie in movie_weighted_scores:
        movie_total_score = sum([weighted_score for (weighted_score, user_sim_score) in movie_weighted_scores[movie]])
        sim_sum = sum([user_sim_score for (weighted_score, user_sim_score) in movie_weighted_scores[movie]])
        movie_scores[movie] = movie_total_score / sim_sum
    return movie_scores

def main():
    print rankedMovies(prefs.prefs, "Toby", 10)
    # print similarUsers(prefs.prefs, "Toby", 10)

if __name__ == "__main__":
    main()
