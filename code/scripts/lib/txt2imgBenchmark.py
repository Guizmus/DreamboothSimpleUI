from diffusers import StableDiffusionPipeline
from diffusers import (DDPMScheduler, DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler,
    EulerDiscreteScheduler, EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler)
import os
import re 
import random
import torch
from torchvision.utils import make_grid
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class modelManager:
    def __init__(self):
        self.pipe=None
        self.scheduler=None
        self.loadedConfig={
            "scheduler":"",
            "model":""
        }
        self.cudaGenerator = torch.Generator(device='cuda')
    def load(self,config):
        to_cuda=False
        global schedulers
        if config["model_path"] != self.loadedConfig["model"]:
            self.pipe = StableDiffusionPipeline.from_pretrained(config["model_path"], torch_dtype=torch.float16,safety_checker=None,requires_safety_checker=False)
            self.loadedConfig["model"] = config["model_path"]
            self.loadedConfig["scheduler"] = ""
            to_cuda=True
        if (config["scheduler"] != self.loadedConfig["scheduler"]):
            self.pipe.scheduler=schedulers[config["scheduler"]].from_pretrained(self.loadedConfig["model"], subfolder="scheduler")
            self.loadedConfig["scheduler"]=config["scheduler"]
            to_cuda=True
        if to_cuda:
            self.pipe.to("cuda")

model = modelManager()
schedulers = {
    "ddpm":DDPMScheduler,
    "ddim":DDIMScheduler,
    "pndm":PNDMScheduler,
    "lms":LMSDiscreteScheduler,
    "euler_a":EulerAncestralDiscreteScheduler,
    "euler":EulerDiscreteScheduler,
    "dpm":DPMSolverMultistepScheduler
}
defaultConfig={
    "negative_prompt":"",
    "steps":20,
    "cfg":7.5,
    "scheduler":"euler_a",
    "seed":-1
}
def configToText(config):
    path = config["model_path"].split("/")
    
    output = "Model : "+path.pop()+"\n"
    if config["negative_prompt"] != "":
        output += "NP : "+config["negative_prompt"]+"\n"
    output += config["scheduler"] +"\n" + str(config["steps"]) + " steps\ncfg "+str(config["cfg"])+"\n"
    output += "Seed : " + str(config["seed"])
    return output

font = ImageFont.truetype("code/resources/fonts/Gidole-Regular.ttf", size=50)
def centered_text_image(txt,size,bgColor="white",fontColor="black"):
    global font
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), txt, font=font)
    draw.text(((W-w)/2, (H-h)/2), txt, font=font, fill=fontColor)
    return transforms.ToTensor()(image)
    
def compareConfigs(
    configsToTest=[{
        "model_path":"data/diffusers/SD-1.5-VAE",
    }],
    output_path="output/",
    prompt_template="a [subject]",
    prompt_values={"subject":["cat","dog"]},
    max_batch_size=4,
    n_samples=2,
    save_images=False,
    save_grid=True,
    size=(512,512)
):
    if (not save_images) and (not save_grid):
        print("No need to run if we don't save anything")
        return False
    global model
    global defaultConfig
    try:
      os.makedirs(output_path, exist_ok=True)
    except OSError as error:
        print(error)
    
    #prompt list prepare
    m = re.findall('\[(\w+)\]',prompt_template)
    if m:
        prompts=[prompt_template]
        while m:
            old_prompts = prompts
            prompts=[]
            new_motif = m.pop()
            for old_prompt in old_prompts:
                for value in prompt_values[new_motif]:
                    prompts.append(old_prompt.replace("["+new_motif+"]",value))
    else: #nothing to replace in prompt = only 1 prompt to run
        prompts=[prompt_template]
    nb_prompts=len(prompts)

    print(str(nb_prompts)+" prompts to run on "+str(len(configsToTest))+" configurations")
    print(str(n_samples)+" samples per prompt. "+str(len(configsToTest)*len(prompts)*n_samples)+" total images.")

    conf_index = 0
    all_images = []
    first_seed=random.randint(100000,9999999)
    if save_grid:
        gridlist=[centered_text_image("",size)]
        for i in range(nb_prompts):
            gridlist.append(centered_text_image(prompts[nb_prompts-i-1],size))
    for config in configsToTest:
        #start of a configuration run
        config = defaultConfig | config
        print("Loading config #"+str(conf_index)+" ",config)
        model.load(config)
        if config["seed"] == -1:
            seed = first_seed
        elif config["seed"]:
            seed = config["seed"]
        else:
            seed = random.randint(100000,9999999)
        config["seed"] = seed
        model.cudaGenerator.manual_seed(seed)
        
        def run_prompts(prompts_to_run):
            print("running prompts:",prompts_to_run)
            negative_prompt=[]
            for i in range(len(prompts_to_run)):
                negative_prompt.append(config["negative_prompt"])
            W, H = size
            images = model.pipe(
                prompts_to_run,
                height=H,
                width=W,
                negative_prompt=negative_prompt,
                num_images_per_prompt=1,
                num_inference_steps=config["steps"],
                guidance_scale=config["cfg"],
                generator=model.cudaGenerator
            ).images
            return images
        config_prompts = []
        for i in range(n_samples):
            config_prompts = config_prompts + prompts
        
        batch=[]
        images_to_save = []
        while config_prompts:
            batch.append(config_prompts.pop())
            if len(batch) >= max_batch_size:
                images_to_save = images_to_save + run_prompts(batch)
                batch=[]
        if batch:
            images_to_save = images_to_save + run_prompts(batch)
        
        #end of a configuration's run, save the pictures
        if save_images:
            img_index=len(os.listdir(output_path))
            for img in images_to_save:
                img.save(output_path+"/"+f'{img_index:04d}'+"Conf"+str(conf_index)+"-seed" + str(seed) + ".png")
                img_index+=1
        if save_grid:
            prompt_index = 0
            repeat_index = 1
            for img in images_to_save:
                if prompt_index == 0:
                    gridlist.append(centered_text_image("Config "+str(conf_index)+" - Iteration "+str(repeat_index)+"\n"+configToText(config),size))
                    repeat_index += 1
                gridlist.append(transforms.ToTensor()(img))
                prompt_index += 1
                if prompt_index >= nb_prompts:
                    prompt_index = 0
        conf_index+=1
        
    if save_grid:
        grid = make_grid(gridlist, nrow=nb_prompts+1)
        img = transforms.ToPILImage()(grid)
        img_index=len(os.listdir(output_path))
        grid_name=f'{img_index:04d}'+"-Grid.png"
        img.save(output_path+"/"+grid_name)
        print("Grid saved : "+grid_name)
        
    print("Comparison finished and saved at "+output_path)
