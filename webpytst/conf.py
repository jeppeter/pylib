#! /usr/bin/env python

import web
import extargsparse
import logging
import os
import sys
import json
import re

def set_log_level(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	elif args.verbose >= 1 :
		loglvl = logging.WARN
	# we delete old handlers ,and set new handler
	if logging.root and logging.root.handlers and len(logging.root.handlers) > 0 :
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

class Conf(object):
	def GET(self):
		logging.info('get conf')
		return '''
		{
			"conf":[
				"0":"12345",
				"1": "11:11:11:11:11:11",
				"2": "11:11:11:11:11:12",
				"3": "11:11:11:11:11:13",
				"4": "11:11:11:11:11:14",
				"5": "11:11:11:11:11:15",
				"6": "11:11:11:11:11:16"]}'''

class ConfNum(object):
	def POST(self):
		data = web.data()
		jsonstr = data.decode('utf-8')
		logging.info('data [%s]'%(jsonstr))
		logging.info('path [%s]'%(web.ctx.path))
		return '''
		{
			"conf":[
				"0":"12345",
				"1": "11:11:11:11:11:11",
				"2": "11:11:11:11:11:12",
				"3": "11:11:11:11:11:13",
				"4": "11:11:11:11:11:14",
				"5": "11:11:11:11:11:15",
				"6": "11:11:11:11:11:16"]}'''


class SetIP(object):
	def POST(self):
		if web.ctx.path == '/setip/dhcp':
			logging.info('dhcp')
		elif web.ctx.path == '/setip/static':
			logging.info('static')
		else:
			return '''{
				"msg" : "invalid input"
			}'''
		return '''{
			"msg" : "设置成功，即将重启"
		}'''


class Ipmi(object):
	def GET(self):
		return '''{"password": "123456"}'''

	def POST(self):
		data = web.data()
		jsonstr = data.decode('utf-8')
		passjson = json.loads(jsonstr)
		logging.info('password %s'%(passjson['password']))
		return '''{"msg": "密码设置成功"}'''

class Reboot(object):
	def GET(self):
		return '''{"msg":"即将重启主机"}'''


class StaticFile(object):
	def GET(self,*args):
		logging.info('path [%s] args[%s]'%(web.ctx.path,args))
		logging.info('BASE_STATIC [%s]'%(os.environ['BASE_STATIC']))
		path = web.ctx.path
		if path == '/' :
			path = '/index.html'
		path = path[1:]
		logging.info('path %s'%(path))
		realpath = os.path.join(os.environ['BASE_STATIC'], path)
		logging.info('file [%s]'%(realpath))
		with open(realpath,'r+b') as fin:
			data = fin.read()
			return data.decode('gbk')
		return ''


def main():
	commandline_fmt='''
	{
		"verbose|v" : "+",
		"port|p" : 3000,
		"basedir|B" : "%s"
	}
	'''
	curdir = os.path.abspath(os.path.dirname(__file__))
	curdir = curdir.replace('\\','\\\\')
	commandline=commandline_fmt%(curdir)
	urls = ('/conf', 'Conf',
		'/conf/0','ConfNum',
		'/conf/1','ConfNum',
		'/conf/2','ConfNum',
		'/conf/3','ConfNum',
		'/conf/4','ConfNum',
		'/conf/5','ConfNum',
		'/conf/6','ConfNum',
		'/setip/dhcp','SetIP',
		'/setip/static','SetIP',
		'/reboot', 'Reboot',
		'/ipmi/password_get','Ipmi',
		'/ipmi/password_set','Ipmi',
		'/','StaticFile',
		'/index.html','StaticFile',
		'/(js|css|img|vendor)/(.*)','StaticFile')
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line(None,parser)
	os.environ['PORT'] = '%s'%(args.port)
	os.environ['BASE_STATIC'] = args.basedir
	sys.argv[1:] = []
	sys.argv.append('0.0.0.0')
	set_log_level(args)
	app = web.application(urls,globals())
	app.run()
	return


if __name__ == '__main__':
	main()