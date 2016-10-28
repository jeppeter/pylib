#! /bin/sh
script_dir=`dirname $0`
python $script_dir/traceimpl.py -vvvv -i $script_dir/basic.c -o $script_dir/basic.i -D $script_dir/preprocess.json preprocess -- -Wall
python $script_dir/traceimpl.py -vvvv -i $script_dir/basic.i -D $script_dir/basic.def impl