#!/bin/bash

mkdir -p deps
cd deps

# Installs pip, so you can install these other packages:
# (Newer python has pip built in).
# wget https://bootstrap.pypa.io/get-pip.py
# sudo python get-pip.py

echo "Installing feedparser"
wget https://pypi.python.org/packages/source/f/feedparser/feedparser-5.2.1.tar.gz
tar xvfz feedparser-5.2.1.tar.gz
cd feedparser-5.2.1
sudo python setup.py install
cd ..
sudo rm -rf feedparser-5.2.1*

echo "Installing PIL"
# Links missing freetype header on osx, for PIL:
ln -s /usr/local/include/freetype2 /usr/local/include/freetype
wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
tar xvfz Imaging-1.1.7.tar.gz
cd Imaging-1.1.7
sudo python setup.py install
cd ..
sudo rm -rf Imaging-1.1.7

echo "Installing BeautifulSoup"
sudo pip install beautifulsoup4
