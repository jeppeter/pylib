echo off

REM 

set SCRIPTDIR=%~dp0
set TOPDIR=%SCRIPTDIR%\..\..

set RUSTBIN=%TOPDIR%\ecsimple\ecsimple\utest\ectst\target\release\ectst.exe
set INSSLSH=%TOPDIR%\ssl_ecgen.sh
set PYTHONFILE=%SCRIPTDIR%\formatcode.py
set OUTDIR=%TOPDIR%\

%OUTDIR%\rust_ecpriv.bat && %OUTDIR%\rust_ecpub.bat && %OUTDIR%\rust_diff.bat && %OUTDIR%\rust_diffpub.bat