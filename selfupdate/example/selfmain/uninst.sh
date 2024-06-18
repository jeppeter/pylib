#! /bin/sh

fname=`readlink -f $0`
dname=`/usr/bin/dirname $fname`
echo "fname [$fname] dname [$dname]"

systemctl --no-ask-password disable selfsvc.service
rm -f /etc/systemd/system/selfsvc.service
systemctl --no-ask-password daemon-reload
systemctl --no-ask-password reset-failed

echo "dname [$dname]"
rm -rf $dname
exit 0

