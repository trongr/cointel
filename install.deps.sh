#!/bin/bash

mkdir -p deps
cd deps

wget https://pypi.python.org/packages/source/f/feedparser/feedparser-5.2.1.tar.gz
tar xvfz feedparser-5.2.1.tar.gz

cd feedparser-5.2.1
sudo python setup.py install

cd ..
sudo rm -rf feedparser-5.2.1*
