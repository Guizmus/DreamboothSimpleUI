@echo off

echo Cloning the example dataset
call git clone -q https://huggingface.co/datasets/Guizmus/DreamboothTrainingExample data/datasets/example

echo Moving testing .bat to root
copy /y .\code\scripts\ShivamExample-1-5.bat .\ShivamExample-1-5.bat
copy /y .\code\scripts\ShivamExample-2-0.bat .\ShivamExample-2-0.bat