#! /usr/bin/env python

import extargsparse
import logging
import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','ecdsa-python')))
import fileop
import loglib
import ellipticcurve

def ecp256sign_handler(args,parser):
	loglib.set_logging(args)
	keys = fileop.read_file(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	sk = ellipticcurve.ecdsa.Ecdsa.fromString(keys)
	sig = ellipticcurve.ecdsa.Ecdsa.sign(conb,sk)
	rets = 'signature\n'
	rets += sig.toBase64()
	fileop.write_file(rets,None)
	sys.exit(0)
	return

def ecp256vfy_handler(args,parser):
	loglib.set_logging(args)
	conb = fileop.read_file_bytes(args.subnargs[0])
	signb = fileop.read_file_bytes(args.subnargs[1])
	pk = ecdsa.VerifyingKey()
	pk.curve = ecdsa.NIST256p.curve
	pk.
	retb = pk.verify(conb,signb)
	sys.stdout.write('retb %s\n'%(retb))
	sys.exit(0)
	return

def ecp256gen_handler(args,parser):
	loglib.set_logging(args)
	sk = ellipticcurve.privateKey.PrivateKey()
	pk = sk.publicKey()
	rets = 'privateKey\n'
	rets += sk.toString()	
	fileop.write_file(rets,None)
	rets = 'publicKey\n'
	rets += pk.toString()
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
		"ecp256vfy<ecp256vfy_handler>##content.bin sign.bin to verify ecdsa##" : {
			"$" : 2
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