#! /usr/bin/env python
import extargsparse
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
from loglib import set_logging,load_log_commandline
import netop


def downurl_handler(args,parser):
	set_logging(args)
	url = args.subnargs[0]
	ofile = None
	if len(args.subnargs) > 1:
		ofile = args.subnargs[1]

	down = netop.DownloadUrl(url,ofile)
	retval = down.download()
	if not retval:
		sys.exit(1)
	sys.exit(0)
	return


def main():
    commandline_fmt='''
    {
        "input|i" : null,
        "output|o" : null,
        "downurl<downurl_handler>##url [outputfile] ... to download for output##" : {
        	"$" : "+"
        }
    }
    '''
    defcpandir = '%s/.cpan'%(os.environ['HOME'])
    commandline = commandline_fmt
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
