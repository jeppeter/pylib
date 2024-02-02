#! /usr/bin/env python

RUST_ERRORS_FORMAT = '''

#[macro_export]
macro_rules! %RUST_NAME%_error_class {
	($type:ident) => {
	#[derive(Debug,Clone)]
	pub struct $type {
		msg :String,		
	}

	#[allow(dead_code)]
	impl $type {
		fn create(c :&str) -> $type {
			$type {msg : format!("{}",c)}
		}
	}

	impl std::fmt::Display for $type {
		fn fmt(&self,f :&mut std::fmt::Formatter) -> std::fmt::Result {
			write!(f,"{}",self.msg)
		}
	}

	impl std::error::Error for $type {}
	};
}

#[macro_export]
macro_rules! %RUST_NAME%_new_error {
	($type:ty,$($a:expr),*) => {
		{
		let mut c :String= format!("[{}:{}][{}]",file!(),line!(),stringify!($type));
		c.push_str(&(format!($($a),*)[..]));
		return Err(Box::new(<$type>::create(c.as_str())));
	  }
	};
}
'''

RUST_LOGGER_FORMAT='''

use std::env;
use std::io::{Write};
use std::fs;
//use std::io::prelude::*;
use lazy_static::lazy_static;
use chrono::{Local,Timelike,Datelike};
use std::sync::RwLock;



fn _%RUST_NAME%_get_environ_var(envname :&str) -> String {
	match env::var(envname) {
		Ok(v) => {
			format!("{}",v)
		},
		Err(_e) => {
			String::from("")
		}
	}
}

#[allow(dead_code)]
struct LogVar {
	level :i32,
	nostderr : bool,
	wfile : Option<fs::File>,
	wfilename :String,
	baklevel :i32,
	baknostderr :bool,
}


fn %RUST_NAME%_proc_log_init(prefix :&str) -> LogVar {
	let mut getv :String;
	let mut retv :i32 = 0;
	let mut nostderr :bool = false;
	let mut coptfile :Option<fs::File> = None;
	let mut key :String;
	let mut fname :String = "".to_string();

	key = format!("{}_LEVEL", prefix);
	getv = _%RUST_NAME%_get_environ_var(&key);
	if getv.len() > 0 {
		match getv.parse::<i32>() {
			Ok(v) => {
				retv = v;
			},
			Err(e) => {
				retv = 0;
				eprintln!("can not parse [{}] error[{}]", getv,e);
			}
		}
	}

	key = format!("{}_NOSTDERR",prefix);
	getv = _%RUST_NAME%_get_environ_var(&key);
	if getv.len() > 0 {
		nostderr = true;
	}



	key = format!("{}_LOGFILE",prefix);
	getv = _%RUST_NAME%_get_environ_var(&key);
	if getv.len() > 0 {
		fname = format!("{}",getv);
		let fo = fs::File::create(&getv);
		if fo.is_err() {
			eprintln!("can not open [{}]", getv);
		} else {
			coptfile = Some(fo.unwrap());
		}
	}

	return LogVar {
		level : retv,
		nostderr : nostderr,
		wfile : coptfile,
		wfilename : fname,
		baklevel : 0,
		baknostderr : true,
	};
}


lazy_static! {
	static ref %RUST_NAME_UPPER%_LOG_LEVEL : RwLock<LogVar> = {
	 	RwLock::new(%RUST_NAME%_proc_log_init("%RUST_NAME_UPPER%"))
	};
}

#[allow(dead_code)]
pub fn set_%RUST_NAME%_logger_disable() {
	let mut %RUST_REFERENCE% = %RUST_NAME_UPPER%_LOG_LEVEL.write().unwrap();
	%RUST_REFERENCE%.baknostderr = %RUST_REFERENCE%.nostderr;
	%RUST_REFERENCE%.baklevel = %RUST_REFERENCE%.level;
	%RUST_REFERENCE%.wfile = None;
	%RUST_REFERENCE%.level = 0;
	%RUST_REFERENCE%.nostderr = true;
	return;
}

#[allow(dead_code)]
pub fn set_%RUST_NAME%_logger_enable() {
	let mut %RUST_REFERENCE% = %RUST_NAME_UPPER%_LOG_LEVEL.write().unwrap();
	%RUST_REFERENCE%.level = %RUST_REFERENCE%.baklevel;
	%RUST_REFERENCE%.nostderr = %RUST_REFERENCE%.baknostderr;	
	if %RUST_REFERENCE%.wfilename.len() > 0 {
		let fo = fs::File::create(&%RUST_REFERENCE%.wfilename);
		if fo.is_ok() {
			%RUST_REFERENCE%.wfile = Some(fo.unwrap());
		}
	}
	return ;
}


#[allow(dead_code)]
pub (crate)  fn %RUST_NAME%_debug_out(level :i32, outs :&str) {
	let %RUST_REFERENCE% = %RUST_NAME_UPPER%_LOG_LEVEL.write().unwrap();
	if %RUST_REFERENCE%.level >= level {
		let c = format!("{}%LINE_RETURN%",outs);
		if !%RUST_REFERENCE%.nostderr {
			let _ = std::io::stderr().write_all(c.as_bytes());
		}

		if %RUST_REFERENCE%.wfile.is_some() {
			let mut wf = %RUST_REFERENCE%.wfile.as_ref().unwrap();
			let _ = wf.write(c.as_bytes());
		}
	}
	return;
}

#[allow(dead_code)]
pub (crate) fn %RUST_NAME%_log_get_timestamp() -> String {
	let now = Local::now();
	return format!("{}/{}/{} {}:{}:{}",now.year(),now.month(),now.day(),now.hour(),now.minute(),now.second());
}

#[macro_export]
macro_rules! %RUST_NAME%_log_error {
	($($arg:tt)+) => {
		let mut c :String= format!("[ECSIMPLE]<ERROR>{}[{}:{}]  ",%RUST_NAME%_log_get_timestamp(),file!(),line!());
		c.push_str(&(format!($($arg)+)[..]));
		%RUST_NAME%_debug_out(0,&c);
	}
}

#[macro_export]
macro_rules! %RUST_NAME%_log_warn {
	($($arg:tt)+) => {
		let mut c :String= format!("[ECSIMPLE]<WARN>{}[{}:{}]  ",%RUST_NAME%_log_get_timestamp(),file!(),line!());
		c.push_str(&(format!($($arg)+)[..]));
		%RUST_NAME%_debug_out(10,&c);
	}
}


#[macro_export]
macro_rules! %RUST_NAME%_log_info {
	($($arg:tt)+) => {
		let mut c :String= format!("[ECSIMPLE]<INFO>{}[{}:{}]  ",%RUST_NAME%_log_get_timestamp(),file!(),line!());
		c.push_str(&(format!($($arg)+)[..]));
		%RUST_NAME%_debug_out(20,&c);
	}
}

#[cfg(feature="debug_mode")]
#[macro_export]
macro_rules! %RUST_NAME%_log_trace {
	($($arg:tt)+) => {
		let mut _c :String= format!("[ECSIMPLE]<TRACE>{}[{}:{}]  ",%RUST_NAME%_log_get_timestamp(),file!(),line!());
		_c.push_str(&(format!($($arg)+)[..]));
		%RUST_NAME%_debug_out(40, &_c);
	}
}

#[cfg(not(feature="debug_mode"))]
#[macro_export]
macro_rules! %RUST_NAME%_log_trace {
	($($arg:tt)+) => {}
}


#[macro_export]
macro_rules! %RUST_NAME%_assert {
	($v:expr , $($arg:tt)+) => {
		if !($v) {
			let mut _c :String= format!("[ECSIMPLE][{}:{}] ",file!(),line!());
			_c.push_str(&(format!($($arg)+)[..]));
			panic!("{}", _c);
		}
	}
}


#[macro_export]
macro_rules! %RUST_NAME%_format_buffer_log {
	($buf:expr,$len:expr,$info:tt,$iv:expr,$($arg:tt)+) => {
		let mut c :String = format!("[ECSIMPLE][{}:{}]",file!(),line!());
		c.push_str(&format!("{} ",$info));
		c.push_str(&%RUST_NAME%_log_get_timestamp());
		c.push_str(": ");
		c.push_str(&(format!($($arg)+)[..]));
		let _ptr :*const u8 = $buf as *const u8;
		let  mut _ci :usize;
		let _totallen: usize = $len as usize;
		let mut _lasti :usize = 0;
		let mut _nb :u8;
		c.push_str(&format!(" buffer [{:?}][{}]",_ptr,_totallen));
		_ci = 0;
		while _ci < _totallen {
			if (_ci % 16) == 0 {
				if _ci > 0 {
					c.push_str("    ");
					while _lasti < _ci {
						unsafe{
							_nb = *_ptr.offset(_lasti as isize);	
						}
						
						if _nb >= 0x20 && _nb <= 0x7e {
							c.push(_nb as char);
						} else {
							c.push_str(".");
						}
						_lasti += 1;
					}
				}
				c.push_str(&format!("%LINE_RETURN%0x{:08x}:", _ci));
			}
			unsafe {_nb = *_ptr.offset(_ci as isize);}			
			c.push_str(&format!(" 0x{:02x}",_nb));
			_ci += 1;
		}

		if _lasti < _ci {
			while (_ci % 16) != 0 {
				c.push_str("     ");
				_ci += 1;
			}

			c.push_str("    ");

			while _lasti < _totallen {
				unsafe {_nb = *_ptr.offset(_lasti as isize);}				
				if _nb >= 0x20 && _nb <= 0x7e {
					c.push(_nb as char);
				} else {
					c.push_str(".");
				}
				_lasti += 1;
			}
			//c.push_str("%LINE_RETURN%");
		}
		%RUST_NAME%_debug_out($iv,&c);
	}
}

#[macro_export]
macro_rules! %RUST_NAME%_debug_buffer_error {
	($buf:expr,$len:expr,$($arg:tt)+) => {
		%RUST_NAME%_format_buffer_log!($buf,$len,"<ERROR>",0,$($arg)+);
	}
}

#[macro_export]
macro_rules! %RUST_NAME%_debug_buffer_warn {
	($buf:expr,$len:expr,$($arg:tt)+) => {
		%RUST_NAME%_format_buffer_log!($buf,$len,"<WARN>",10,$($arg)+);
	}
}

#[macro_export]
macro_rules! %RUST_NAME%_debug_buffer_info {
	($buf:expr,$len:expr,$($arg:tt)+) => {
		%RUST_NAME%_format_buffer_log!($buf,$len,"<INFO>",20,$($arg)+);
	}
}

#[macro_export]
macro_rules! %RUST_NAME%_debug_buffer_debug {
	($buf:expr,$len:expr,$($arg:tt)+) => {
		%RUST_NAME%_format_buffer_log!($buf,$len,"<DEBUG>",30,$($arg)+);
	}
}

#[cfg(feature="debug_mode")]
#[macro_export]
macro_rules! %RUST_NAME%_debug_buffer_trace {
	($buf:expr,$len:expr,$($arg:tt)+) => {
		%RUST_NAME%_format_buffer_log!($buf,$len,"<TRACE>",40,$($arg)+);
	}
}

#[cfg(not(feature="debug_mode"))]
#[macro_export]
macro_rules! %RUST_NAME%_debug_buffer_trace {
	($buf:expr,$len:expr,$($arg:tt)+) => {}
}

'''


import extargsparse
import sys
import socket
import logging
import re
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import fileop



def set_logging(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    curlog = logging.getLogger(args.lognames)
    #sys.stderr.write('curlog [%s][%s]\n'%(args.logname,curlog))
    curlog.setLevel(loglvl)
    if len(curlog.handlers) > 0 :
        curlog.handlers = []
    formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d<%(levelname)s>\t%(message)s')
    if not args.lognostderr:
        logstderr = logging.StreamHandler()
        logstderr.setLevel(loglvl)
        logstderr.setFormatter(formatter)
        curlog.addHandler(logstderr)

    for f in args.logfiles:
        flog = logging.FileHandler(f,mode='w',delay=False)
        flog.setLevel(loglvl)
        flog.setFormatter(formatter)
        curlog.addHandler(flog)
    for f in args.logappends:       
        if args.logrotate:
            flog = logging.handlers.RotatingFileHandler(f,mode='a',maxBytes=args.logmaxbytes,backupCount=args.logbackupcnt,delay=0)
        else:
            sys.stdout.write('appends [%s] file\n'%(f))
            flog = logging.FileHandler(f,mode='a',delay=0)
        flog.setLevel(loglvl)
        flog.setFormatter(formatter)
        curlog.addHandler(flog)
    return

def load_log_commandline(parser):
    logcommand = '''
    {
        "verbose|v" : "+",
        "logname" : "root",
        "logfiles" : [],
        "logappends" : [],
        "logrotate" : true,
        "logmaxbytes" : 10000000,
        "logbackupcnt" : 2,
        "lognostderr" : false
    }
    '''
    parser.load_command_line_string(logcommand)
    return parser

def parse_int(v):
    c = v
    base = 10
    if c.startswith('0x') or c.startswith('0X') :
        base = 16
        c = c[2:]
    elif c.startswith('x') or c.startswith('X'):
        base = 16
        c = c[1:]
    return int(c,base)

def errorsfmt_handler(args,parser):
	set_logging(args)
	s = RUST_ERRORS_FORMAT.replace('%RUST_NAME%',args.subnargs[0])
	fileop.write_file(s,args.output)
	sys.exit(0)
	return

def loggerfmt_handler(args,parser):
	set_logging(args)
	name = args.subnargs[0]
	nameref = '%sref'%(name.lower())
	nameupper = '%s'%(name.upper())
	s = RUST_LOGGER_FORMAT.replace('%RUST_NAME%',name)
	s = s.replace('%RUST_REFERENCE%',nameref)
	s = s.replace('%RUST_NAME_UPPER%',nameupper)
	s = s.replace('%LINE_RETURN%','\\n')
	fileop.write_file(s,args.output)
	sys.exit(0)
	return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "fmterrors<errorsfmt_handler>##nameprefix to replace name prefix##" : {
        	"$" : 1
        },
        "fmtlogger<loggerfmt_handler>##nameprefix to used name prefix##" : {
        	"$" : 1
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()
