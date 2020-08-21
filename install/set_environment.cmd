echo off
pushd %2
REG ADD "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /f  /v %1 /d %cd%
popd