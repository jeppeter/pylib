#!/usr/bin/env python

##extractstart 
import os
import sys
import json
import logging
import re
import importlib
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import __key__ as keyparse
if sys.version[0] == '2':
    import StringIO
else:
    import io as StringIO


##extractend

COMMAND_SET = 10
SUB_COMMAND_JSON_SET = 20
COMMAND_JSON_SET = 30
ENVIRONMENT_SET = 40
ENV_SUB_COMMAND_JSON_SET = 50
ENV_COMMAND_JSON_SET = 60
DEFAULT_SET = 70




class _LoggerObject(object):
    def __init__(self,cmdname='extargsparse'):
        self.__logger = logging.getLogger(cmdname)
        if len(self.__logger.handlers) == 0:
            loglvl = logging.WARN
            lvlname = '%s_LOGLEVEL'%(cmdname)
            lvlname = lvlname.upper()
            if lvlname in os.environ.keys():
                v = os.environ[lvlname]
                vint = 0
                try:
                    vint = int(v)
                except:
                    vint = 0
                if vint >= 4:
                    loglvl = logging.DEBUG
                elif vint >= 3:
                    loglvl = logging.INFO
            handler = logging.StreamHandler()
            fmt = "%(levelname)-8s %(message)s"
            fmtname = '%s_LOGFMT'%(cmdname)
            fmtname = fmtname.upper()
            if fmtname in os.environ.keys():
                v = os.environ[fmtname]
                if v is not None and len(v) > 0:
                    fmt = v
            formatter = logging.Formatter(fmt)
            handler.setFormatter(formatter)
            self.__logger.addHandler(handler)
            self.__logger.setLevel(loglvl)
            # we do not want any more output debug
            self.__logger.propagate = False

    def format_string(self,arr):
        s = ''
        if isinstance(arr,list):
            i = 0
            for c in arr:
                s += '[%d]%s\n'%(i,c)
                i += 1
        elif isinstance(arr,dict):
            for c in arr.keys():
                s += '%s=%s\n'%(c,arr[c])
        else:
            s += '%s'%(arr)
        return s

    def format_call_msg(self,msg,callstack):
        inmsg = ''  
        if callstack is not None:
            try:
                frame = sys._getframe(callstack)
                inmsg += '[%-10s:%-20s:%-5s] '%(frame.f_code.co_filename,frame.f_code.co_name,frame.f_lineno)
            except:
                inmsg = ''
        inmsg += msg
        return inmsg

    def info(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.info('%s'%(inmsg))

    def error(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.error('%s'%(inmsg))

    def warn(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.warn('%s'%(inmsg))

    def debug(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.debug('%s'%(inmsg))

    def fatal(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.fatal('%s'%(inmsg))

    def call_func(self,funcname,*args,**kwargs):
        mname = '__main__'
        fname = funcname
        try:
            if '.' not in funcname:
                m = importlib.import_module(mname)
            else:
                sarr = re.split('\.',funcname)
                mname = '.'.join(sarr[:-1])
                fname = sarr[-1]
                m = importlib.import_module(mname)
        except ImportError as e:
            self.error('can not load %s'%(mname))
            return None

        for d in dir(m):
            if d == fname:
                val = getattr(m,d)
                if hasattr(val,'__call__'):
                    return val(*args,**kwargs)
        self.error('can not call %s'%(funcname))
        return None

class ExtArgsOptions(_LoggerObject):
    default_values = {
        'prog' : sys.argv[0],
        'usage' : '',
        'description' : '',
        'epilog' : '',
        'version' : '0.0.1',
        'errorhandler' : 'exit',
        'helphandler' : None,
        'longprefix' : '--',
        'shortprefix' : '-',
        'nohelpoption' : False,
        'nojsonoption' : False,
        'helplong' : 'help',
        'helpshort' : 'h',
        'jsonlong' : 'json',
        'cmdprefixadded' : True,
        'parseall' : True,
        'screenwidth' : 80,
        'flagnochange' :  False
    }
    def __setting_object(self,setting):
        for k in setting.keys():
            if k.startswith('_'):
                continue
            setattr(self,k,setting[k])
        return

    def __setting_string(self,setting):
        try:
            d = json.loads(setting)
            d = keyparse.Utf8Encode(d).get_val()
            self.__setting_object(d)
        except:
            pass
        return

    def __init__(self,setting=None):
        super(ExtArgsOptions,self).__init__()
        self.__obj = dict()
        self.__access = dict()
        self.__logger = _LoggerObject()
        # now to set the default values
        for k in self.__class__.default_values.keys():
            self.__setattr__(k,self.__class__.default_values[k])
        if setting is not None:
            if isinstance(setting,str):
                self.__setting_string(setting)
            elif isinstance(setting,dict):
                self.__setting_object(setting)
        return

    def __setattr__(self,key,val):
        if not key.startswith('_'):
            self.info('%s=%s'%(key,val),2)
            self.__obj[key] = val
            self.__access[key] = True
            return
        self.__dict__[key] = val
        return

    def __getattr__(self,key):
        if not key.startswith('_'):
            if key in self.__obj.keys():
                return self.__obj[key]
            return None
        return self.__dict__[key]

    def __format(self):
        s = '{'
        for k in self.__obj.keys():
            s += '%s=%s;'%(k,self.__obj[k])
        s += '}'
        return s

    def __str__(self):
        return self.__format()

    def __repr__(self):
        return self.__format()

    def is_accessed(self,k):
        if k.startswith('_'):
            return False
        if k not in self.__access.keys():
            return False
        return self.__access[k]


class _HelpSize(_LoggerObject):
    #####################################
    ##
    ##  parser.opts = []
    ##  parser.cmdname = ''
    ##  parser.subcommands = []
    ##  parser.callfunction = None
    ##  parser.helpinfo  = None
    ##  parser.keycls = keycls
    #####################################    
    sizewords = ['optnamesize','optexprsize','opthelpsize','cmdnamesize','cmdhelpsize']
    def __init__(self):
        super(_HelpSize,self).__init__()
        self.optnamesize = 0
        self.optexprsize = 0
        self.opthelpsize = 0
        self.cmdnamesize = 0
        self.cmdhelpsize = 0
        return

    def __setattr__(self,name,value):
        if name in self.__class__.sizewords:
            if value >= getattr(self,name,0):
                self.__dict__[name] = value
            return
        self.__dict__[name] = value
        return

    def __str__(self):
        s = '{'
        i = 0
        for n in sizewords:
            if i > 0:
                s += ','
            s += '%s=%d'%(n,getattr(self,n,0))
            i += 1
        s += '}'
        return s


class _ParserCompact(_LoggerObject):
    def __get_help_info(self,keycls):
        if keycls.attr is not None and keycls.attr.opthelp is not None:
            helpinfo = self.call_func(keycls.attr.opthelp,keycls)
        else:
            helpinfo = ''
            if keycls.type == 'bool':
                if keycls.value :
                    helpinfo += '%s set false default(True)'%(keycls.optdest)
                else:
                    helpinfo += '%s set true default(False)'%(keycls.optdest)
            elif keycls.type == 'string' and keycls.value == '+':
                if keycls.isflag:
                    helpinfo += '%s inc'%(keycls.optdest)
                else:
                    raise Exception('cmd(%s) can not set value(%s)'%(keycls.cmdname,keycls.value))
            elif keycls.type == 'help' :
                helpinfo += 'to display this help information'
            else:
                if keycls.isflag :
                    helpinfo += '%s set default(%s)'%(keycls.optdest,keycls.value)
                else:
                    helpinfo += '%s command exec'%(keycls.cmdname)
            if keycls.helpinfo:
                helpinfo = keycls.helpinfo
        return helpinfo

    def __init__(self,keycls=None,opt=None):
        if opt is not None and not issubclass(opt.__class__, ExtArgsOptions):
            raise Exception('opt not ExtArgsOptions type')
        super(_ParserCompact,self).__init__()
        if keycls is not None:
            assert(keycls.iscmd)
            self.keycls = keycls
            self.cmdname = keycls.cmdname
            self.cmdopts = []
            self.subcommands = []
            self.helpinfo = '%s handler'%(self.cmdname)
            if keycls.helpinfo is not None:
                self.helpinfo = keycls.helpinfo
            self.callfunction = None
            if keycls.function is not None:
                self.callfunction = keycls.function
        else:
            # it is main cmd
            self.keycls = keyparse.ExtKeyParse('','main',{},False)
            self.cmdname = ""
            self.cmdopts = []
            self.subcommands = []
            self.helpinfo = None
            self.callfunction = None        
        self.screenwidth = 80
        if opt is not None and issubclass(opt.__class__,ExtArgsOptions) and opt.screenwidth is not None:
            self.screenwidth = opt.screenwidth
        if self.screenwidth < 40:
            self.screenwidth = 40
        self.epilog = None
        self.description = None
        self.prog = None
        self.usage = None
        self.version = None
        if opt is not None:
            self.prog = opt.prog
        return

    def __get_opt_help(self,opt):        
        lname = opt.longopt
        sname = opt.shortopt
        optname = lname 
        if sname is not None:
            optname += '|%s'%(sname)
        optexpr = ''
        if opt.type != 'bool' and opt.type != 'args' and opt.type != 'dict' and opt.type != 'help':
            optexpr = opt.varname
            optexpr = optexpr.replace('-','_')
        opthelp = self.__get_help_info(opt)
        return optname,optexpr,opthelp

    # return optnamesize optexprsize opthelpsize
    #  cmdnamesize cmdhelpsize
    def get_help_size(self,helpsize=None,recursive=0):
        if helpsize is None:
            helpsize = _HelpSize()
        cmdname,cmdhelp = self.__get_cmd_help(self)
        helpsize.cmdnamesize = len(cmdname)
        helpsize.cmdhelpsize = len(cmdhelp)
        for opt in self.cmdopts:
            if opt.type == 'args' :
                continue
            optname,optexpr,opthelp = self.__get_opt_help(opt)
            helpsize.optnamesize = len(optname) + 1
            helpsize.optexprsize = len(optexpr) + 1
            helpsize.opthelpsize = len(opthelp) + 1        

        if recursive != 0:
            for cmd in self.subcommands:
                if recursive > 0:
                    helpsize = cmd.get_help_size(helpsize,recursive-1)
                else:
                    helpsize = cmd.get_help_size(helpsize,recursive)
        for cmd in self.subcommands:
            helpsize.cmdnamesize = len(cmd.cmdname) + 2
            helpsize.cmdhelpsize = len(cmd.helpinfo)
        return helpsize

    def __get_cmd_help(self,cmd):
        cmdname = ''
        cmdhelp = ''
        if cmd.cmdname is not None:
            cmdname = '[%s]'%(cmd.cmdname)
        if cmd.helpinfo is not None:
            cmdhelp = '%s'%(cmd.helpinfo)
        return cmdname,cmdhelp

    def __get_indent_string(self,s,indentsize,maxsize):
        rets = ''
        curs = ' ' * indentsize
        for c in s:
            if (c == ' ' or c == '\t') and len(curs) >= maxsize:
                rets += curs + '\n'
                curs = ' ' * indentsize
                continue
            curs += c
        if curs.strip(' \t') != '':
            rets += curs + '\n'
        curs = ''
        return rets


    def get_help_info(self,helpsize=None,parentcmds=[]):
        if helpsize is None:
            helpsize = self.get_help_size()
        s = ''
        if len(parentcmds) == 0 and self.usage is not None and len(self.usage) > 0:
            s += '%s'%(self.usage)
        else:
            rootcmds = self
            curcmd = self            
            if len(parentcmds) > 0:
                rootcmds = parentcmds[0]
            self.debug('curcmd %s'%(curcmd))
            if rootcmds.prog is not None:
                s += '%s'%(rootcmds.prog)
            else:
                s += '%s'%(sys.argv[0])
            if rootcmds.version is not None:
                s += ' %s'%(rootcmds.version)
            if len(parentcmds) > 0:
                for c in parentcmds:
                        s += ' %s'%(c.cmdname)
            s += ' %s'%(self.cmdname)
            if curcmd.helpinfo is not None and len(curcmd.helpinfo) > 0:
                s += ' %s'%(curcmd.helpinfo)
            else:
                if len(self.cmdopts) > 0:
                    s += ' [OPTIONS]'
                if len(self.subcommands) > 0:
                    s += ' [SUBCOMMANDS]'
                for args in self.cmdopts:
                    if args.flagname == '$':
                        if isinstance(args.nargs,str):
                            if args.nargs == '+' :
                                s += ' args...'
                            elif args.nargs == '*':
                                s += ' [args...]'
                            elif args.nargs == '?':
                                s += ' arg'
                        else:
                            if args.nargs > 1:
                                s += ' args...'
                            elif args.nargs == 1:
                                s += ' arg'
                            else:
                                s += ''
                            break
            s += '\n'
        if self.description is not None:
            s += '%s\n'%(self.description)        
        if len(self.cmdopts) > 0:
            s += '[OPTIONS]\n'
            for opt in self.cmdopts:
                if opt.type == 'args' :
                    continue
                optname,optexpr,opthelp = self.__get_opt_help(opt)
                curs = ''
                curs += ' ' * 4 
                curs += '%-*s %-*s %-*s\n'%(helpsize.optnamesize,optname,helpsize.optexprsize,optexpr,helpsize.opthelpsize,opthelp)
                if len(curs) < self.screenwidth :
                    s += curs
                else:
                    curs = ''
                    curs += ' ' * 4
                    curs += '%-*s %-*s'%(helpsize.optnamesize,optname,helpsize.optexprsize,optexpr)
                    s += curs + '\n'
                    if self.screenwidth >= 60:
                        s += self.__get_indent_string(opthelp,20, self.screenwidth)
                    else:
                        s += self.__get_indent_string(opthelp,15,self.screenwidth)

        if len(self.subcommands)>0:
            s += '[SUBCOMMANDS]\n'
            for cmd in self.subcommands:
                cmdname,cmdhelp = self.__get_cmd_help(cmd)
                curs = ''
                curs += ' ' * 4
                curs += '%-*s %-*s'%(helpsize.cmdnamesize,cmdname,helpsize.cmdhelpsize,cmdhelp)
                if len(curs) < self.screenwidth:
                    s += curs + '\n'
                else:
                    curs = ''
                    curs += ' ' * 4
                    curs += '%-*s'%(helpsize.cmdnamesize,cmdname)
                    s += curs + '\n'
                    if self.screenwidth >= 60:                        
                        s += self.__get_indent_string(cmdhelp,20, self.screenwidth)
                    else:
                        s += self.__get_indent_string(cmdhelp,15,self.screenwidth)

        if self.epilog is not None:
            s += '\n%s\n'%(self.epilog)
        self.info('%s'%(s))
        return s

    def __str__(self):
        s = '@%s|'%(self.cmdname)
        if len(self.subcommands) > 0:
            s += 'subcommands[%d]<'%(len(self.subcommands))
            i = 0
            for c in self.subcommands:
                if i > 0:
                    s += '|'
                s += '%s'%(c.cmdname)
                i += 1
            s += '>'

        if len(self.cmdopts) > 0:
            s += 'cmdopts[%d]<'%(len(self.cmdopts))
            i = 0
            for opt in self.cmdopts:
                s += '%s'%(opt)
            s += '>'
        return s

class _ParseState(_LoggerObject):
    def __init__(self,args,maincmd,optattr=None):
        super(_ParseState,self).__init__()
        if optattr is None:
            optattr = ExtArgsOptions()
        elif not issubclass(optattr.__class__,ExtArgsOptions):
            raise Exception('[%s] not ExtArgsOptions or subclass'%(optattr))
        self.__cmdpaths=[maincmd]
        self.__curidx=0
        self.__curcharidx=-1
        self.__shortcharargs = -1
        self.__longargs = -1
        self.__keyidx = -1
        self.__validx = -1
        self.__args = args
        self.__ended = 0
        self.__longprefix = optattr.longprefix
        self.__shortprefix = optattr.shortprefix
        if self.__shortprefix is None or self.__longprefix is None or \
            self.__longprefix != self.__shortprefix:
            self.__bundlemode = True
        else:
            self.__bundlemode = False
        self.__parseall = optattr.parseall
        self.__leftargs = []
        return

    def format_cmdname_path(self,curparser=None):
        cmdname = ''
        if curparser is  None:
            curparser = self.__cmdpaths
        for c in curparser:
            if len(cmdname) > 0:
                cmdname += '.'
            cmdname += c.cmdname
        return cmdname

    def __find_sub_command(self,name):
        cmdparent = self.__cmdpaths[-1]
        for cmd in cmdparent.subcommands:
            if cmd.cmdname == name:
                # we find the next command
                self.__cmdpaths.append(cmd)
                return cmd.keycls
        return None

    def add_parse_args(self,nargs):
        if self.__curcharidx >= 0 :
            if nargs > 0 and self.__shortcharargs > 0:
                raise Exception('[%s] already set args'%(self.__args[self.__curidx]))
            if self.__shortcharargs < 0:
                self.__shortcharargs = 0
            self.__shortcharargs += nargs
        else:
            if self.__longargs > 0:
                raise Exception('[%s] not handled '%(self.__args[self.__curidx]))
            if self.__longargs < 0:
                self.__longargs = 0
            self.__longargs += nargs
            self.info('longargs [%d] nargs[%d]'%(self.__longargs,nargs))
        return



    def __find_key_cls(self):
        if self.__ended > 0 :
            return None
        if self.__longargs >= 0:
            # we handled this over
            assert(self.__curcharidx < 0)
            self.__curidx += self.__longargs
            assert(len(self.__args) >= self.__curidx)
            self.__longargs = -1
            self.__validx = -1
            self.__keyidx = -1
        oldcharidx = self.__curcharidx
        oldidx = self.__curidx
        if oldidx >= len(self.__args):
            self.__curidx = oldidx
            self.__curcharidx = -1
            self.__shortcharargs = -1
            self.__longargs = -1
            self.__keyidx = -1
            self.__validx = -1
            self.__ended = 1
            return None
        if oldcharidx >= 0:
            c = self.__args[oldidx]
            if len(c) <= oldcharidx:
                # this is the end of shortopt like -vhc pass c option
                oldidx += 1
                self.info('oldidx [%s]'%(oldidx))
                if self.__shortcharargs > 0:
                    oldidx += self.__shortcharargs
                self.info('oldidx [%s] __shortcharargs [%d]'%(oldidx,self.__shortcharargs))
                self.__curidx= oldidx
                self.__curcharidx = -1
                self.__shortcharargs = -1
                self.__keyidx = -1
                self.__validx = -1
                self.__longargs = -1
                return self.__find_key_cls()
            # ok we should get the value
            curch = c[oldcharidx]
            self.info('argv[%d][%d] %c'%(oldidx,oldcharidx,curch))
            # we look for the end of the pass
            idx = len(self.__cmdpaths) - 1
            while idx >= 0:
                cmd = self.__cmdpaths[idx]
                #self.info('[%d]%s'%(idx,cmd))
                for opt in cmd.cmdopts:
                    if not opt.isflag:
                        continue
                    if opt.flagname == '$':
                        continue
                    if opt.shortflag is not None:
                        #self.info('opt %s %c %c'%(opt,opt.shortflag,curch))
                        if opt.shortflag == curch:
                            self.__keyidx = oldidx
                            self.__validx = (oldidx + 1)
                            self.__curidx = oldidx
                            self.__curcharidx = (oldcharidx + 1)
                            logging.info('%s validx [%s]'%(opt,self.__validx))
                            return opt
                idx -= 1
            # now it is nothig to find so we assume that this is the command name
            raise Exception('can not parse (%s)'%(self.__args[oldidx]))
        else:
            if self.__bundlemode:            
                curarg = self.__args[oldidx]
                if curarg.startswith(self.__longprefix):
                    if curarg == self.__longprefix:
                        self.__keyidx = -1
                        self.__curidx = oldidx + 1
                        self.__curcharidx = -1
                        self.__validx = (oldidx + 1)
                        self.__shortcharargs = -1
                        self.__longargs = -1
                        self.__ended = 1
                        if len(self.__args) > self.__curidx:
                            self.__leftargs.extend(self.__args[self.__curidx:])
                        return None
                    #self.info('argv[%d] %s oldcharidx %d'%(oldidx,self.__args[oldidx],oldcharidx))
                    idx = len(self.__cmdpaths) -1
                    while idx >= 0:
                        cmd = self.__cmdpaths[idx]
                        for opt in cmd.cmdopts:
                            if not opt.isflag:
                                continue
                            if opt.flagname == '$':
                                continue
                            self.info('[%d]longopt %s curarg %s'%(idx,opt.longopt,curarg))
                            if opt.longopt == curarg:
                                self.__keyidx = oldidx
                                oldidx += 1
                                self.__validx = oldidx
                                self.__shortcharargs = -1
                                self.__longargs = -1
                                self.info('oldidx %d (len %d)'%(oldidx,len(self.__args)))
                                self.__curidx = oldidx
                                self.__curcharidx = -1
                                return opt
                        idx -= 1
                    raise Exception('can not parse (%s)'%(self.__args[oldidx]))
                elif curarg.startswith(self.__shortprefix):
                    if curarg == self.__shortprefix:
                        if self.__parseall:
                            self.__leftargs.append(curarg)
                            oldidx += 1
                            self.__curidx = oldidx
                            self.__curcharidx = -1
                            self.__longargs = -1
                            self.__shortcharargs = -1
                            self.__keyidx = -1
                            self.__validx = -1
                            return self.__find_key_cls()
                        else:
                            self.__ended = 1
                            self.__leftargs.extend(self.__args[oldidx:])
                            self.__validx = oldidx
                            self.__keyidx = -1
                            self.__curidx = oldidx
                            self.__curcharidx = -1
                            self.__shortcharargs = -1
                            self.__longargs = -1
                            return None
                    # not to 
                    oldcharidx = len(self.__shortprefix)
                    self.__curidx = oldidx
                    self.__curcharidx = oldcharidx
                    # to find the next one
                    return self.__find_key_cls()
            else:
                # not bundle mode ,it means that the long prefix and short prefix are the same
                # so we should test one by one
                # first to check for the long opt
                idx = len(self.__cmdpaths) -1
                curarg = self.__args[oldidx]
                while idx >= 0:
                    cmd = self.__cmdpaths[idx]
                    for opt in cmd.cmdopts:
                        if not opt.isflag:
                            continue
                        if opt.flagname == '$':
                            continue
                        self.info('[%d](%s) curarg [%s]'%(idx,opt.longopt,curarg))
                        if opt.longopt == curarg:
                            self.__keyidx = oldidx
                            self.__validx = (oldidx + 1)
                            self.__shortcharargs = -1
                            self.__longargs = -1
                            self.info('oldidx %d (len %d)'%(oldidx,len(self.__args)))
                            self.__curidx = (oldidx + 1)
                            self.__curcharidx = -1
                            return opt
                    idx -= 1
                idx = len(self.__cmdpaths) - 1
                while idx >= 0:
                    cmd = self.__cmdpaths[idx]
                    for opt in cmd.cmdopts:
                        if not opt.isflag:
                            continue
                        if opt.flagname == '$':
                            continue
                        self.info('[%d](%s) curarg [%s]'%(idx,opt.shortopt,curarg))
                        if opt.shortopt is not None and opt.shortopt == curarg:
                            self.__keyidx = oldidx
                            self.__validx = (oldidx +1)
                            self.__shortcharargs = -1
                            self.__longargs = -1
                            self.info('oldidx %d (len %d)'%(oldidx,len(self.__args)))
                            self.__curidx = oldidx
                            self.__curcharidx = len(opt.shortopt)
                            self.info('[%s]shortopt (%s)'%(oldidx,opt.shortopt))
                            return opt
                    idx -= 1

        # come here because we may be the command
        keycls = self.__find_sub_command(self.__args[oldidx])
        if keycls is not None:
            # ok we should set next search
            self.info('find %s'%(self.__args[oldidx]))
            self.__keyidx = oldidx
            self.__curidx = (oldidx + 1)
            self.__validx = (oldidx + 1)
            self.__curcharidx = -1
            self.__shortcharargs = -1
            self.__longargs = -1
            return keycls
        if self.__parseall:
            # we put it into the 
            self.__leftargs.append(self.__args[oldidx])
            oldidx += 1
            self.__keyidx = -1
            self.__validx = oldidx
            self.__curidx = oldidx
            self.__curcharidx = -1
            self.__shortcharargs = -1
            self.__longargs = -1
            return self.__find_key_cls()
        else:
            # this is over
            self.__ended = 1
            self.__leftargs.extend(self.__args[oldidx:])
            self.__keyidx = -1
            self.__curidx = oldidx
            self.__curcharidx = -1
            self.__shortcharargs = -1
            self.__longargs = -1
            return None


    def step_one(self):
        key = None
        value = None
        keycls = None
        if self.__ended > 0 :
            self.info('args %s __curidx %d'%(self.__args,self.__curidx))
            value = self.__leftargs
            return self.__curidx,self.__leftargs,None
        keycls = self.__find_key_cls()
        if keycls is None:
            assert(self.__ended > 0)
            return self.__curidx,self.__leftargs,None
        key = self.__args[self.__keyidx]
        if not keycls.iscmd:
            optval = keycls.optdest
        elif keycls.iscmd:
            optval = self.format_cmdname_path(self.__cmdpaths)
        return self.__validx,optval,keycls

    def get_cmd_paths(self):
        return self.__cmdpaths


class NameSpaceEx(object):
    def __init__(self):
        self.__obj = dict()
        self.__access = dict()
        self.__logger = _LoggerObject()
        return

    def __setattr__(self,key,val):
        if not key.startswith('_'):
            self.__logger.info('%s=%s'%(key,val),2)
            self.__obj[key] = val
            self.__access[key] = True
            return
        self.__dict__[key] = val
        return

    def __getattr__(self,key):
        if not key.startswith('_'):
            if key in self.__obj.keys():
                return self.__obj[key]
            return None
        return self.__dict__[key]

    def __str__(self):
        s = '{'
        for k in self.__obj.keys():
            s += '%s=%s;'%(k,self.__obj[k])
        s += '}'
        return s

    def __repr__(self):
        return self.__str__()

    def __has_accessed(self,name):
        if name in self.__access.keys():
            return True
        return False

    def is_accessed(self,name):
        return self.__has_accessed(name)

    def get_keys(self):
        return self.__obj.keys()

def set_attr_args(self,args,prefix):
    if not issubclass(args.__class__,NameSpaceEx):
        raise Exception('args not NameSpaceEx')
    for p in args.get_keys():
        if len(prefix) == 0 or p.startswith('%s_'%(prefix)):
            setattr(self,p,getattr(args,p))
    return

class _OptCheck(object):
    def __reset(self):
        self.__longopt = []
        self.__shortopt = []
        self.__varname = []
        return
    def __init__(self):
        self.__reset()
        return

    def copy(self,other):
        if not issubclass(other.__class__,_OptCheck):
            raise Exception('other not _OptCheck function')
        self.__reset()
        self.__longopt.extend(other.__longopt)
        self.__shortopt.extend(other.__shortopt)
        self.__varname.extend(other.__varname)
        return

    def add_and_check(self,typename,value):
        if typename == 'longopt':
            if value in self.__longopt:
                return False
            self.__longopt.append(value)
            return True
        elif typename == 'shortopt':
            if value in self.__shortopt:
                return False
            self.__shortopt.append(value)
            return True
        elif typename == 'varname':
            if value in self.__varname:
                return False
            self.__varname.append(value)
            return True
        return False



class ExtArgsParse(_LoggerObject):
    reserved_args = ['subcommand','subnargs','nargs','extargs','args']
    priority_args = [SUB_COMMAND_JSON_SET,COMMAND_JSON_SET,ENVIRONMENT_SET,ENV_SUB_COMMAND_JSON_SET,ENV_COMMAND_JSON_SET]

    def __format_cmd_from_cmd_array(self,cmdarray):
        if cmdarray is None:
            return ''
        cmdname = ''
        for c in cmdarray:
            if len(cmdname) > 0:
                cmdname += '.'
            cmdname += '%s'%(c.cmdname)
        return cmdname

    def __need_args_error(args,validx,keycls,params):
        keyval = ''
        if validx > 0:
            keyval = params[validx-1]
        if keyval == keycls.longopt:
            keyval = keycls.longopt
        elif keycls.shortflag is not None and shortflag in keyval:
            keyval = keycls.shortopt
        self.error_msg('[%s] need args'%(keyval))        
        return

    def __bool_action(self,args,validx,keycls,params):
        if keycls.value :
            setattr(args,keycls.optdest,False)
        else:
            setattr(args,keycls.optdest,True)
        return 0

    def __append_action(self,args,validx,keycls,params):
        if validx >= len(params):
            self.__need_args_error(validx,keycls,params)
        value = params[validx]
        sarr = getattr(args,keycls.optdest,None)
        if sarr is None:
            sarr = []
        sarr.append(value)
        setattr(args,keycls.optdest,sarr)
        return 1

    def __string_action(self,args,validx,keycls,params):
        if validx >= len(params):
            self.__need_args_error(validx,keycls,params)
        setattr(args,keycls.optdest,params[validx])
        return 1


    def __jsonfile_action(self,args,validx,keycls,params):
        return self.__string_action(args,validx,keycls,params)

    def __int_action(self,args,validx,keycls,params):
        if validx >= len(params):
            self.__need_args_error(validx,keycls,params)
        try:
            base = 10
            value = params[validx]
            self.info('set value [%d][%s]'%(validx,value))
            if value.startswith('0x') or value.startswith('0X'):
                value = value[2:]
                base = 16
            elif value.startswith('x') or value.startswith('X'):
                base = value[1:]
                base = 16
            num = int(value,base)
            setattr(args,keycls.optdest,num)
        except:
            msg = '%s not valid int'%(value)
            self.error_msg(msg)            
        return 1

    def __inc_action(self,args,validx,keycls,params):
        val = getattr(args,keycls.optdest,None)
        if val is None:
            val = 0
        val += 1
        setattr(args,keycls.optdest,val)
        return 0

    def __float_action(self,args,validx,keycls,params):
        if validx >= len(params):
            self.__need_args_error(validx,keycls,params)
        try:
            value = params[validx]
            num = float(value)
            setattr(args,keycls.optdest,num)
        except:
            msg = 'can not parse %s'%(value)
            self.error_msg(msg)
        return 1

    def __help_action(self,args,validx,keycls,value):
        self.print_help(sys.stdout,value)
        sys.exit(0)
        return 0

    def __command_action(self,args,validx,keycls,params):
        return 0


    def __json_value_base(self,args,keycls,value):
        setattr(args,keycls.optdest,value)
        return

    def __json_value_error(self,args,keycls,value):
        raise Exception('error set json value')
        return

    def __get_full_trace_back(self,trback,tabs=1,cnt=0):
        s = ''
        frm = getattr(trback,'tb_frame',None)
        if frm is not None:
            code = getattr(frm,'f_code',None)
            if code is not None:
                s += ' ' * tabs * 4
                s += '[%d][%s:%s:%s]\n'%(cnt,code.co_filename,code.co_name,frm.f_lineno)
                ntrace = getattr(trback,'tb_next',None)
                if ntrace is not None:
                    s += self.__get_full_trace_back(ntrace,tabs,cnt+1)
        return s


    def error_msg(self,message):
        output = False
        if len(self.__output_mode) > 0:
            if self.__output_mode[-1] == 'bash':
                s = ''
                s += 'cat >&2 <<EXTARGSEOF\n'
                s += 'parse command error\n    %s\n'%(message)
                s += 'EXTARGSEOF\n'
                s += 'exit 3\n'
                sys.stdout.write('%s'%(s))
                output = True
                sys.exit(3)
        if not output :
            s = 'parse command error\n'
            s += '    %s'%(self.format_call_msg(message,2))

        if self.__error_handler== 'exit':
            sys.stderr.write('%s'%(s))
            sys.exit(3)
        else:
            raise Exception(s)
        return

    def __check_flag_insert(self,keycls,curparser=None):
        if curparser :
            lastparser = curparser[-1]
        else:
            lastparser = self.__maincmd
        for k in lastparser.cmdopts:
            if k.flagname != '$' and keycls.flagname != '$':
                if k.type != 'help' and keycls.type != 'help':
                    if k.optdest == keycls.optdest:
                        return False
                elif k.type == 'help' and keycls.type == 'help':
                    return False
            elif k.flagname == '$' and keycls.flagname == '$':
                return False
        #self.info('append [%s] %s'%(self.__format_cmd_from_cmd_array(curparser),keycls))
        lastparser.cmdopts.append(keycls)
        return True

    def __check_flag_insert_mustsucc(self,keycls,curparser=None):
        valid = self.__check_flag_insert(keycls,curparser)
        if not valid:
            cmdname = ''
            if curparser:
                i = 0
                for c in curparser:
                    if i > 0:
                        cmdname += '.'
                    cmdname += c.cmdname
                    i += 1
            msg = '(%s) already in command(%s)'%(keycls.flagname,cmdname)
            self.error_msg(msg)
        return

    def __load_command_line_base(self,prefix,keycls,curparser=None):
        if keycls.isflag and keycls.flagname != '$' and keycls.flagname in self.__class__.reserved_args:
            self.error_msg('(%s) in reserved_args (%s)'%(keycls.flagname,self.__class__.reserved_args))
        self.__check_flag_insert_mustsucc(keycls,curparser)
        return True

    def __load_command_line_args(self,prefix,keycls,curparser=None):
        return self.__check_flag_insert(keycls,curparser)

    def __load_command_line_help(self,keycls,curparser=None):
        return self.__check_flag_insert(keycls,curparser)

    def __load_command_line_jsonfile(self,keycls,curparser=None):
        return self.__check_flag_insert(keycls,curparser)

    def __load_command_line_json_added(self,curparser=None):
        prefix = ''        
        key = '%s##json input file to get the value set##'%(self.__jsonlong)
        value = None
        prefix = self.__format_cmd_from_cmd_array(curparser)
        prefix = prefix.replace('.','_')
        keycls = keyparse.ExtKeyParse(prefix,key,value,True,False,True,self.__longprefix,self.__shortprefix)
        return self.__load_command_line_jsonfile(keycls,curparser)

    def __load_command_line_help_added(self,curparser=None):
        key = '%s'%(self.__helplong)
        if self.__helpshort:
            key += '|%s'%(self.__helpshort)
        key += '##to display this help information##'
        value = None
        keycls = keyparse.ExtKeyParse('',key,value,True,True,False,self.__longprefix,self.__shortprefix)
        #self.info('[%s] add help'%(self.__format_cmd_from_cmd_array(curparser)))
        return self.__load_command_line_help(keycls,curparser)


    def __init__(self,options=None,priority=None):
        super(ExtArgsParse,self).__init__()
        self.info('options (%s)'%(options))
        if priority is None:
            priority = [SUB_COMMAND_JSON_SET,COMMAND_JSON_SET,ENVIRONMENT_SET,ENV_SUB_COMMAND_JSON_SET,ENV_COMMAND_JSON_SET]
        if options is None:
            self.info('options None set default')
            options = ExtArgsOptions()
        self.__options = options
        self.__maincmd = _ParserCompact(None,options)

        self.__help_handler = options.helphandler
        self.__output_mode = []
        self.__ended = 0
        self.__longprefix = options.longprefix
        self.__shortprefix = options.shortprefix
        self.__nohelpoption = options.nohelpoption
        self.__nojsonoption = options.nojsonoption
        self.__helplong = options.helplong
        self.__helpshort = options.helpshort
        self.__jsonlong = options.jsonlong
        self.__cmdprefixadded = options.cmdprefixadded
        self.__error_handler = options.errorhandler

        self.__load_command_map = {
            'string' : self.__load_command_line_base,
            'unicode' : self.__load_command_line_base,
            'int' : self.__load_command_line_base,
            'long' : self.__load_command_line_base,
            'float' : self.__load_command_line_base,
            'list' : self.__load_command_line_base,
            'bool' : self.__load_command_line_base,
            'args' : self.__load_command_line_args,
            'command' : self.__load_command_subparser,
            'prefix' : self.__load_command_prefix,
            'count': self.__load_command_line_base,
            'help' : self.__load_command_line_base ,
            'jsonfile' : self.__load_command_line_base
        }
        self.__opt_parse_handle_map = {
            'string' : self.__string_action,
            'unicode' : self.__string_action,
            'bool' : self.__bool_action,
            'int' : self.__int_action,
            'long' : self.__int_action,
            'list' : self.__append_action,
            'count' : self.__inc_action,
            'help' : self.__help_action,
            'jsonfile' : self.__string_action,
            'command' : self.__command_action ,
            'float' : self.__float_action
        }
        for p in priority:
            if p not in self.__class__.priority_args:
                msg = '(%s) not in priority values'%(p)
                self.error_msg(msg)
        self.__load_priority = priority
        self.__parse_set_map = {
            SUB_COMMAND_JSON_SET : self.__parse_sub_command_json_set,
            COMMAND_JSON_SET : self.__parse_command_json_set,
            ENVIRONMENT_SET : self.__parse_environment_set,
            ENV_SUB_COMMAND_JSON_SET : self.__parse_env_subcommand_json_set,
            ENV_COMMAND_JSON_SET : self.__parse_env_command_json_set
        }
        self.__set_json_value = {
            'string' : self.__json_value_base,
            'unicode' : self.__json_value_base,
            'bool' : self.__json_value_base,
            'int' : self.__json_value_base,
            'long' : self.__json_value_base,
            'list' : self.__json_value_base,
            'count' : self.__json_value_base,
            'jsonfile' : self.__json_value_base,
            'float' : self.__json_value_base,
            'command' : self.__json_value_error,
            'help' : self.__json_value_error
        }
        return

    def __call_json_value(self,args,keycls,value):
        if keycls.attr is not None and keycls.attr.jsonfunc is not None:
            self.call_func(keycls.attr.jsonfunc,args,keycls,value)
            return
        self.__set_json_value[keycls.type](args,keycls,value)
        return

    def __format_cmdname_path(self,curparser=None):
        cmdname = ''
        if curparser is not None:
            for c in curparser:
                if len(cmdname) > 0:
                    cmdname += '.'
                cmdname += c.cmdname
        return cmdname

    def __find_commands_in_path(self,cmdname,curparser=None):
        sarr = ['']
        if cmdname is not None:
            sarr = re.split('\.',cmdname)
        commands = []
        i = 0
        if self.__maincmd is not None:
            commands.append(self.__maincmd)
        while i <= len(sarr) and cmdname is not None and len(cmdname) > 0:
            if i == 0:
                pass
            else:
                curcommand = self.__find_command_inner(sarr[i-1],commands)
                if curcommand is None:
                    break
                commands.append(curcommand)
            i += 1
        return commands


    def __find_command_inner(self,name,curparser=None):
        sarr = re.split('\.',name)
        curroot = self.__maincmd
        nextparsers = []
        if curparser is not None:
            nextparsers = curparser
            curroot = curparser[-1]
        if len(sarr) > 1:
            nextparsers.append(curroot)
            for c in curroot.subcommands:
                if c.cmdname == sarr[0]:
                    nextparsers = []
                    if curparser is not None:
                        nextparsers = curparser
                    nextparsers.append(c)
                    return self.__find_command_inner('.'.join(sarr[1:]),nextparsers)
        else:
            for c in curroot.subcommands:
                if c.cmdname == sarr[0]:
                    return c
        return None


    def __find_subparser_inner(self,cmdname,parentcmd=None):
        if cmdname is None or len(cmdname) == 0:
            return parentcmd
        if parentcmd is None:
            parentcmd = self.__maincmd
        sarr = re.split('\.',cmdname)
        for c in parentcmd.subcommands:
            if c.cmdname == sarr[0]:
                findcmd = self.__find_subparser_inner('.'.join(sarr[1:]),c)
                if findcmd is not None:
                    return findcmd
        return None


    def __get_subparser_inner(self,keycls,curparser=None):
        cmdname = ''
        parentname = self.__format_cmdname_path(curparser)
        cmdname += parentname
        if len(cmdname) > 0:
            cmdname += '.'
        cmdname += keycls.cmdname
        cmdparser = self.__find_subparser_inner(cmdname)
        if cmdparser is not None:
            return cmdparser        
        cmdparser = _ParserCompact(keycls,self.__options)

        if len(parentname) == 0:
            #self.info('append to main')
            self.__maincmd.subcommands.append(cmdparser)
        else:
            #self.info('append to %s'%(curparser[-1].cmdname))
            curparser[-1].subcommands.append(cmdparser)
        return cmdparser


    def __load_command_subparser(self,prefix,keycls,lastparser=None):
        if not isinstance( keycls.value,dict):
            msg = '(%s) value must be dict'%(keycls.origkey)
            self.error_msg(msg)
        if keycls.iscmd and keycls.cmdname in self.__class__.reserved_args:
            msg = 'command(%s) in reserved_args (%s)'%(keycls.cmdname,self.__class__.reserved_args)
            self.error_msg(msg)
        parser = self.__get_subparser_inner(keycls,lastparser)
        nextparser = [self.__maincmd]
        if lastparser is not None:
            nextparser = lastparser
        nextparser.append(parser)
        self.info('nextparser %s'%(self.format_string(nextparser)))
        self.info('keycls %s'%(keycls))
        # this would add prefix
        if self.__cmdprefixadded:
            newprefix = prefix
            if len(newprefix) > 0:
                newprefix += '_'
            newprefix += keycls.cmdname
        else:
            # it will just not add the prefix
            newprefix = ''
        self.__load_command_line_inner(newprefix,keycls.value,nextparser)
        nextparser.pop()
        return True

    def __load_command_prefix(self,prefix,keycls,curparser=None):
        if keycls.prefix in self.__class__.reserved_args:
            msg = 'prefix (%s) in reserved_args (%s)'%(keycls.prefix,self.__class__.reserved_args)
            self.error_msg(msg)
        self.__load_command_line_inner(keycls.prefix,keycls.value,curparser)
        return True

    def __load_command_line_inner(self,prefix,d,curparser=None):
        if not self.__nojsonoption:
            self.__load_command_line_json_added(curparser)
        # to add parser
        if not self.__nohelpoption:
            self.__load_command_line_help_added(curparser)
        parentpath = [self.__maincmd]
        if curparser is not None:
            parentpath = curparser
        for k in d.keys():
            v = d[k]
            self.info('%s , %s , %s , True'%(prefix,k,v))
            keycls = keyparse.ExtKeyParse(prefix,k,v,False,False,False,self.__longprefix,self.__shortprefix,self.__options.flagnochange)
            valid = self.__load_command_map[keycls.type](prefix,keycls,parentpath)
            if not valid:
                msg = 'can not add (%s,%s)'%(k,v)
                self.error_msg(msg)
        self.info('%s'%(self.format_string(parentpath)))
        return

    def load_command_line(self,d):
        if self.__ended != 0:
            raise Exception('you have call parse_command_line before call load_command_line_string or load_command_line')
        if not isinstance(d,dict):
            raise Exception('input parameter(%s) not dict'%(d))
        self.__load_command_line_inner('',d,None)
        return

    def __get_except_info(self):
        trback = sys.exc_info()[2]
        exceptname = sys.exc_info()[1]
        rets = ''
        rets += 'exception %s:\n'%(exceptname)
        rets +='trace back:\n'
        rets += self.__get_full_trace_back(trback,1,0)
        return rets

    def load_command_line_string(self,s):
        try:
            d = json.loads(s)
        except:
            msg = '(%s) not valid json string\n%s'%(s,self.__get_except_info())
            self.error_msg(msg)
        #self.info('d (%s)'%(d))
        self.load_command_line(d)
        return

    def __print_help(self,cmdparser=None):
        if self.__help_handler is not None and self.__help_handler == 'nohelp':
            return 'no help information'
        curcmd = self.__maincmd
        cmdpaths = []
        if cmdparser is not  None:
            self.info('cmdparser %s'%(self.format_string(cmdparser)))
            curcmd = cmdparser[-1]
            i = 0
            while i < len(cmdparser) - 1:
                cmdpaths.append(cmdparser[i])
                i += 1
        return curcmd.get_help_info(None,cmdpaths)

    def print_help(self,fp=sys.stderr,cmdname=''):
        self.__set_command_line_self_args()
        paths = self.__find_commands_in_path(cmdname)
        if paths is  None:
            self.error_msg('can not find [%s] cmd'%(cmdname))
        s = self.__print_help(paths)
        if len(self.__output_mode) > 0 :
            if self.__output_mode[-1] == 'bash':
                outs = 'cat <<EOFMM\n%s\nEOFMM\nexit 0'%(s)
                sys.stdout.write(outs)
                sys.exit(0)
        fp.write(s)
        #sys.exit(0)
        return

    def __get_args_accessed(self,args,optdest):
        funcname = '_%s__has_accessed'%('NameSpaceEx')
        funcptr = getattr(args,funcname,None)
        if funcptr is None :
            raise Exception('%s not found ,internal error'%(funcname))
        return funcptr(optdest)

    def __set_jsonvalue_not_defined(self,args,cmd,key,value):
        for chld in cmd.subcommands:
            args = self.__set_jsonvalue_not_defined(args,chld,key,value)
        for opt in cmd.cmdopts:
            if opt.isflag and opt.type != 'prefix' and opt.type != 'args' and opt.type != 'help':
                if opt.optdest == key:
                    if not self.__get_args_accessed(args,opt.optdest):
                        if str(keyparse.TypeClass(value)) != str(keyparse.TypeClass(opt.value)):
                            self.warn('%s  type (%s) as default value type (%s)'%(key,str(keyparse.TypeClass(value)),str(keyparse.TypeClass(opt.value))))
                        else:
                            # here we do not set the args directly ,because we should make sure this will give
                            # call back options ,so we do this by the calling
                            self.__call_json_value(args,opt,value)
                            #setattr(args,key,value)
                    return args
        return args


    def __load_jsonvalue(self,args,prefix,jsonvalue):
        for k in jsonvalue:
            if isinstance(jsonvalue[k],dict):
                newprefix = ''
                if len(prefix) > 0:
                    newprefix += '%s_'%(prefix)
                newprefix += k
                args = self.__load_jsonvalue(args,newprefix,jsonvalue[k])
            else:
                newkey = ''
                if (len(prefix) > 0):
                    newkey += '%s_'%(prefix)
                newkey += k
                args = self.__set_jsonvalue_not_defined(args,self.__maincmd,newkey,jsonvalue[k])
        return args


    def __load_jsonfile(self,args,cmdname,jsonfile):
        assert( not self.__nojsonoption)
        assert(jsonfile is not None)
        prefix = ''
        if cmdname is not None :
            prefix += cmdname
        # replace prefix ok
        prefix = prefix.replace('.','_')
        fp = None
        try:
            fp = open(jsonfile,'r+')
        except:
            msg = 'can not open(%s)\n%s'%(jsonfile,self.__get_except_info())
            self.error_msg(msg)
        try:
            jsonvalue = json.load(fp)
            fp.close()
            fp = None
        except:
            if fp is not None:
                fp.close()
            fp = None
            msg = 'can not parse (%s)\n%s'%(jsonfile,self.__get_except_info())
            self.error_msg(msg)
        jsonvalue = keyparse.Utf8Encode(jsonvalue).get_val()
        self.info('load (%s) prefix(%s) value (%s)'%(jsonfile,prefix,repr(jsonvalue)))
        return self.__load_jsonvalue(args,prefix,jsonvalue)



    def __set_parser_default_value(self,args,cmd):
        for chld in cmd.subcommands:
            args = self.__set_parser_default_value(args,chld)
        for opt in cmd.cmdopts:
            if opt.isflag and opt.type != 'prefix' and opt.type != 'args' and opt.type != 'help':
                args = self.__set_jsonvalue_not_defined(args,cmd,opt.optdest,opt.value)
        return args

    def __set_default_value(self,args):
        args = self.__set_parser_default_value(args,self.__maincmd)
        return args

    def __set_environ_value_inner(self,args,prefix,cmd):
        for chld in cmd.subcommands:
            args = self.__set_environ_value_inner(args,prefix,chld)

        for keycls in cmd.cmdopts:
            if keycls.isflag and keycls.type != 'prefix' and keycls.type != 'args' and keycls.type != 'help':
                optdest = keycls.optdest
                oldopt = optdest
                if args.is_accessed(oldopt):
                    # have set ,so we do not set it
                    continue
                optdest = optdest.upper()
                optdest = optdest.replace('-','_')
                if '_' not in optdest:
                    optdest = 'EXTARGS_%s'%(optdest)
                val = os.getenv(optdest,None)               
                if val is not None:
                    # to check the type
                    val = keyparse.Utf8Encode(val).get_val()
                    if keycls.type == 'string' or keycls.type == 'jsonfile':
                        value = val
                        self.__call_json_value(args,keycls,value)
                    elif keycls.type == 'bool':                     
                        value = False
                        if val.lower() == 'true':
                            value = True
                        elif val.lower() == 'false':
                            value = False
                        self.__call_json_value(args,keycls,value)
                    elif keycls.type == 'list':
                        try:
                            lval = eval(val)
                            lval = keyparse.Utf8Encode(lval).get_val()
                            if not isinstance(lval,list):
                                raise Exception('(%s) environ(%s) not valid'%(optdest,val))
                            value = lval
                            self.__call_json_value(args,keycls,value)
                        except:
                            self.warn('can not set (%s) for %s = %s\n%s'%(optdest,oldopt,val,self.__get_except_info()))
                    elif keycls.type == 'int' or keycls.type == 'count' or keycls.type == 'long':
                        try:
                            val = val.lower()
                            base = 10
                            if val.startswith('0x') :
                                val = val[2:]
                                base = 16
                            elif val.startswith('x'):
                                val = val[1:]
                                base = 16
                            lval = int(val,base)
                            value = lval
                            self.__call_json_value(args,keycls,value)
                        except:
                            self.warn('can not set (%s) for %s = %s\n%s'%(optdest,oldopt,val,self.__get_except_info()))
                    elif keycls.type == 'float':
                        try:
                            lval = float(val)
                            value = lval
                            self.__call_json_value(args,keycls,value)
                        except:
                            self.warn('can not set (%s) for %s = %s\n%s'%(optdest,oldopt,val,self.__get_except_info()))
                    else:
                        msg = 'internal error when (%s) type(%s)'%(keycls.optdest,keycls.type)
                        self.error_msg(msg)
        return args



    def __set_environ_value(self,args):
        args = self.__set_environ_value_inner(args,'',self.__maincmd)
        return args

    def __check_varname_inner(self,paths=None,optcheck=None):
        if optcheck is None:
            optcheck = _OptCheck()
        parentpaths = [self.__maincmd]
        if paths is not None:
            parentpaths = paths

        for opt in parentpaths[-1].cmdopts:
            if opt.isflag:
                if opt.type == 'help' or opt.type == 'args':
                    continue
                bval = optcheck.add_and_check('varname',opt.varname)
                if not bval:
                    msg = '%s is already in the check list'%(opt.varname)
                    self.error_msg(msg)
                bval = optcheck.add_and_check('longopt',opt.longopt)
                if not bval:
                    msg = '%s is already in the check list'%(opt.longopt)
                    self.error_msg(msg)
                if opt.shortopt is not None:
                    bval = optcheck.add_and_check('shortopt',opt.shortopt)
                    if not bval:
                        msg = '%s is already in the check list'%(opt.longopt)
                        self.error_msg(msg)

        for chld in parentpaths[-1].subcommands:
            curpaths = parentpaths
            curpaths.append(chld)
            copyoptcheck = _OptCheck()
            copyoptcheck.copy(optcheck)
            self.__check_varname_inner(curpaths,copyoptcheck)
            curpaths.pop()

        return

    def __set_command_line_self_args_inner(self,paths=None):
        parentpaths = [self.__maincmd]
        if paths is not None:
            parentpaths = paths

        setted = False
        for opt in parentpaths[-1].cmdopts:
            if opt.isflag and opt.flagname == '$':
                setted = True
                break
        if not setted:
            #self.info('set [%s] $'%(self.__format_cmd_from_cmd_array(parentpaths)))
            cmdname = self.__format_cmd_from_cmd_array(parentpaths)
            if cmdname is None:
                self.error_msg('can not get cmd (%s) whole name'%(curcmd))
            # replace with prefix
            prefix = cmdname.replace('.','_')
            curkey = keyparse.ExtKeyParse('','$','*',True)
            self.__load_command_line_args('',curkey,parentpaths)


        for chld in parentpaths[-1].subcommands:
            curpaths = parentpaths
            curpaths.append(chld)
            self.__set_command_line_self_args_inner(curpaths)
            curpaths.pop()
        return


    def __set_command_line_self_args(self,paths=None):
        if self.__ended != 0:
            return
        self.__set_command_line_self_args_inner(paths)
        self.__check_varname_inner()
        self.__ended = 1
        return

    def __parse_sub_command_json_set(self,args):
        # now we should get the 
        # first to test all the json file for special command
        subcmdname = getattr(args,'subcommand',None)
        # we do not get the json ok
        if subcmdname is not None and not self.__nojsonoption:
            cmds = self.__find_commands_in_path(subcmdname)
            idx = len(cmds)
            while idx >= 2:
                subname = self.__format_cmd_from_cmd_array(cmds[:idx])
                prefix = subname.replace('.','_')
                jsondest = '%s_%s'%(prefix,self.__jsonlong)
                jsonfile = getattr(args,jsondest,None)
                if jsonfile is not None:
                    # ok we should make this parse
                    args = self.__load_jsonfile(args,subname,jsonfile)
                idx -= 1
        return args

    def __parse_command_json_set(self,args):
        # to get the total command
        jsonfile = getattr(args,'%s'%(self.__jsonlong),None)
        if jsonfile is not None and not self.__nojsonoption:
            args = self.__load_jsonfile(args,'',jsonfile)
        return args

    def __parse_environment_set(self,args):
        # now get the environment value
        args = self.__set_environ_value(args)
        return args

    def __parse_env_subcommand_json_set(self,args):
        # now to check for the environment as the put file
        subcmdname = getattr(args,'subcommand',None)
        if subcmdname is not None and not self.__nojsonoption:
            cmds = self.__find_commands_in_path(subcmdname)
            idx = len(cmds)
            while idx >= 2:
                subname = self.__format_cmd_from_cmd_array(cmds[:idx])
                prefix = subname.replace('.','_')
                jsondest = '%s_%s'%(prefix,self.__jsonlong)
                jsondest = jsondest.replace('-','_')
                jsondest = jsondest.upper()
                jsonfile = os.getenv(jsondest,None)
                if jsonfile is not None:
                    # ok we should make this parse
                    args = self.__load_jsonfile(args,subname,jsonfile)
                idx -= 1
        return args

    def __parse_env_command_json_set(self,args):
        # to get the json existed 
        jsonenv = 'EXTARGSPARSE_%s'%(self.__jsonlong)
        jsonenv = jsonenv.upper()
        jsonenv = jsonenv.replace('-','_')
        jsonenv = jsonenv.replace('.','_')
        jsonfile = os.getenv(jsonenv,None)
        if jsonfile is not None and not self.__nojsonoption:
            args = self.__load_jsonfile(args,'',jsonfile)
        return args


    def __format_cmdname_msg(self,cmdname,msg):
        retmsg = cmdname
        if len(retmsg) > 0:
            retmsg += ' command '
        retmsg += msg
        return retmsg

    def __set_args(self,args,cmdpaths,vals):
        argskeycls = None
        cmdname = self.__format_cmdname_path(cmdpaths)
        self.info('[%s] %s'%(cmdname,self.format_string(cmdpaths[-1].cmdopts)))
        for c in cmdpaths[-1].cmdopts:
            if c.flagname == '$':
                argskeycls = c
                break
        if argskeycls is None:
            self.error_msg('can not find args in (%s)'%(cmdname))
        if vals is not None and not isinstance(vals,list):
            msg = self.__format_cmdname_msg(cmdname,'invalid type args (%s) %s'%(type(vals),vals))
            self.error_msg(msg)
        if argskeycls.nargs == '*' or argskeycls.nargs == '+' or argskeycls.nargs == '?':
            if argskeycls.nargs == '?':
                if vals is not None and len(vals) > 1:
                    msg = self.__format_cmdname_msg(cmdname,'args \'?\' must <= 1')
                    self.error_msg(msg)
            elif argskeycls.nargs == '+':
                if (vals is None or len(vals) == 0):
                    msg = self.__format_cmdname_msg(cmdname,'args must at least 1')
                    self.error_msg(msg)
        else:
            nargs = argskeycls.nargs
            if vals is None:
                if nargs != 0:
                    msg = self.__format_cmdname_msg(cmdname,'args must 0 but(%s)'%(vals))
                    self.error_msg(msg)
            else:
                if len(vals) != nargs:
                    msg = self.__format_cmdname_msg(cmdname,'vals(%s) %d != nargs %d'%(vals,len(vals),nargs))
                    self.error_msg(msg)
        keyname = 'args'
        if len(cmdpaths) > 1:
            keyname = 'subnargs'        
        if vals is None:
            self.info('set %s %s'%(keyname,[]))
            setattr(args,keyname,[])
        else:
            self.info('set %s %s'%(keyname,vals))
            setattr(args,keyname,vals)

        subcmdname = self.__format_cmd_from_cmd_array(cmdpaths)
        if len(subcmdname) > 0:
            setattr(args,'subcommand',subcmdname)
        return args


    def __call_opt_method(self,args,validx,keycls,params):
        if keycls.attr is not None and keycls.attr.optparse is not None:
            nargs = self.call_func(keycls.attr.optparse,args,validx,keycls,params)
        else:
            nargs = self.__opt_parse_handle_map[keycls.type](args,validx,keycls,params)
        return nargs

    def parse_args(self,params=None):
        if params is None:
            params = sys.argv[1:]
        parsestate = _ParseState(params,self.__maincmd,self.__options)
        args = NameSpaceEx()
        try:
            while True:
                validx,optval,keycls = parsestate.step_one()
                #self.info('key %s val %s keycls %s'%(key,val,keycls))
                if keycls is None:
                    cmdpaths = parsestate.get_cmd_paths()
                    s = ''
                    for c in cmdpaths:
                        s += '%s'%(c)
                    self.info('cmdpaths %s'%(s))
                    args = self.__set_args(args,cmdpaths,optval)
                    self.info('args %s'%(args))
                    break
                elif keycls.type == 'help':
                    # now we should give special 
                    cmdpaths = parsestate.get_cmd_paths()
                    helpcmdname = self.__format_cmd_from_cmd_array(cmdpaths)
                    self.__call_opt_method(args,validx,keycls,helpcmdname)
                else:
                    nargs = self.__call_opt_method(args,validx,keycls,params)
                parsestate.add_parse_args(nargs)
                self.info('%s'%(args))
        except Exception as e:
            self.error_msg('parse (%s) error(%s)\n%s'%(params,e,self.__get_except_info()))
        return args

    def __debug_opts(self,rootcmd=None,tabs=0):
        s = ''
        if rootcmd is None:
            rootcmd = self.__maincmd
        s += ' ' * tabs * 4
        s += '%s'%(rootcmd)
        for c in rootcmd.subcommands:
            s += __debug_opts(c,tabs + 1)
        return s



    def parse_command_line(self,params=None,Context=None,mode=None):
        # we input the self command line args by default
        pushmode = False
        if mode is not None:
            pushmode = True
            self.__output_mode.append(mode)
        args = NameSpaceEx()
        try:
            self.__set_command_line_self_args()
            if params is None:
                params = sys.argv[1:]
            args = self.parse_args(params)
            for p in self.__load_priority:
                self.info('set priority [%s]'%(p))
                args = self.__parse_set_map[p](args)

            # set the default value
            args = self.__set_default_value(args)
            # now test whether the function has
            if args.subcommand is not None:
                cmds = self.__find_commands_in_path(args.subcommand)
                funcname = cmds[-1].keycls.function
                if funcname is not None and (len(self.__output_mode) == 0 or self.__output_mode[-1] == ''):
                    self.call_func(funcname,args,Context)
                    return args
        finally:
            if pushmode:
                self.__output_mode.pop()
                pushmode = False
        return args

    def __get_subcommands(self,cmdname,cmdpaths=None):
        if cmdpaths is None:
            cmdpaths = [self.__maincmd]
        retnames = None
        if cmdname is None or len(cmdname) == 0:
            retnames = []
            for c in cmdpaths[-1].subcommands:
                retnames.append(c.cmdname)            
            return sorted(retnames)
        sarr = re.split('\.',cmdname)
        for c in cmdpaths[-1].subcommands:
            if c.cmdname == sarr[0]:
                cmdpaths.append(c)
                return self.__get_subcommands('.'.join(sarr[1:]),cmdpaths)
        return retnames

    def __get_cmdkey(self,cmdname,cmdpaths=None):
        if cmdpaths is None:
            cmdpaths = [self.__maincmd]
        retkey = None
        if cmdname is None or len(cmdname) == 0:
            retkey = cmdpaths[-1].keycls
            return retkey
        sarr = re.split('\.',cmdname)
        for c in cmdpaths[-1].subcommands:
            if c.cmdname == sarr[0]:
                cmdpaths.append(c)
                return self.__get_cmdkey('.'.join(sarr[1:]),cmdpaths)
        return None

    def get_subcommands(self,cmdname=None):
        self.__set_command_line_self_args()
        return self.__get_subcommands(cmdname)

    def get_cmdkey(self,cmdname=None):
        self.__set_command_line_self_args()
        return self.__get_cmdkey(cmdname)

    def __sort_cmdopts(self,retopts=None):
        if retopts is not None:
            normalopts = []
            argsopt = None
            for opt in retopts:
                if opt.type == 'args':
                    assert(argsopt is None)
                    argsopt = opt
                    continue
                normalopts.append(opt)
            i = 0
            while i < len(normalopts):
                j = i + 1
                while j < len(normalopts):
                    if normalopts[j].optdest <  normalopts[i].optdest:
                        tmpopt = normalopts[j]
                        normalopts[j] = normalopts[i]
                        normalopts[i] = tmpopt
                    j += 1
                i += 1
            retopts = []
            if argsopt is not None:
                retopts.append(argsopt)
            retopts.extend(normalopts)
        return retopts


    def __get_cmdopts(self,cmdname,cmdpaths=None):
        if cmdpaths is None:
            cmdpaths = [self.__maincmd]
        retopts = None
        if cmdname is None or len(cmdname) == 0:
            retopts = cmdpaths[-1].cmdopts
            # now sorted the retopts
            return self.__sort_cmdopts(retopts)

        sarr = re.split('\.',cmdname)
        for c in cmdpaths[-1].subcommands:
            if c.cmdname == sarr[0]:
                cmdpaths.append(c)
                return self.__get_cmdopts('.'.join(sarr[1:]),cmdpaths)
        return None

    def get_cmdopts(self,cmdname=None):
        self.__set_command_line_self_args()
        return self.__get_cmdopts(cmdname)




def Debug_set_2_args(args,validx,keycls,params):
    if (validx + 2) > len(params):
        raise Exception('need 2 args')
    val = getattr(args,keycls.optdest,None)
    if val is None:
        val = []
    val.append(params[validx].upper())
    val.append(params[(validx + 1)].upper())
    setattr(args,keycls.optdest,val)
    return 2












