@echo off
cls

echo Checking dependancies
set "VENV_NAME=venv/diffusers"

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
	echo Error, a Diffusers venv already exists, you cannot install it again without removing %VENV_NAME% first
	exit
)

echo Creating Venv
call conda create -y --prefix %VENV_NAME%  python=3.10 
call activate %VENV_NAME%/ 

echo Cloning Diffusers
call git clone -q https://github.com/huggingface/diffusers code/resources/diffusers 

echo Installing Torch
call pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116 

echo Installing Diffusers
call pip install --upgrade git+https://github.com/huggingface/diffusers.git transformers accelerate scipy ftfy

echo Installing xformers
call pip install -U -I --no-deps https://github.com/C43H66N12O12S2/stable-diffusion-webui/releases/download/f/xformers-0.0.14.dev0-cp310-cp310-win_amd64.whl 

echo Installing PySimpleGUI
call pip install PySimpleGUI

echo Environment configuration
call accelerate config
call accelerate env

copy /y .\code\scripts\UI_DiffusersComparator.bat .\UI_DiffusersComparator.bat

echo Diffusers installed