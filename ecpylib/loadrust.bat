echo off

REM 

set SCRIPTDIR=%~dp0
set TOPDIR=%SCRIPTDIR%\..\..

set RUSTBIN=%TOPDIR%\ecsimple\ecsimple\utest\ectst\target\release\ectst.exe
set INSSLSH=%TOPDIR%\ssl_ecgen.sh
set PYTHONFILE=%SCRIPTDIR%\formatcode.py
set OUTDIR=%TOPDIR%\

python %PYTHONFILE% -i %INSSLSH% -o %OUTDIR%\rust_ecpriv.bat fmtrustecprivload
python %PYTHONFILE% -i %INSSLSH% -o %OUTDIR%\rust_ecpub.bat fmtrustecpubload
python %PYTHONFILE% -i %INSSLSH% -o %OUTDIR%\rust_diff.bat fmtrustdiff
python %PYTHONFILE% -i %INSSLSH% -o %OUTDIR%\rust_diffpub.bat fmtrustdiffpub


