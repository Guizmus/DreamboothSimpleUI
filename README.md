# DreamboothSimpleUI

This is a set of tools meant for training on Windows with Dreambooth. It includes :

* a UI to install the rest
* easy download and install of ShivamShirao, EveryDream, and my DiffusersComparatorUI
* ShivamShirao come with example use on the less VRAM I could make them run on (12GB for Shivam)
* DiffusersComparatorUI lets you do a comparison on prompts and generation parameters (like sampler, steps, ...) on multiple diffusers, in order to help you stress test checkpoints made during training.

It requires you to have Conda installed, in Path and initialised ("conda init cmd.exe")

It also needs Git in Path.

To download the models, be sure to have accepted their user agreements.

Run the UI.bat to choose what to install/download. If you install one of the 3 tools meant for training, the console will wait on you to complete the setup of Accelerate. Use the values "0" (local machine), "0" (no distributed training), "NO" (use CPU), "NO" (Deepseed), "all" and "fp16". I haven't managed to automate this step.

Run the TestShivam.bat to start a test with the provided example if you installed it, or change the parameters in the bat file to fit your training.

Run UI_DiffusersComparator.bat to start the diffusers comparator UI.

## Install


    
    git clone https://github.com/Guizmus/DreamboothSimpleUI
	cd DreamboothSimpleUI
	UI.bat
    
