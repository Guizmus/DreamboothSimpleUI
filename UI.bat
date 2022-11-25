@echo off
cls

echo Checking dependancies
set STDOUT=code/stdout.txt
set STRERR=code/stderr.txt

REM checking dependancies
WHERE conda --version > %STDOUT% 2> %STRERR%
IF %ERRORLEVEL% NEQ 0 (
	echo Conda wasn't found. Install conda and run "conda init cmd.exe"
	exit
) else (echo Conda is available)
WHERE git --version > %STDOUT% 2> %STRERR%
IF %ERRORLEVEL% NEQ 0 (
	echo Git wasn't found. Install git and make sure it is in PATH
	exit
) else (echo Git is available)

REM setting up venv for UI
set "VENV_NAME=venv/UI" > %STDOUT% 2> %STRERR%
if not exist %VENV_NAME%\ (
	echo Preparing UI venv
	call conda create -y --prefix %VENV_NAME%  python=3.10 > %STDOUT% 2> %STRERR%
	call activate %VENV_NAME%/ > %STDOUT% 2> %STRERR%
	call pip install PySimpleGUI > %STDOUT% 2> %STRERR%
) else (
	echo Activating venv
	call activate %VENV_NAME%/ > %STDOUT% 2> %STRERR%
)

echo Starting UI
call python code/scripts/installUI.py
