@echo off

call %CGRU_LOCATION%\software_setup\setup_nuke.cmd

"%NUKE_EXE%" %*

