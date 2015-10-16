#!/bin/bash

src=$1
target=$2
sortedbed=/tmp/$(basename ${target}).tmp
chromsizes=/tmp/dm3.genome

tail -n +2 $src \
    | awk -F "\t" '{OFS="\t"; print $1,$2,$3 + 1}' \
    | sort -k1,1 -k2,2n > $sortedbed

mysql --user=genome --host=genome-mysql.cse.ucsc.edu -A -e \
    "select chrom, size from dm3.chromInfo" > $chromsizes

bedToBigBed -type=bed3 $sortedbed $chromsizes $target
rm $sortedbed $chromsizes

