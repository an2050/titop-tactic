echo off
pushd %~dp0

set CGRU_LOCATION=%cd%\..\..\cgru.2.3.1
setx CGRU_LOCATION %CGRU_LOCATION%

set CGPIPELINE=%cd%\..
setx CGPIPELINE %CGPIPELINE%

call create_lnk.cmd

call set_environment.cmd "CGPIPELINE" %CGPIPELINE%
call set_environment.cmd "CGRU_LOCATION" %CGRU_LOCATION%

pause
