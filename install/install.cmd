echo off
pushd %~dp0

set TM=%cd%\..\TaskManager.cmd
set TI=%cd%\..\ico\tm.ico
call Shortcut.exe /f:%userprofile%\Desktop\TaskManager.lnk /a:c /t:%TM% /i:%TI%

set AFR=%cd%\..\..\start_render.cmd
set AFRI=%cd%\..\ico\af.ico
call Shortcut.exe /f:%userprofile%\Desktop\AF_Render.lnk /a:c /t:%AFR% /i:%AFRI%

set AFK=%cd%\..\..\start_keeper.cmd
set AFKI=%cd%\..\ico\af_keeper.ico
call Shortcut.exe /f:%userprofile%\Desktop\AF_Keeper.lnk /a:c /t:%AFK% /i:%AFKI%

call set_environment.cmd "CGPIPELINE" %cd%\..
call set_environment.cmd "CGRU_LOCATION" %cd%\..\..\cgru.2.3.1
pause