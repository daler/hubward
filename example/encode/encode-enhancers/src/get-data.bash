#!/bin/bash
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
(
    cd $HERE/../raw-data
    wget http://compbio.med.harvard.edu/modencode/webpage/enh_calls_final/comparative_enhancer_calls.tar.gz
    tar -xzvf comparative_enhancer_calls.tar.gz
    rm comparative_enhancer_calls.tar.gz
)
