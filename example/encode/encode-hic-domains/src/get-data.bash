#!/bin/bash
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
(
   cd $HERE/../raw-data

   # Hi-C domains in embryo
   wget http://compbio.med.harvard.edu/modencode/webpage/hic/HiC_EL.bed
)

