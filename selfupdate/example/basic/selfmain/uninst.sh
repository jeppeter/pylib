#! /bin/sh

fname=`readlink -f $0`
dname=`/usr/bin/dirname $fname`
echo "fname [$fname] dname [$dname]"

python $dname/selfmain removecode -vvvv

echo "dname [$dname]"
rm -rf $dname
exit 0

