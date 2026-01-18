@echo off
setlocal
set PYTHONPATH=%~dp0
start /B pythonw run_tray.py
endlocal
