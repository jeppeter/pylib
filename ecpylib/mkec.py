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
	keyb = fileop.read_file(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	sk = ellipticcurve.privateKey.PrivateKey.fromString(keyb)
	sig = ellipticcurve.ecdsa.Ecdsa.sign(conb,sk)
	rets = 'signature\n'
	rets += sig.toBase64()
	rets += '\n'
	fileop.write_file(rets,None)
	fileop.write_file(sig.toBase64(),args.output)
	sys.exit(0)
	return

def ecp256vfy_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	signb = fileop.read_file(args.subnargs[2])
	pk = ellipticcurve.publicKey.PublicKey.fromString(keyb)
	signv = ellipticcurve.signature.Signature.fromBase64(signb)
	retv = ellipticcurve.ecdsa.Ecdsa.verify(conb,signv,pk)
	sys.stdout.write('retb %s\n'%(retv))
	sys.exit(0)
	return

def ecp256gen_handler(args,parser):
	loglib.set_logging(args)
	sk = ellipticcurve.privateKey.PrivateKey()
	pk = sk.publicKey()
	rets = 'privatekey\n'
	rets += sk.toString()
	rets += '\n'
	fileop.write_file(rets,None)
	rets = 'publicKey\n'
	rets += pk.toString()
	rets += '\n'
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