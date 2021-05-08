#!/usr/bin/env bash

apt update
apt upgrade
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa
apt update

apt install python3.9
apt install python3.9-distutils

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

update-alternatives --remove python /usr/bin/python2
update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1