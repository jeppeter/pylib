import os, sys
import win32security
import win32con
import win32process

CONVENTIONAL_ACES = {
  win32security.ACCESS_ALLOWED_ACE_TYPE : "ALLOW", 
  win32security.ACCESS_DENIED_ACE_TYPE : "DENY"
}

def enable_priv():
  new_privs = ((win32security.LookupPrivilegeValue('',win32security.SE_SECURITY_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_TCB_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_SHUTDOWN_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_RESTORE_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_TAKE_OWNERSHIP_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_CREATE_PERMANENT_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_ENABLE_DELEGATION_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_CHANGE_NOTIFY_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_DEBUG_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_PROF_SINGLE_PROCESS_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_SYSTEM_PROFILE_NAME),win32con.SE_PRIVILEGE_ENABLED),
               #(win32security.LookupPrivilegeValue('',win32security.SE_LOCK_MEMORY_NAME),win32con.SE_PRIVILEGE_ENABLED)
              )
  ph=win32process.GetCurrentProcess()
  th = win32security.OpenProcessToken(ph,win32security.TOKEN_ALL_ACCESS)  ##win32con.TOKEN_ADJUST_PRIVILEGES)
  win32security.AdjustTokenPrivileges(th,0,new_privs)
  return



def list_acl(fname):
  rets = ''
  owner = win32security.GetNamedSecurityInfo(fname, win32security.SE_FILE_OBJECT, win32security.OWNER_SECURITY_INFORMATION)
  if owner is not None:
    (username,domain,nameuse) = win32security.LookupAccountSid(None,owner.GetSecurityDescriptorOwner())
    if domain is not None and len(domain) > 0:
      rets += '    owner %s\\%s\n'%(domain,username)
    else:
      rets += '    owner %s\n'%(username)
  group = win32security.GetNamedSecurityInfo(fname, win32security.SE_FILE_OBJECT, win32security.GROUP_SECURITY_INFORMATION)
  if group is not None:
    (groupname,domain, nameuse) = win32security.LookupAccountSid(None,group.GetSecurityDescriptorGroup())
    if domain is not None and len(domain) > 0:
      rets += '    group %s\\%s\n'%(domain,groupname)
    else:
      rets += '    group %s\n'%(groupname)
  else:
    rets += '    group none\n'
  dacl = win32security.GetNamedSecurityInfo(fname, win32security.SE_FILE_OBJECT,
      win32security.DACL_SECURITY_INFORMATION).GetSecurityDescriptorDacl()
  if dacl is not None:
    for i in range(dacl.GetAceCount()):
      ace = dacl.GetAce(i)
      (atype, aflag) = ace[0]
      if atype in CONVENTIONAL_ACES:
        mask , sid = ace[1:]
      else:
        mask, otype,itype , sid = ace[1:]
      name, domain,ptype = win32security.LookupAccountSid(None,sid)
      rets += '    DACL %s %s\\%s %x\n'%(CONVENTIONAL_ACES.get(atype,"OTHER"), domain, name,mask)
  sacl = win32security.GetNamedSecurityInfo(fname, win32security.SE_FILE_OBJECT, win32security.SACL_SECURITY_INFORMATION).GetSecurityDescriptorSacl()
  if sacl is not None:
    for i in range(sacl.GetAceCount()):
      ace = sacl.GetAce(i)
      (atype, aflag) = ace[0]
      if atype in CONVENTIONAL_ACES:
        mask , sid = ace[1:]
      else:
        mask, otype,itype , sid = ace[1:]
      name, domain,ptype = win32security.LookupAccountSid(None,sid)
      rets += '    SACL %s %s\\%s %x\n'%(CONVENTIONAL_ACES.get(atype,"OTHER"), domain, name,mask)
  return rets

def main():
  enable_priv()
  for c in sys.argv[1:]:
    rets = list_acl(c)
    sys.stdout.write('%s acl:\n'%(c))
    sys.stdout.write('%s'%(rets))
  return

main()
