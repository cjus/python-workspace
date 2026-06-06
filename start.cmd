@echo off
rem Windows launcher for the Jupyter AI workspace -- thin shim around start.ps1
rem (see that file for what it actually does).
rem
rem -ExecutionPolicy Bypass applies to THIS process only: it does not change
rem your machine's policy. It exists because Windows' default "Restricted"
rem policy blocks .ps1 files, which would otherwise stop first-time users cold.
rem powershell.exe (Windows PowerShell 5.1) is used because it ships with
rem Windows; start.ps1 is written to be compatible with it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
exit /b %ERRORLEVEL%
