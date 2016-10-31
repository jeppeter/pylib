
import StringIO
import logging
import pycparser
import sys

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
		self.parent_typename = ''
		self.typename = ''
		self.memname = ''
		self.ptrtype = 0
		self.arraytype = 0
		self.arraysize = []
		self.enumtype = False
		self.prevnode = None
		self.structnode = None
		self.funcdeclnode = None
		self.namevarname = None
		self.checkptridx = 0
		self.checkarrayidx = 0
		return

	def __str__(self):
		s = ''
		cnt = 0
		curprevnode = self.prevnode
		while curprevnode is not None:
			cnt += 1
			curprevnode = curprevnode.prevnode
		s += '[%d]parent_typename(%s)typename(%s)'%(cnt,self.parent_typename,self.typename)
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
		s += 'namevarname(%s)'%(self.namevarname)
		s += 'checkptridx(%d)'%(self.checkptridx)
		s += 'checkarrayidx(%d)'%(self.checkarrayidx)
		s += 'prevnode(%s)'%(self.prevnode)
		return s

	def __iadd__(self,other):
		if not isinstance(other,NodeTypeDecl):
			raise Exception('not NodeTypeDecl')
		if len(other.parent_typename) > 0:
			self.parent_typename = other.parent_typename
		if len(other.typename) > 0:
			self.typename = other.typename
		if len(other.memname) > 0 :
			self.memname = other.memname
		if other.ptrtype > 0:
			self.ptrtype += other.ptrtype
		if other.arraytype > 0 :
			self.arraytype += other.arraytype
		if len(other.arraysize) != 0:
			self.arraysize.extend(other.arraysize)
		if other.enumtype :
			self.enumtype = other.enumtype
		if self.prevnode is None and other.prevnode is not None:
			self.prevnode = other.prevnode
		if self.structnode is None and other.structnode is not None:
			self.structnode = other.structnode
		if self.funcdeclnode is None and other.funcdeclnode is not None:
			self.funcdeclnode = other.funcdeclnode
		return	self	

	def clone(self,other):
		if not isinstance(other,NodeTypeDecl):
			raise Exception('not NodeTypeDecl')
		self.parent_typename = other.parent_typename
		self.typename = other.typename
		self.memname = other.memname
		self.ptrtype = other.ptrtype
		self.arraytype = other.arraytype
		self.arraysize = other.arraysize
		self.enumtype = other.enumtype
		self.prevnode = other
		self.structnode = other.structnode
		self.funcdeclnode = other.funcdeclnode
		self.namevarname = other.namevarname
		self.checkptridx = other.checkptridx
		self.checkarrayidx = other.checkarrayidx
		return

def get_node_desc(node,tabs=0):
	sio = StringIO.StringIO()
	node.show(sio,offset=tabs*4)
	return sio.getvalue()

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

def debug_node_array(nodearr,fmt):
	return __debug_node_array(nodearr,fmt)

def __get_struct_decl(cnode):
	retnames=[]
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.Struct):
			#logging.info('append (%s)'%(child.name))
			retnames.append(child.name)
		else:
			retnames.extend(__get_struct_decl(child))
	return retnames


def __get_inner_struct(cnode):
	retnodes = []
	for (cname,c) in cnode.children():
		if isinstance(c,pycparser.c_ast.Struct):
			retval = __has_decl_mem(c)
			if retval:
				retnodes.append(c)
		else:
			retnodes.extend(__get_inner_struct(c))
	return retnodes

def get_struct_node(ast,structname):
	retnode = []
	if structname in ast.structdef.keys():
		retnode.append(ast.structdef[structname])
	return retnode


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
	retnode = []
	if enumname in ast.enumdef.keys():
		retnode.append(ast.enumdef[enumname])
	return retnode

def get_decl_types(cnode):
	retnodes = []
	for (cname,child) in cnode.children():
		if isinstance(child,pycparser.c_ast.IdentifierType):
			retnodes.append(' '.join(child.names))
		else:
			retnodes.extend(get_decl_types(child))
	return retnodes

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
			nodetype.arraysize.append(int(d.value))
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
	assert(nodetype.arraytype >= len(nodetype.arraysize))
	if nodetype.arraytype > len(nodetype.arraysize):
		# this like int *m_arr[32][][]; 
		logging.info('arraytype %d len(%d)'%(nodetype.arraytype,len(nodetype.arraysize)))
		morecnt = (nodetype.arraytype - len(nodetype.arraysize))
		nodetype.arraytype -= morecnt
		nodetype.ptrtype += morecnt
	return nodetype

def __get_typedef_type_name(ast,cnode):
	nodetype = NodeTypeDecl()
	for (cname,c) in cnode.children():
		if isinstance(c,pycparser.c_ast.IdentifierType):
			nodetype.typename = ' '.join(c.names)
		elif isinstance(c,pycparser.c_ast.PtrDecl):
			nodetype += __get_typedef_type_name(ast,c)
			nodetype.ptrtype += 1
		elif isinstance(c,pycparser.c_ast.ArrayDecl):
			nodetype += __get_typedef_type_name(ast,c)
			nodetype.arraytype += 1
		elif isinstance(c,pycparser.c_ast.Constant):
			nodetype.arraysize.append(int(c.value))
		elif isinstance(c,pycparser.c_ast.FuncDecl):
			nodetype.funcdeclnode = c
		else:
			logging.warn('unknown type (%s)\n%s'%(cname,get_node_desc(c)))
			nodetype += __get_decl_type_name(ast,c)
	return nodetype

def get_typedef_type_name(ast,cnode):
	nodetype = NodeTypeDecl()
	nodetype += __get_typedef_type_name(ast,cnode)
	return nodetype


def get_declare_member(cnodes):
	retnodes = []
	for (cname,c) in cnodes.children():
		if isinstance(c,pycparser.c_ast.Decl):
			retnodes.append(c)
	return retnodes


def __append_list_prevnode(prevnode,cnode):
	nodetype = NodeTypeDecl()
	nodetype.prevnode = prevnode
	nodetype.structnode = cnode
	return nodetype

def __callback_struct_enum_def(newast,c,prevnode,callback):
	nodetype = __append_list_prevnode(prevnode,c)
	if callback is not None:
		callback(newast,c,nodetype)
	nodetype = None
	return

def __get_name_prevnode(cnode,prevnode):
	retnames = []
	curname = None
	if hasattr(cnode,'name'):
		curname = cnode.name
	else:
		assert(isinstance(cnode,pycparser.c_ast.IdentifierType) or \
				isinstance(cnode,pycparser.c_ast.FuncDecl))
	curprevnode = prevnode
	if curname is not None:
		retnames.append(curname)
	while curprevnode is not None:
		cn = curprevnode.structnode
		if isinstance(cn ,pycparser.c_ast.TypeDecl):
			if cn.declname is not None:
				curname = cn.declname
				retnames.append(curname)
		elif isinstance(cn,pycparser.c_ast.Typedef):
			if cn.name is not None:
				curname = cn.name
				retnames.append(curname)
		curprevnode = curprevnode.prevnode
	return retnames

def __has_func_pointer(cnode,prevnode):
	curprevnode = prevnode
	retval = False
	while curprevnode is not None:
		cn = curprevnode.structnode
		if isinstance(cn , pycparser.c_ast.PtrDecl):
			retval =  True
			break
		curprevnode = curprevnode.prevnode
	if retval:
		# we check that it is under Typedef node
		curprevnode = prevnode
		while curprevnode is not None:
			cn = curprevnode.structnode
			if isinstance(cn , pycparser.c_ast.Typedef):
				retval =  True
				break
			curprevnode = curprevnode.prevnode
	return retval

basic_types = [
	'long unsigned int',
	'unsigned char',
	'unsigned short int',
	'unsigned int',
	'unsigned long int',
	'signed char',
	'signed short int',
	'signed int',
	'signed long int',
	'long int',
	'int',
	'void',
	'char',
	'short int']

def __get_identifier_node(prevnode):
	# we get the toppest node
	retnode = None
	curprevnode = prevnode
	i = 0
	while curprevnode is not None:
		cn = curprevnode.structnode
		retnode = cn
		if isinstance(cn ,pycparser.c_ast.TypeDecl) or isinstance(cn,pycparser.c_ast.Typedef) or \
			isinstance(cn,pycparser.c_ast.PtrDecl) or isinstance(cn,pycparser.c_ast.ArrayDecl) or \
			isinstance(cn,pycparser.c_ast.IdentifierType) or isinstance(cn,pycparser.c_ast.FuncDecl):
			pass
		else:
			logging.warn('unknown IdentifierType[%d](%s)\n%s'%(i,cn.__class__.__name__,get_node_desc(cn)))
		i += 1
		curprevnode = curprevnode.prevnode
	return retnode

def __make_struct_enum_def(newast,cnode,prevnode):
	if isinstance(cnode,pycparser.c_ast.Typedef) or isinstance(cnode,pycparser.c_ast.Decl) or \
			isinstance(cnode,pycparser.c_ast.PtrDecl) or isinstance(cnode,pycparser.c_ast.TypeDecl) or \
			isinstance(cnode,pycparser.c_ast.ArrayDecl) or \
			isinstance(cnode,pycparser.c_ast.Constant) or isinstance(cnode,pycparser.c_ast.BinaryOp) or \
			isinstance(cnode,pycparser.c_ast.InitList) or isinstance(cnode,pycparser.c_ast.NamedInitializer) or\
			isinstance(cnode,pycparser.c_ast.CompoundLiteral) or isinstance(cnode,pycparser.c_ast.Typename) or \
			isinstance(cnode,pycparser.c_ast.Cast) or isinstance(cnode,pycparser.c_ast.UnaryOp) or \
			isinstance(cnode,pycparser.c_ast.StructRef):
		for (cname,c) in cnode.children():
			__callback_struct_enum_def(newast,c,prevnode,__make_struct_enum_def)
	elif isinstance(cnode,pycparser.c_ast.Struct):
		retnodes = get_declare_member(cnode)
		if len(retnodes) > 0:
			retnames = __get_name_prevnode(cnode,prevnode)
			if len(retnames) > 0:
				for curname in retnames:
					if curname not in newast.structdef.keys():
						newast.structdef[curname] = cnode
					else:
						if get_node_desc(cnode) != get_node_desc(newast.structdef[curname]) :
							logging.warn('(%s)(%s) already defined (%s)'%(
								curname,get_node_desc(cnode),get_node_desc(newast.structdef[curname])))
			else:
				newast.structnotlists.append(cnode)
				newast.structnotlists_prevnode.append(prevnode)
		else:
			newast.structnotlists.append(cnode)
			newast.structnotlists_prevnode.append(prevnode)
	elif isinstance(cnode,pycparser.c_ast.Enum):
		retval = __has_enum_list(cnode)
		if retval :
			retnames = __get_name_prevnode(cnode,prevnode)
			if len(retnames) > 0 :
				for curname in retnames:
					if curname not in newast.enumdef.keys():
						newast.enumdef[curname] = cnode
					else:
						if get_node_desc(cnode) != get_node_desc(newast.enumdef[curname]):
							logging.warn('(%s)(%s) already defined (%s)'%(
								curname,get_node_desc(cnode),get_node_desc(newast.enumdef[curname])))
			else:
				newast.enumnotlists.append(cnode)
				newast.enumnotlists_prevnode.append(prevnode)
		else:
			newast.enumnotlists.append(cnode)
			newast.enumnotlists_prevnode.append(prevnode)

	elif  isinstance(cnode,pycparser.c_ast.FuncDef) or \
		isinstance(cnode,pycparser.c_ast.ID) or isinstance(cnode,pycparser.c_ast.Union):
		pass
	elif isinstance(cnode,pycparser.c_ast.IdentifierType):
		# now we should make like typedef unsigned long uint32_t;
		# this is the code
		retnames = __get_name_prevnode(cnode,prevnode)
		name = ' '.join(cnode.names)	
		if len(name) > 0:
			if name not in basic_types and name not in newast.structdef.keys():
				logging.warn('(%s) not in basic types'%(name))
			structnode = __get_identifier_node(prevnode)
			if len(retnames) > 0:
				for curname in retnames:
					if curname not in newast.structdef.keys():
						newast.structdef[curname] = structnode
					else:
						if get_node_desc(structnode) != get_node_desc(newast.structdef[curname]):
							logging.warn('[%s]\n    %s\n!!!!!!!!!!!!!\n   %s\n++++++++++++\n'%(
								curname,get_node_desc(structnode),get_node_desc(newast.structdef[curname])))
			else:
				logging.warn('(%s) no defines'%(prevnode))
		else:
			logging.warn('(%s) IdentifierType\n   %s'%(prevnode,get_node_desc(cnode)))
	elif isinstance(cnode,pycparser.c_ast.FuncDecl):
		if __has_func_pointer(cnode,prevnode):
			# we have defined this pointer
			retnames = __get_name_prevnode(cnode,prevnode)
			# no names
			structnode = __get_identifier_node(prevnode)
			if len(retnames) > 0:
				for curname in retnames:
					if curname not in newast.structdef.keys():
						newast.structdef[curname] = structnode
					else:
						if get_node_desc(structnode) != get_node_desc(newast.structdef[curname]):
							logging.warn('[%s]\n    %s\n!!!!!!!!!!!!!\n   %s\n++++++++++++\n'%(
								curname,get_node_desc(structnode),get_node_desc(newast.structdef[curname])))
			else:
				logging.warn('(%s) no defines'%(prevnode))
	else:
		logging.warn('can not pass %s(%s)'%(cnode.__class__.__name__,get_node_desc(cnode)))
	return

class NewAst(object):
	pass

def make_struct_enum_def(ast):
	newast = NewAst()
	newast.structdef = dict()
	newast.enumdef = dict()
	newast.structnotlists = []
	newast.enumnotlists = []
	newast.structnotlists_prevnode = []
	newast.enumnotlists_prevnode = []
	newast.ast = ast

	for (cname,c) in ast.children():
		if isinstance(c,pycparser.c_ast.Decl) and c.name is not None:
			# we do not scan for declare
			# like extern File* stderr;
			continue
		prevnode = NodeTypeDecl()
		prevnode.structnode = c
		__make_struct_enum_def(newast,c,prevnode)
		prevnode = None

	i = 0
	assert(len(newast.enumnotlists) == len(newast.enumnotlists_prevnode))
	while i < len(newast.enumnotlists):
		k = newast.enumnotlists[i]
		p = newast.enumnotlists_prevnode[i]
		enumnode = None
		if k.name is not None:
			if k.name in newast.enumdef.keys():
				enumnode = newast.enumdef[k.name]
		retnames = __get_name_prevnode(k,p)
		if len(retnames) > 0:
			for n in retnames:
				if n not in newast.enumdef.keys() :
					if enumnode is None:
						logging.warn('[%d]\n    %s(%s)'%(i,get_node_desc(k),p))
					else:
						newast.enumdef[n] = enumnode
				elif enumnode is not None:
					if get_node_desc(enumnode) != get_node_desc(newast.enumdef[n]):
						logging.warn('[%d]\n    %s(%s)\n   %s'%(
							i,get_node_desc(k),p,get_node_desc(newast.enumdef[n])))
		else:
			logging.warn('[%d]node:\n    %s\n    %s'%(i,get_node_desc(k),p))
		# now to get the name
		i += 1
	newast.enumnotlists = []
	newast.enumnotlists_prevnode = []
	i = 0
	assert(len(newast.structnotlists) == len(newast.structnotlists_prevnode))
	while i < len(newast.structnotlists):
		k = newast.structnotlists[i]
		p = newast.structnotlists_prevnode[i]
		structnode = None
		if k.name is not None:
			if k.name in newast.structdef.keys():
				structnode = newast.structdef[k.name]
		retnames = __get_name_prevnode(k,p)
		if len(retnames) > 0:
			for n in retnames:
				if n not in newast.structdef.keys() :
					if structnode is None:
						logging.warn('[%d]\n    %s(%s)'%(i,get_node_desc(k),p))
					else:
						newast.structdef[n] = structnode
				elif structnode is not None:
					if get_node_desc(structnode) != get_node_desc(newast.structdef[n]):
						logging.warn('[%d]\n    %s(%s)\n   %s'%(
							i,get_node_desc(k),p,get_node_desc(newast.structdef[n])))
		else:
			logging.warn('[%d]node:\n    %s\n    %s'%(i,get_node_desc(k),p))
		# now to get the name
		i += 1
	newast.structnotlists = []
	newast.structnotlists_prevnode = []
	newast.ast = ast
	return newast


def parse_file_callback(gccecommand,file,callback=None,ctx=None):
	if len(gccecommand) == 0:
		ast = pycparser.parse_file(file,use_cpp=False)
	else:
		ast = pycparser.parse_file(file,use_cpp=True,cpp_path=gccecommand[0],
			cpp_args=gccecommand[1:])
	newast = make_struct_enum_def(ast)
	if callback is not None:
		callback(ctx,newast)
	return ast
