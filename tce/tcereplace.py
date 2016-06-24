#!python

import re
import os
import sys
import argparse
import logging
import hashlib
import tempfile
import pwd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import dbgexp
import cmdpack
import tcebase
import tcedep
import extargsparse

class TceReplace(tcebase.TceBase):
	def __init__(self,args):
		super(TceReplace,self).__init__()
		self.set_tce_attrs(args)
		return

	def trans_var(self,instr):
		outstr = instr
		for p in vars(self):
			if p.startswith('tce_vars_'):
				curk = re.sub('^tce_vars_','', p)
				outstr = re.sub(curk.upper(),getattr(self,p),outstr)
		return outstr

	def trans_deps(self,dmaps):
		outmaps = dmaps
		cont=True
		while cont:
			cont = False
			for k in outmaps.keys():
				curk = self.trans_var(k)
				if k != curk:
					logging.info('delete %s'%(k))
					outmaps.pop(k,None)
					cont = True
					break
				kv = outmaps[k]
				curarr = []
				for v in kv:
					curv = self.trans_var(v)
					if curv != v:
						logging.info('trans (%s => %s)'%(v,curv))
					curarr.append(curv)
				outmaps[k] = curarr
		return outmaps

def transdep_handler(args,context):
	tcebase.set_log_level(args)
	depmaps = tcedep.get_alldep_from_file(args)
	tcereplace = TceReplace(args)
	depmaps = tcereplace.trans_deps(depmaps)
	if len(args.subnargs) > 0 :
		for p in args.subnargs:
			tcedep.format_tree(args,depmaps,p)
	else:
		tcedep.format_tree(args,depmaps,None)
	sys.exit(0)
	return


tce_replace_command_line = {
	'transdep<transdep_handler>## transdep_handler pkg... ##' : {
		'$' : '*'
	},
	'+tce' : {
		'vars_kernel## to specify the kernel for it ##' : '4.2.0-tinycore64'
	}
}


def main():
	usage_str='%s [options] {commands} pkgs...'%(sys.argv[0])
	parser = extargsparse.ExtArgsParse(description='tce encapsulation',usage=usage_str)
	parser = tcebase.add_tce_args(parser)
	parser.load_command_line(tce_replace_command_line)
	args = parser.parse_command_line(None,parser)
	tcedep.Usage(3,'please specified a command',parser)
	return

if __name__ =='__main__':
	main()
