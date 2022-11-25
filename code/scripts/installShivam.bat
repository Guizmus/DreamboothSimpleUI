@echo off
cls

echo Checking dependancies
set "VENV_NAME=venv/shivam"
set "VENV_PATH=venv\shivam"

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
	echo Error, a Shivam venv already exists, you cannot install it again without removing %VENV_NAME% first
	exit
)

echo Creating Venv
call conda create -y --prefix %VENV_NAME%  python=3.10 
call activate %VENV_NAME%/ 

echo Cloning ShivamShrirao
call git clone -q https://github.com/ShivamShrirao/diffusers.git code/resources/shivam 

echo Cloning Bitsandbytes
call git clone -q https://github.com/bmaltais/kohya_ss.git code/resources/kohya_ss 

echo Installing Torch
call pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116 

echo Installing Diffusers
call pip install git+https://github.com/ShivamShrirao/diffusers.git 

echo Installing requirements
cd code/resources/shivam/examples/dreambooth 
(
  echo accelerate
  echo transformers^>=4.21.0
  echo ftfy
  echo albumentations
  echo tensorboard
  echo modelcards
) > requirements.txt
call pip install -U -r requirements.txt 
call pip install --upgrade git+https://github.com/huggingface/diffusers.git transformers accelerate scipy 
cd ../../../../..

echo Installing OmegaCong
call pip install OmegaConf 

echo Installing pytorch_lightning
call pip install pytorch_lightning 

echo Installing xformers
call pip install -U -I --no-deps https://github.com/C43H66N12O12S2/stable-diffusion-webui/releases/download/f/xformers-0.0.14.dev0-cp310-cp310-win_amd64.whl 

echo Installing bitsandbytes
call pip install bitsandbytes==0.35.0 

echo Overwriting bitsandbytes libraries

echo Copying resources in Shivam
copy /y "code\resources\kohya_ss\bitsandbytes_windows\*.dll" "%VENV_PATH%\Lib\site-packages\bitsandbytes\"
copy /y "code\resources\kohya_ss\bitsandbytes_windows\cextension.py" "%VENV_PATH%\Lib\site-packages\bitsandbytes\cextension.py"
copy /y "code\resources\kohya_ss\bitsandbytes_windows\main.py" "%VENV_PATH%\Lib\site-packages\bitsandbytes\cuda_setup\main.py" 

echo Environment configuration
call accelerate config
call accelerate env

echo Shivam installed