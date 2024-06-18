#! /bin/sh

fname=`readlink -f $0`
dnmae=`dirname $fname`

systemctl --no-ask-password disable selfsvc.service
rm -f /etc/systemd/system/selfsvc.service
rm -f /etc/systemd/system/default.target.wants/selfsvc.service
systemctl --no-ask-password daemon-reload
systemctl --no-ask-password reset-failed

rm -rf $dname
exit 0

