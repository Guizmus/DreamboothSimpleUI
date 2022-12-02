import os
import re 
import random
from torchvision.utils import make_grid
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from ModelManager import modelManager


model = modelManager()
defaultConfig={
    "negative_prompt":"",
    "steps":20,
    "cfg":7.5,
    "scheduler":"euler_a",
    "seed":-1
}
def configToText(config,iteration_count):
    path = config["model_path"].split("/")
    
    output = "Model : "+path.pop()+"\n"
    if config["negative_prompt"] != "":
        output += "NP : "+config["negative_prompt"]+"\n"
    output += config["scheduler"] +"\n" + str(config["steps"]) + " steps\ncfg "+str(config["cfg"])+"\n"
    output += "Seed : " + str(config["seed"]+iteration_count-1)
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
    
def prepare_grid_row(prompts,prompts_per_grid,size,title):
    grids = []
    nb_prompts = len(prompts)
    prompts_left = nb_prompts
    max_char = 20
    while prompts_left > 0:
        new_grid=[centered_text_image(title,size)]
        for j in range(min(prompts_left,prompts_per_grid)):
            prompt = prompts[prompts_left-1]
            prompt = "\n".join([prompt[i:i+max_char] for i in range(0, len(prompt), max_char)])
            new_grid.append(centered_text_image(prompt,size))
            prompts_left -= 1
        grids.append(new_grid)
    return grids
    

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
    size=(512,512),
    max_grid_cols=10,
    max_grid_rows=10,
    title=""
):
    max_grid_rows += 1
    max_grid_cols += 1
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
    nb_configs=len(configsToTest)
    print(str(nb_prompts)+" prompts to run on "+str(nb_configs)+" configurations")
    print(str(n_samples)+" samples per prompt. "+str(nb_configs*nb_prompts*n_samples)+" total images.")

    all_images = []
    first_seed=random.randint(100000,9999999)
    if save_grid:
        prompts_per_grid=nb_prompts
        while prompts_per_grid > max_grid_cols:
            prompts_per_grid = int(prompts_per_grid/2)
        promps_per_grid = max(1,prompts_per_grid)
        configs_per_grid = nb_configs
        while configs_per_grid*n_samples > max_grid_rows:
            configs_per_grid = int(configs_per_grid/2)
        configs_per_grid = max(1,configs_per_grid)
        # grids = prepare_grid_row(prompts,prompts_per_grid,size)
                
    for conf_index in range(len(configsToTest)):
        config = configsToTest[conf_index]
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
            if conf_index % configs_per_grid == 0:
                grids = prepare_grid_row(prompts,prompts_per_grid,size,title)
                
            for i in range(len(images_to_save)):
                img=images_to_save[i]
                grid_column = i % nb_prompts
                grid_index = int(grid_column/(promps_per_grid))
                iteration_count = int(i/nb_prompts)+1
                if grid_column % promps_per_grid == 0:
                    grids[grid_index].append(centered_text_image("Config "+str(conf_index)+" - Iteration "+str(iteration_count)+"\n"+configToText(config,iteration_count),size))
                grids[grid_index].append(transforms.ToTensor()(img))
            if ((conf_index+1) % configs_per_grid == 0) or (conf_index  == len(configsToTest) -1):
                #outputing the grids
                prompts_left = nb_prompts
                for grid in grids:
                    gridTensor = make_grid(grid, nrow=min(promps_per_grid,prompts_left)+1)
                    prompts_left -= promps_per_grid
                    img = transforms.ToPILImage()(gridTensor)
                    img_index=len(os.listdir(output_path))
                    grid_name=f'{img_index:04d}'+"-Grid.png"
                    img.save(output_path+"/"+grid_name)
                    print("Grid saved : "+grid_name)
        
    print("Comparison finished and saved at "+output_path)
