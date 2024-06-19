
TOPDIR= $(shell pwd)
UPDIR=${TOPDIR}/../..

PYTHON:=$(shell which python)
ifeq (${PYTHON},)
PYTHON=$(shell which python3)
endif

all:selfupdate

selfupdate:${UPDIR}/selfupdate.tmpl ${UPDIR}/makeselfupdate ${TOPDIR}/selfmain ${TOPDIR}/stopservice.py ${TOPDIR}/updatecode.py ${TOPDIR}/update_config.json ${TOPDIR}/commandparse.py 
	${PYTHON} ${UPDIR}/makeselfupdate -i ${UPDIR}/selfupdate.tmpl replcode STOP_SERVICE_CODE ${TOPDIR}/stopservice.py | ${PYTHON} ${UPDIR}/makeselfupdate replcode UPDATE_CODE ${TOPDIR}/updatecode.py | ${PYTHON} ${UPDIR}/makeselfupdate replcode UPDATE_CONFIG ${TOPDIR}/update_config.json | ${PYTHON} ${UPDIR}/makeselfupdate replcode COMMAND_PARSER_CODE ${TOPDIR}/commandparse.py | ${PYTHON} ${UPDIR}/makeselfupdate zip64 -o selfupdate UPDATE_DATA_BASE64 ./selfmain



clean:
	rm -f selfupdate