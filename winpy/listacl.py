import os, sys
import win32security

CONVENTIONAL_ACES = {
  win32security.ACCESS_ALLOWED_ACE_TYPE : "ALLOW", 
  win32security.ACCESS_DENIED_ACE_TYPE : "DENY"
}

def list_acl(fname):
  dacl = win32security.GetNamedSecurityInfo(fname, win32security.SE_FILE_OBJECT,
      win32security.DACL_SECURITY_INFORMATION).GetSecurityDescriptorDacl()
  rets = ''
  for i in range(dacl.GetAceCount()):
    ace = dacl.GetAce(i)
    (atype, aflag) = ace[0]
    if atype in CONVENTIONAL_ACES:
      mask , sid = ace[1:]
    else:
      mask, otype,itype , sid = ace[1:]
    name, domain,ptype = win32security.LookupAccountSid(None,sid)
    rets += '%s %s\\%s %x\n'%(CONVENTIONAL_ACES.get(atype,"OTHER"), domain, name,mask)
  return rets

def main():
  for c in sys.argv[1:]:
    rets = list_acl(c)
    sys.stdout.write('%s acl:\n'%(c))
    sys.stdout.write('%s'%(rets))
  return

main()
