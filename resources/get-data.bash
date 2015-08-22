#!/usr/bin/bash
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
(
    cd $HERE/../raw-data
    wget $URL
    # process URL here....
)

