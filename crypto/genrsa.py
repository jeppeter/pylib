#!/usr/bin/python

import os
import sys
import math
import extargsparse
import logging

def get_prime_number(num=2048):
	primes = [2,3,5,7]
	curnum = 8

	while len(primes) < num:
		isprime = True
		for i in xrange(len(primes)):
			if (primes[i] ** 2) > curnum:
				break
			if (curnum % primes[i]) == 0:
				isprime = False
				break

		if isprime:
			primes.append(curnum)
			if (len(primes) % 10000) == 0:
				sys.stdout.write('.')
				sys.stdout.flush()
			if (len(primes) % 100000) == 0:
				sys.stdout.write('\n')
		curnum += 1
	return primes

def log_set(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	elif args.verbose >= 1 :
		loglvl = logging.WARNING
	# we delete old handlers ,and set new handler
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def prime_handler(args,context):
	log_set(args)
	logging.info('args context %s'%(args.subnargs))
	primes = get_prime_number(int(args.subnargs[0]))
	sys.stdout.write('static int prime[%s] = {'%(args.subnargs[0]))
	i = 0
	for p in primes:
		if (i % 6) == 0:
			sys.stdout.write(' /* 0x%08x */\n\t'%(i))
			sys.stdout.write('%08d'%(p))
		else:
			sys.stdout.write(',%08d'%(p))
		i += 1

	sys.stdout.write('\n};\n')
	sys.exit(0)
	return

def main():
	d = {
		'verbose|v' : '+',
		'prime<prime_handler>## [num] get prime in number ##' : {
			'$' : 1
		}
	}

	parser = extargsparse.ExtArgsParse(usage='%s num')
	parser.load_command_line(d)
	args = parser.parse_command_line()
	return

if __name__ == '__main__':
	main()