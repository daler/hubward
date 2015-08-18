#!/bin/bash
set -x
echo $(pwd)
BIN=$PREFIX/bin
mkdir -p $BIN
cp bedToBigBed $BIN
chmod +x $BIN/bedToBigBed
