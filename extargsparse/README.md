# extargsparse 
> python command package for json string set

### simple example
```python
import extargsparse
commandline = '''
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

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line()
    print ('verbose = %d'%(args.verbose))
    print ('flag = %s'%(args.flag))
    print ('number = %d'%(args.number))
    print ('list = %s'%(args.list))
    print ('string = %s'%(args.string))
    print ('args = %s'%(args.args))
```

> if the command line like this
> python test.py -vvvv -f -n 30 -l bar1 -l bar2 var1 var2

> result is like this

```shell
verbose = 4
flag = True
number = 30
list = ['bar1','bar2']
string = 'string_var'
args = ['var1','var2']
```


### some complex example

```python
import extargsparse
commandline = '''
{
	"verbose|v" : "+",
	"port|p" : 3000,
	"dep" : {
		"list|l" : [],
		"string|s" : "s_var",
		"$" : "+"
	}
}
'''

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(['-vvvv','-p','5000','dep','-l','arg1','--dep-list','arg2','cc','dd'])
    print ('verbose = %d'%(args.verbose))
    print ('port = %s'%(args.port))
    print ('subcommand = %s'%(args.subcommand))
    print ('list = %s'%(args.dep_list))
    print ('string = %s'%(args.dep_string))
    print ('subnargs = %s'%(args.subnargs))
```

> result is like this

```shell
verbose = 4
port = 5000
subcommand = dep
list = ['arg1','arg2']
string = 's_var'
subnargs = ['cc','dd']
```


### callback handle function example

```python
import extargsparse
import os
commandline = '''
{
	'verbose|v' : '+',
	'port|p' : 3000,
	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}
}
'''

def dep_handler(args):
    print ('verbose = %d'%(args.verbose))
    print ('port = %s'%(args.port))
    print ('subcommand = %s'%(args.subcommand))
    print ('list = %s'%(args.dep_list))
    print ('string = %s'%(args.dep_string))
    print ('subnargs = %s'%(args.subnargs))
    os.exit(0)
    return

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(['-vvvv','-p',5000,'dep','-l','arg1','-l','arg2','cc','dd'])
```

> result is like this

```shell
verbose = 4
port = 5000
subcommand = dep
list = ['arg1','arg2']
string = 's_var'
subnargs = ['cc','dd']
```


### with extension flag example

```python
import extargsparse
import os
commandline = '''
{
	'verbose|v' : '+',
	'port|p+http' : 3000,
	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}
}
'''

def dep_handler(args):
    print ('verbose = %d'%(args.verbose))
    print ('port = %s'%(args.http_port))
    print ('subcommand = %s'%(args.subcommand))
    print ('list = %s'%(args.dep_list))
    print ('string = %s'%(args.dep_string))
    print ('subnargs = %s'%(args.subnargs))
    os.exit(0)
    return

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(['-vvvv','-p',5000,'dep','-l','arg1','-l','arg2','cc','dd'])
```

> result is like this

```shell
verbose = 4
port = 5000
subcommand = dep
list = ['arg1','arg2']
string = 's_var'
subnargs = ['cc','dd']
```

### with extension flag bundle example

```python
import extargsparse
import os
commandline = '''
{
	'verbose|v' : '+',
	'+http' : {
		'port|p' : 3000,
		'visual_mode|V' : false
	},
	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}
}
'''

def dep_handler(args):
    print ('verbose = %d'%(args.verbose))
    print ('port = %s'%(args.http_port))
    print ('visual_mode = %s'%(args.http_visual_mode))
    print ('subcommand = %s'%(args.subcommand))
    print ('list = %s'%(args.dep_list))
    print ('string = %s'%(args.dep_string))
    print ('subnargs = %s'%(args.subnargs))
    os.exit(0)
    return

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(['-vvvv','-p','5000','--http-visual-mode','dep','-l','arg1','--dep-list','arg2','cc','dd'])
```

> result is like this

```shell
verbose = 4
port = 5000
visual_mode = True
subcommand = dep
list = ['arg1','arg2']
string = 's_var'
subnargs = ['cc','dd']
```
### with complex flag set

```python
import extargsparse
import os
commandline = '''
{
	'verbose|v' : '+',
	'$port|p' : {
		'value' : 3000,
		'type' : 'int',
		'nargs' : 1 , 
		'help' : 'port to connect'
	},
	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}
}
'''

def dep_handler(args):
    print ('verbose = %d'%(args.verbose))
    print ('port = %s'%(args.port))
    print ('subcommand = %s'%(args.subcommand))
    print ('list = %s'%(args.list))
    print ('string = %s'%(args.string))
    print ('subnargs = %s'%(args.subnargs))
    os.exit(0)
    return

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(['-vvvv','-p','5000','dep','-l','arg1','-l','arg2','cc','dd'])
```

> result is like this

```shell
verbose = 4
port = 5000
visual_mode = True
subcommand = dep
list = ['arg1','arg2']
string = 's_var'
subnargs = ['cc','dd']
```

## Rules

* all key is with value of dict will be flag
 **   like this 'flag|f' : true
     --flag or -f will set the False value for this ,default value is True
 **  like 'list|l' : [] 
     --list or -l will append to the flag value ,default is []

* if value is dict, the key is not start with special char ,it will be the sub command name 
  ** for example 'get' : {
       'connect|c' : 'http://www.google.com',
       'newone|N' : false
  } this will give the sub command with two flag (--get-connect or -c ) and ( --get-newone or -N ) default value is 'http://www.google.com' and False

* if value is dict , the key start with '$' it means the flag description dict 
  ** for example '$verbose|v' : {
  	'value' : 0,
  	'type' : '+',
  	'nargs' : 0,
  	'help' : 'verbose increment'
  }   it means --verbose or -v will be increment and default value 0 and need args is 0  help (verbose increment)

* if the value is dict ,the key start with '+' it means add more bundles of flags
  **  for example  	'+http' : {
		'port|p' : 3000,
		'visual_mode|V' : false
	} --http-port or -p  and --http-visual-mode or -V will set the flags ,short form it will not affected

* if the subcommand follows <.*> it will call function 
  **  for example 	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}  the dep_handler will call __main__ it is the main package ,other packages will make the name of it ,and the 
	   args is the only one add

* special flag '$' is for args in main command '$' for subnargs in sub command


* special flag --json for parsing args in json file in main command
* special flag '--%s-json'%(args.subcommand) for  subcommand for example
   ** --dep-json dep.json will set the json command for dep sub command ,and it will give the all omit the command
   for example 	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}  
    in dep.json
    {
    	'list' : ['jsonval1','jsonval2'],
    	'string' : 'jsonstring',
    	'$' : ['narg1','narg2']
    }

*** example
```python
import extargsparse
import os
commandline = '''
{
	'verbose|v' : '+',
	'+http' : {
		'port|p' : 3000,
		'visual_mode|V' : false
	},
	'dep<__main__.dep_handler>' : {
		'list|l' : [],
		'string|s' : 's_var',
		'$' : '+'
	}
}
'''

def dep_handler(args):
    print ('verbose = %d'%(args.verbose))
    print ('port = %s'%(args.http_port))
    print ('visual_mode = %s'%(args.http_visual_mode))
    print ('subcommand = %s'%(args.subcommand))
    print ('list = %s'%(args.dep_list))
    print ('string = %s'%(args.dep_string))
    print ('subnargs = %s'%(args.subnargs))
    os.exit(0)
    return

def main():
    parser = extargsparse.ExtArgsParse(usage=' sample commandline parser ')
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(['-vvvv','-p','5000','--http-visual-mode','dep','--dep-json','dep.json','-l','arg1','--dep-list','arg2','cc','dd'])
```

result like this
```shell
verbose = 4
port = 5000
visual_mode = True
subcommand = dep
list = ['arg1','arg2']
string = 'jsonstring'
subnargs = ['cc','dd']
```
> because we modify the value in the command line ,so the json file value is ignored

*  you can specify the main command line to handle the json for example
   {
   	 'dep' : {
   	 	'string' : 'jsonstring',
   	 	'list' : ['jsonlist1','jsonlist2'],
   	 	'$' : ['jsonarg1','jsonarg2']
   	 },
   	 'port' : 6000,
   	 'verbose' : 4
   }

* you can specify the json file by environment value for main file json file the value is
   **EXTARGSPARSE_JSONFILE
      for subcommand json file is
      DEP_JSONFILE  DEP is the subcommand name uppercase

   ** by the environment variable can be set for main command
      EXTARGSPARSE_PORT  is for the main command -p|--port etc
      for sub command is for DEP_LIST for dep command --list


* note the priority of command line is 
   **   command input
   **   command json file input
   **   environment variable input _if the common args ,it will start with EXTARGS_ 
   **   environment json file input
   **   default value input by the load string


* flag option key
   **  flagname the flagname of the value
   **  shortflag flag set for the short
   **  value  the default value of flag
   **  nargs it accept args '*' for any '?' 1 or 0 '+' equal or more than 1 , number is the number
   **  helpinfo for the help information
