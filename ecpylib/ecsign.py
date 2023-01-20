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
	sk = ecdsa.SigningKey.generate(ecdsa.NIST256p)
	pubk = sk.verifying_key.pubkey.generator.order()
	privk = sk.privkey.secret_multiplier
	rets = fileop.format_int_val(privk,'private key')
	fileop.write_file(rets,None)
	rets = fileop.format_int_val(pubk,"public key")
	fileop.write_file(rets,None)
	vc = ecdsa.NIST256p.order
	rets = fileop.format_int_val(pubk,"vc")
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