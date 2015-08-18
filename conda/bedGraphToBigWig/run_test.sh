cat > chromsizes << EOF
chr1	1000
EOF

cat > a.bed << EOF
chr1	1	5	0.5
chr1	10	20	100.2
EOF

bedGraphToBigWig a.bed chromsizes a.bw
