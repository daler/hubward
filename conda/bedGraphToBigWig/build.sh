#!/bin/bash
set -x
echo $(pwd)
BIN=$PREFIX/bin
mkdir -p $BIN
cp bedGraphToBigWig $BIN
chmod +x $BIN/bedGraphToBigWig
