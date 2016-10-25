#! python


import extargsparse
import pycparser
import sys
import re
import StringIO
import logging

class Utf8Encode:
	def __dict_utf8(self,val):
		newdict =dict()
		for k in val.keys():
			newk = self.__encode_utf8(k)
			newv = self.__encode_utf8(val[k])
			newdict[newk] = newv
		return newdict

	def __list_utf8(self,val):
		newlist = []
		for k in val:
			newk = self.__encode_utf8(k)
			newlist.append(newk)
		return newlist

	def __encode_utf8(self,val):
		retval = val

		if sys.version[0]=='2' and isinstance(val,unicode):
			retval = val.encode('utf8')
		elif isinstance(val,dict):
			retval = self.__dict_utf8(val)
		elif isinstance(val,list):
			retval = self.__list_utf8(val)
		return retval

	def __init__(self,val):
		self.__val = self.__encode_utf8(val)
		return

	def __str__(self):
		return self.__val

	def __repr__(self):
		return self.__val
	def get_val(self):
		return self.__val

class NodeTypeDecl(object):
	def __init__(self):
		self.typename = ''
		self.memname = ''
		self.ptrtype = 0
		self.arraytype = 0
		self.arraysize = 0
		self.enumtype = False
		self.prevnode = None
		self.structnode = None
		self.funcdeclnode = None
		return

	def __str__(self):
		s = ''
		s += 'type(%s)'%(self.typename)
		s += 'mem(%s)'%(self.memname)
		s += 'ptrtype(%s)'%(self.ptrtype)
		s += 'arraytype(%s)'%(self.arraytype)
		s += 'arraysize(%s)'%(self.arraysize)
		s += 'enumtype(%s)'%(self.enumtype)
		if self.structnode is not None:
			s += 'structnode(%s)'%(get_node_desc(self.structnode))
		else:
			s += 'structnode(None)'
		if self.funcdeclnode is not None:
			s += 'funcdeclnode(%s)'%(get_node_desc(self.funcdeclnode))
		else:
			s += 'funcdelc(None)'
		s += 'prevnode(%s)'%(self.prevnode)
		return s

	def __iadd__(self,other):
		if not isinstance(other,NodeTypeDecl):
			raise Exception('not NodeTypeDecl')
		if len(other.typename) > 0:
			self.typename = other.typename
		if len(other.memname) > 0 :
			self.memname = other.memname
		if other.ptrtype > 0:
			self.ptrtype += other.ptrtype
		if other.arraytype > 0 :
			self.arraytype += other.arraytype
		if other.arraysize != 0:
			self.arraysize = other.arraysize
		if other.enumtype :
			self.enumtype = other.enumtype
		if self.prevnode is None and other.prevnode is not None:
			self.prevnode = other.prevnode
		if self.structnode is None and other.structnode is not None:
			self.structnode = other.structnode
		if self.funcdeclnode is None and other.funcdeclnode is not None:
			self.funcdeclnode = other.funcdeclnode
		return	self	

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
		elif isinstance(child,pycparser.c_ast.FuncDecl):
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
	retval = False
	for (cname ,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.EnumeratorList):
			return True
		else:
			retval = __has_enum_list(child)
			if retval:
				return True
	return False

def __get_enum_decl(cnode):
	retnames=[]
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.Enum) and child.name is not None:
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
		assert(times < 50)
		k = possiblenodes[0]
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

	i = 0
	for k in searched:
		if i > 0 :
			fout.write('\n')
		fout.write('%s'%(__debug_node_array(nodedecl[k],k)))
		i += 1
	return


def __get_decl_type_name(ast,cnode):
	nodetype = NodeTypeDecl()
	for (dname,d) in cnode.children():
		if isinstance(d,pycparser.c_ast.TypeDecl):
			nodetype += __get_decl_type_name(ast,d)
		elif isinstance(d,pycparser.c_ast.IdentifierType):
			nodetype.typename = ' '.join(d.names)
		elif isinstance(d,pycparser.c_ast.PtrDecl):
			nodetype += __get_decl_type_name(ast,d)
			nodetype.ptrtype += 1
		elif isinstance(d,pycparser.c_ast.ArrayDecl):
			nodetype += __get_decl_type_name(ast,d)
			nodetype.arraytype += 1
		elif isinstance(d,pycparser.c_ast.Constant):
			nodetype.arraysize += int(d.value)
		elif isinstance(d,pycparser.c_ast.Struct):
			nodetype.structnode = d
			if d.name is not None:
				nodetype.typename = d.name
		elif isinstance(d,pycparser.c_ast.FuncDecl):
			nodetype.funcdeclnode = d
		else:
			logging.warn('unknown type (%s)\n%s'%(dname,get_node_desc(d)))
			nodetype += __get_decl_type_name(ast,d)
	return nodetype

def get_decl_type_name(ast,cnode):
	nodetype = NodeTypeDecl()
	nodetype.memname = cnode.name
	nodetype += __get_decl_type_name(ast,cnode)
	return nodetype


def structmem_impl(args,ast):
	fout = sys.stdout
	for k in args.subnargs:
		sarr = re.split('\.',k)
		typename = sarr[0]
		if len(sarr) <= 1:
			cnodes = get_struct_node(ast,typename)
			if len(cnodes) > 0:
				fout.write('%s\n%s'%(__debug_node_array(cnodes,typename)))
			else:
				cnodes = get_enum_node(ast,typename)
				if len(cnodes) > 0:
					fout.write('%s\n%s'%(__debug_node_array(cnodes,typename)))
				else:
					fout.write('%s\n    None\n'%(typename))
		else:
			memname = sarr[1]
			cnodes = get_struct_node(ast,typename)
			output = False
			if len(cnodes) > 0:
				i = 1
				curnode = cnodes[0]
				cont = True
				while cont and i < len(sarr) and (curnode is not None):
					cont = False
					for (cname,child) in curnode.children():
						if isinstance(child,pycparser.c_ast.Decl):
							nodetype = get_decl_type_name(ast,child)
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
							logging.info('%s\n%s\n'%(nodetype,get_node_desc(child)))
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
			cnodes = get_struct_node(ast,typename)
			if len(cnodes) > 0:
				retnodes = get_declare_member(cnodes[0])
				fout.write(__debug_node_array(retnodes,'%s members'%(typename)))
			else:
				cnodes = get_enum_node(ast,typename)
				if len(cnodes) > 0:
					fout.write('%s\n%s'%(__debug_node_array(cnodes,typename)))
				else:
					fout.write('%s\n    None\n'%(typename))
		else:
			memname = sarr[1]
			cnodes = get_struct_node(ast,typename)
			output = False
			if len(cnodes) > 0:
				i = 1
				curnode = cnodes[0]
				cont = True
				while cont and i < len(sarr) and (curnode is not None):
					cont = False
					for (cname,child) in curnode.children():
						if isinstance(child,pycparser.c_ast.Decl):
							nodetype = get_decl_type_name(ast,child)
							if nodetype and  nodetype.memname == memname:
								if (i+1) == len(sarr):
									retnodes = get_declare_member(nodetype.structnode)
									fout.write(__debug_node_array(retnodes,'%s members'%(k)))
									nodetype = None
									output = True
									break
								else:
									i += 1
									curnode = nodetype.structnode
									memname = sarr[i]
									cont = True
									break
							logging.info('%s\n%s\n'%(nodetype,get_node_desc(child)))
							nodetype = None
			if not output:
				fout.write('%s\n    None\n'%(k))
	return


def get_declare_member(cnodes):
	retnodes = []
	for (cname,c) in cnodes.children():
		if isinstance(c,pycparser.c_ast.Decl):
			retnodes.append(c)
	return retnodes

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

def structmem_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	parse_file_callback(gccecommand,args.input,structmem_impl,args)
	sys.exit(0)
	return

def listmem_handler(args,parser):
	set_logging(args)
	if args.input is None:
		raise Exception('specify by --input|-i for file input')
	gccecommand = []
	parse_file_callback(gccecommand,args.input,listmem_impl,args)
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