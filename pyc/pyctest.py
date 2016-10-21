#! python


import extargsparse
import pycparser
import sys
import re
import StringIO
import logging

def get_node_desc(node,tabs=0):
	sio = StringIO.StringIO()
	node.show(sio,offset=tabs*4)
	return sio.getvalue()

def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return


def __get_struct_node(ast,structname=None):
	cnodes = []
	for (cname,child) in ast.children():
		if isinstance(child,pycparser.c_ast.Typedef) and ( structname is None or  child.name == structname):
			#logging.info('append\n%s'%(get_node_desc(child)))
			cnodes.append(child)
		elif isinstance(child,pycparser.c_ast.Typedef):
			cnodes.extend(__get_struct_node(child,structname))
		elif isinstance(child,pycparser.c_ast.TypeDecl):
			cnodes.extend(__get_struct_node(child,structname))
		elif isinstance(child,pycparser.c_ast.Decl) and child.name is None:
			cnodes.extend(__get_struct_node(child,structname))
		elif isinstance(child,pycparser.c_ast.Union) and child.name is None:
			cnodes.extend(__get_struct_node(child,structname))
		elif isinstance(child,pycparser.c_ast.Struct) and ( structname is None or child.name == structname):
			#logging.info('append\n%s'%(get_node_desc(child)))
			cnodes.append(child)
		elif isinstance(child,pycparser.c_ast.Struct):
			cnodes.extend(__get_struct_node(child,structname))
	return cnodes


def __has_decl_mem(cnode):
	retval = False
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.Decl):
			return True
	return retval


def __debug_node_array(nodearr,fmt):
	s = ''
	s += '%s\n'%(fmt)
	i = 0
	for k in nodearr:
		s += '[%d]\n%s'%(i,get_node_desc(k))
		i += 1
	return s

def __get_struct_decl(cnode):
	retnames=[]
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.Struct):
			#logging.info('append (%s)'%(child.name))
			retnames.append(child.name)
		else:
			retnames.extend(__get_struct_decl(child))
	return retnames

def get_struct_node(ast,structname):
	possiblenodes = __get_struct_node(ast,structname)
	abandonnodes = []
	retnode = []
	times = 0
	while len(possiblenodes) > 0:
		assert(times < 50)
		k = possiblenodes[0]
		#logging.info('cmp\n%s'%(get_node_desc(k)))
		possiblenodes= possiblenodes[1:]
		if __has_decl_mem(k):
			# if it is the node has declare ,so we have it
			retnode.append(k)
		else:
			abandonnodes.append(k)
			for n in __get_struct_decl(k):
				# it like typedef struct __st st_t; we find __st
				#logging.info('get struct (%s)'%(n))
				getnodes = __get_struct_node(ast,n)
				i = 0
				for ck in getnodes:
					i += 1
					#logging.info('[%d]ck\n%s'%(i,get_node_desc(ck)))
					if ck in retnode:
					#if __nodes_in(retnode,ck):
						continue
					#if __nodes_in(possiblenodes,ck):
					if ck in possiblenodes:
						continue
					#if __nodes_in(abandonnodes,ck):
					if ck in abandonnodes:
						continue
					#logging.info('will add\n%s'%(get_node_desc(ck)))
					possiblenodes.append(ck)
		times += 1
	return retnode

def __get_enum_node(ast,enumname=None):
	cnodes = []
	for (cname,child) in ast.children():
		if isinstance(child,pycparser.c_ast.Typedef) and (enumname is None or child.name == enumname):
			cnodes.append(child)
		elif isinstance(child,pycparser.c_ast.Typedef):
			cnodes.extend(__get_enum_node(child,enumname))
		elif isinstance(child,pycparser.c_ast.TypeDecl):
			cnodes.extend(__get_enum_node(child,enumname))
		elif isinstance(child,pycparser.c_ast.Decl) and child.name is None:
			cnodes.extend(__get_enum_node(child,enumname))
		elif isinstance(child,pycparser.c_ast.Union) and child.name is None:
			cnodes.extend(__get_enum_node(child,enumname))
		elif isinstance(child,pycparser.c_ast.Enum) and ( enumname is None or child.name == enumname):
			#logging.info('append\n%s'%(get_node_desc(child)))
			cnodes.append(child)
	return cnodes

def __has_enum_list(cnode):
	for (cname ,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.EnumeratorList):
			return True
	return False

def __get_enum_decl(cnode):
	retnames=[]
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.Enum):
			#logging.info('append (%s)'%(child.name))
			retnames.append(child.name)
		else:
			retnames.extend(__get_enum_decl(child))
	return retnames

def get_enum_node(ast,enumname):
	possiblenodes = __get_enum_node(ast,enumname)
	abandonnodes = []
	retnode = []
	times = 0
	while len(possiblenodes) > 0:
		try:
			assert(times < 50)
		except:
			logging.error('search for (%s)(%s)'%(sys.exc_info()[0],enumname))
			sys.exit(3)
		k = possiblenodes[0]
		#logging.info('cmp\n%s'%(get_node_desc(k)))
		possiblenodes= possiblenodes[1:]
		if __has_enum_list(k):
			# if it is the node has declare ,so we have it
			retnode.append(k)
		else:
			abandonnodes.append(k)
			for n in __get_enum_decl(k):
				# it like typedef struct __st st_t; we find __st
				#logging.info('get struct (%s)'%(n))
				getnodes = __get_enum_node(ast,n)
				i = 0
				for ck in getnodes:
					i += 1
					#logging.info('[%d]ck\n%s'%(i,get_node_desc(ck)))
					if ck in retnode:
					#if __nodes_in(retnode,ck):
						continue
					#if __nodes_in(possiblenodes,ck):
					if ck in possiblenodes:
						continue
					#if __nodes_in(abandonnodes,ck):
					if ck in abandonnodes:
						continue
					#logging.info('will add\n%s'%(get_node_desc(ck)))
					possiblenodes.append(ck)
		times += 1
	return retnode

def get_decl_types(cnode):
	retnodes = []
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.IdentifierType):
			retnodes.append(' '.join(child.names))
		else:
			retnodes.extend(get_decl_types(child))
	return retnodes


def struct_impl(args,ast):
	fout = sys.stdout
	for k in args.subnargs:
		n = get_struct_node(ast,k)
		if len(n) > 0:
			fout.write('%s\n'%(k))
			i = 0
			for cn in n:
				fout.write('  [%d]:\n%s\n'%(i,get_node_desc(cn,1)))
				i += 1
		else:
			n = get_enum_node(ast,k)
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
		curnode = get_struct_node(ast,curname)
		if len(curnode) > 0:
			if curname not in nodedecl.keys():
				searched.append(curname)
				nodedecl[curname] = curnode
				declnames = get_decl_types(curnode[0])
				for n in declnames:
					if n in nodedecl.keys():
						continue
					if n == curname:
						continue
					if n in scannames:
						continue
					scannames.append(n)
		else:
			curnode = get_enum_node(ast,curname)
			if len(curnode) > 0:
				if curname not in nodedecl.keys():
					searched.append(curname)
					nodedecl[curname] = curnode

	for k in searched:
		fout.write('%s\n%s'%(k,get_node_desc(nodedecl[k])))
	return



def parse_file_callback(gccecommand,file,callback=None,ctx=None):
	if len(gccecommand) == 0:
		ast = pycparser.parse_file(file,use_cpp=False)
	else:
		ast = pycparser.parse_file(file,use_cpp=True,cpp_path=gccecommand[0],
			cpp_args=gccecommand[1:])
	if callback is not None:
		callback(ctx,ast)
	return ast


def struct_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	parse_file_callback(gccecommand,args.input,struct_impl,args)
	sys.exit(0)
	return

def structtotal_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	parse_file_callback(gccecommand,args.input,structtotal_impl,args)
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