

def _inner_add_code(cfile,lines,startcode='SELFMAIN',headed=False):
    s = read_file(cfile)
    sarr = re.split('\n',s)
    outs = ''
    startnote = '##%sBEGIN'%(startcode)
    endnote = '##%sEND'%(startcode)
    inserted = False
    started = False
    idx = 0
    for l in sarr:
        idx += 1
        l = l.rstrip('\r')
        outs += '%s\n'%(l)
        if headed and not inserted:
            outs += '%s\n'%(startnote)
            outs += '%s\n'%(lines)
            outs += '%s\n'%(endnote)
            inserted = True
    if not inserted:
        outs += '%s\n'%(startnote)
        outs += '%s\n'%(lines)
        outs += '%s\n'%(endnote)
    nsarr = re.split('\n',outs)
    nouts = ''
    for l in nsarr:
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        nouts += '%s\n'%(l)
    write_file(nouts,cfile)
    return True



def main_add_code_start(cfile,scriptn,startcode='SELFMAIN'):
    return _inner_add_code(cfile,'%s start'%(scriptn),startcode,False)

def main_add_code_stop(cfile,scriptn,startcode='SELFMAIN'):
    return _inner_add_code(cfile,'%s stop'%(scriptn),startcode,True)


def updatesvc_add_code_start(cfile,scriptn,startcode='UPDATEBASIC'):
    return _inner_add_code(cfile,'%s %s --reboot updatesvc'%(sys.executable,scriptn),startcode,False)

def updatesvc_add_code_stop(cfile,scriptn,startcode='UPDATEBASIC'):
    return _inner_add_code(cfile,'echo "nothing to do"',startcode,True)

def _inner_remove_code(cfile,startcode='SELFMAIN'):
    s = read_file(cfile)
    sarr = re.split('\n',s)
    outs = ''
    startnote = '##%sBEGIN'%(startcode)
    endnote = '##%sEND'%(startcode)
    inserted = False
    started = False
    idx = 0
    for l in sarr:
        idx += 1
        l = l.rstrip('\r')
        if not started and l.startswith(startnote):
            logging.info('at [%d] [%s]'%(idx,l))
            started = True
        if not started:
            outs += '%s\n'%(l)
        if started and l.startswith(endnote):
            logging.info('at end [%d] [%s]'%(idx,l))
            started = False

    write_file(outs,cfile)
    return True

def main_remove_code_stop(cfile,startcode='SELFMAIN'):
    return _inner_remove_code(cfile,startcode)

def main_remove_code_start(cfile,startcode='SELFMAIN'):
    return _inner_remove_code(cfile,startcode)

def updatesvc_remove_code_start(cfile,startcode='UPDATEBASIC'):
    return _inner_remove_code(cfile,startcode)

def updatesvc_remove_code_stop(cfile,startcode='UPDATEBASIC'):
    return _inner_remove_code(cfile,startcode)


def disable_main_svc(args):
    retval = False
    try:
        nret = main_remove_code_start('/oem/btlunch.sh')
        n2ret = main_remove_code_stop('/oem/btstop.sh')
        if nret and n2ret:
            retval = True
    except:
        logging.error('%s'%(traceback.format_exc()))
        retval = False
    return retval


def inst_update_svc(args):
    global UPDATE_SVC_FILE
    retval = False
    try:
        bfile = os.path.basename(__file__)
        nfile = os.path.join(args.svcdir,bfile)
        nret = updatesvc_add_code_start('/oem/btlunch.sh',nfile)
        n2ret = updatesvc_add_code_stop('/oem/btstop.sh',nfile)
        if nret and n2ret:
            retval = True
    except:
        logging.error('%s'%(traceback.format_exc()))
        retval = False
    return retval

def remove_update_svc(args):
    try:
        nret = updatesvc_remove_code_start('/oem/btlunch.sh')
        n2ret = updatesvc_remove_code_stop('/oem/btstop.sh')
        if nret and n2ret:
            retval = True       
    except:
        logging.error('%s'%(traceback.format_exc()))
        retval = False
    return retval

def _check_code(cfile,startcode='SELFMAIN'):
    s = read_file(cfile)
    sarr = re.split('\n',s)
    startnote = '##%sBEGIN'%(startcode)
    endnote = '##%sEND'%(startcode)
    inserted = False
    started = False
    for l in sarr:
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        if not started and l.startswith(startnote):
            started = True
        elif started and l.startswith(endnote):
            started = False
            inserted = True
    return inserted

def main_check_code(cfile,startcode='SELFMAIN'):
    return _check_code(cfile,startcode)

def check_main_svc(args):
    retval = False
    nret = main_check_code('/oem/btlunch.sh')
    n2ret = main_check_code('/oem/btstop.sh')
    if nret or n2ret:
        retval = True
    return retval
