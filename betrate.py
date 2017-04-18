#! /usr/bin/env python

import extargsparse
import math


def get_result(losecnt,wincnt,loseratio,winratio):
	assert(loseratio >= 0.0)
	assert(winratio >= 0.0)
	#print('loseratio %s winratio %s'%(loseratio,winratio))
	shv = math.log(loseratio)
	exv = math.log(winratio)
	return math.exp(exv * wincnt + shv * losecnt)

def caculate_number(startlose,startwin,losecnt,wincnt,expval,epsilon = 0.00001):
	loseratio = startlose
	winratio = startwin
	lshr = 0.0
	hshr = 1.0
	lexr = 1.0
	hexr = math.ceil(math.exp(math.log(expval)/wincnt*10))	
	if hexr < winratio:
		hexr = winratio * 10
	if winratio < lexr:
		winratio = lexr
		hexr = lexr
	if loseratio < lshr or loseratio > hshr:
		loseratio = (lshr + hshr) / 2
	while True:
		if math.fabs(loseratio - lshr) < epsilon and \
			math.fabs(loseratio - hshr) < epsilon and \
			math.fabs(winratio - hexr) < epsilon and \
			math.fabs(winratio - lexr) < epsilon :
			return loseratio,winratio
		res = get_result(losecnt,wincnt,loseratio,winratio)
		#print('loseratio %s winratio %s res %s expval %s'%(loseratio,winratio,res,expval))
		if math.fabs(expval - res) < epsilon:
			return loseratio,winratio
		elif expval < res:
			if math.fabs(lshr - loseratio)  < epsilon:
				tmph = winratio
				winratio = winratio - ((winratio - lexr)/2)
				hexr = tmph
			else:
				hshr = loseratio
				loseratio = loseratio - ((loseratio - lshr) / 2)
		elif expval > res:
			if math.fabs(hshr - loseratio)  < epsilon:
				tmpl = winratio
				winratio = winratio + ((hexr - winratio) / 2)
				lexr = tmpl
			else:
				lshr = loseratio
				loseratio = loseratio + ((hshr - loseratio) / 2)
	return loseratio,winratio


def main():
	commandline='''
	{
		"startwin" : 1.02,
		"startlose" : 0.98,
		"wincnt" : 130,
		"losecnt" : 120,
		"wintotal" : 10.0,
		"epsilon" : 0.00001
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line()
	loseratio ,winratio = caculate_number(args.startlose,args.startwin,args.losecnt,args.wincnt,args.wintotal,args.epsilon)
	print('losecnt %d wincnt %d total %s loseratio %s winratio %s'%(args.losecnt,args.wincnt,args.wintotal,loseratio,winratio))
	print('betrate %s'%(((winratio - 1.0) / (1.0 - loseratio))+1.0))
	print('winrate %s'%(float(args.wincnt) / (float(args.losecnt)+float(args.wincnt))))
	return

main()