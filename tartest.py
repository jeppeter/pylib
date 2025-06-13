#! /usr/bin/env python

import extargsparse
import tarfile
import logging
import sys
import os
import tempfile
import shutil
import subprocess
import time
import datetime

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','pythonlib'))
sys.path.append('/usr/sbin/nanopi')
from common_util import set_logging,set_logging_args
import tarmode

def main():
    commandline='''
    {
    	"reserved" : false,
        "input|i" : null,
        "output|o" : null
    }
    '''
    parser = extargsparse.ExtArgsParse()
    set_logging_args(parser)
    parser.load_command_line_string(commandline)
    parser = tarmode.load_tar_commands(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
