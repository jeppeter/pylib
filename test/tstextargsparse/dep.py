#!/usr/bin/python

import os
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))
import extargsparse

def set_log_level(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	elif args.verbose >= 1 :
		loglvl = logging.WARN
	# we delete old handlers ,and set new handler
	delone = True
	logger = logging.getLogger()
	while delone:
		delone = False
		for hdl in logger.handlers:
			logger.removeHandler(hdl)
			delone = True	
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return


def dep_handler(args,context):
	set_log_level(args)
	logging.info('get dep')
	sys.exit(0)
	return

def rdep_handler(args,context):
	set_log_level(args)
	logging.info('get rdep')
	sys.exit(0)
	return

def inst_handler(args,context):
	set_log_level(args)
	logging.info('get inst')
	sys.exit(0)
	return

def rc_handler(args,context):
	set_log_level(args)
	logging.info('get rc')
	sys.exit(0)
	return

def debdep_handler(args,context):
	set_log_level(args)
	logging.info('get debdep')
	sys.exit(0)
	return

def debname_handler(args,context):
	set_log_level(args)
	logging.info('get debname')
	sys.exit(0)
	return

def essentials_handler(args,context):
	set_log_level(args)
	logging.info('get essentials')
	sys.exit(0)
	return

def prepare_handler(args,context):
	set_log_level(args)
	logging.info('prepare handler')
	sys.exit(0)
	return

dpkg_dep_commandline = {
	'dep<__main__.dep_handler>## get dpkg depend ##' : {
		'$' : '+'
	},
	'rdep<__main__.rdep_handler>## get dpkg rdepndend ##' : {
		'$' : '+'
	},
	'inst<__main__.inst_handler>## list all install for dpkg ##':{
		'$' : 0
	},
	'rc<__main__.rc_handler>## list all rc mode packages ##' : {
		'$' : 0
	},
	'essentials<__main__.essentials_handler>## list all essentials package ##' : {
		'$' : 0
	},
	'debdep<__main__.debdep_handler>## list dependend for the .deb file ##' : {
		'$' : '+'
	},
	'debname<__main__.debname_handler>## list package name for .deb file ##' : {
		'$' : '+'
	},
	'prepare<__main__.prepare_handler>## to make prepare for every running ##' : {
		'$' : 0
	}
}

dpkg_const_keywords = {
	'root' : '/',
	'dpkg' : 'dpkg',
	'aptcache': 'apt-cache',
	'aptget' : 'apt-get',
	'cat' : 'cat',
	'rm' : 'rm',
	'sudoprefix' : 'sudo',
	'trymode' : False,
	'mount' : 'mount',
	'umount' : 'umount',
	'chroot' : 'chroot',
	'chown' : 'chown',
	'chmod' : 'chmod',
	'jsonfile' : None ,
	'rollback' : True,
	'reserved' : False
}

dpkg_command_line = {
	'verbose|v' : '+',
	'+dpkg' : dpkg_const_keywords
}


def main():
	usage_str='%s '%(sys.argv[0])
	parser = extargsparse.ExtArgsParse(description='dpkg encapsulation',usage=usage_str)
	parser.load_command_line(dpkg_dep_commandline)
	parser.load_command_line(dpkg_command_line)
	args = parser.parse_command_line()
	return

if __name__ == '__main__':
	main()