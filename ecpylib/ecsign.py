#! /usr/bin/env python

import ecdsa
import extargsparse
import logging
import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
import fileop
import loglib



def ecp256sign_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file_bytes(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	sk = ecdsa.SigningKey.from_string(keyb,curve=ecdsa.NIST256p)
	sig = sk.sign(conb)
	rets = fileop.format_bytes(sig,'signature')
	fileop.write_file(rets,args.output)
	sys.exit(0)
	return

def ecp256vfy_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file_bytes(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	signb = fileop.read_file_bytes(args.subnargs[2])
	sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
	pk = sk.get_verifying_key()
	retb = pk.verify(conb,signb)
	sys.stdout.write('retb %s\n'%(retb))
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