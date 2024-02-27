#!/usr/bin/env python

##extractstart 
import os
import sys
import logging
import re
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


##extractend 

class KeyAttr(object):
    def __init__(self,attr):
        self.__obj = dict()
        self.__splitchar = ';'
        self.__attr = ''
        if attr is not None:
            if isinstance(attr,str) or (sys.version== '2' and isinstance(attr,unicode)):
                if attr.lower().startswith('split=') and len(attr) >= 7:
                    c = attr[6]
                    if c == '.':
                        self.__splitchar= '\.'
                    elif c == '\\':
                        self.__splitchar= '\\'
                    elif c == '\/':
                        self.__splitchar= '\/'
                    elif c == ':':
                        self.__splitchar= ':'
                    elif c == '@':
                        self.__splitchar= '@'
                    elif c == '+':
                        self.__splitchar = '\+'
                    else:
                        raise Exception('can not accept (%s) as split char'%(c))
                sarr = re.split(self.__splitchar,attr)
                for c in sarr:              
                    if c.lower().startswith('split=') or len(c) == 0:
                        # because this is the new
                        continue
                    key,val = re.split('=',c,2)
                    if val is not None:
                        self.__obj[key] = val
                    else:
                        self.__obj[key] = True
            elif isinstance(attr,dict):
                for k in attr.keys():
                    self.__obj[k] = attr[k]
        return

    def __str__(self):
        s = '{'
        for k in sorted(self.__obj.keys()):
            s += '%s=%s;'%(k,self.__obj[k])
        s += '}'
        return s


    def __getattr__(self,name):
        if name.startswith('_'):
            return self.__dict__[name]
        if name in self.__obj.keys():
            return self.__obj[name]
        return None


class TypeClass(object):
    def __init__(self,v):
        self.__type = type(v)
        if isinstance(v,str):
            self.__type = 'string'
        elif isinstance(v,dict):
            self.__type = 'dict'
        elif isinstance(v,list):
            self.__type = 'list'
        elif isinstance(v,bool):
            self.__type = 'bool'
        elif isinstance (v,int):
            self.__type = 'int'
        elif isinstance(v ,float):
            self.__type = 'float'
        elif sys.version[0] == '2' and isinstance(v,unicode):
            self.__type = 'unicode'
        elif v is None:
            # we use default string
            self.__type = 'string'
        elif isinstance(v,long):
            self.__type = 'long'
        else:
            raise Exception('(%s)unknown type (%s)'%(v,type(v)))
        return

    def get_type(self):
        return self.__type

    def __str__(self):
        return self.__type

    def __repr__(self):
        return self.__type


class Utf8Encode(object):
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

class ExtKeyParse(object):
    flagspecial = ['value','prefix']
    flagwords = ['flagname','helpinfo','shortflag','nargs','varname']
    cmdwords = ['cmdname','function','helpinfo']
    otherwords = ['origkey','iscmd','isflag','type','attr','longprefix','shortprefix']
    formwords = ['longopt','shortopt','optdest','needarg']
    def __reset(self):
        self.__value = None
        self.__prefix = ''
        self.__flagname = None
        self.__helpinfo = None
        self.__shortflag = None
        self.__nargs = None
        self.__varname = None
        self.__cmdname = None
        self.__function = None
        self.__origkey = None
        self.__iscmd = None
        self.__isflag = None
        self.__type = None
        self.__attr = None
        self.__nochange = False
        self.__longprefix= '--'
        self.__shortprefix = '-'
        return

    def __eq_name__(self,other,name):
        if name in self.__class__.flagwords or name in self.__class__.flagspecial or \
            name in self.__class__.cmdwords or name in self.__class__.otherwords or \
            name in self.__class__.formwords :
            keyname = self.__get_inner_name(name)
            if self.__dict__[keyname] is None and \
                other.__dict__[keyname] is None:
                return True
            elif self.__dict__[keyname] is not None and \
                 other.__dict__[keyname] is None:
                 return False
            elif self.__dict__[keyname] is None and \
                 other.__dict__[keyname] is not None:
                 return False
            elif self.__dict__[keyname] != other.__dict__[keyname]:
                return False
            return True
        return False

    def __eq_attr__(self,other):
        sattr = self.__attr
        kname = self.__get_inner_name('attr')
        oattr = other.__dict__[kname]
        if sattr is None and oattr is None:
            return True
        if sattr is not None and oattr is None:
            return False
        if sattr is None and oattr is not None:
            return False
        if str(sattr) != str(oattr):
            return False
        return True

    def __eq__(self,other):        
        if not self.__eq_name__(other,'type'):
            return False
        if not self.__eq_name__(other,'origkey'):
            return False
        if not self.__eq_name__(other,'prefix'):
            return False
        if not self.__eq_name__(other,'type'):
            return False
        if not self.__eq_name__(other,'value'):
            return False
        if not self.__eq_attr__(other):
            return False
        if self.__longprefix != other.__longprefix:
            return False
        if self.__shortprefix != other.__shortprefix:
            return False        
        return True

    def __ne__(self,other):
        return not self.__eq__(other)


    def __validate(self):
        if self.__isflag:
            assert(not self.__iscmd )
            if self.__function is not None:
                raise Exception('(%s) can not accept function'%(self.__origkey))
            if self.__type == 'dict' and self.__flagname:
                # in the prefix we will get dict ok
                raise Exception('(%s) flag can not accept dict'%(self.__origkey))
            if self.__type != str(TypeClass(self.__value)) and self.__type != 'count' and self.__type != 'help' and self.__type != 'jsonfile':
                raise Exception('(%s) value (%s) not match type (%s)'%(self.__origkey,self.__value,self.__type))
            if self.__flagname is None :
                # we should test if the validate flag
                if self.__prefix is None:
                    raise Exception('(%s) should at least for prefix'%(self.__origkey))
                self.__type = 'prefix'
                if str(TypeClass(self.__value)) != 'dict':
                    raise Exception('(%s) should used dict to make prefix'%(self.__origkey))
                if self.__helpinfo :
                    raise Exception('(%s) should not have help info'%(self.__origkey))
                if self.__shortflag:
                    raise Exception('(%s) should not set shortflag'%(self.__origkey))
            elif self.__flagname == '$':
                # this is args for handle
                self.__type = 'args'
                if self.__shortflag :
                    raise Exception('(%s) can not set shortflag for args'%(self.__origkey))
            else:
                if len(self.__flagname) <= 0:
                    raise Exception('(%s) can not accept (%s)short flag in flagname'%(self.__origkey,self.__flagname))
            if self.__shortflag:
                if len(self.__shortflag) > 1:
                    raise Exception('(%s) can not accept (%s) for shortflag'%(self.__origkey,self.__shortflag))

            if self.__type == 'bool':
                # this should be zero
                if self.__nargs is not None and self.__nargs != 0:
                    raise Exception('bool type (%s) can not accept not 0 nargs'%(self.__origkey))
                self.__nargs = 0
            elif self.__type == 'help':
                if self.__nargs is not None and self.__nargs != 0:
                    raise Exception('help type (%s) can not accept not 0 nargs'%(self.__origkey))
                self.__nargs = 0
            elif self.__type != 'prefix' and self.__flagname != '$' and self.__type != 'count' :
                if self.__flagname != '$' and self.__nargs != 1 and self.__nargs is not None:
                    raise Exception('(%s)only $ can accept nargs option'%(self.__origkey))
                self.__nargs = 1
            else:
                if self.__flagname == '$' and self.__nargs is None:
                    # we make sure any args to have
                    self.__nargs = '*'
        else:
            if self.__cmdname is None or len(self.__cmdname) == 0 :
                raise Exception('(%s) not set cmdname'%(self.__origkey))
            if self.__shortflag :
                raise Exception('(%s) has shortflag (%s)'%(self.__origkey,self.__shortflag))
            if self.__nargs:
                raise Exception('(%s) has nargs (%s)'%(self.__origkey,self.__nargs))
            if self.__type != 'dict':
                raise Exception('(%s) command must be dict'%(self.__origkey))
            if self.__prefix is None:
                self.__prefix = ''
            if len(self.__prefix) == 0:
                self.__prefix += self.__cmdname         
            self.__type = 'command'
        if self.__isflag and self.__varname is None and self.__flagname is not None:
            if self.__flagname != '$':
                self.__varname = self.optdest
            else:
                if len(self.__prefix) > 0:
                    self.__varname = 'subnargs'
                else:
                    self.__varname = 'args'
        return

    def __set_flag(self,prefix,key,value):
        self.__isflag = True
        self.__iscmd = False
        self.__origkey = key
        if 'value' not in value.keys():
            self.__value = None
            self.__type = 'string'      

        for k in value.keys():
            if k in self.__class__.flagwords:
                innerkey = self.__get_inner_name(k)
                if self.__dict__[innerkey] and self.__dict__[innerkey] != value[k]:
                    raise Exception('set (%s) for not equal value (%s) (%s)'%(k,self.__dict__[innerkey],value[k]))
                if not (str(TypeClass(value[k])) == 'string' or str(TypeClass(value[k])) == 'int' or str(TypeClass(value[k])== 'unicode')):
                    raise Exception('(%s)(%s)(%s) can not take other than int or string (%s)'%(self.__origkey,k,value[k],TypeClass(value[k])))              
                self.__dict__[innerkey] = value[k]
            elif k in self.__class__.flagspecial:
                innerkey = self.__get_inner_name(k)
                if k == 'prefix':
                    if str(TypeClass(value[k])) != 'string' or value[k] is None:
                        raise Exception('(%s) prefix not string or None'%(self.__origkey))
                    newprefix = ''
                    if prefix and len(prefix):
                        newprefix += '%s_'%(prefix)
                    newprefix += value[k]
                    self.__prefix = newprefix
                elif k == 'value':
                    if str(TypeClass(value[k])) == 'dict':
                        raise Exception('(%s)(%s) can not accept dict'%(self.__origkey,k))
                    self.__value = value[k]
                    self.__type = str(TypeClass(value[k]))
                else:
                    self.__dict__[innerkey] = value[k]
            elif k == 'attr':
                if self.__attr is None:
                    self.__attr = KeyAttr(value[k])
        if len(self.__prefix) == 0  and len(prefix) > 0:
            self.__prefix = prefix
        return



    def __parse(self,prefix,key,value,isflag,ishelp,isjsonfile):
        flagmod = False
        cmdmod = False
        flags = None
        self.__origkey = key
        if '$' in self.__origkey:
            if self.__origkey[0] != '$':
                raise Exception('(%s) not right format for ($)'%(self.__origkey))
            ok = 1
            try:
                idx = self.__origkey.index('$',1)
                ok = 0
            except:
                pass
            if ok == 0 :
                raise Exception('(%s) has ($) more than one'%(self.__origkey))
        if isflag or ishelp or isjsonfile:
            m = self.__flagexpr.findall(self.__origkey)
            if m and len(m)>0:
                flags = m[0]
            if flags is None :
                m = self.__mustflagexpr.findall(self.__origkey)
                if m and len(m) > 0:
                    flags = m[0]
            if flags is None and self.__origkey[0] == '$':
                self.__flagname = '$'
                flagmod = True
            if flags is not None:
                if '|' in flags:
                    sarr = re.split('\|',flags)
                    if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
                        raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
                    self.__flagname = sarr[0]
                    self.__shortflag = sarr[1]
                else:
                    self.__flagname = flags
                flagmod = True
        else:
            m = self.__mustflagexpr.findall(self.__origkey)
            if m and len(m) > 0:
                flags = m[0]
                if '|' in flags:
                    sarr = re.split('\|',flags)
                    if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
                        raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
                    self.__flagname = sarr[0]
                    self.__shortflag = sarr[1]
                else:
                    if len(flags) <= 1 :
                        raise Exception('(%s) flag must have long opt'%(self.__origkey))
                    self.__flagname = flags
                flagmod = True
            elif self.__origkey[0] == '$':
                # it means the origin is '$'
                self.__flagname = '$'
                flagmod = True
            m = self.__cmdexpr.findall(self.__origkey)
            if m and len(m) > 0:
                assert(not flagmod)
                if '|' in m[0]:
                    flags = m[0]
                    if '|' in flags:
                        sarr = re.split('\|',flags)
                        if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
                            raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
                        self.__flagname = sarr[0]
                        self.__shortflag = sarr[1]
                    else:
                        assert( False )
                    flagmod = True
                else:
                    self.__cmdname = m[0]
                    cmdmod = True
        m = self.__helpexpr.findall(self.__origkey)
        if m and len(m) > 0:
            self.__helpinfo = m[0]
        newprefix = ''
        if prefix and len(prefix) > 0 :
            newprefix = '%s'%(prefix)
        m = self.__prefixexpr.findall(self.__origkey)
        if m and len(m) > 0:
            if len(newprefix) > 0:
                newprefix += '_'
            newprefix += m[0]
            self.__prefix = newprefix
        else:
            if len(newprefix) > 0:
                self.__prefix = newprefix
        if flagmod :
            self.__isflag = True
            self.__iscmd = False
        if cmdmod :
            self.__iscmd = True
            self.__isflag = False
        if  not flagmod and not cmdmod :
            self.__isflag = True
            self.__iscmd = False
        self.__value = value
        if not ishelp and not isjsonfile:
            self.__type = str(TypeClass(value))
        elif ishelp:
            self.__type = 'help'
            self.__nargs = 0
        elif isjsonfile:
            self.__type = 'jsonfile'
            self.__nargs = 1
        if self.__type == 'help' and value is not None:
            raise Exception('help type must be value None')
        if cmdmod and self.__type != 'dict':
            flagmod = True
            cmdmod = False
            self.__isflag = True
            self.__iscmd = False
            self.__flagname = self.__cmdname
            self.__cmdname = None

        if self.__isflag and self.__type == 'string' and self.__value == '+' and self.__flagname != '$':
            self.__value = 0
            self.__type = 'count'
            self.__nargs = 0

        if self.__isflag and self.__flagname == '$' and self.__type != 'dict':
            if not ((self.__type == 'string' and (self.__value  in '+?*' )) or self.__type == 'int') :
                raise Exception('(%s)(%s)(%s) for $ should option dict set opt or +?* specialcase or type int'%(prefix,self.__origkey,self.__value))
            else:
                self.__nargs = self.__value
                self.__value = None
                self.__type = 'string'
        if self.__isflag and self.__type == 'dict' and self.__flagname:
            self.__set_flag(prefix,key,value)
            # now we should 
        m = self.__attrexpr.findall(self.__origkey)
        if m and len(m) > 0:
            self.__attr = KeyAttr(m[0])

        # we put here for the lastest function
        m = self.__funcexpr.findall(self.__origkey)
        if m and len(m):
            if flagmod:
                # we should put the flag mode
                self.__varname = m[0]
            else:
                self.__function = m[0]
        self.__validate()
        return

    def __get_inner_name(self,name):
        innerkeyname = name
        if (name in self.__class__.flagwords) or \
            (name in self.__class__.flagspecial) or \
           (name in self.__class__.cmdwords) or \
           (name in self.__class__.otherwords):
            innerkeyname = '_%s__%s'%(self.__class__.__name__,name)
        return innerkeyname



    def __init__(self,prefix,key,value,isflag=False,ishelp=False,isjsonfile=False,longprefix='--',shortprefix='-',nochange=False):
        key = Utf8Encode(key).get_val()
        prefix = Utf8Encode(prefix).get_val()
        value = Utf8Encode(value).get_val()

        self.__reset()
        self.__helpexpr = re.compile('##([^\#\!]+)##$',re.I)
        self.__cmdexpr = re.compile('^([^\#\<\>\+\$\!]+)',re.I)
        self.__prefixexpr = re.compile('\+([a-zA-Z]+[a-zA-Z_\-0-9]*)',re.I)
        self.__funcexpr = re.compile('<([^\<\>\#\$\| \t\!]+)>',re.I)
        self.__flagexpr = re.compile('^([a-zA-Z_\|\?\-]+[a-zA-Z_0-9\|\?\-]*)',re.I)
        self.__mustflagexpr = re.compile('^\$([a-zA-Z_\|\?]+[a-zA-Z_0-9\|\?\-]*)',re.I)
        self.__attrexpr = re.compile('\!([^\<\>\$!\#\|]+)\!')
        self.__origkey = key
        self.__longprefix = longprefix
        self.__shortprefix = shortprefix
        self.__nochange = nochange
        if isinstance(key,dict):
            raise Exception('can not accept key for dict type')
        else:
            self.__parse(prefix,key,value,isflag,ishelp,isjsonfile)
        return

    def __form_word(self,keyname):
        if keyname == 'longopt':
            if not self.__isflag or self.__flagname is None or self.__type == 'args':
                raise Exception('can not set (%s) longopt'%(self.__origkey))
            longopt = '%s'%(self.__longprefix)
            if self.__type == 'bool' and self.__value :
                # we set no
                longopt += 'no-'
            if len(self.__prefix) > 0 and self.__type != 'help':
                longopt += '%s_'%(self.__prefix)
            longopt += self.__flagname
            if not self.__nochange:
                longopt = longopt.lower()
                longopt = longopt.replace('_','-')
            return longopt
        elif keyname == 'shortopt':
            if not self.__isflag or self.__flagname is None or self.__type == 'args':
                raise Exception('can not set (%s) shortopt'%(self.__origkey))
            shortopt = None
            if self.__shortflag:
                shortopt = '%s%s'%(self.__shortprefix,self.__shortflag)
            return shortopt
        elif keyname == 'optdest':
            if not self.__isflag or self.__flagname is None or self.__type == 'args':
                raise Exception('can not set (%s) optdest'%(self.__origkey))
            optdest = ''
            if len(self.__prefix) > 0:
                optdest += '%s_'%(self.__prefix)
            optdest += self.__flagname
            optdest = optdest
            if not self.__nochange:
                optdest = optdest.lower()
            # this is for the 
            optdest = optdest.replace('-','_')
            return optdest
        elif keyname == 'needarg':
            if not self.__isflag:
                return 0
            if self.__type == 'int' or self.__type == 'list' or self.__type == 'long' or \
                self.__type == 'float' or self.__type == 'unicode' or self.__type == 'string' or \
                self.__type == 'jsonfile':
                return 1
            return 0

        assert(False)
        return



    def __getattr__(self,keyname):
        if keyname in self.__class__.formwords:
            return self.__form_word(keyname)
        innername = self.__get_inner_name(keyname)
        return self.__dict__[innername]

    def __setattr__(self,keyname,value):
        if (keyname in self.__class__.flagspecial) or \
            (keyname in self.__class__.flagwords) or \
            (keyname in self.__class__.cmdwords) or \
            (keyname in self.__class__.otherwords):
            raise AttributeError
        self.__dict__[keyname] = value
        return

    def __format_string(self):
        s = '{'
        s += '<type:%s>'%(self.__type)
        s += '<origkey:%s>'%(self.__origkey)
        if self.__iscmd:
            s += '<cmdname:%s>'%(self.__cmdname)
            if self.__function:
                s += '<function:%s>'%(self.__function)
            if self.__helpinfo:
                s += '<helpinfo:%s>'%(self.__helpinfo)
            if len(self.__prefix) > 0:
                s += '<prefix:%s>'%(self.__prefix)
        if self.__isflag:
            if self.__flagname:
                s += '<flagname:%s>'%(self.__flagname)
            if self.__shortflag:
                s += '<shortflag:%s>'%(self.__shortflag)
            if len(self.__prefix) > 0 :
                s += '<prefix:%s>'%(self.__prefix)
            if self.__nargs is not None  :
                s += '<nargs:%s>'%(self.__nargs)
            if self.__varname is not None:
                s += '<varname:%s>'%(self.__varname)
            if self.__value is not None:
                s += '<value:%s>'%(self.__value)
            s += '<longprefix:%s>'%(self.__longprefix)
            s += '<shortprefix:%s>'%(self.__shortprefix)
        if self.__attr is not None:
            s += '<attr:%s>'%(self.__attr)
        s += '}'
        return s

    def __str__(self):
        return self.__format_string()
    def __repr__(self):
        return self.__format_string()

    def change_to_flag(self):
        if not self.__iscmd or self.__isflag:
            raise Exception('(%s) not cmd to change'%(self.__origkey))
        if self.__function is not None:
            self.__varname = self.__function
            self.__function = None
        assert(self.__flagname is None)
        assert(self.__shortflag is None)
        assert(self.__cmdname is not None)
        self.__flagname = self.__cmdname
        self.__cmdname = None
        self.__iscmd = False
        self.__isflag = True
        self.__validate()
        return





