#! /usr/bin/env python

import extargsparse
import sys
import logging

class BinPol:
    """Binary polinomy.

    This class represents a binary polinomy, as well as the defined operations
    in Z2. Note that not every possible operation is implemented, but only the
    needed to generate the AES related tables (see project description).

    """

    def __init__(self, x, irreducible_polynomial=None, grade=None):
        self.dec = x
        self.hex = hex(self.dec)[2:]
        self.bin = reversed(list(bin(self.dec)[2:]))
        self.bin = [int(bit) for bit in self.bin]

        if grade is not None:
            self.grade = grade
        else:
            self.grade = len(self.bin)-1

        self.irreducible_polynomial = irreducible_polynomial

    def __str__(self):
        h = self.hex
        if self.dec < 16:
            h = '0' + h
        return h

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.grade

    def __setitem__(self, key, value):
        if value in [0, 1]:
            while len(self.bin) <= key:
                self.bin.append(0)
            self.bin[key] = value
        self.__update_from_bin()

    def __getitem__(self, key):
        if key < len(self.bin):
            return self.bin[key]
        else:
            return 0

    def __add__(self, x):
        r = BinPol(self.dec, self.irreducible_polynomial)
        for i, a in enumerate(x.bin):
            r[i] = r[i] ^ a
        r.__update_from_bin()
        return r

    def __mul__(self, x):
        r = BinPol(0, self.irreducible_polynomial)
        for i, a in enumerate(self.bin):
            for j, b in enumerate(x.bin):
                if a and b:
                    logging.info('[%d]a[%d]b [%s]'%(i,j,r[i+j]))
                    r[i+j] = r[i+j] ^ 1
        #r.__update_from_bin()
        return r

    def __pow__(self, x):
        r = BinPol(1, self.irreducible_polynomial)
        for i in range(1, x+1):
            r = r * BinPol(self.dec)
            logging.info('[%s][%03d][%s]'%(x,i,r))
            #r.__update_from_bin()
            if (r.irreducible_polynomial
                    and r.grade >= r.irreducible_polynomial.grade):
                last = r
                r = r + r.irreducible_polynomial
                #r.__update_from_bin()
                logging.info('[%s][%03d][%s] => [%s]([%s])'%(x,i,last,r,r.irreducible_polynomial))

        return r

    def __update_from_bin(self):
        self.__remove_most_significant_zeros()
        self.dec = 0
        for i, a in enumerate(self.bin):
            if a:
                self.dec += 2**i
        self.hex = hex(self.dec)[2:]
        self.grade = len(self.bin)-1

    def __remove_most_significant_zeros(self):
        last = 0
        for i, a in enumerate(self.bin):
            if a:
                last = i
        del(self.bin[last+1:])


def get_8bit(b):
	return b & 0xff

def gmul(a,b):
	p = 0
	i = 0
	while i < 8:
		if b & 0x1:
			p = p ^ a
		hibit = a & 0x80;
		a <<= 1
		a = get_8bit(a)
		if hibit:
			# this 0x1b is x^4 + x^3 + x + 1 mod x^8 + x^4 + x^3 + x + 1 = x^8
			a = a ^ 0x1b
		b >>= 1
		b = get_8bit(b)
		i = i + 1
	return p

def set_log_level(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	elif args.verbose >= 1 :
		loglvl = logging.WARN
	# we delete old handlers ,and set new handler
	if logging.root is not None and logging.root.handlers is not None and len(logging.root.handlers) > 0:
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def parse_int(r):
	rint = 0
	base=10
	if r.startswith('x') or r.startswith('X'):
		base=16
		r = r[1:]
	elif r.startswith('0x') or r.startswith('0X'):
		base = 16
		r = r[2:]
	rint = int(r,base)
	return rint

def format_result(a,b,p):
	return '[%03d,%03d][%03d]'%(a,b,p)

def format_array_result(arr,p):
	s = '['
	i = 0
	while i < len(arr):
		c = parse_int(arr[i])
		if i > 0:
			s += ','
		s += '%03d'%(c)
		i = i + 1
	s += ']'
	s += '[%03d]'%(p)
	return s

def mul_handler(args,parser):
	set_log_level(args)
	if len(args.subnargs) < 2:
		raise Exception('must at least 2 args')
	a = parse_int(args.subnargs[0])
	b = parse_int(args.subnargs[1])
	p = gmul(a,b)
	k = 2
	while k < len(args.subnargs):
		c = parse_int(args.subnargs[k])
		p = gmul(p,c)
		k = k + 1
	sys.stdout.write(format_array_result(args.subnargs,p))
	sys.stdout.write('\n')
	sys.exit(0)
	return

def exp(bnum,num):
	if num == 0:
		return 1
	rnum = bnum
	for i in range(1,num):
		rnum = gmul(rnum ,bnum)
	return rnum

def explist_handler(args,parser):
	set_log_level(args)
	bnum = parse_int(args.subnargs[0])
	k = 1
	s = ''
	s += '[%02x'%(1)
	for i in range(1,256):
		p = exp(bnum,i)
		if k > 0:
			s += ','
		else:
			if i > 0:
				s += ',\n'
			s += '['
		s += '%02x'%(p)
		k = k + 1
		if k >= 16:
			s += ']'
			k = 0
	if k > 0:
		s += ']\n'
	sys.stdout.write(s)
	sys.exit(0)
	return

def generate_altable(gnum):
	atable = []
	ltable = []
	for i in range(256):
		atable.append(exp(gnum,i))
		ltable.append(0)
	cnt = 0
	while cnt < 256:
		ltable[atable[cnt]] =  cnt
		cnt = cnt + 1
	return atable, ltable

def format_table(tbl,note):
	s = ''
	s += '%s = \n'%(note)
	k = 0
	j = 0
	while k < len(tbl):
		if j > 0 :
			s += ','
		else:
			if k > 0:
				s += ',\n'
			s += '['
		s += '0x%02x'%(tbl[k])
		j = j + 1
		if j >= 16:
			j = 0
			s += ']'
		k = k + 1
	return s

def altable_handler(args,parser):
	set_log_level(args)
	gnum = parse_int(args.subnargs[0])
	atable ,ltable = generate_altable(gnum)
	s = format_table(atable,'atable')
	sys.stdout.write('%s\n'%(s))
	s = format_table(ltable,'ltable')
	sys.stdout.write('%s\n'%(s))
	sys.exit(0)
	return


def exp_handler(args,parser):
	set_log_level(args)
	bnum = parse_int(args.subnargs[0])
	enum = parse_int(args.subnargs[1])
	irr = BinPol(0b100011011)
	base = BinPol(bnum,irr)
	base **= enum
	sys.stdout.write('%03d ** %03d = %s'%(bnum,enum,base))
	sys.exit(0)
	return

def inv_table(atbl,ltbl):
	invtabl = [ 0 for i in  range(256)]
	for i in range(1,256):
		invtabl[i] = atbl[0xff - ltbl[i]]
	return invtabl

def get_invtable(bnum):
	atable,ltable = generate_altable(bnum)
	invtable = inv_table(atable,ltable)
	return invtable

def inv_handler(args,parser):
	set_log_level(args)
	bnum = parse_int(args.subnargs[0])
	invtable = get_invtable(bnum)
	s = format_table(invtable,'invtable')
	sys.stdout.write('%s\n'%(s))
	sys.exit(0)
	return

def set_bit_xor(origbit,s):
	if origbit:
		origbit = 1
	if s :
		origbit ^= 1
	else:
		origbit ^= 0
	return origbit

def sbox_table(bnum,cival):
	invtable = get_invtable(bnum)
	i = 0
	sbox = []
	while i < len(invtable):
		k = 0
		curval = invtable[i]
		tval = 0
		while k < 8:
			kbit = 0
			kbit = set_bit_xor(kbit,(curval & ( 1 << k)))
			kbit = set_bit_xor(kbit,(curval & ( 1 << ((k+4)%8))))
			kbit = set_bit_xor(kbit,(curval & (1 << ((k+5)%8))))
			kbit = set_bit_xor(kbit,(curval & (1 << ((k+6)%8))))
			kbit = set_bit_xor(kbit,(curval & (1 << ((k+7)%8))))
			kbit = set_bit_xor(kbit,cival & (1 << k))
			if kbit :
				tval |= (1 << k)
			k = k + 1
		logging.info('[%s][%02x] ^ [%02x] = [%02x]'%(i,invtable[i], cival,tval))
		sbox.append(tval)
		i = i + 1
	return sbox

def sbox_handler(args,parser):
	set_log_level(args)
	bnum = parse_int(args.subnargs[0])
	sboxtbl = sbox_table(bnum,0x63)
	s = format_table(sboxtbl, 'sbox')
	sys.stdout.write('%s\n'%(s))
	invtable = get_invtable(bnum)
	sys.exit(0)
	return


def main():
	commandline='''
	{
		"verbose|v" : "+",
		"mul<mul_handler>" : {
			"$" : "+"
		},
		"explist<explist_handler>" : {
			"$" : 1
		},
		"altable<altable_handler>" : {
			"$" : 1
		},
		"exp<exp_handler>" : {
			"$" : 2
		},
		"inv<inv_handler>" : {
			"$" : 1
		},
		"sbox<sbox_handler>" : {
			"$" : 1
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	raise Exception('unknown subcommand[%s]'%(args.subcommand))
	return


if __name__ == '__main__':
	main()
