echo off

REM 

set SCRIPTDIR=%~dp0
set TOPDIR=%SCRIPTDIR%\..\..

set RUSTBIN=%TOPDIR%\ecsimple\ecsimple\utest\ectst\target\release\ectst.exe
set INSSLSH=%TOPDIR%\ssl_ecgen.sh
set PYTHONFILE=%SCRIPTDIR%\formatcode.py
set OUTDIR=%TOPDIR%\

set TIMES=50
REM set ECNAME=secp112r1
set ECNAME=

if [%1] == [] goto pass_1
set ECNAME=%1
:pass_1

if [%2] == [] goto pass_2
set TIMES=%2
:pass_2


python %PYTHONFILE% -o %OUTDIR%\rust_ecgen.bat fmtrustecgen -C %TIMES% %ECNAME%