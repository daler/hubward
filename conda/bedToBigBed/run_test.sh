cat > chromsizes << EOF
chr1	1000
EOF

cat > a.bed << EOF
chr1	1	5
chr1	10	20
EOF

bedToBigBed a.bed chromsizes a.bb
