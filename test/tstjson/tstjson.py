
import json

loads = '''
{
  "dep":{
    "list" : ["jsonval1","jsonval2"],
    "string" : "jsonstring"
  }
}
'''
d = json.loads(loads)
print ('d (%s)'%(d))