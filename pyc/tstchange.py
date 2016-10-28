#! python

import sys
import logging
import inspect
import re

class NodeTypeDecl(object):
	def __init__(self):
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
		s += '[%d]type(%s)'%(cnt,self.typename)
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

def __format_tabs(tabs,ins):
	s = ' ' * 4 * tabs
	s += ins
	s += '\n'
	return s

def __format_comment_tabs(args,tabs,ins,callnum=1):
	s = ''
	logging.info('%s'%(ins))
	if args.verbose >= 3:
		(frame, file, lineno,funcname, lines, index) = inspect.getouterframes(inspect.currentframe())[callnum]
		s += '/* %s:%d:%s (%s) */'%(file,lineno,funcname,ins)
	elif args.verbose >= 1 :
		s += '/*%s*/'%(ins)
	else:
		return ''
	return __format_tabs(tabs,s)



def __change_argname(args,tabs,argname,nodetype,fmtstr,tup,newtabs=False):
	s = ''
	oldnamevar = None
	if nodetype:
		oldnamevar = nodetype.namevarname
	argfmt = re.sub(r'%d',r'%s',fmtstr)
	news = argfmt%tup
	logging.info('news (%s)'%(news))
	newargname = news.format(argname=argname)
	if nodetype and (nodetype.namevarname or newtabs ) :
		if newtabs:
			newnamevar = 'memname%d'%(tabs)
		else:
			newnamevar = '%s_%d'%(nodetype.namevarname,tabs)
		if nodetype and (newnamevar == nodetype.namevarname):
			newnamevar = '%s_%d'%(nodetype.namevarname,tabs)
		if newnamevar not in args.char_array_args:
			args.char_array_args.append(newnamevar)
		varstr = 'snprintf(%s,sizeof(%s),"'%(newnamevar,newnamevar)
		varfmt = fmtstr.format(argname=r'%s')
		varstr += varfmt
		if nodetype and nodetype.namevarname:
			varstr += '",%s'%(nodetype.namevarname)
		else:
			varstr += '","%s"'%(argname)
		i = 0
		while i < len(tup):
			varstr += ',%s'%(tup[i])
			i += 1
		varstr += ');'
		s += __format_tabs(tabs,'%s'%(varstr))
		nodetype.namevarname = newnamevar
	return s,newargname,oldnamevar


def main():
	args = NodeTypeDecl()
	args.verbose = 4
	args.char_array_args = []
	nodetype = NodeTypeDecl()
	nodetype.namevarname = 'memname1'
	argname = 'info'
	_curs,_argsname,oldnamevar = __change_argname(args,1,argname,nodetype,r'(*{argname})',tuple())
	print('_curs(%s) _argsname(%s)'%(_curs,_argsname))
	nodetype.namevarname = 'memname1'
	_curs,_argsname,oldnamevar = __change_argname(args,1,argname,nodetype,r'({argname}->%s)',tuple(['member']))
	print('_curs(%s) _argsname(%s)'%(_curs,_argsname))
	nodetype.namevarname = None
	argname="info->m_char"
	_curs,_argsname,oldnamevar = __change_argname(args,1,argname,nodetype,r'{argname}[%d][%d][%d]',tuple(['cnt1','cnt2','cnt3']),True)
	print('_curs(%s) _argsname(%s)'%(_curs,_argsname))
	nodetype.namevarname = 'memname1'


	return

if __name__ == '__main__':
	loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	main()