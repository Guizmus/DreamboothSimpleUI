import argparse
from PySimpleGUI import UserSettings
import sys
sys.path.insert(1, 'code/scripts/lib/')
from txt2imgBenchmark import compareConfigs

def parse_args():
    parser = argparse.ArgumentParser(description="Does the jobs it is asked for.")

    parser.add_argument(
        "--jobJSON",
        type=str,
        default=None,
        required=True,
        help="Save file of the job to do",
    )

    args = parser.parse_args()
    return args

args = parse_args()

settings = UserSettings(filename="settings/jobqueue/"+args.jobJSON)
params = settings['params']

prompt_values = {}
for alias in params["prompt_alias"]:
    prompt_values[alias['key']]=alias['val'].split(",")
    
if params['size'] == '512':
    size = (512,512)
elif params['size'] == '768':
    size = (768,768)
else:
    size = (int(params['height']),int(params['width']))
    
configsToTest = []
negative_prompts = params['negative_prompt'].split('|')
steps = params['steps'].split(',')
cfgs = params['cfgs'].split(',')
schedulers = params['scheduler'].split(',')
seeds = params['seed'].split(',')
for diffuser in params['diffusers_list']:
    for negative_prompt in negative_prompts:
        for step in steps:
            for scheduler in schedulers:
                for cfg in cfgs:
                    for seed in seeds:
                        configsToTest.append({
                            "model_path":diffuser,
                            "negative_prompt":negative_prompt,
                            "steps":int(step),
                            "cfg":float(cfg),
                            "scheduler":scheduler,
                            "seed":None if seed == "None" else int(seed)
                        })

compareConfigs(
    configsToTest=configsToTest,
    output_path=params['output'],
    prompt_template=params['prompt_template'],
    prompt_values=prompt_values,
    max_batch_size=params['batch_size'],
    n_samples=params['n_samples'],
    save_images=params['save_pics'],
    save_grid=params['save_grid'],
    size=size,
    title=params["title"],
    max_grid_cols=params["grid_height"],
    max_grid_rows=params["grid_width"],
)