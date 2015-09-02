#!/usr/bin/env python
from PIL import Image, ImageDraw
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
        try:
            title, wc = getwordcounts(feedURL)
        except Exception as e:
            print "Can't read: " + feedURL
            continue
        wordcounts[title] = wc
        for word, count in wc.items():
            apcount.setdefault(word, 0)
            if count > 1:
                apcount[word] += 1
    return apcount, wordcounts

# Return list of all words
def makeWordList(apcount, wordcounts):
    # # Don't filter out (un)common words
    # wordlist = [w for (w, bc) in apcount.items()]

    # Filter out (un)common words. Should drastically reduce number of
    # words so hcluster can perform reasonably well
    wordlist = []
    for w, bc in apcount.items():
        frac = float(bc) / len(wordcounts) # fraction of blogs word appears in
        if frac > 0.05 and frac < 0.9:
            wordlist.append(w)

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

# Very inefficient if you try to cluster a long list of nodes
def hcluster(rows, distance):
    currentclustid = -1
    distances = {} # distances is the cache of distance calculations
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))] # Clusters are initially just the rows
    ROW_LEN = len(clust[0].vec) # This is the total number of words in all the blogs

    print "Clustering: num iteration: " + str(len(clust))
    depth = 0
    while len(clust) > 1:
        depth += 1
        print "Cluster iteration: " + str(depth)
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)
        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                l = clust[i]
                r = clust[j]
                if (l.id, r.id) not in distances:
                    distances[(l.id, r.id)] = distance(l.vec, r.vec)
                d = distances[(l.id, r.id)]
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

# Each leaf node is on its own line, so this is just the number of
# leaf nodes. Used to calculate the height of the drawing
def getheight(clust):
    # Is this an endpoint? Then the height is just 1
    if clust.left == None and clust.right == None: return 1
    # Otherwise the height is the same of the heights of
    # each branch
    return getheight(clust.left) + getheight(clust.right)

# Used to calculate the width of the drawing, cause the tree is drawn
# side ways:
def getdepth(clust):
    # The distance of an endpoint is 0.0
    if clust.left == None and clust.right == None: return 0
    # The distance of a branch is the greater of its two sides
    # plus its own distance
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
    # height and width
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)
    scaling = float(w - 150) / depth # width is fixed, so scale distances accordingly

    # Create a new image with a white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line((0, h / 2, 10, h / 2), fill=(255, 0, 0))

    # Draw the first node
    drawnode(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')

def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # Line length
        ll = clust.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))

        # Call the function to draw the left and right nodes
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))

def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata

def main():
    feedlist = "feedlist.txt"
    matrixfile = "wordmatrix.txt"
    apcount, wordcounts = getWordsFromFeedList(feedlist)
    wordlist = makeWordList(apcount, wordcounts)
    makeWordMatrix(wordlist, wordcounts, matrixfile)

    print "Clustering blog words"
    blognames, words, blogwords = readMatrixFile(matrixfile)
    blogword_clust = hcluster(blogwords, distance=similar.pearsonDist)
    # printclust(blogword_clust, blognames)
    drawdendrogram(blogword_clust, blognames, jpeg='blogclust.jpg')

    print "Clustering word blogs"
    wordblogs = rotatematrix(blogwords)
    wordblog_clust = hcluster(wordblogs, distance=similar.pearsonDist)
    # printclust(wordblog_clust, blognames)
    drawdendrogram(wordblog_clust, words, jpeg='wordclust.jpg')

if __name__ == "__main__":
    main()
