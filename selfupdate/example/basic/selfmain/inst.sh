#! /bin/sh

fname=`readlink -f $0`
dname=`dirname $0`
instdir=/userdata/media/selfsvc
if [ $# -gt 0 ]
then
	instdir=$1
	shift
fi
instdir=`readlink -f $instdir`

if [ "$dname" != "$instdir" ]
then

	if [ ! -d "$instdir" ]
	then
		mkdir -p "$instdir" || (echo "cannot mkdir $instdir" >&2; exit 3)
	fi
	# now to copy 
	cp -f $dname/uninst.sh $instdir/
	cp -f $dname/inst.sh $instdir/
	cp -f $dname/selfmain $instdir/
	cp -f $dname/config.json $instdir/
	if [ -d $instdir/pythonlib ]
	then
		rm -rf $instdir/pythonlib
	fi
	cp -r $dname/pythonlib $instdir/

fi

chmod +x $instdir/uninst.sh
chmod +x $instdir/selfmain
chmod +x $instdir/inst.sh

python $instdir/selfmain outsvc -i $dname/selfsvc.tmpl  -o $instdir/selfsvc -vvvv
chmod +x $instdir/selfsvc
python $instdir/selfmain addcode -vvvvv

exit 0

