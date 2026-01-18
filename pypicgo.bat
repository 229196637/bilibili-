@echo off
setlocal
set PYTHONPATH=%~dp0
python -m pypicgo.cli.main %*
endlocal
