#! /bin/bash

scriptfile=`readlink -f $0`
scriptdir=`dirname $scriptfile`
outdir=/mnt/zdisk/

#ecname=secp112r1
ecname=
times=50
if [ $# -gt 0 ]
then
	ecname=$1
	shift
fi

if [ $# -gt 0 ]
then
	times=$1
	shift
fi


python $scriptdir/formatcode.py -o $outdir/ssl_ecgen.sh -C $times $ecname fmtsslecgen