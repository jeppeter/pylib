#! /usr/bin/env python

LOG_C_CODE='''

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <execinfo.h>

int get_%LOGGER_NAME%_level()
{
	static int st_%LOGGER_NAME%_level = %LOGGER_UPPER_NAME%_LOG_ERROR;
	static int st_%LOGGER_NAME%_inited = 0;
	char* envstr=NULL;

	if (st_%LOGGER_NAME%_inited != 0) {
		return st_%LOGGER_NAME%_level;
	}

	envstr = getenv("%LOGGER_UPPER_NAME%_LOG_LEVEL");
	if (envstr != NULL) {
		st_%LOGGER_NAME%_level = atoi(envstr);
	}
	st_%LOGGER_NAME%_inited = 1;
	return st_%LOGGER_NAME%_level;
}

int check_%LOGGER_NAME%_level(int level)
{
	int inlevel = 0;

	inlevel = get_%LOGGER_NAME%_level();
	if (inlevel >= level) {
		return 1;
	}
	return 0;
}

char* format_%LOGGER_NAME%_level(int level)
{
	if (level <= %LOGGER_UPPER_NAME%_LOG_ERROR) {
		return "ERROR";
	} else if (level > %LOGGER_UPPER_NAME%_LOG_ERROR && level <= %LOGGER_UPPER_NAME%_LOG_WARN) {
		return "WARN";
	} else if (level > %LOGGER_UPPER_NAME%_LOG_WARN && level <= %LOGGER_UPPER_NAME%_LOG_INFO) {
		return "INFO";
	} else if (level > %LOGGER_UPPER_NAME%_LOG_INFO && level <= %LOGGER_UPPER_NAME%_LOG_DEBUG) {
		return "DEBUG";
	}
	return "TRACE";
}

int %LOGGER_NAME%_back_trace(int level,char* file, int lineno,const char* fmt,...)
{
	void** ptracebuf= NULL;
	int tracesize = 16;
	int tracelen = 0;
	int ret;
	char** psymbols=NULL;
	va_list ap;
	int i;
	int retlen = 0;

	if (check_%LOGGER_NAME%_level(level) == 0 ){
		retlen += 1;
		return retlen;
	}

	while(1) {
		if (ptracebuf) {
			free(ptracebuf);
		}
		ptracebuf=  NULL;
		ptracebuf = malloc(sizeof(*ptracebuf) * tracesize);
		if (ptracebuf == NULL) {
			break;
		}

		ret = backtrace(ptracebuf,tracesize);
		if (ret >= tracesize) {
			tracesize <<= 1;
			continue;
		}
		tracelen = ret;

		psymbols = backtrace_symbols(ptracebuf,tracelen);
		if (psymbols == NULL) {
			break;
		}

		retlen += fprintf(stderr,"[%s:%d] SYMBOLSFUNC <%s> ",file,lineno,format_%LOGGER_NAME%_level(level));
		if (fmt != NULL) {
			va_start(ap,fmt);
			vfprintf(stderr,fmt,ap);
		}

		for(i=1;i<tracelen;i++) {
			retlen += fprintf(stderr,"%LINE_RETURN%FUNC[%d] [%s] [%p]",i-1, psymbols[i],ptracebuf[i]);
		}
		retlen += fprintf(stderr,"%LINE_RETURN%");
		break;
	}

	if (psymbols) {
		free(psymbols);
	}
	psymbols = NULL;

	if (ptracebuf) {
		free(ptracebuf);
	}
	ptracebuf = NULL;
	return retlen;
}



/* @param flag bit0= do not complain loudly if no wather is active
*/
int %LOGGER_NAME%_log(int level,const char* file,int lineno, const char* fmt,...)
{
	va_list ap;
	int retlen = 0;

	if (check_%LOGGER_NAME%_level(level) == 0) {
		retlen += 1;
		return retlen;
	}

	retlen += fprintf(stderr,"[%s:%d] <%s> ",file,lineno,format_%LOGGER_NAME%_level(level));
	va_start(ap,fmt);
	retlen += vfprintf(stderr,fmt,ap);
	retlen += fprintf(stderr,"%LINE_RETURN%");
	fflush(stderr);
	return retlen;
}

int %LOGGER_NAME%_buffer_log(int level, const char* file,int lineno,void* pbuf,int size,const char* fmt,...)
{
	unsigned char* ptr=(unsigned char*)pbuf;
	int lasti;
	int i;
	va_list ap;
	int retlen=0;

	if (check_%LOGGER_NAME%_level(level) == 0) {
		retlen += 1;
		return retlen;
	}

	retlen += fprintf(stderr,"[%s:%d] <%s> [%p] size[%d:0x%x]", file,lineno,format_%LOGGER_NAME%_level(level),ptr,size,size);
	va_start(ap,fmt);
	retlen += vfprintf(stderr,fmt,ap);

	lasti = 0;
	for(i=0;i<size;i++) {
		if ((i % 16) == 0) {
			if (i > 0) {
				retlen += fprintf(stderr,"    ");
				while(lasti != i) {
					if (ptr[lasti] >= 0x20 && ptr[lasti] <= 0x7e) {
						retlen += fprintf(stderr,"%c",ptr[lasti]);
					} else {
						retlen += fprintf(stderr, ".");
					}
					lasti ++;
				}
			}
			retlen += fprintf(stderr,"%LINE_RETURN%0x%08x:",i);
		}
		retlen += fprintf(stderr," 0x%02x",ptr[i]);
	}

	if (lasti != i) {
		while((i % 16)!=0) {
			retlen += fprintf(stderr,"     ");
			i ++;
		}

		retlen += fprintf(stderr,"    ");
		while(lasti < size) {
			if (ptr[lasti] >= 0x20 && ptr[lasti] <= 0x7e) {
				retlen += fprintf(stderr,"%c",ptr[lasti]);
			} else {
				retlen += fprintf(stderr, ".");
			}
			lasti ++;
		}		
 	}
 	retlen += fprintf(stderr,"%LINE_RETURN%");
 	return retlen;
}
'''

GCC_PUSH_CODE='''
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wvariadic-macros"
'''

GCC_POP_CODE='''
#pragma GCC diagnostic pop
'''

LOG_H_CODE='''
#ifndef %HEADER_GUIDED%
#define %HEADER_GUIDED%



#define %LOGGER_UPPER_NAME%_LOG_ERROR              0
#define %LOGGER_UPPER_NAME%_LOG_WARN               10
#define %LOGGER_UPPER_NAME%_LOG_INFO               20
#define %LOGGER_UPPER_NAME%_LOG_DEBUG              30
#define %LOGGER_UPPER_NAME%_LOG_TRACE              40



#define %LOGGER_UPPER_NAME%_BACKTRACE_ERROR(...)  do{ %LOGGER_NAME%_back_trace(%LOGGER_UPPER_NAME%_LOG_ERROR,__FILE__,__LINE__,__VA_ARGS__); }while(0)
#define %LOGGER_UPPER_NAME%_ERROR(...)       %LOGGER_NAME%_log(%LOGGER_UPPER_NAME%_LOG_ERROR,__FILE__,__LINE__,__VA_ARGS__);
#define %LOGGER_UPPER_NAME%_BUFFER_ERROR(ptr,size,...)  %LOGGER_NAME%_buffer_log(%LOGGER_UPPER_NAME%_LOG_ERROR,__FILE__,__LINE__,(void*)(ptr),(int)(size),__VA_ARGS__);

#define %LOGGER_UPPER_NAME%_BACKTRACE_WARN(...)  do{ %LOGGER_NAME%_back_trace(%LOGGER_UPPER_NAME%_LOG_WARN,__FILE__,__LINE__,__VA_ARGS__); }while(0)
#define %LOGGER_UPPER_NAME%_WARN(...)       %LOGGER_NAME%_log(%LOGGER_UPPER_NAME%_LOG_WARN,__FILE__,__LINE__,__VA_ARGS__);
#define %LOGGER_UPPER_NAME%_BUFFER_WARN(ptr,size,...)  %LOGGER_NAME%_buffer_log(%LOGGER_UPPER_NAME%_LOG_WARN,__FILE__,__LINE__,(void*)(ptr),(int)(size),__VA_ARGS__);

#define %LOGGER_UPPER_NAME%_BACKTRACE_INFO(...)  do{ %LOGGER_NAME%_back_trace(%LOGGER_UPPER_NAME%_LOG_INFO,__FILE__,__LINE__,__VA_ARGS__); }while(0)
#define %LOGGER_UPPER_NAME%_INFO(...)       %LOGGER_NAME%_log(%LOGGER_UPPER_NAME%_LOG_INFO,__FILE__,__LINE__,__VA_ARGS__);
#define %LOGGER_UPPER_NAME%_BUFFER_INFO(ptr,size,...)  %LOGGER_NAME%_buffer_log(%LOGGER_UPPER_NAME%_LOG_INFO,__FILE__,__LINE__,(void*)(ptr),(int)(size),__VA_ARGS__);


#define %LOGGER_UPPER_NAME%_BACKTRACE_DEBUG(...)  do{ %LOGGER_NAME%_back_trace(%LOGGER_UPPER_NAME%_LOG_DEBUG,__FILE__,__LINE__,__VA_ARGS__); }while(0)
#define %LOGGER_UPPER_NAME%_DEBUG(...)       %LOGGER_NAME%_log(%LOGGER_UPPER_NAME%_LOG_DEBUG,__FILE__,__LINE__,__VA_ARGS__);
#define %LOGGER_UPPER_NAME%_BUFFER_DEBUG(ptr,size,...)  %LOGGER_NAME%_buffer_log(%LOGGER_UPPER_NAME%_LOG_DEBUG,__FILE__,__LINE__,(void*)(ptr),(int)(size),__VA_ARGS__);

#define %LOGGER_UPPER_NAME%_BACKTRACE_TRACE(...)  do{ %LOGGER_NAME%_back_trace(%LOGGER_UPPER_NAME%_LOG_TRACE,__FILE__,__LINE__,__VA_ARGS__); }while(0)
#define %LOGGER_UPPER_NAME%_TRACE(...)       %LOGGER_NAME%_log(%LOGGER_UPPER_NAME%_LOG_TRACE,__FILE__,__LINE__,__VA_ARGS__);
#define %LOGGER_UPPER_NAME%_BUFFER_TRACE(ptr,size,...)  %LOGGER_NAME%_buffer_log(%LOGGER_UPPER_NAME%_LOG_TRACE,__FILE__,__LINE__,(void*)(ptr),(int)(size),__VA_ARGS__);


#endif /* %HEADER_GUIDED% */

'''


import extargsparse
import sys
import socket
import logging
import re
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import fileop
import logop
import strutils


def logc_handler(args,parser):
	logop.set_logging(args)
	name = args.subnargs[0]
	nameupper = '%s'%(name.upper())
	s = LOG_C_CODE.replace('%LOGGER_NAME%',name)
	s = s.replace('%LOGGER_UPPER_NAME%',nameupper)
	s = s.replace('%LINE_RETURN%','\\n')
	fileop.write_file(s,args.output)
	sys.exit(0)
	return

def logh_handler(args,parser):
	logop.set_logging(args)
	name = args.subnargs[0]
	nameupper = '%s'%(name.upper())
	head_name = 'log.h'
	if args.output is not None:
		head_name = os.path.basename(args.output)
	head_name = head_name.upper()
	head_name = head_name.replace('.','_')
	logging.info('strutils has\n%s'%(dir(strutils)))
	ranstr = strutils.rand_bytes(16)
	ranstr = ranstr.upper()
	head_guided = '__%s_%s__'%(head_name,ranstr)
	s = LOG_H_CODE.replace('%LOGGER_NAME%',name)
	s = s.replace('%LOGGER_UPPER_NAME%',nameupper)
	s = s.replace('%HEADER_GUIDED%', head_guided)
	fileop.write_file(s,args.output)
	sys.exit(0)
	return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "logc<logc_handler>##nameprefix to used name prefix##" : {
        	"$" : 1
        },
        "logh<logh_handler>##nameprefix to used##" : {
        	"$" : 1
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    logop.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()
