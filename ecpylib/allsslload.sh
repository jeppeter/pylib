#! /bin/bash

scriptfile=`readlink -f $0`
scriptdir=`dirname $scriptfile`
outdir=/mnt/zdisk/

sh $outdir/ssl_ecload.sh && sh $outdir/ssl_diff.sh