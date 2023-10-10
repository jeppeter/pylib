#! /bin/bash

scriptfile=`readlink -f $0`
scriptdir=`dirname $scriptfile`
indir=/mnt/zdisk/
infile=$indir/rust_ecgen.bat
outdir=/mnt/zdisk/
pythonfile=$scriptdir/formatcode.py

python $pythonfile -i $infile -o $outdir/ssl_ecload.sh fmtsslecload
python $pythonfile -i $infile -o $outdir/ssl_diff.sh fmtssldiff
