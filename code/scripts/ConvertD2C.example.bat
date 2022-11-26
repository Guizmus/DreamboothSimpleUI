@echo off
cls
call activate venv/shivam/
set "CURPATH=%~dp0"

call python code/resources/shivam/scripts/convert_diffusers_to_original_stable_diffusion.py ^
	--model_path=%CURPATH%output/1.5-Shivam-Test/50 ^
	--checkpoint_path=%CURPATH%output/1.5-Shivam-Test_50.ckpt ^
	--half

pause