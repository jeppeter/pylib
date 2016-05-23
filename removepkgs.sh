#!/bin/sh

python3 pylib/dpkg/dpkgrm.py -vvvv --root /home/wrc/source/rescueiso/iso/ubdesk_inst/ rm libgnome-menu-3-0 cups-common  gir1.2-ebookcontacts-1.2 libx11-6 libgnome-keyring0 libqtcore4 libunity9 gir1.2-glib-2.0 qtcore4-l10n  libavahi-common3 libgeoip1 libasound2 network-manager
python3 pylib/dpkg/dpkgrm.py -vvvv --root /home/wrc/source/rescueiso/iso/ubdesk_inst/ rm libsqlite3-0 gcc-4.8-base