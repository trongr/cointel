#!/usr/bin/env python
import feedparser
import re
import codecs

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

def main():
    apcount, wordcounts = getWordsFromFeedList("feedlist.txt")
    wordlist = makeWordList(apcount, wordcounts)
    makeWordMatrix(wordlist, wordcounts, "wordmatrix.txt")

if __name__ == "__main__":
    main()
