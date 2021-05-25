#!/usr/bin/env bash

sudo apt install python3-pip python3-gi python3-libdiscid python3-distutils
pip3 install -r requirements.txt
sudo python3 setup.py install
