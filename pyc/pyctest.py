#! python


import extargsparse
import pycparser
import sys
import re
import logging

import pycencap



def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return



def struct_impl(args,ast):
	fout = sys.stdout
	for k in args.subnargs:
		n = pycencap.get_struct_node(ast,k)
		if len(n) > 0:
			fout.write('%s\n'%(k))
			i = 0
			for cn in n:
				fout.write('  [%d]:\n%s\n'%(i,get_node_desc(cn,1)))
				i += 1
		else:
			n = pycencap.get_enum_node(ast,k)
			if len(n) > 0:
				fout.write('%s\n'%(k))
				i = 0
				for cn in n:
					fout.write('  [%d]:\n%s\n'%(i,get_node_desc(cn,1)))
					i += 1
			else:
				fout.write('%s None\n'%(k))
	return

def structtotal_impl(args,ast):
	fout = sys.stdout
	scannames = args.subnargs
	nodedecl = dict()
	wrongnames = []
	searched = []

	while len(scannames) > 0:
		curname = scannames[0]
		scannames = scannames[1:]
		curnode = pycencap.get_struct_node(ast,curname)
		if len(curnode) > 0:
			if curname not in nodedecl.keys():
				searched.append(curname)
				nodedecl[curname] = curnode
				declnames = pycencap.get_decl_types(curnode[0])
				for n in declnames:
					if n in nodedecl.keys():
						continue
					if n == curname:
						continue
					if n in scannames:
						continue
					scannames.append(n)
		else:
			curnode = pycencap.get_enum_node(ast,curname)
			if len(curnode) > 0:
				if curname not in nodedecl.keys():
					searched.append(curname)
					nodedecl[curname] = curnode

	i = 0
	for k in searched:
		if i > 0 :
			fout.write('\n')
		fout.write('%s'%(pycencap.debug_node_array(nodedecl[k],k)))
		i += 1
	return



def structmem_impl(args,ast):
	fout = sys.stdout
	for k in args.subnargs:
		sarr = re.split('\.',k)
		typename = sarr[0]
		if len(sarr) <= 1:
			cnodes = pycencap.get_struct_node(ast,typename)
			if len(cnodes) > 0:
				fout.write('%s\n%s'%(pycencap.debug_node_array(cnodes,typename)))
			else:
				cnodes = pycencap.get_enum_node(ast,typename)
				if len(cnodes) > 0:
					fout.write('%s\n%s'%(pycencap.debug_node_array(cnodes,typename)))
				else:
					fout.write('%s\n    None\n'%(typename))
		else:
			memname = sarr[1]
			cnodes = pycencap.get_struct_node(ast,typename)
			output = False
			if len(cnodes) > 0:
				i = 1
				curnode = cnodes[0]
				cont = True
				while cont and i < len(sarr) and (curnode is not None):
					cont = False
					for (cname,child) in curnode.children():
						if isinstance(child,pycparser.c_ast.Decl):
							nodetype = pycencap.get_decl_type_name(ast,child)
							if nodetype and  nodetype.memname == memname:
								if (i+1) == len(sarr):
									fout.write('%s\n    %s\n'%(k,nodetype))
									nodetype = None
									output = True
									break
								else:
									i += 1
									curnode = nodetype.structnode
									memname = sarr[i]
									cont = True
									break
							logging.info('%s\n%s\n'%(nodetype,pycencap.get_node_desc(child)))
							nodetype = None
			if not output:
				fout.write('%s\n    None\n'%(typename))
	return

def listmem_impl(args,ast):
	fout = sys.stdout
	for k in args.subnargs:
		sarr = re.split('\.',k)
		typename = sarr[0]
		if len(sarr) <= 1:
			cnodes = pycencap.get_struct_node(ast,typename)
			if len(cnodes) > 0:
				retnodes = pycencap.get_declare_member(cnodes[0])
				fout.write(pycencap.debug_node_array(retnodes,'%s members'%(typename)))
			else:
				cnodes = pycencap.get_enum_node(ast,typename)
				if len(cnodes) > 0:
					fout.write('%s\n%s'%(pycencap.debug_node_array(cnodes,typename)))
				else:
					fout.write('%s\n    None\n'%(typename))
		else:
			memname = sarr[1]
			cnodes = pycencap.get_struct_node(ast,typename)
			output = False
			if len(cnodes) > 0:
				i = 1
				curnode = cnodes[0]
				cont = True
				while cont and i < len(sarr) and (curnode is not None):
					cont = False
					for (cname,child) in curnode.children():
						if isinstance(child,pycparser.c_ast.Decl):
							nodetype = pycencap.get_decl_type_name(ast,child)
							if nodetype and  nodetype.memname == memname:
								if (i+1) == len(sarr):
									retnodes = pycencap.get_declare_member(nodetype.structnode)
									fout.write(pycencap.debug_node_array(retnodes,'%s members'%(k)))
									nodetype = None
									output = True
									break
								else:
									i += 1
									curnode = nodetype.structnode
									memname = sarr[i]
									cont = True
									break
							logging.info('%s\n%s\n'%(nodetype,pycencap.get_node_desc(child)))
							nodetype = None
			if not output:
				fout.write('%s\n    None\n'%(k))
	return


def sortlist_impl(args,ast):
	fout = sys.stdout
	if args.output is not None:
		fout = open(args.output,'w+')
	fout.write('structdef(%d)\n'%(len(ast.structdef.keys())))
	i = 0
	for k in sorted(ast.structdef.keys()):
		fout.write('[%d]%s\n%s'%(i,k,pycencap.get_node_desc(ast.structdef[k])))
		i += 1

	fout.write('enumdef(%d)\n'%(len(ast.enumdef.keys())))
	i = 0
	for k in sorted(ast.enumdef.keys()):
		fout.write('[%d]%s\n%s'%(i,k,pycencap.get_node_desc(ast.enumdef[k])))
		i += 1

	if fout != sys.stdout:
		fout.close()
	fout = None			
	return

def dump_impl(args,ast):
	fout = sys.stdout
	if args.output is not None:
		fout = open(args.output,'w+')
	ast.ast.show(fout)
	if fout != sys.stdout:
		fout.close()
	fout = None
	return



def struct_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,struct_impl,args)
	sys.exit(0)
	return

def structtotal_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,structtotal_impl,args)
	sys.exit(0)
	return

def structmem_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,structmem_impl,args)
	sys.exit(0)
	return

def listmem_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,listmem_impl,args)
	sys.exit(0)
	return

def sortlist_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,sortlist_impl,args)
	sys.exit(0)
	return

def dump_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,dump_impl,args)
	sys.exit(0)
	return


command_line = {
	'input|i' : None,
	'output|o' : None,
	'verbose|v' : '+',
	'struct<struct_handler>## get struct node ##' : {
		'$' : '+'
	},
	'structtotal<structtotal_handler>## get all struct node for declare ##' : {
		'$' : '+'
	},
	'structmem<structmem_handler>## list structure member nodetype ##' : {
		'$' : '+'
	},
	'listmem<listmem_handler>## list member ##' : {
		'$' : '+'
	},
	'sortlist<sortlist_handler>## sortlist handler##' : {
		'$' : 0
	},
	'dump<dump_handler>## dump handler for tree##' : {
		'$' : 0
	}
}

def main():
	global command_line
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line(command_line)
	parser.parse_command_line(None,parser)
	return

if __name__ == '__main__':
	main()