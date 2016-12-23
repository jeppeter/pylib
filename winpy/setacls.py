#! python


import sys
import os
import extargsparse
import subprocess
import logging
import platform


WIN_MAX_PATH=255

def run_cmd(cmd):
	logging.info('run %s'%(cmd))
	nullfd = open('NUL','w')
	subprocess.check_call(cmd,stdout=nullfd)
	nullfd.close()
	return

def set_owner(filedir,args,isfile):
	cmds = []
	cmds.append('icacls')
	cmds.append(filedir)
	cmds.append('/setowner')
	cmds.append(args.owner)	
	run_cmd(cmds)
	return False



def dir_walk(directory,callback,ctx):
	for root,subdirs,files in os.walk(directory):
		for d in subdirs:
			if callback is not None:
				curd = os.path.join(root,d)
				cont = callback(curd,ctx,False)
				if cont :
					return
		for f in files:
			if callback is not None:
				curf = os.path.join(root,f)
				cont = callback(curf,ctx,True)
				if cont :
					return
	return


def get_grant(filedir):
	retdict = dict()
	abspath = os.path.abspath(filedir)
	if len(abspath) > WIN_MAX_PATH:
		logging.error('(%s) path so long'%(abspath))
		return retdict
	cmds = []
	cmds.append('icacls')
	cmds.append(abspath)
	icacls = subprocess.Popen(cmds,stdout=subprocess.PIPE,stderr=None)
	retlines = icacls.stdout.readlines()
	if len(retlines) < 1:
		raise Exception('can not get %s icacls'%(abspath))
	logging.info('retlines %d'%(len(retlines)))
	i = 0
	patexpr = re.compile('\(([^\)]+)\)')
	while i < (len(retlines) - 1):
		l = retlines[i]
		i += 1
		l = l.rstrip('\r\n')
		l = l.replace(abspath,'',1)
		l = re.sub('^\s+','',l)
		sarr = re.split(':',l)
		if len(sarr) < 2:
			logging.error('can not get for (%s)'%(l))
			continue
		username = sarr[0]
		m = patexpr.findall(l)
		if username not in retdict.keys():
			retdict[username] = dict()
		if len(m) > 0:
			appends = []
			grantname = 'GRANT'
			if 'DENY' in m :
				grantname = 'DENY'
			if grantname in retdict[username].keys():
				appends = retdict[username][grantname]
			for c in m:
				if c == 'DENY' or c == 'GRANT':
					continue
				if c not in appends:
					appends.append(c)
			retdict[username][grantname] = appends
	for username in retdict.keys():
		# we fixup the grants
		if 'DENY' in retdict[username].keys():
			denies = retdict[username]['DENY']
			grants = []
			if 'GRANT' in retdict[username].keys():
				grants = retdict[username]['GRANT']
			for c in denies:
				if c in grants:
					grants.remove(c)
			retdict[username]['GRANT'] = grants
	return retdict


def takeown(args,directory,ownname,isrecursive=False):
	cmds = []
	cmds.append('takeown.exe')
	cmds.append('/F')
	cmds.append(directory)
	if isrecursive:
		cmds.append('/R')
	run_cmd(cmds)
	#if isrecursive:
	#	dir_walk(directory,set_owner,args)
	#else:
	#	set_owner(directory,args,True)
	return

def set_grant_callback(filedir,ownname,isfile):
	cmds = []
	abspath = os.path.abspath(filedir)
	if len(abspath) > WIN_MAX_PATH:
		logging.error('(%s) path so long'%(abspath))
		return False
	cmds.append('icacls.exe')
	cmds.append(filedir)
	# remove inheritance
	cmds.append('/inheritance:r')
	# to set grant
	cmds.append('/grant:r')
	cmds.append('%s:F'%(ownname))
	run_cmd(cmds)
	return False


def set_grant(args,directory,ownname,isrecursive=False):
	if isrecursive:
		dir_walk(directory,set_grant_callback,ownname)
	else:
		set_grant_callback(directory,args,ownname)
	return

def set_log_level(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    elif args.verbose >= 1 :
        loglvl = logging.WARN
    # we delete old handlers ,and set new handler
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return


def main():
	commandline='''
	{
		"owner|o" : null,
		"recursive|R" : true,
		"verbose|v" : "+",
		"$" : "+"
	}
	'''
	options = extargsparse.ExtArgsOptions()
	options.errorhandle = 'raise'
	parser = extargsparse.ExtArgsParse(options)
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line()
	if args.owner is None:
		if 'USERNAME' in os.environ.keys():
			args.owner = '%s\\%s'%(platform.node(),os.environ['USERNAME'])
		else:
			try:
				import getpass
				args.owner = '%s\\%s'%(platform.node(),getpass.getuser())
			except:
				raise Exception('can not getpass')
	set_log_level(args)
	for d in args.args:
		takeown(args,d,args.owner,args.recursive)
		set_grant(args,d,args.owner,args.recursive)
	return

if __name__ == '__main__':
	main()
