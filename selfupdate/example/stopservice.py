

def disable_main_svc(args):
	retval = False
	try:
		cmds = ['systemctl','disable','selfsvc.service']
		nret = subprocess.call(cmds)
		logging.info('run %s nret %s'%(cmds,nret))
		if nret != 0:
			retval = False
			return retval
		else:
			retval = True
		svcfile = '/etc/systemd/system/selfsvc.service'
		os.remove(svcfile)		
	except:
		logging.error('%s'%(traceback.format_exc()))
		retval = False
	return retval

UPDATE_SVC_FILE='''
[Unit]
Description=selfupdate  service
After=network.target
Requires=

[Service]
ExecStart=python3 %UPDATE_FILE% updatesvc
Type=forking
User=root

[Install]
WantedBy=default.target

'''

def inst_update_svc(args):
	global UPDATE_SVC_FILE
	retval = False
	bfile = os.path.basename(__file__)
	outf = os.path.join(args.svcdir,bfile)
	logging.info('outf [%s]'%(outf))
	outs = UPDATE_SVC_FILE.replace('%UPDATE_FILE%',outf,-1)
	logging.info('outs\n%s'%(outs))
	svcfile = '/etc/systemd/system/selfupdate.service'
	try:
		write_file(outs,svcfile)
		cmds = ['systemctl','daemon-reload']
		nret = subprocess.call(cmds)
		logging.info('call %s nret [%s]'%(cmds,nret))
		cmds = ['systemctl','enable','selfupdate.service']
		nret = subprocess.call(cmds)
		logging.info('call %s nret [%s]'%(cmds,nret))
		retval = True
	except:
		logging.error('%s'%(traceback.format_exc()))
		retval = False
	return retval

def remove_update_svc(args):
	svcfile = '/etc/systemd/system/selfupdate.service'
	retval = False
	try:
		cmds = ['systemctl','disable','selfupdate.service']
		nret = subprocess.call(cmds)
		logging.info('call %s nret [%s]'%(cmds,nret))
		os.remove(svcfile)
		cmds = ['systemctl','daemon-reload']
		nret = subprocess.call(cmds)
		logging.info('call %s nret [%s]'%(cmds,nret))
		retval = True
	except:
		logging.error('%s'%(traceback.format_exc()))
		retval = False
	return retval

def check_main_svc(args):
	mainsvcfile = '/etc/systemd/system/selfsvc.service'
	lnfile = '/etc/systemd/system/default.target.wants/selfsvc.service'
	if os.path.exists(mainsvcfile) or os.path.exists(lnfile):
		return True
	return False
