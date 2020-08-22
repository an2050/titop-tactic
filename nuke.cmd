echo off
pushd %TMP%\nk
call %CGPIPELINE%\python\python27\python.exe "%CGPIPELINE%\starter.py" _nuke

rem call python "%CGPIPELINE%\starter.py" _nuke