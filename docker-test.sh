#!/bin/bash


set -e
set -x

(cd .. && cp -r hubward /tmp/hubward)
cd /tmp/hubward

# Install hubward
python setup.py install

# SSH (to localhost) setup
service ssh start
mkdir -p /root/.ssh
ssh-keygen -f /root/.ssh/id_rsa -N ""
ssh-keyscan -H localhost >> /root/.ssh/known_hosts
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

# Finally run the example
git clone https://github.com/daler/hubward-studies.git
cd hubward-studies
hubward process yip-2012
hubward process lieberman-2009

