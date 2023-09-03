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


class RandomBytes(object):
	def __init__(self):
		fname = os.getenv('ECSIMPLE_RANDFILE')
		self.fname = fname
		if self.fname is not None:
			with open(self.fname,'rb'):
				self.fbytes = b''
				while True:
					retb = read(self.fp,1024)
					if retb is None or len(retb) == 0:
						break
					self.fbytes += retb
			self.curidx = 0
		else:
			self.fbytes = None
			self.curidx = -1
	def get_bytes(bsize):
		if self.fbytes is None:
			retb = os.urandom(bsize)
		else:
			if (self.curidx + bsize) < len(self.fbytes):
				retb=  self.fbytes[self.curidx:(self.curidx + bsize)]
				self.curidx += bsize
			else:
				raise Exception('[%d] + [%d] > [%d]'%(self.curidx,bsize,len(self.fbytes)))
		return retb


DEFAULT_RANDOP=None

def ec_random(bsize):
	global DEFAULT_RANDOP
	if DEFAULT_RANDOP is None:
		DEFAULT_RANDOP = RandomBytes()
	return DEFAULT_RANDOP.get_bytes(bsize)


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
	if args.ecpriv is None:
		rets = fileop.format_bytes(rb,'privatekey')
		fileop.write_file(rets,args.ecpriv)
	else:
		fileop.write_file_bytes(rb,args.ecpriv)
	rb =  pk.to_string()
	if args.ecpub is None:
		rets = fileop.format_bytes(rb,'publickey')
		fileop.write_file(rets,args.ecpub)
	else:
		fileop.write_file_bytes(rb,args.ecpub)
	sys.exit(0)
	return


def ecp224sign_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file_bytes(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	sk = ecdsa.SigningKey.from_string(keyb,curve=ecdsa.NIST224p)
	sig = sk.sign(conb)
	rets = fileop.format_bytes(sig,'signature')
	fileop.write_file(rets,None)
	fileop.write_file_bytes(sig,args.output)
	sys.exit(0)
	return

def ecp224vfy_handler(args,parser):
	loglib.set_logging(args)
	keyb = fileop.read_file_bytes(args.subnargs[0])
	conb = fileop.read_file_bytes(args.subnargs[1])
	signb = fileop.read_file_bytes(args.subnargs[2])
	pk = ecdsa.VerifyingKey.from_string(keyb,curve=ecdsa.NIST224p)
	retb = pk.verify(signb,conb)
	sys.stdout.write('retb %s\n'%(retb))
	sys.exit(0)
	return

def ecp224gen_handler(args,parser):
	loglib.set_logging(args)
	if len(args.subnargs) > 0:
		secnum = fileop.parse_int(args.subnargs[0])
		sk = ecdsa.SigningKey.from_secret_exponent(secnum,ecdsa.NIST224p)
	else:
		sk = ecdsa.SigningKey.generate(ecdsa.NIST224p)
	pk = sk.get_verifying_key()
	rb  = sk.to_string()
	if args.ecpriv is None:
		rets = fileop.format_bytes(rb,'privatekey')
		fileop.write_file(rets,args.ecpriv)
	else:
		fileop.write_file_bytes(rb,args.ecpriv)
	rb =  pk.to_string()
	if args.ecpub is None:
		rets = fileop.format_bytes(rb,'publickey')
		fileop.write_file(rets,args.ecpub)
	else:
		fileop.write_file_bytes(rb,args.ecpub)
	sys.exit(0)
	return


def main():
	commandline='''
	{
		"input|i" : null,
		"output|o" : null,
		"ecpriv" : null,
		"ecpub" : null,
		"ecp256sign<ecp256sign_handler>##key.bin content.bin to sign in ecdsa##" : {
			"$" : 2
		},
		"ecp256vfy<ecp256vfy_handler>##key.bin content.bin sign.bin to verify ecdsa##" : {
			"$" : 3
		},
		"ecp256gen<ecp256gen_handler>##to generate gen##" : {
			"$" : 0
		},
		"ecp224sign<ecp224sign_handler>##key.bin content.bin to sign in ecdsa##" : {
			"$" : 2
		},
		"ecp224vfy<ecp224vfy_handler>##key.bin content.bin sign.bin to verify ecdsa##" : {
			"$" : 3
		},
		"ecp224gen<ecp224gen_handler>##to generate gen##" : {
			"$" : 0
		}	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser = loglib.load_log_commandline(parser)
	parser.parse_command_line(None,parser)
	raise Exception('can not reach here')
	return

if __name__ == '__main__':
	main()