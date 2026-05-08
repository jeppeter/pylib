#! /usr/bin/env python

import logging
import os
import sys
import re
import xlrd
import json
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import extargsparse
import fileop
import logop
import strop

CHECK_COMPANY_IDX_NEW = 2
CHECK_COMPANY_IDX = 3
START_RIDX = 7
START_RIDX_NEW = 5
STOCKCODE_CIDX = 1
SHARESNUM_CIDX = 5
SHARESNUM_CIDX_NEW = 4
AMOUNT_CIDX = 11
AMOUNT_CIDX_NEW = 7
KEYWORD_STOCKCODE = 'stockcode'
KEYWORD_SHARES = 'shares'
KEYWORD_AMOUNT = 'amount'
KEYWORD_CURRENCY = 'currency'
KEYWORD_TOTAL_CASH = 'totalcash'

class ParseSheet(object):
    def __init__(self,fname):
        self.fname = fname
        self.ridx = 0
        return

    def parse_one_ridx_old(self,sh,ridx):
        stkexpr = re.compile('([0-9]+)',re.I)
        try:
            self.ridx = ridx
            retcd = dict()
            stkcode1 = sh.cell_value(ridx,STOCKCODE_CIDX)
            logging.info('stkcode [%s]'%(stkcode1))
            stkcode = '%s'%(stkcode1)
            m = stkexpr.findall(stkcode)
            if m is not None and len(m) > 0:
                stkcode = m[0]
            retcd[KEYWORD_STOCKCODE] = strop.parse_int(stkcode)
            shares = sh.cell_value(ridx, SHARESNUM_CIDX)
            retcd[KEYWORD_SHARES] = strop.parse_float_with_comma(shares)
            amnt = sh.cell_value(ridx,AMOUNT_CIDX)
            cashexpr =re.compile('^([^\\s]+)\\s+([0-9,\\.]+)',re.I)
            m = cashexpr.findall(amnt)
            if m is not None and len(m) > 0:
                retcd[KEYWORD_CURRENCY] = m[0][0]
                retcd[KEYWORD_TOTAL_CASH] = strop.parse_float_with_comma(m[0][1])
            else:
                retcd[KEYWORD_CURRENCY] = 'HKD'
                retcd[KEYWORD_TOTAL_CASH] = 0.0
        except:
            logging.error('[%s:%d]error\n%s'%(self.fname,self.ridx,traceback.format_exc()))
            return None
        return retcd

    def parse_one_ridx_new(self,sh,ridx):
        try:
            self.ridx = ridx
            retcd = dict()
            stkcode = sh.cell_value(ridx,STOCKCODE_CIDX)
            retcd[KEYWORD_STOCKCODE] = strop.parse_int(stkcode)
            shares = sh.cell_value(ridx, SHARESNUM_CIDX_NEW)
            retcd[KEYWORD_SHARES] = strop.parse_float_with_comma(shares)
            amnt = sh.cell_value(ridx,AMOUNT_CIDX_NEW)
            cashexpr =re.compile('^([^\\s]+)\\s+([0-9,\\.]+)',re.I)
            m = cashexpr.findall(amnt)
            if m is not None and len(m) > 0:
                retcd[KEYWORD_CURRENCY] = m[0][0]
                retcd[KEYWORD_TOTAL_CASH] = strop.parse_float_with_comma(m[0][1])
            else:
                retcd[KEYWORD_CURRENCY] = 'HKD'
                retcd[KEYWORD_TOTAL_CASH] = 0.0

        except:
            logging.error('[%s:%d]error\n%s'%(self.fname,self.ridx,traceback.format_exc()))
            return None
        return retcd

    def _check_new_style(self,sh):
        try:
            retval = False
            compval = sh.cell_value(CHECK_COMPANY_IDX_NEW,0)
            if compval.lower() == 'company':
                retval = True
        except:
            logging.error('%s'%(traceback.format_exc()))
            return False
        return retval

    def parse_one_sheet(self):
        retmap = dict()
        try:
            bk = xlrd.open_workbook(self.fname)
            sh = bk.sheet_by_index(0)
            if self._check_new_style(sh):
                val = sh.cell_value(START_RIDX_NEW,0)
                if len(val) != 0:
                    curidx = START_RIDX_NEW
                    while True:
                        val = sh.cell_value(curidx,0)
                        if len(val) == 0:
                            break
                        # now to parse 
                        cd = self.parse_one_ridx_new(sh,curidx)
                        if cd is not None:
                            retmap['%05d'%(cd[KEYWORD_STOCKCODE])] = cd
                        curidx += 1
            else:
                val = sh.cell_value(START_RIDX,0)
                if len(val) != 0:
                    curidx = START_RIDX
                    while True:
                        val = sh.cell_value(curidx,0)
                        logging.info('val [%s]'%(val))
                        if len(val) == 0 or val.lower() == 'nil' :
                            break
                        # now to parse 
                        cd = self.parse_one_ridx_old(sh,curidx)
                        if cd is not None:
                            retmap['%05d'%(cd[KEYWORD_STOCKCODE])] = cd
                        curidx += 1
        except:
            logging.error('error on [%s:%d]\n%s'%(self.fname,self.ridx,traceback.format_exc()))
            return None
        return retmap



def parse_sheet_dir(dname):
    fexpr = re.compile('.*\\.xls$',re.I)
    totalretvp = dict()
    for (r,ds,fs) in os.walk(dname):
        for f in fs:
            curf = os.path.join(r,f)
            if fexpr.match(curf):
                v = ParseSheet(curf)
                retmap = v.parse_one_sheet()
                if retmap is None:
                    continue
                for k in retmap.keys():
                    v = retmap[k]
                    if k in totalretvp.keys():
                        logging.info('[%s]totalretvp[%s]\n%s\nv\n%s'%(curf,k,json.dumps(totalretvp[k],indent=4),json.dumps(v)))
                        totalretvp[k][KEYWORD_SHARES] += v[KEYWORD_SHARES]
                        totalretvp[k][KEYWORD_TOTAL_CASH] += v[KEYWORD_TOTAL_CASH]
                    else:
                        totalretvp[k] = v
    return totalretvp




def onesheet_handler(args,parser):
    logop.set_logging(args)
    if args.input is None:
        raise Exception('need set args input')
    v= ParseSheet(args.input)
    retv =v.parse_one_sheet()
    if retv is None:
        sys.exit(5)
    sys.stdout.write('%s'%(json.dumps(retv,indent=4)))
    sys.exit(0)

def dirsearch_handler(args,parser):
    logop.set_logging(args)
    for d in args.subnargs:
        retv = parse_sheet_dir(d)
        sys.stdout.write('%s\n'%(json.dumps(retv,indent=4)))
    sys.exit(0)



def cellval_handler(args,parser):
    logop.set_logging(args)
    if args.input is None:
        raise Exception('need set args input')
    book = xlrd.open_workbook(args.input)
    sh = book.sheet_by_index(0)
    ridx = strop.parse_int(args.subnargs[0])
    cidx = strop.parse_int(args.subnargs[1])
    val = sh.cell_value(rowx=ridx,colx=cidx)
    sys.stdout.write('[%d:%d]=[%s]\n'%(ridx,cidx,val))
    sys.exit(0)

class HuigouValue(object):
    def __init__(self,rdict):
        self.stock_code=  rdict[KEYWORD_STOCKCODE]
        self.shares = rdict[KEYWORD_SHARES]
        self.totalcash = rdict[KEYWORD_TOTAL_CASH]
        return

    def __eq__(self,other):
        if self.totalcash == other.totalcash:
            return True
        return False

    def __lt__(self,other):
        if self.totalcash < other.totalcash:
            return True
        return False

    def __gt__(self,other):
        if self.totalcash > other.totalcash:
            return True
        return False

    def __str__(self):
        s = 'code :%d , cash %f , shares %f'%(self.stock_code,self.totalcash,self.shares)
        return s

def sortval_handler(args,parser):
    logop.set_logging(args)
    vals = []
    for s in args.subnargs:
        s = fileop.read_file(s)
        rdict = json.loads(s)
        for v in rdict.values():
            vals.append(HuigouValue(v))
    vals = sorted(vals,reverse=True)
    for i in vals:
        sys.stdout.write('%s\n'%(i))

    sys.exit(0)



def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "cellval<cellval_handler>##row col to get value##" : {
            "$" : 2
        },
        "onesheet<onesheet_handler>##to parse for one sheet###" : {
            "$" : 0
        },
        "dirsearch<dirsearch_handler>##dname to parse##" : {
            "$" : "+"
        },
        "sortval<sortval_handler>##file ... to sort from the value##" : {
            "$" : "+"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    logop.load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return

if __name__ =='__main__':
    main()  