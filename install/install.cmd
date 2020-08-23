echo off
pushd %~dp0 

cd %cd%\..
set root=%cd%

cd %root%\..\cgru.2.3.x
set cgru=%cd%

set CGRU_LOCATION="C:\cgru.2.3.x"

mkdir %CGRU_LOCATION%
xcopy %cgru% %CGRU_LOCATION% /Y /E /H >nul

setx CGRU_LOCATION %CGRU_LOCATION%

set CGPIPELINE=%root%
setx CGPIPELINE %CGPIPELINE%

pushd %~dp0
call create_lnk.cmd

call set_environment.cmd "CGPIPELINE" %CGPIPELINE%
call set_environment.cmd "CGRU_LOCATION" %CGRU_LOCATION%

pause
