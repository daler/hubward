#!/bin/bash


set -e
set -x

# Install hubward
python setup.py install

# Example script uses git to track changes; configure it here to avoid warning
# messages
git config --global user.email "none@example.com"
git config --global user.name "hubward-example"

# Write an example config file
cat >> /tmp/test-hubward.yaml <<EOF
hub_url_pattern: "http://localhost/{genome}/compiled/compiled.hub.txt"
hub_remote_pattern: "/root/{genome}/compiled/compiled.hub.txt"
host: localhost
user: root
email: root@localhost
ucsc_cache_dir: .
EOF

# SSH (to localhost) setup
service ssh start
mkdir -p /root/.ssh
ssh-keygen -f /root/.ssh/id_rsa -N ""
ssh-keyscan -H localhost >> /root/.ssh/known_hosts
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

# Finally run the example
./run-example.bash

# Clean up
#rm -r encode encodetracks.hub.txt encodetracks.genomes.txt dm3 /tmp/test-hubward.yaml
