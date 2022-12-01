@echo off
cls

REM setting up venv for UI
set "VENV_NAME=venv/diffusers"
echo Activating venv
call activate %VENV_NAME%/
echo Starting UI
call python code/scripts/JobQueueUI.py
