#! /usr/bin/env python

import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
import extargsparse
from loglib import set_logging,load_log_commandline
from strop import parse_int
from procop import ProcExpolore


def ps_handler(args,parser):
	set_logging(args)
	ps = ProcExpolore()
	ps.snapshot()
	pinfos = ps.result()
	for k,v in pinfos.items():
		sys.stdout.write('[%s]=[%s]\n'%(k,v))

	sys.exit(0)
	return



def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "ps<ps_handler>##to list process information##" : {
        	"$" : 0
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
