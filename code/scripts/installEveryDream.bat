@echo off
cls

echo Checking dependancies
set "VENV_NAME=venv/everydream"

WHERE conda --version 
IF %ERRORLEVEL% NEQ 0 (
	echo Conda wasn't found. Install conda and run "conda init cmd.exe"
	exit
) else (echo Conda is available)
WHERE git --version 
IF %ERRORLEVEL% NEQ 0 (
	echo Git wasn't found. Install git and make sure it is in PATH
	exit
) else (echo Git is available)

if exist %VENV_NAME%\ (
	echo Error, an EveryDream venv already exists, you cannot install it again without removing %VENV_NAME% first
	exit
)

echo Cloning EveryDream
call git clone -q https://github.com/victorchall/EveryDream-trainer code/resources/everydream 

echo Creating Venv
call conda env create -f code/resources/everydream/environment.yaml --prefix %VENV_NAME%

echo EveryDream installed