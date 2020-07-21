@echo off
rem SetLocal EnableDelayedExpansion
rem set content=
rem for /F "tokens=* delims===" %%i in (test.py) do set "content=!content! %%i"
rem cmd /c "C:\Program Files\Shotgun\RV-7.8.0\bin\rvpush.exe" -tag target py-exec %content%
rem echo %content%
rem EndLocal

rem for /F "tokens=*" %%i in (test.py) do set "content=%%i"
rem echo %content%
rem cmd /c "C:\Program Files\Shotgun\RV-7.8.0\bin\rvpush.exe" -tag target py-exec %content%


for /F "tokens=*" %%i in (test.py) do cmd /c ""C:\Program Files\Shotgun\RV-7.8.0\bin\rvpush.exe"" -tag target py-exec %%i
rem cmd /c ""C:\Program Files\Shotgun\RV-7.8.0\bin\rvpush.exe"" -tag target py-exec print('hello')
