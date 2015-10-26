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
cd hubward-studies/test
hubward process yip-2012
hubward process lieberman-2009

hubward liftover \
    --from_assembly hg18 \
    --to_assembly hg19 \
    lieberman-2009 \
    lieberman-2009-hg19

cat > group.yaml << EOF
name: "hubward-example"
genome: "hg19"
short_label: "Hubward example"
long_label: "Hubward example tracks"
hub_url: "http://example.com/hubs/example.hub.txt"
email: "dalerr@niddk.nih.gov"

studies:
    - "yip-2012"
    - "lieberman-2009-hg19"
EOF


hubward upload --host localhost --user root --hub_remote $(pwd)/uploaded_hub group.yaml
rm group.yaml
