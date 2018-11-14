#! /bin/sh

# to generate the file for sshcmd.py

_keyfile="private.key"
_rsafile="private.rsa"

if [ $# -gt 0 ]
	then
	_keyfile=$1
	shift
fi

if [ $# -gt 0 ]
	then
	_rsafile=$1
	shift
fi

openssl genrsa -out "$_keyfile" 2048
openssl rsa -in "$_keyfile" -out "$_rsafile"