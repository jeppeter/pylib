#! /usr/bin/env python


import extargsparse
import pysftp
import os
import logging

def chdir_sftp(sftp,args):
	if args.remotedir is not None:
		sftp.cd(args.remotedir)
	if args.localdir is not None:
		sftp.lcd(args.localdir)
	return

def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	if logging.root is not None and len(logging.root.handlers) > 0:
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return


def upload_sftp(args,parser):
	set_logging(args)
	with pysftp.Connection(args.host, username=args.username,password = args.password) as sftp:
		chdir_sftp(sftp,args)
		for f in args.subnargs:
			logging.info('upload %s'%(f))
			if os.path.isdir(f):
				sftp.put_d(f)
			else:
				sftp.put(f)
	return

def download_sftp(args,parser):
	set_logging(args)
	with pysftp.Connection(args.host, username=args.username,password = args.password) as  sftp:
		chdir_sftp(sftp,args)
		for f in args.subnargs:
			logging.info('upload %s'%(f))
			if sftp.isdir(f):
				sftp.get_d(f)
			else:
				sftp.get(f)
	return

def main():
	commandline_fmt='''
	{
		"remotedir|R" : null,
		"localdir|L" : null,
		"host|H" : "127.0.0.1",
		"username|u" : "%s",
		"password|p" : "",
		"verbose|v" : "+",
		"download<download_sftp>" : {
			"$" : "+"
		},
		"upload<upload_sftp>" : {
			"$" : "+"
		}

	}
	'''
	commandline = commandline_fmt%(os.getlogin())
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line()
	return

if __name__ == '__main__':
	main()
