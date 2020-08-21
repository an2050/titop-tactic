echo off

set TM=%CGPIPELINE%\TaskManager.cmd
set TI=%CGPIPELINE%\ico\tm.ico
call Shortcut.exe /f:%userprofile%\Desktop\TaskManager.lnk /a:c /t:%TM% /i:%TI%

set AFR=%CGRU_LOCATION%\start\AFANASY\render.cmd
set AFRI=%CGPIPELINE%\ico\af.ico
call Shortcut.exe /f:%userprofile%\Desktop\AF_Render.lnk /a:c /t:%AFR% /i:%AFRI%

set AFK=%CGRU_LOCATION%\start.cmd
set AFKI=%CGPIPELINE%\ico\af_keeper.ico
call Shortcut.exe /f:%userprofile%\Desktop\AF_Keeper.lnk /a:c /t:%AFK% /i:%AFKI%

set NK=%CGPIPELINE%\nuke.cmd
set NKI=%CGPIPELINE%\ico\nuke.ico
call Shortcut.exe /f:%userprofile%\Desktop\_nuke.lnk /a:c /t:%NK% /i:%NKI%

set HOU=%CGPIPELINE%\houdini.cmd
set HOUI=%CGPIPELINE%\ico\houdini.ico
call Shortcut.exe /f:%userprofile%\Desktop\_houdini.lnk /a:c /t:%HOU% /i:%HOUI%