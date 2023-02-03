#! /usr/bin/env python

import extargsparse
import logging
import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','python-ecdsa','src')))
import fileop
import loglib
import ecdsa



def ecp256sign_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file_bytes(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	sk = ecdsa.SigningKey.from_string(keyb,curve=ecdsa.NIST256p)
	sig = sk.sign(conb)
	rets = fileop.format_bytes(sig,'signature')
	fileop.write_file(rets,None)
	fileop.write_file_bytes(sig,args.output)
	sys.exit(0)
	return

def ecp256vfy_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file_bytes(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	signb = fileop.read_file_bytes(args.subnargs[2])
	pk = ecdsa.VerifyingKey.from_string(keyb,curve=ecdsa.NIST256p)
	retb = pk.verify(signb,conb)
	sys.stdout.write('retb %s\n'%(retb))
	sys.exit(0)
	return

def ecp256gen_handler(args,parser):
	loglib.set_logging(args)
	sk = ecdsa.SigningKey.generate(ecdsa.NIST256p)
	pk = sk.get_verifying_key()
	rb  = sk.to_string()
	rets = fileop.format_bytes(rb,'privatekey')
	fileop.write_file(rets,None)
	rb =  pk.to_string()
	rets = fileop.format_bytes(rb,'publickey')
	fileop.write_file(rets,None)
	sys.exit(0)
	return



def main():
	commandline='''
	{
		"input|i" : null,
		"output|o" : null,
		"ecp256sign<ecp256sign_handler>##key.bin content.bin to sign in ecdsa##" : {
			"$" : 2
		},
		"ecp256vfy<ecp256vfy_handler>##key.bin content.bin sign.bin to verify ecdsa##" : {
			"$" : 3
		},
		"ecp256gen<ecp256gen_handler>##to generate gen##" : {
			"$" : 0
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser = loglib.load_log_commandline(parser)
	parser.parse_command_line(None,parser)
	raise Exception('can not reach here')
	return

if __name__ == '__main__':
	main()