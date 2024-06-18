#! /bin/sh

fname=`readlink -f $0`
dname=`dirname $0`
instdir=/usr/bin/selfsvc
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
	cp -f $dname/selfsvc.service.tmpl $instdir/
	cp -f $dname/inst.sh $instdir/
	cp -f $dname/selfmain $instdir/
	cp -f $dname/selfsvc $instdir/
	cp -f $dname/config.json $instdir/

	chmod +x $instdir/uninst.sh
	chmod +x $instdir/selfmain
	chmod +x $instdir/inst.sh
	chmod +x $instdir/selfsvc
fi

#echo "python3 $instdir/selfmain -i $instdir/selfsvc.service.tmpl -o /etc/systemd/system/selfsvc.service outsvc -vvvv $instdir/selfsvc"
python3 $instdir/selfmain -i $instdir/selfsvc.service.tmpl -o /etc/systemd/system/selfsvc.service outsvc $instdir/selfsvc

systemctl --no-ask-password enable selfsvc.service
systemctl --no-ask-password daemon-reload
exit 0

