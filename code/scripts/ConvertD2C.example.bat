@echo off
cls
echo This should be run once you have downloaded 1.5+VAE diffusers.
echo Close now if not
pause
call activate venv/shivam/
set "CURPATH=%~dp0"
mkdir "data/ckpt"

call python code/resources/shivam/scripts/convert_diffusers_to_original_stable_diffusion.py ^
	--model_path=%CURPATH%data/diffusers/SD-1.5-VAE ^
	--checkpoint_path=%CURPATH%data/ckpt/1.5_VAE.ckpt
	REM --half => to use if you want a pruned ckpt

echo conversion ended : data/ckpt/1.5_VAE.ckpt
pause