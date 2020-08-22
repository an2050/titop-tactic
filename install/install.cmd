echo off
pushd %~dp0 

cd %cd%\..
set root=%cd%

cd %root%\..\cgru.2.3.1
set CGRU_LOCATION=%cd%
setx CGRU_LOCATION %CGRU_LOCATION%

set CGPIPELINE=%root%
setx CGPIPELINE %CGPIPELINE%

ECHO CD IS %cd%
ECHO CGPIPELINE IS %CGPIPELINE%
ECHO CGRU_LOCATION IS %CGRU_LOCATION%

popd
call create_lnk.cmd

call set_environment.cmd "CGPIPELINE" %CGPIPELINE%
call set_environment.cmd "CGRU_LOCATION" %CGRU_LOCATION%

pause
