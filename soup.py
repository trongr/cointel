#!/usr/bin/env python
import sys
import os
import time
import re
from urllib2 import urlopen, URLError, HTTPError
from bs4 import BeautifulSoup

def dlfile(url, filename):
    try:
        print "downloading " + url
        url = re.sub(r'^//|^/|^https://', 'http://', url)
        f = urlopen(url)
        with open(filename, "wb") as local_file:
            local_file.write(f.read())
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url
    except Exception, e:
        print "Unknown exception:", e, url

def soupImgs(url):
    c=urlopen(url)
    soup=BeautifulSoup(c.read( ), "html.parser")
    return soup("img")

def dlImgs(urls, dst_dir):
    SCRAPING_REQUEST_STAGGER = 1.0 # in seconds
    for img_url in urls:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), dst_dir)
        filename = os.path.join(directory, os.path.basename(img_url))
        if not os.path.exists(filename):
            dlfile(img_url, filename)
            # todo. stagger by domain instead of on every request
            time.sleep(SCRAPING_REQUEST_STAGGER)
        else:
            print "File already downloaded: skipping", img_url

def getImgURL(imgs):
    urls = []
    for img in imgs:
        urls.append(img["src"])
    return urls

def main():
    url = sys.argv[1]
    imgs = soupImgs(url)
    imgs_urls = getImgURL(imgs)
    dlImgs(imgs_urls, "tmp")

if __name__ == "__main__":
    main()
