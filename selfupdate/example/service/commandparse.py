
def make_default_args():
	js = '''
	{
		"verbose" : 0,
		"reserved" : false,
		"username" : "root",
		"password" : "Bt@2022bmc",
		"reboot" : false,
		"svcdir" : "/usr/bin/selfupdate",
		"instdir" : "/usr/bin/selfsvc",
		"tempfname" : "selfupdate",
		"uploaddir" : "/usr/bin/uploadsvc",
		"tempdname" : "selfmain",
		"uninstname" : "uninst.sh",
		"instname" : "inst.sh"
	}
	'''
	args = NameSpaceEx(js)
	return args


def new_args_parser():
	parser = argparse.ArgumentParser(prog=os.path.basename(os.path.abspath(__file__)).replace('.py',''))
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-R','--reserved',action='store_true',default=False)
	parser.add_argument('-r','--reboot',action='store_true',default=False)
	parser.add_argument('--username',action='store',default='pyuser')
	parser.add_argument('--password',action='store',default='pyuser')
	parser.add_argument('--svcdir',action='store',default='/usr/bin/selfupdate')
	parser.add_argument('--instdir',action='store',default='/usr/bin/selfsvc')
	parser.add_argument('--tempfname',action='store',default='selfupdate')
	parser.add_argument('--tempdname',action='store',default='selfmain')
	parser.add_argument('--uploaddir',action='store',default='/usr/bin/uploadsvc')
	parser.add_argument('--uninstname',action='store',default='uninst.sh')
	parser.add_argument('--instname',action='store',default='inst.sh')
	return parser
