from diffusers import StableDiffusionPipeline
from diffusers import (DDPMScheduler, DDIMScheduler, PNDMScheduler, LMSDiscreteScheduler,
    EulerDiscreteScheduler, EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler)
import torch
schedulers = {
    "ddpm":DDPMScheduler,
    "ddim":DDIMScheduler,
    "pndm":PNDMScheduler,
    "lms":LMSDiscreteScheduler,
    "euler_a":EulerAncestralDiscreteScheduler,
    "euler":EulerDiscreteScheduler,
    "dpm":DPMSolverMultistepScheduler
}
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