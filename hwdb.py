#! /usr/bin/env python

import os
import sys
import extargsparse
import logging
import re
import struct
import traceback


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import fileop

GL_LINES=1

def format_tab_line(tab,s):
    global GL_LINES
    rets = ''
    for i in range(tab):
        rets += '    '
    try:
        rets += s
    except:
        logging.info('encode at [%d]\n%s'%(GL_LINES,traceback.format_exc()))
    rets += '\n'
    GL_LINES += 1
    return rets


class HwdbTrieEntry(object):
    def __reset_value(self):
        self.c = b''
        self.child_off = 0
        self.bin_off = 0
        return

    def __init__(self):
        self.__reset_value()
        return

    def dump_data(self,indb,offset):
        if len(indb) < (offset + 16) :
            raise Exception('len(0x%x) < (0x%x + 0x10)'%(len(indb),offset))
        passed = offset
        self.c = indb[offset]
        passed += 8
        self.child_off = struct.unpack('<Q',indb[passed:(passed + 8)])[0]
        passed += 8
        self.bin_off = offset

        return passed

    def format(self,tab=0):
        s = ''
        s += format_tab_line(tab,'ChildEntry:0x%x'%(self.bin_off))
        s += format_tab_line(tab+1,'{')
        s += format_tab_line(tab+2,'c : "%c",'%(self.c))
        s += format_tab_line(tab+2,'child_off : 0x%x'%(self.child_off))
        s += format_tab_line(tab+1,'}')
        return s

class HwdbTrieValueEntry(object):
    def __reset_value(self):
        self.key_off = 0
        self.value_off = 0
        self.key = ''
        self.value = ''
        return

    def __init__(self):
        self.__reset_value()
        return

    def dump_data(self,indb,offset):
        if len(indb) < (offset + 16) :
            raise Exception('len(0x%x) < (0x%x + 0x10)'%(len(indb),offset))
        passed = offset
        self.key_off , self.value_off = struct.unpack('<QQ',indb[passed:(passed+16)])
        # now to get 
        kb = b''
        vb = b''
        if sys.version[0] == '3':
            curoff = self.key_off
            while curoff < len(indb):
                if indb[curoff]==0:
                    break
                kb += struct.pack('B',indb[curoff])
                curoff += 1
            try:
                self.key = kb.decode('utf-8')
            except:
                logging.error('at [0x%x] keyoff error'%(self.key_off))
            curoff = self.value_off
            while curoff < len(indb):
                if indb[curoff]==0:
                    break
                vb += struct.pack('B',indb[curoff])
                curoff += 1
            try:
                self.value = vb.decode('utf-8')
            except:
                logging.error('at [0x%x] valueoff error'%(self.value_off))
        else:
            curoff = self.key_off
            while curoff < len(indb):
                if indb[curoff]==0:
                    break
                kb += indb[curoff]
                curoff += 1
            try:
                self.key = str(kb)
            except:
                logging.error('at [0x%x] keyoff error'%(self.key_off))

            curoff = self.value_off
            while curoff < len(indb):
                if indb[curoff]==0:
                    break
                vb += indb[curoff]
                curoff += 1
            try:
                self.value = str(vb)
            except:
                logging.error('at [0x%x] valueoff error'%(self.value_off))

        passed += 16
        return passed

    def format(self,tab=0):
        s = ''
        s += format_tab_line(tab,'ValueEntry')
        s += format_tab_line(tab+1,'{')
        s += format_tab_line(tab+2,'key_off : 0x%x,'%(self.key_off))
        s += format_tab_line(tab+2,'value_off : 0x%x'%(self.value_off))
        s += format_tab_line(tab+2,'key : %s'%(self.key))
        s += format_tab_line(tab+2,'value : %s'%(self.value))
        s += format_tab_line(tab+1,'}')
        return s

class HwdbTrieNode(object):
    def __reset_value(self):
        self.childents = []
        self.children = []
        self.values = []
        self.children_count = 0
        self.prefix_off = 0
        self.values_count = 0
        self.is_end = False
        self.total_path = ''
        self.vkeys = dict()
    def __init__(self):
        self.__reset_value()
        return

    def format(self,tab=0):
        s = ''
        s += format_tab_line(tab,'Node')
        s += format_tab_line(tab+1,'{')
        s += format_tab_line(tab+2,'prefix_off : 0x%x'%(self.prefix_off))
        if self.is_end:
            s += format_tab_line(tab+2,'total_path : %s'%(self.total_path))
        else:
            idx = 0
            while idx < len(self.children):
                s += format_tab_line(tab+2,'ChildEnt[%d]'%(idx))
                s += self.childents[idx].format(tab+2)
                s += format_tab_line(tab+2,'Children[%d]'%(idx))
                s += self.children[idx].format(tab+2)
                idx += 1
        idx = 0
        while idx < len(self.values):
            s += format_tab_line(tab+2,'Value[%d]'%(idx))
            s += self.values[idx].format(tab+2)
            idx += 1
        s += format_tab_line(tab+1,'}')
        return s

    def dump_data(self,indb,offset,prefix=''):
        self.__reset_value()
        if len(indb) < (offset + 24):
            raise Exception('len (0x%x) < ( 0x%x + 0x18)'%(len(indb),offset))
        passed = offset
        self.prefix_off = struct.unpack('<Q',indb[passed:(passed+8)])[0]
        passed += 8
        self.children_count = indb[passed]
        passed += 8
        self.values_count = struct.unpack('<Q',indb[passed:(passed+8)])[0]
        passed += 8

        curoff = passed
        if self.children_count == 0:
            self.is_end = True
            self.total_path = prefix
        else:
            idx = 0
            curoff = passed
            while idx < self.children_count:
                chldent = HwdbTrieEntry()
                lastoff = curoff
                curoff =  chldent.dump_data(indb,lastoff)
                self.childents.append(chldent)
                if sys.version[0] == '3':
                    setprefix = b''
                    setprefix = prefix.encode('utf-8')
                    setprefix += struct.pack('B',chldent.c)
                else:
                    setprefix = b''
                    setprefix = bytes(prefix)
                    setprefix += chldent.c
                nprefix = ''
                try:
                    if sys.version[0] == '3':
                        nprefix = setprefix.decode('utf-8')
                    else:
                        nprefix = str(setprefix)
                except:
                    nprefix = ''
                    logging.error('on c error %s at off [0x%x] prefix %s'%(chldent.c,lastoff,prefix))
                chld = HwdbTrieNode()
                noff = chld.dump_data(indb,chldent.child_off,nprefix)
                self.children.append(chld)
                idx += 1
        if self.values_count != 0:
            idx = 0
            while idx < self.values_count:
                valueent = HwdbTrieValueEntry()
                curoff = valueent.dump_data(indb,curoff)
                self.values.append(valueent)
                idx += 1
        return passed
        


class HwdbTrie(object):
    def __reset_value(self):
        self.root = None
        self.version = 0
        self.filesize = 0
        self.hdrsize = 0
        self.nodesize = 0
        self.chldentsize = 0
        self.valentsize = 0
        self.rootoff = 0
        self.nodelen = 0
        self.strslen = 0
        return
    def __init__(self):
        self.__reset_value()
        return

    def dump_data(self,indb):       
        if len(indb) < 72:
            raise Exception('indb [%d] need at least 72'%(len(indb)))
        self.__reset_value()
        passed = 0
        magic = indb[:8]
        passed += 8
        if magic != b'KSLPHHRH':
            raise Exception('need KSLPHHRH but get %s'%(fileop.format_bytes(magic,'HEADER')))
        self.version,self.filesize,self.hdrsize,self.nodesize,self.chldentsize,self.valentsize,self.rootoff,self.nodeslen,self.strslen = struct.unpack('<QQQQQQQQQ',indb[passed:(passed+72)])
        logging.info('version 0x%x filesize 0x%x hdrsize 0x%x nodesize 0x%x child entry size 0x%x value entry size 0x%x'%(self.version,self.filesize,self.hdrsize,self.nodesize,self.chldentsize,self.valentsize))
        logging.info('rootoff 0x%x nodelen 0x%x strslen 0x%x'%(self.rootoff,self.nodelen,self.strslen))
        if len(indb) < self.hdrsize:
            raise Exception('hdrsize 0x%x > len(0x%x)'%(self.hdrsize,len(indb)))
        passed += 72

        self.root = HwdbTrieNode()
        self.root.dump_data(indb,self.rootoff)
        return passed

    def format(self,tab=0):
        s = ''
        s += format_tab_line(tab,'Root')
        s += format_tab_line(tab+1,'{')
        s += format_tab_line(tab+1,'version : 0x%x'%(self.version))
        s += format_tab_line(tab+1,'filesize : 0x%x'%(self.filesize))
        s += format_tab_line(tab+1,'hdrsize : 0x%x'%(self.hdrsize))
        s += format_tab_line(tab+1,'nodesize : 0x%x'%(self.nodesize))
        s += format_tab_line(tab+1,'chldentsize : 0x%x'%(self.chldentsize))
        s += format_tab_line(tab+1,'valentsize : 0x%x'%(self.valentsize))
        s += format_tab_line(tab+1,'rootoff : 0x%x'%(self.rootoff))
        s += format_tab_line(tab+1,'nodeslen : 0x%x'%(self.nodeslen))
        s += format_tab_line(tab+1,'strslen : 0x%x'%(self.strslen))
        s += self.root.format(tab+1)
        s += format_tab_line(tab+1,'}')
        return s




def dump_handler(args,parser):
    fileop.set_logging(args)
    for f in args.subnargs:
        trif = HwdbTrie()
        indb = fileop.read_file_bytes(f)
        trif.dump_data(indb)
        s = trif.format(0)
        fileop.write_file(s,args.output)
    sys.exit(0)
    return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "dump<dump_handler>##hwdb.bin ... to dump file ##" : {
            "$" : "+"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    fileop.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()    
