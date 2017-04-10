import sys

def get_cur_info(depth=1):
	frm = sys._getframe((depth))
	return '[%s:%s:%d]'%(frm.f_code.co_filename,frm.f_code.co_name,frm.f_lineno)


def filter_log(callstack=2):
	def filter_call(f):
		def set_filter(*args,**kwargs):
			s = '%s call %s args['%(get_cur_info(callstack),f.__name__)
			idx = 0
			for c in args:
				if idx >0 :
					s += ','
				s += '%s'%(c)
				idx += 1
			s += ']'
			s += ' kwargs ('
			idx = 0
			for k in kwargs.keys():
				if idx > 0 :
					s += ','
				s += '%s : %s'%(k,kwargs[k])
				idx += 1
			s += ')\n'
			sys.stderr.write('%s'%(s))
			retval = f (*args,**kwargs)
			s = '%s %s retval (%s)\n'%(get_cur_info(callstack),f.__name__,repr(retval))
			sys.stderr.write('%s'%(s))
			return retval
		return set_filter
	return filter_call


@filter_log(2)
def call_retwo(cc=None,bb='WW'):
	return 'ss','ee'

def main():
	call_retwo()
	return
main()
