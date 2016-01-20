#!/bin/bash


set -e
set -x

conda config --add channels r
conda config --add channels bioconda

git clone https://github.com/daler/hubward-studies.git /tmp/hubward-studies
conda install -y --file /tmp/hubward-studies/requirements.txt

# make a copy of everything to avoid making changes in the current directory
(cd .. && cp -r hubward /tmp/hubward)

cd /tmp/hubward

# Finally run the example
conda install -y --file conda-requirements.txt --file requirements.txt

# Install hubward
python setup.py install

# SSH (to localhost) setup
service ssh start
mkdir -p /root/.ssh
ssh-keygen -f /root/.ssh/id_rsa -N ""
ssh-keyscan -H localhost >> /root/.ssh/known_hosts
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys


cd /tmp/hubward-studies/test
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


# check existence of expected files after "upload"
for _filename in \
    lieberman2009.html \
    lieberman2009Anchor_bin.bigBed \
    lieberman2009HiC_chr1152000005299999.bigWig \
    lieberman2009Paired_interactions.bam \
    lieberman2009Paired_interactions.bam.bai \
    trackDb.txt \
    yip2012.html \
    yip2012K562_DRME.bigBed \
    yip2012K562_DRMWE.bigBed \
; do
    filename="$(pwd)/hg19/$_filename"
    [[ -f $filename ]] || (echo "$filename not found"; exit 1)
done
[[ -f "$(pwd)/uploaded_hub" ]] || (echo "$(pwd)/uploaded_hub not found"; exit 1)

rm group.yaml


# Ensure the skeleton itself works
cd /tmp
hubward skeleton demo1
hubward process demo1
hubward upload demo1/example-group.yaml --user root
rm -r demo1

# Skeleton with metadata-builder
hubward skeleton --use-metadata-builder demo2
hubward process demo2
hubward upload demo2/example-group.yaml --user root
rm -r demo2
