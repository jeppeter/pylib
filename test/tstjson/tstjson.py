
import json

loads = '''
		{
			"verbose|v##increment verbose mode##" : "+",
			"flag|f## flag set##" : false,
			"number|n" : 0,
			"list|l" : [],
			"string|s" : "string_var",
			"$" : {
				"value" : [],
				"nargs" : "*",
				"type" : "string"
			}
		}
'''
d = json.loads(loads)
print ('d (%s)'%(d))