echo off
SET HYTHONEXE=%1\bin\hython.exe
call %HYTHONEXE% %CGPIPELINE%\_lib\hou_lib\initHoudiniScene.py %*
echo hython bridge process...