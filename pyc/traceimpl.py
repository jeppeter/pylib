#! /usr/bin/python


import sys
import pycparser
import extargsparse
import platform
import logging
import cmdpack
import json
import StringIO
import inspect
import re

import pycencap


def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return





def __format_tabs(tabs,ins):
	s = ' ' * 4 * tabs
	s += ins
	s += '\n'
	return s

def __format_comment_tabs(args,tabs,ins,callnum=1):
	s = ''
	if args.verbose >= 3:
		(frame, file, lineno,funcname, lines, index) = inspect.getouterframes(inspect.currentframe())[callnum]
		s += '/* %s:%d:%s (%s) */'%(file,lineno,funcname,ins)
	elif args.verbose >= 1 :
		s += '/*%s*/'%(ins)
	else:
		return ''
	return __format_tabs(tabs,s)


def __format_basic_check_inner(args,tabs,typename,argname,prevnode,ast,funcname):
	s = ''
	_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,prevnode,r'(*({argname}))',tuple([]))
	s += _curs
	s += __format_tabs(tabs,'%s(%s,*(%s));'%(funcname,_argname,argname))
	if prevnode:
		prevnode.namevarname = oldnamevar
	return s

def __format_array_callback(args,tabs,typename,argname,nodetype,ast,callback,ctx):
	s = ''
	logging.info('(%s)(%s)(%s) callback(%s)'%(typename,argname,nodetype,callback))
	origtabs = tabs
	setnodename = 0
	innerargname = argname
	assert(nodetype and nodetype.arraytype > 0)
	#if nodetype.namevarname is None:
	#	# we use strname later when not specified the namevar
	#	strname = 'memname%d'%(tabs)
	#	if strname not in args.char_array_args:
	#		s += __format_comment_tabs(args,tabs,'push (%s)'%(strname))
	#		args.char_array_args.append(strname)
	cntnamearr = []
	s += __format_tabs(tabs,'')
	s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s) callback(%s)'%(typename,argname,nodetype,callback))
	sizename = 'size%d'%(tabs)
	if sizename not in args.int_args:
		args.int_args.append(sizename)
	if 'accessok' not in args.int_args:
		args.int_args.append('accessok')
	# now first to check for the size
	sizestr = '%s = sizeof((%s'%( sizename,innerargname)
	i = 0
	while i < len(nodetype.arraysize):
		# for like size5 = sizeof((info->mem[0][0]));
		# format
		sizestr += '[0]'
		i += 1
	sizestr += '))'
	i = 0
	while i < len(nodetype.arraysize):
		sizestr += '* %d'%(nodetype.arraysize[i])
		i += 1
	sizestr += ';'
	s += __format_tabs(tabs,sizestr)
	s += __format_tabs(tabs,'accessok = access_pointer((void*)(%s),%s,ACCESS_READ);'%(innerargname,sizename))
	s += __format_tabs(tabs,'if (accessok >= 0) {')
	# to check pointer
	tabs += 1
	assert(len(nodetype.arraysize) == nodetype.arraytype)
	# we start from the start[cnt1][cnt2][cnt3]; list
	i = len(nodetype.arraysize) - 1
	while i >= 0:
		cntname = 'cnt%d'%(tabs)
		cntnamearr.append(cntname)
		if cntname not in args.int_args:
			args.int_args.append(cntname)
		s += __format_tabs(tabs,'for(%s = 0 ; %s < %d;%s ++){'%(
			cntname,cntname,nodetype.arraysize[i],cntname))
		tabs += 1
		i -= 1

	origname = nodetype.namevarname
	tupleargs = []
	if nodetype.ptrtype == 0:
		format_args = r'(&({argname}'
	else:
		format_args = r'({argname}'
	i = 0
	while i < len(cntnamearr):
		format_args += r'[%d]'
		tupleargs.append(cntnamearr[i])
		i += 1
	if nodetype.ptrtype == 0:
		format_args += r'))'
	else:
		format_args += r')'

	s += __format_comment_tabs(args,tabs,'format_args (%s) tupleargs(%s)'%(format_args,tuple(tupleargs)))
	logging.info('format_args (%s) tupleargs(%s)'%(format_args,tuple(tupleargs)))
	_curs , _argname ,oldnamevar = __change_argname(args,tabs,argname,nodetype,format_args,tuple(tupleargs),True)
	s += _curs

	if True:
		pass
	else:
		_argname = '%s'%(innerargname)
		i = 0
		while i < len(cntnamearr):
			_argname += '[%s]'%(cntnamearr[i])
			i += 1
		if nodetype.ptrtype > 0:
			fmtstr = 'snprintf(%s,sizeof(%s),"(%s'%(strname,strname,innerargname)
		else:
			fmtstr = 'snprintf(%s,sizeof(%s),"(&(%s'%(strname,strname,innerargname)
		i = 0 
		while i < len(nodetype.arraysize):
			fmtstr += '[%d]'
			i += 1
		if nodetype.ptrtype > 0:
			fmtstr += ')"'
		else:
			fmtstr += '))"'
		i = 0
		while i < len(nodetype.arraysize):
			fmtstr += ',%s'%(cntnamearr[i])
			i += 1
		fmtstr += ');'

		s += __format_tabs(tabs,fmtstr)
		if nodetype.ptrtype == 0:
			_argname = "&(%s)"%(_argname)
		#s += __format_comment_tabs(args,tabs,'_argname (%s)'%(_argname))
		nodetype.namevarname = strname
		setnodename = 1
	assert(nodetype.checkarrayidx == 0)
	nodetype.checkarrayidx = nodetype.arraytype
	if callback is not None:
		s += callback(args,tabs,typename,_argname,nodetype,ast,ctx)
	nodetype.checkarrayidx = 0
	i = len(cntnamearr) - 1
	while i >= 0:
		tabs -= 1
		s += __format_tabs(tabs,'} /* %s cycle*/'%(cntnamearr[i]))
		i -= 1
	tabs -= 1
	s += __format_tabs(tabs,'} else {')
	if nodetype :
		nodetype.namevarname = oldnamevar
	tabs += 1
	if nodetype.namevarname:
		s += __format_tabs(tabs,'qemu_log_mask(LOG_TRACE,"%%s pointer(%%p:%%d(0x%%x)) not accessible\\n",%s,%s,%s,%s);'%(
			nodetype.namevarname,argname,sizename,sizename))
	else:
		s += __format_tabs(tabs,'qemu_log_mask(LOG_TRACE,"%s pointer(%%p:%%d(0x%%x)) not accessible\\n",%s,%s,%s);'%(
			argname,argname,sizename,sizename))
	tabs -= 1
	s += __format_tabs(tabs,'}')
	assert(origtabs == tabs)
	return s

def __format_basic_array_callback(args,tabs,typename,argname,nodetype,ast,funcname):
	s = ''
	logging.info('(%s)(%s)(%s)'%(typename,argname,nodetype))
	if nodetype.ptrtype > nodetype.checkptridx:
		nodetype.checkptridx += 1
		s += check_pointer_structure(args,tabs,typename,argname,nodetype,ast,__format_basic_array_callback,funcname)
		nodetype.checkptridx -= 1
	else:
		if nodetype.namevarname:
			_strname = nodetype.namevarname
		else:
			_strname = '"%s"'%(argname)
		s += __format_basic_check_inner(args,tabs,typename,argname,nodetype,ast,funcname)
		_strname = None
	return s

def __format_basic_inner_func(args,tabs,argname,nodetype,ast,funcname):
	s = ''
	incnt = 0
	if nodetype.arraytype > nodetype.checkarrayidx:
		s += __format_array_callback(args,tabs,nodetype.typename,argname,nodetype,ast,__format_basic_array_callback,funcname)
	elif nodetype.ptrtype > 0:
		s += check_pointer_structure(args,tabs,nodetype.typename,argname,None,ast,__format_basic_check_inner,funcname)
	else:
		_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(*{argname})',tuple([]))
		s += _curs
		if nodetype and  nodetype.namevarname is not None:
			s += __format_tabs(tabs,'%s(%s,%s);'%(funcname,nodetype.namevarname,_argname))
		else:
			s += __format_tabs(tabs,'%s("%s",%s);'%(funcname,_argname,_argname))
		if nodetype:
			nodetype.namevarname = oldnamevar
	return s

def __format_structure_bool_inner(args,tabs,argname,nodetype,ast):
	return __format_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_bool')

def __format_structure_int_inner(args,tabs,argname,nodetype,ast):
	return __format_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_int')


def __format_structure_buffer_pointer(args,tabs,argname,ptrname,sizename,ast):
	s = ''
	s += __format_tabs(tabs,'qemu_log_trace_buffer("%s->%s","%s->%s",%s->%s,%s->%s);'%(argname,ptrname,argname,ptrname,argname,ptrname,argname,sizename))
	return s

def __format_structure_pointer_inner(args,tabs,argname,nodetype,ast):
	return __format_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_pointer')

def __format_structure_pointer_direct(args,tabs,argname,nodetype,ast):
	s = ''
	if nodetype.namevarname:
		s += __format_tabs(tabs,'qemu_log_trace_pointer(%s,%s);'%(nodetype.namevarname,argname))
	else:
		s += __format_tabs(tabs,'qemu_log_trace_pointer("%s",%s);'%(argname,argname))
	return s

def __format_structure_int64_inner(args,tabs,argname,nodetype,ast):
	return __format_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_int64')

def __format_function_pionter_inner(args,tabs,argname,nodetype,ast):
	s = ''
	if nodetype and nodetype.namevarname:
		s += __format_tabs(tabs,'qemu_log_trace_function_pointer(%s,%s);'%(nodetype.namevarname,argname))
	else:
		s += __format_tabs(tabs,'qemu_log_trace_function_pointer("%s",%s);'%(argname,argname))
	return s

def __format_struct_char_inner_callback(args,tabs,typename,argname,prevnode,ast,ctx):
	return __format_structure_char_inner(args,tabs,argname,prevnode,ast)

def __format_structure_char_inner(args,tabs,argname,nodetype,ast):
	s = ''
	if nodetype and  (nodetype.arraytype > 0) :
		if nodetype.ptrtype > 0:
			if (nodetype.checkptridx+1) >= nodetype.ptrtype :
				if nodetype.namevarname is not None:
					s += __format_tabs(tabs,'qemu_log_trace_string(%s,%s);'%(nodetype.namevarname,argname))
				else:
					s += __format_tabs(tabs,'qemu_log_trace_string("%s",%s);'%(argname,argname))
			else:
				s += __format_comment_tabs(args,tabs,'(%s)(%s)'%(argname,nodetype))
				_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(*{argname})',tuple([]))
				s += _curs
				nodetype.checkptridx += 1
				s += check_pointer_structure(args,tabs,None,_argname,nodetype,ast,__format_struct_char_inner_callback,None)
				nodetype.checkptridx -= 1
				if nodetype :
					nodetype.namevarname = oldnamevar
		else:
			_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(*{argname})',tuple())
			s += _curs
			if nodetype is not None and nodetype.namevarname is not None:
				s += __format_comment_tabs(args,tabs,'(%s)(%s)'%(_argname,nodetype))
				s += __format_tabs(tabs,'qemu_log_trace_char(%s,%s);'%(nodetype.namevarname,_argname))
			else:
				s += __format_comment_tabs(args,tabs,'(%s)(%s)'%(_argname,nodetype))
				s += __format_tabs(tabs,'qemu_log_trace_char("%s",%s);'%(_argname,_argname))
			if nodetype:
				nodetype.namevarname = oldnamevar
	elif nodetype and  (nodetype.ptrtype > 0) :
		if (nodetype.checkptridx+1) >= nodetype.ptrtype :
			if nodetype.namevarname is not None:
				s += __format_tabs(tabs,'qemu_log_trace_string(%s,%s);'%(nodetype.namevarname,argname))
			else:
				s += __format_tabs(tabs,'qemu_log_trace_string("%s",%s);'%(argname,argname))
		else:
			s += __format_comment_tabs(args,tabs,'(%s)(%s)'%(argname,nodetype))
			_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(*{argname})',tuple([]))
			s += _curs
			nodetype.checkptridx += 1
			s += check_pointer_structure(args,tabs,None,_argname,nodetype,ast,__format_struct_char_inner_callback,None)
			nodetype.checkptridx -= 1
			if nodetype :
				nodetype.namevarname = oldnamevar
	else :
		if nodetype is not None and nodetype.namevarname is not None:
			s += __format_comment_tabs(args,tabs,'(%s)(%s)'%(argname,nodetype))
			s += __format_tabs(tabs,'qemu_log_trace_char(%s,%s);'%(nodetype.namevarname,argname))
		else:
			s += __format_comment_tabs(args,tabs,'(%s)(%s)'%(argname,nodetype))
			s += __format_tabs(tabs,'qemu_log_trace_char("%s",%s);'%(argname,argname))
	return s

format_funcs = {
	'_Bool' : __format_structure_bool_inner,
	'uint8_t' : __format_structure_int_inner,
	'uint16_t' : __format_structure_int_inner,
	'uint32_t' : __format_structure_int_inner ,
	'unsigned int' : __format_structure_int_inner,
	'uint64_t' : __format_structure_int64_inner,
	'gpointer' : __format_structure_pointer_inner,
	'char' : __format_structure_char_inner ,
	'int' : __format_structure_int_inner ,
	'unsigned' : __format_structure_int_inner
}

def __last_basic_inner_func(args,tabs,argname,nodetype,ast,funcname):
	s = ''
	if nodetype.namevarname:
		_argname = nodetype.namevarname
	else:
		_argname = '"(%s->%s)"'%(argname,nodetype.memname)
		if nodetype.ptrtype == 0:
			_argname = '"&(%s->%s)"'%(argname,nodetype.memname)

	if nodetype.ptrtype > nodetype.checkptridx:
		#s += __format_comment_tabs(args,tabs,'')
		s += __format_tabs(tabs,'%s(%s,%s);'%(funcname,_argname,argname))
	else:
		#s += __format_comment_tabs(args,tabs,'')
		s += __format_tabs(tabs,'%s(%s,*(%s));'%(funcname,_argname,argname))
	return s


def __last_bool_inner(args,tabs,argname,nodetype,ast):
	return __last_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_bool')

def __last_int_inner(args,tabs,argname,nodetype,ast):
	return __last_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_int')

def __last_pointer_inner(args,tabs,argname,nodetype,ast):
	return __last_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_pointer')

def __last_int64_inner(args,tabs,argname,nodetype,ast):
	return __last_basic_inner_func(args,tabs,argname,nodetype,ast,'qemu_log_trace_int64')



last_funcs = {
	'_Bool' : __last_bool_inner,
	'uint8_t' : __last_int_inner,
	'uint16_t' : __last_int_inner,
	'uint32_t' : __last_int_inner ,
	'unsigned int' : __last_int_inner,
	'uint64_t' : __last_int64_inner,
	'gpointer' : __last_pointer_inner,
	'int' : __last_int_inner,
	'char' : __format_structure_char_inner,
	'long unsigned int' : __last_int_inner,
	'unsigned char' : __format_structure_char_inner
}



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
			s += __format_comment_tabs(args,tabs,'add (%s)'%(newnamevar))
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



def __has_type_decl(ast,typename):
	cnodes = pycencap.get_struct_node(ast,typename)
	if len(cnodes) > 0:
		return True
	cnodes = pycencap.get_enum_node(ast,typename)
	if len(cnodes) > 0 :
		return True
	return False

def __format_multiple_pointer_structure(args,tabs,typename,argname,prevnode,ast,ctx):
	s = ''
	if prevnode is None or (prevnode.checkptridx >= (prevnode.ptrtype - 1)):
		s += check_pointer_structure(args,tabs,typename,argname,prevnode,ast,__format_structure_callback,ctx)
	else:
		prevnode.checkptridx += 1
		_argname = '(*(%s))'%(argname)
		curs,_argname,oldnamevar = __change_argname(args,tabs,argname,prevnode,r'(*({argname}))',tuple())
		s += curs
		s += check_pointer_structure(args,tabs,typename,_argname,prevnode,ast,__format_multiple_pointer_structure,ctx)
		if prevnode :
			prevnode.namevarname = oldnamevar
		prevnode.checkptridx -= 1
	return s

def __format_multiple_function_pointer(args,tabs,typename,argname,prevnode,ast,ctx):
	s = ''
	if prevnode is None or (prevnode.checkptridx >= (prevnode.ptrtype-1)):
		s += __format_function_pionter_inner(args,tabs,argname,prevnode,ast)
	else:
		prevnode.checkptridx += 1
		curs,_argname,oldnamevar = __change_argname(args,tabs,argname,prevnode,r'(*({argname}))',tuple())
		s += curs
		s += check_pointer_structure(args,tabs,typename,_argname,prevnode,ast,__format_multiple_pointer_structure,ctx)
		if prevnode :
			prevnode.namevarname = oldnamevar
		prevnode.checkptridx -= 1
	return s

def __format_structure_array_callback(args,tabs,typename,argname,nodetype,ast,ctx):
	s = ''
	logging.info('(%s)(%s)(%s)'%(typename,argname,nodetype))
	#s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)'%(typename,argname,nodetype))
	output = False
	prevnode = None
	if nodetype :
		prevnode = nodetype.prevnode
	curs , output = __check_recycle_direct(args,tabs,typename,argname,nodetype,ast,output)
	if output :
		# it is for output
		s += curs
		return s
	logging.info('pass __check_recycle')
	#s += __format_comment_tabs(args,tabs,'pass __check_recycle')
	if nodetype and nodetype.ptrtype > nodetype.checkptridx:
		s += check_pointer_structure(args,tabs,typename,argname,nodetype,ast,__format_structure_callback,ctx)
	else:
		s += format_structure(args,tabs,typename,argname,nodetype,ast)
	return s

def __check_endings(args,tabs,typename,argname,prevnode,nodetype,ast,node,output):
	s = ''
	if not output and 'endings' in args.cfgdict.keys():
		edict = args.cfgdict['endings']
		if nodetype.parent_typename in edict.keys():
			struct_endings = edict[nodetype.parent_typename]
			if 'pointers' in struct_endings.keys():
				if nodetype.memname in struct_endings['pointers']:
					output = True
					s += __format_structure_pointer_direct(args,tabs,argname,nodetype,ast)
					logging.info('endings (%s)'%(s))
	return s, output

def __check_recycle_direct(args,tabs,typename,argname,nodetype,ast,output):
	s = ''
	if not output:
		curnode = None
		if nodetype:
			curnode = nodetype.prevnode
		while curnode is not None:
			if curnode.typename == typename:
				# we have pass it ,so we do not make anymore
				#s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)(%s)  already debug'%(typename,argname,nodetype.memname,nodetype))
				if  nodetype.ptrtype > 0:
					s += __format_structure_pointer_direct(args,tabs,argname,nodetype,ast)
				elif nodetype.arraytype == 0 and nodetype.ptrtype == 0 and not nodetype.enumtype:
					_argname = '(&(%s))'%(argname)
					curs , _argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(&({argname}))',tuple())
					s += curs
					s += __format_structure_pointer_direct(args,tabs,_argname,nodetype,ast)
					if nodetype:
						nodetype.namevarname = oldnamevar
					nodetype.namevarname = origname
				output = True
				break
			curnode = curnode.prevnode
	return s, output

def __check_recycle(args,tabs,typename,argname,prevnode,nodetype,ast,node,output):
	s = ''
	if not output:
		curnode = prevnode
		#if curnode is not None:
		#	curnode = curnode.prevnode
		while curnode is not None:
			if curnode.typename == typename:
				# we have pass it ,so we do not make anymore
				s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)(%s)  already debug'%(typename,argname,nodetype.memname,nodetype))
				if  nodetype.ptrtype > 0:
					s += __format_structure_pointer_direct(args,tabs,argname,nodetype,ast)
				elif nodetype.arraytype == 0 and nodetype.ptrtype == 0 and not nodetype.enumtype:
					s += __format_structure_pointer_direct(args,tabs,argname,nodetype,ast)
				output = True
				break
			curnode = curnode.prevnode
	return s, output


def __check_paires(args,tabs,typename,argname,prevnode,nodetype,ast,node,outbufferidx,output):
	s = ''
	if not output and 'pairs' in args.cfgdict.keys():
		pdict = args.cfgdict['pairs']
		if nodetype.parent_typename in pdict.keys():
			struct_pairs = pdict[nodetype.parent_typename]
			findidx = -1
			if 'pointers' in struct_pairs.keys():
				i = 0
				for k in struct_pairs['pointers']:
					if k == nodetype.memname:
						findidx = i
						break
					i += 1
			if findidx < 0 and 'lengths' in struct_pairs.keys():
				i = 0
				for k in struct_pairs['lengths']:
					if k == nodetype.memname:
						findidx = i
						break
					i += 1
			if findidx >= 0:
				output = True
				if findidx not in outbufferidx:
					_ptrname = struct_pairs['pointers'][findidx]
					_sizename = struct_pairs['lengths'][findidx]
					s += __format_structure_buffer_pointer(args,tabs,nodetype.parent_argname,_ptrname,_sizename,ast)
					outbufferidx.append(findidx)
	return s,outbufferidx,output

def __format_structure_struct_basic(args,tabs,typename,argname,nodetype,ast,node,outbufferidx):
	s = ''
	s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)'%(typename,argname,nodetype))
	nodetypeset = 0
	output = False
	prevnode = None
	if nodetype :
		prevnode = nodetype.prevnode
	curs , output = __check_endings(args,tabs,typename,argname,prevnode,nodetype,ast,node,output)
	s += curs

	if not output:
		if nodetype.arraytype > nodetype.checkarrayidx:
			# in array ,so we should make this debug more 
			s += __format_array_callback(args,tabs,nodetype.typename,argname,nodetype,ast,__format_structure_array_callback,None)
			output = True

	# now first to check whether it is debug in the last
	curs , output = __check_recycle(args,tabs,typename,argname,prevnode,nodetype,ast,node,output)
	s += curs
	if nodetype and nodetype.prevnode is None and nodetype != prevnode:
		nodetypeset = 1
		nodetype.prevnode = prevnode
	curs , outbufferidx,output = __check_paires(args,tabs,typename,argname,prevnode,nodetype,ast,node,outbufferidx,output)
	s += curs

	if not output:
		if  (nodetype.structnode is not None):
			if  nodetype.ptrtype == 0 and nodetype.arraytype == 0 and not nodetype.enumtype :
				declnodes = pycencap.get_declare_member(nodetype.structnode)
				logging.info(pycencap.debug_node_array(declnodes,'declnodes (%s)'%(nodetype)))
				if len(declnodes) > 0:
					s += __format_comment_tabs(args,tabs,'')
					# this is inner structure defined ,so we should make the inner structure handle
					# like 
					# struct DeviceState {
					#    struct  { BusState* lh_first; } gpios;
					#    struct ClientHeaders {BusState* lh_first;} headers;
					# }
					s += __format_structure_struct_inner(args,tabs,'',argname,nodetype,ast,nodetype.structnode)
					output = True

	if not output:
		if (nodetype.funcdeclnode is not None):
			if nodetype.ptrtype > (nodetype.checkptridx+1):
				# we use pointer 
				s += check_pointer_structure(args,tabs,typename,argname,nodetype,ast,__format_multiple_function_pointer,1)
				output = True
			elif nodetype.ptrtype > 0:
				s += __format_structure_pointer_direct(args,tabs,argname,nodetype,ast)
				output = True
			else:
				s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)(%s)  not valid function pointer'%(typename,argname,nodetype.memname,nodetype))
				logging.info('/* (%s)(%s)(%s)(%s)  not valid function pointer */'%(typename,argname,nodetype.memname,nodetype))

	if not output:
		s += __format_comment_tabs(args,tabs,'typename (%s)'%(nodetype.typename))
		if nodetype.typename in format_funcs.keys():
			output = True
			s += format_funcs[nodetype.typename](args,tabs,argname,nodetype,ast)

	if not output:
		if __has_type_decl(ast,nodetype.typename):
			s += __format_comment_tabs(args,tabs,'')
			output = True
			if nodetype.arraytype > nodetype.checkarrayidx:
				s += __format_array_callback(args,tabs,nodetype.typename,argname,nodetype,ast,__format_structure_array_callback,None)
			elif nodetype.ptrtype > nodetype.checkptridx:
				s += check_pointer_structure(args,tabs,nodetype.typename,argname,nodetype,ast,__format_multiple_pointer_structure,None)
			else:
				s += format_structure(args,tabs,nodetype.typename,argname,nodetype,ast)
		elif nodetype.ptrtype > 0 :
			output = True
			s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)(%s)  structure not found'%(typename,argname,nodetype.memname,nodetype))
			s += __format_structure_pointer_direct(args,tabs,argname,nodetype,ast)
	if not output:
		s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)(%s)  type not found'%(typename,argname,nodetype.memname,nodetype))
		logging.warn('%s->%s not format\n%s'%(typename,nodetype.memname,pycencap.get_node_desc(node)))
	if nodetypeset != 0:
		nodetype.prevnode = None
	return s,outbufferidx




def __format_structure_struct_inner(args,tabs,typename,argname,prevnode,ast,node):
	s = ''
	outbufferidx = []
	logging.info('Type(%s)(%s)(%s)'%(typename,argname,prevnode))
	if node.__class__.__name__ == 'Typedef':
		# this is typedef structure ,so we should make this
		nodetype = pycencap.get_typedef_type_name(ast,node)
		nodetype.prevnode = prevnode
		# now to give the parent type
		if prevnode:
			nodetype.parent_typename = prevnode.parent_typename
			nodetype.parent_argname = prevnode.parent_argname
			nodetype.memname = prevnode.memname
			nodetype.namevarname = prevnode.namevarname
		if nodetype.funcdeclnode is not None:
			# this is function ,so we should make this function pointer
			# function must be function pointer ,so we do this
			assert(nodetype.ptrtype > 0)			
			# because in the function declare ,it is must be pointer ,so we did this
			_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(*{argname})',tuple([]))
			s += _curs
			_curs,outbufferidx= __format_structure_struct_basic(args,tabs,nodetype.typename,
				_argname,nodetype,ast,node,outbufferidx)			
			s += _curs
			if nodetype:
				nodetype.namevarname = oldnamevar
		else:
			# this is the node for structure
			if nodetype.typename in pycencap.basic_types:
				_curs,outbufferidx = __format_structure_struct_basic(args,tabs,nodetype.typename,argname,nodetype,ast,node,outbufferidx)
				s += _curs
				s += __format_comment_tabs(args,tabs,'node(%s)'%(nodetype))
			else:
				# that is for the structure we find ,so we should find the struct node
				_curs,outbufferidx= __format_structure_struct_basic(args,tabs,nodetype.typename,
					argname,nodetype,ast,node,outbufferidx)
				s += _curs
				s += __format_comment_tabs(args,tabs,'node(%s)'%(nodetype))
		nodetype = None
	else:
		for (cname,c) in node.children():
			if c.__class__.__name__ == 'Decl':
				nodetype = pycencap.get_decl_type_name(ast,c)
				assert(nodetype is not None)
				nodetype.prevnode = prevnode
				if prevnode and prevnode.namevarname:
					nodetype.namevarname = prevnode.namevarname
				if prevnode:
					nodetype.parent_typename = prevnode.typename
					nodetype.parent_argname = argname
				assert(len(nodetype.memname) > 0)
				# now this would be ok for change
				logging.info('Type(%s)(%s)(%s)'%(typename,argname,nodetype))
				#_curs,outbufferidx= __format_structure_struct_basic(args,tabs,typename,argname,nodetype,ast,c,outbufferidx)
				if nodetype.arraytype > 0:
					# for the array type ,so we should make this combine by
					# structptr->arraymem [arrsize1][arrsize2];
					_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'{argname}->%s',tuple([nodetype.memname]))
				elif nodetype.ptrtype > 0 :
					_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'({argname}->%s)',tuple([nodetype.memname]))
				else:
					# this is not pointer ,we should change all into the pointer
					# so we make this handle
					_curs,_argname,oldnamevar = __change_argname(args,tabs,argname,nodetype,r'(&({argname}->%s))',tuple([nodetype.memname]))
				s += _curs
				_curs,outbufferidx= __format_structure_struct_basic(args,tabs,nodetype.typename,
					_argname,nodetype,ast,c,outbufferidx)
				s += _curs
				nodetype = None
			elif c.__class__.__name__ == 'FuncDecl' : 
				logging.info('argname(%s)prevnode(%s)'%(argname,prevnode))
				s += __format_function_pionter_inner(args,tabs,argname,prevnode,ast)
			else:
				s += __format_comment_tabs(args,tabs,'%s : %s\n%s'%(c.__class__.__name__,cname,pycencap.get_node_desc(c)))
				logging.warn('%s : %s\n%s'%(c.__class__.__name__,cname,pycencap.get_node_desc(c)))
	return s



def format_structure(args,tabs,typename,argname,prevnode,ast):
	s = ''
	if tabs > args.maxdepth:
		logging.error('exceeding maxdepth %d (typename:%s)(argname:%s) prevnode(%s)'%(args.maxdepth,typename,argname,prevnode))
		return s
	output = False
	cnodes = pycencap.get_struct_node(ast,typename)
	assert(len(cnodes) <= 1)
	if len(cnodes) > 0 :
		s += __format_structure_struct_inner(args,tabs,typename,argname,prevnode,ast,cnodes[0])
	else:
		cnodes = pycencap.get_enum_node(ast,typename)
		logging.info(pycencap.debug_node_array(cnodes,'cnodes'))
		assert(len(cnodes) <= 1)
		if len(cnodes) > 0 :
			s += __format_tabs(tabs,'qemu_log_trace_int("*(%s)",*(%s));'%(argname,argname))
		else:
			if typename in last_funcs.keys() and prevnode and prevnode.prevnode:
				# it is the basic type so we should give this
				nodetype = pycencap.NodeTypeDecl()
				nodetype.clone(prevnode)
				#s += __format_comment_tabs(args,tabs,'(%s)(%s)(%s)'%(typename,argname,prevnode))
				s += last_funcs[nodetype.typename](args,tabs,argname,nodetype,ast)
				nodetype = None
			else:
				s += __format_comment_tabs(args,tabs,'can not get (%s) argname (%s)'%(typename,argname))
				logging.warn('can not get (%s) argname (%s)'%(typename,argname))
	return s

def init_args_declare(args):
	args.char_array_args = []
	args.int_args = []
	return

def __format_structure_callback(args,tabs,typename,memname,prevnode,ast,ctx):
	logging.info('type(%s)(%s)(%s)'%(typename,memname,prevnode))
	return format_structure(args,tabs,typename,memname,prevnode,ast)

def check_pointer_structure(args,tabs,typename,memname,prevnode,ast,callback=None,ctx=None):
	s = ''
	if 'accessok' not in args.int_args:
		args.int_args.append('accessok')
	sizename = 'size%d'%(tabs)
	if sizename not in args.int_args:
		args.int_args.append(sizename)
	#s += __format_comment_tabs(args,tabs,'Type(%s) (%s)(%s) callback(%s)'%(typename,memname,prevnode,callback))
	s += __format_tabs(tabs,'%s = sizeof(*(%s));'%(sizename,memname))
	s += __format_tabs(tabs,'accessok = access_pointer((void*)(%s),%s,ACCESS_READ);'%(memname,sizename))
	s += __format_tabs(tabs,'if (accessok >= 0) {')
	if callback is not None:
		tabs += 1
		s += callback(args,tabs,typename,memname,prevnode,ast,ctx)
		tabs -= 1
	s += __format_tabs(tabs,'} else {')
	tabs += 1
	if prevnode and prevnode.namevarname:
		s += __format_tabs(tabs,'qemu_log_mask(LOG_TRACE,"%%s pointer(%%p:%%ld(0x%%lx)) not accessible\\n",%s,%s,sizeof(*%s),sizeof(*%s));'%(
			prevnode.namevarname,memname,memname,memname))
	else:
		s += __format_tabs(tabs,'qemu_log_mask(LOG_TRACE,"%s pointer(%%p:%%ld(0x%%lx)) not accessible\\n",%s,sizeof(*%s),sizeof(*%s));'%(
			memname,memname,memname,memname))
	tabs -= 1
	s += __format_tabs(tabs,'}')
	return s

def format_impl_trace(args,funcname,ast):
	s = ''
	params = ''
	i = 0
	tabs = 0
	init_args_declare(args)
	for p in args.funcdict['params']:
		assert(p['name'])
		assert(p['type'])
		if i > 0:
			params += ','
		params += '%s %s'%(p['type'],p['name'])
		i += 1

	s += __format_tabs(tabs,'void impl_trace_%s(%s)'%(funcname,params))
	s += __format_tabs(tabs,'{')
	# now to check the 
	for k in args.funcdict['struct']:
		assert(k['name'])
		assert(k['type'])
		assert(k['arg'])
		decls = ''
		decls += k['type']
		if 'pointertype' in k.keys() and k['pointertype']:
			decls += '*'
		decls += ' %s = (%s'%(k['name'],k['type'])
		if 'pointertype' in k.keys() and k['pointertype']:
			decls += '*'
		decls += ')%s;'%(k['arg'])
		tabs += 1
		s += __format_tabs(tabs,decls)
		tabs -= 1
	tabs += 1
	# we should get the type and first to declare
	structs = ''
	for k in args.funcdict['struct']:
		# space to skip
		structs += __format_tabs(tabs,'')
		roottype = pycencap.NodeTypeDecl()
		roottype.typename = k['type']
		structs += check_pointer_structure(args,tabs,k['type'],k['name'],roottype,ast,__format_structure_callback,None)
		roottype = None

	# now to make sure the 
	for k in args.int_args:
		s += __format_tabs(tabs,'int %s;'%(k))

	for k in args.char_array_args:
		s += __format_tabs(tabs,'char %s[256];'%(k))

	# to make split
	s += __format_tabs(tabs,'')
	s += __format_tabs(tabs,'qemu_log_trace_prefix("%s");'%(funcname))
	s += structs
	# to format the last return run
	s += __format_tabs(tabs,'qemu_log_trace_endfunc("%s");'%(funcname))
	s += __format_tabs(tabs,'return;')
	tabs -= 1
	s += __format_tabs(tabs,'}')
	assert(tabs == 0)	
	return s

def impl_parse_file(args,ast):
	# first to get the defjson
	assert(args.defjson is not None)
	configfp = open(args.defjson,'r+')
	configdict = json.load(configfp)
	configfp.close()
	configfp = None
	configdict = pycencap.Utf8Encode(configdict).get_val()
	fout = sys.stdout
	args.cfgdict= configdict
	if args.output:
		fout = open(args.output,'w+')
	# first to define all the function declare
	fout.write('\n')
	for k in sorted(configdict.keys()):
		if isinstance(configdict[k],dict) :
			# this is the function we call 
			if 'params' in configdict[k].keys() :
				args.funcdict = configdict[k]
				s = format_impl_trace(args,k,ast)
				fout.write('\n')
				#fout.write(decls)
				fout.write(s)
				fout.write('\n')

	if fout != sys.stdout:
		fout.close()
	fout = None

	return

def impl_handler(args,parser):
	set_logging(args)
	if args.input is None:
		sys.stderr.write('%s need input'%(args.subcommand))
		sys.exit(3)
		return
	if platform.system().lower() != 'linux':
		raise Exception('(%s)only linux support'%(platform.system()))
	if args.defjson is None:
		raise Exception('please set defjson by(--defjson|-d)')
	if len(args.subnargs) > 0:
		gccecommand = args.cc
		gccecommand.extend(args.subnargs)
	else:
		gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,impl_parse_file,args)
	sys.exit(0)
	return

def show_impl(args,ast):
	fout = sys.stdout
	if args.output is not None:
		fout = open(args.output,'w+')
	ast.ast.show(buf=fout)
	if fout != sys.stdout:
		fout.close()
	fout = None
	return

def show_handler(args,parser):
	set_logging(args)
	if args.input is None:
		sys.stderr.write('%s need input'%(args.subcommand))
		sys.exit(3)
		return
	if platform.system().lower() != 'linux':
		raise Exception('(%s)only linux support'%(platform.system()))
	if len(args.subnargs) > 0:
		gccecommand = [args.cc]
		gccecommand.extend(args.subnargs)
	else:
		gccecommand = []
	pycencap.parse_file_callback(gccecommand,args.input,show_impl,args)
	sys.exit(0)
	return

def preprocess_handler(args,parser):
	set_logging(args)
	if args.input is None:
		sys.stderr.write('%s need input'%(args.subcommand))
		sys.exit(3)
		return
	if platform.system().lower() != 'linux':
		raise Exception('(%s)only linux support'%(platform.system()))
	if args.defjson is None:
		raise Exception('please set defjson by(--defjson|-d)')
	jsonfp = open(args.defjson,'r+')
	jsondict = json.load(jsonfp)
	jsonfp.close()
	jsonfp = None	
	jsondict = pycencap.Utf8Encode(jsondict).get_val()
	#logging.info('jsondict (%s)'%(jsondict))
	cmds = [args.cc]
	if 'defines' in jsondict.keys() and isinstance(jsondict['defines'],dict):
		for k in jsondict['defines'].keys():
			s = '\'-D%s=%s\''%(k,jsondict['defines'][k])
			cmds.append(s)
			#logging.info('append (%s)'%(s))

	cmds.extend(args.subnargs)
	cmds.append('-E')
	if args.output is not None:
		cmds.append('-o')
		cmds.append(args.output)	
	cmds.append(args.input)
	runcmd = ' '.join(cmds)
	retval = cmdpack.run_cmd_wait(runcmd,1,0)
	if retval != 0:
		logging.error('run (%s) error(%d)'%(cmds,retval))
	sys.exit(retval)
	return

command_line = {
	'impl<impl_handler>## impl trace input ##' : {
		'$' : '*'
	},
	'preprocess<preprocess_handler>## preprocess file ##' : {
		'$' : '*'
	},
	'show<show_handler>## show ast ##' : {
		'$' : '*'
	},
	'maxdepth|d' : 50,
	'input|i' : None,
	'output|o' : None,
	'verbose|v' : '+',
	'cc|C' : '/usr/bin/gcc',
	'defjson|D' : None
}

def main():
	global command_line
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line(command_line)
	parser.parse_command_line(None,parser)
	return

if __name__ == '__main__':
	main()