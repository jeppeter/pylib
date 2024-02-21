#! /usr/bin/env python

import extargsparse
import logging
import sys
import os
import apt



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import fileop
import logop


def cachelist_handler(args,parser):
	logop.set_logging(args)
	cache = apt.Cache()
	for p in cache:
		sys.stdout.write('%s %s\ncandidate\ndependencies\n'%(p,dir(p),dir(p.candidate)))
	sys.exit(0)
	return

def depmap_handler(args,parser):
	logop.set_logging(args)
	depmap = dict()
	rdepmap = dict()
	cache = apt.Cache()
	for p in cache:
		if 'dependencies' in dir(p.candidate):
			sys.stdout.write('%s deps %s\n'%(p,p.candidate.dependencies))
		else:
			sys.stdout.write('%s candidate\n%s\n'%(p,dir(p.candidate)))
	sys.exit(0)
	return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "cachelist<cachelist_handler>##to list cache##" : {
            "$" : 0
        },
        "depmap<depmap_handler>##to format dep map##" : {
        	"$" : 0
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