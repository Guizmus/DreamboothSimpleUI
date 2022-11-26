@echo off

echo Cloning the example dataset
call git clone -q https://huggingface.co/datasets/Guizmus/DreamboothTrainingExample data/datasets/example

echo Moving testing .bat to root
copy /y .\code\scripts\Shivam-1-5.example.bat .\Shivam-1-5.example.bat
copy /y .\code\scripts\Shivam-2-0.example.bat .\Shivam-2-0.example.bat
copy /y .\code\scripts\ConvertD2C.example.bat .\ConvertD2C.example.bat
copy /y .\code\scripts\EveryDream-1-5.example.bat .\EveryDream-1-5.example.bat