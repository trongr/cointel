#!/usr/bin/env python
import feedparser
import re
import codecs
import similar

# removes tags and returns list of alphabetic (non numeric) words
def getwords(html):
    txt = re.compile(r'<[^>]+>').sub('', html)
    words = re.compile(r'[^A-Za-z]+').split(txt)
    return [word.lower() for word in words if word != '']

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(feedURL):
    print "Parsing feed: " + feedURL
    d = feedparser.parse(feedURL)
    wc = {}
    # Loop over all the entries and add them to word counts
    for e in d.entries:
        if 'summary' in e: summary = e.summary
        else: summary = e.description
        words = getwords(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    return d.feed.title, wc

def getWordsFromFeedList(feedList):
    print "Getting words from feed list: " + feedList
    # apcount is used later to filter out very (un)common words
    apcount = {} # {word:num_blogs_word_appears_in}
    wordcounts = {} # {blog_title:{word:count}}
    for feedURL in file(feedList):
        title, wc = getwordcounts(feedURL)
        wordcounts[title] = wc
        for word, count in wc.items():
            apcount.setdefault(word, 0)
            if count > 1:
                apcount[word] += 1
    return apcount, wordcounts

# Return list of all words
def makeWordList(apcount, wordcounts):
    wordlist = [w for (w, bc) in apcount.items()]
    # todo. Use apcount to filter (un)common words
    # for w, bc in apcount.items():
    #     frac = float(bc) / len(feedlist)
    #     if frac > 0.1 and frac < 0.5:
    #         wordlist.append(w)
    return wordlist

# First row of matrixFile is the header: BLOG WORD1 WORD2....  The
# remaining rows contain the blog name, followed by the word count of
# WORDi in that blog
def makeWordMatrix(wordlist, wordcounts, matrixFile):
    out = codecs.open(matrixFile, encoding='utf-8', mode='w')
    out.write('Blog')
    for word in wordlist:
        out.write('\t%s' % word)
    out.write('\n')
    for blog, wc in wordcounts.items():
        out.write(blog)
        for word in wordlist:
            if word in wc:
                out.write('\t%d' % wc[word])
            else:
                out.write('\t0')
        out.write('\n')

def readMatrixFile(matrixFile):
    lines = [line for line in file(matrixFile)]
    colnames = lines[0].strip().split('\t')[1:] # First line is the column titles
    rownames = []
    data = [] # items are word counts in each blog
    for line in lines[1:]:
        p = line.strip().split('\t')
        rownames.append(p[0]) # First column in each row is the rowname
        data.append([float(x) for x in p[1:]]) # The data for this row is the remainder of the row
    return rownames, colnames, data

class bicluster:
    # vec contains data for this cluster, or the merged data of its
    # children
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        # id is only used to attach the right blog name. todo:
        # refactor so bicluster takes blog name as another param
        self.id = id
        self.distance = distance

def hcluster(rows, distance):
    currentclustid = -1
    distances = {} # distances is the cache of distance calculations
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))] # Clusters are initially just the rows
    ROW_LEN = len(clust[0].vec) # This is the total number of words in all the blogs

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)
        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]
                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # calculate the average of the two closest clusters and merge them:
        left = clust[lowestpair[0]]
        right = clust[lowestpair[1]]
        mergevec = [(left.vec[i] + right.vec[i]) / 2.0 for i in range(ROW_LEN)]
        newcluster = bicluster(mergevec, left=left, right=right,
                               distance=closest, id=currentclustid)

        currentclustid -= 1 # cluster ids that weren't in the original set are negative
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]

def printclust(clust, labels=None, n=0):
    # indent to make a hierarchy layout
    for i in range(n):
        print ' ',
    if clust.id < 0: # negative id means that this is branch
        print '-'
    else: # positive id means that this is an endpoint
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]

    # now print the right and left branches
    if clust.left != None:
        printclust(clust.left, labels=labels, n=n+1)
    if clust.right != None:
        printclust(clust.right, labels=labels, n=n+1)

def main():
    feedlist = "feedlist.txt"
    matrixfile = "wordmatrix.txt"
    apcount, wordcounts = getWordsFromFeedList(feedlist)
    wordlist = makeWordList(apcount, wordcounts)
    makeWordMatrix(wordlist, wordcounts, matrixfile)
    rownames, colnames, data = readMatrixFile(matrixfile)
    clust = hcluster(data, distance=similar.pearsonDist)
    printclust(clust, rownames)

if __name__ == "__main__":
    main()
