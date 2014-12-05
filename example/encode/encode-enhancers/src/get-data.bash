#!/bin/bash
# The get-data.bash file usually starts with this, which gets 
# the absolute path to the script.
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute in a subshell:
(
    cd $HERE/../raw-data
    wget http://compbio.med.harvard.edu/modencode/webpage/enh_calls_final/comparative_enhancer_calls.tar.gz
    tar -xzvf comparative_enhancer_calls.tar.gz
)
