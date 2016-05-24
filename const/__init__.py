#!/usr/bin/python

class ConstantClassBase(object):
    __keyword=''
    __dict = dict()
    def __init__(self,keyword,values):
        ConstantClassBase.__keyword = keyword.lower()
        for k in values:
            curkey = '%s%s'%(keyword,k)
            curkey = curkey.upper()
            ConstantClassBase.__dict[curkey] = values[k]
        return


    def KEYWORD(self):
        return ConstantClassBase.__keyword

    def __getattr__(self,keyname):
        if keyname.lower().startswith(ConstantClassBase.__keyword):
            if keyname in ConstantClassBase.__dict.keys():
                return ConstantClassBase.__dict[keyname]
        return object.__getattr__(self,keyname,None)

    def __setattr__(self,keyname,value):
        if keyname.lower().startswith(ConstantClassBase.__keyword):
            if keyname in ConstantClassBase.__dict.keys():
                raise Exception('%s is readonly'%(keyname))
            object.__setattr__(self,keyname,value)
        elif keyname == ConstantClassBase.__keyword:
            raise Exception('%s is readonly'%(keyname))
        object.__setattr__(self,keyname,value)
        return

    def __dir__(self):
        return ConstantClassBase.__dict.keys()
