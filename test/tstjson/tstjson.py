
import json

loads= '''
{
		"verbose|v" : "+",
		"+http" : {
			"url|u" : "http://www.google.com",
			"visual_mode|V": false
		},
		"$port|p" : {
			"value" : 3000,
			"type" : "int",
			"nargs" : 1 , 
			"helpinfo" : "port to connect"
		},
		"dep" : {
			"list|l" : [],
		"string|s" : "s_var",
		"$" : "+"
	}
}
'''

d = json.loads(loads)
print ('d (%s)'%(d))