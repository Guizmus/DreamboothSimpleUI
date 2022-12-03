import os
from sys import executable
import PySimpleGUI as sg
import subprocess
from job_blocs import Bloc

directories = {
    "diffusers" : "data/diffusers",
    "output" : "output/shivam",
    "concepts" : "config/concepts",
}



class ShivamShrirao:
    def set_window(w):
        global window
        window = w
    #used in the jobqueue, needed
    def layout_card(job):
        return [[
            sg.Checkbox(job.params['title'],key=job.key+"-CHECKBOX-active",tooltip="If checked, this job will be run when the queue reaches it",default=job.params['active']),
        ]]
    #used for the content of the job tab, needed
    def layout_tab(job):
        
        title_row = [
            sg.Text("Job name : ",tooltip="The name of the job, so you know what is what."),
            sg.Input(job.params['title'],key=job.key+"-INPUT-title",expand_x=True,justification="center",tooltip="The name of the job, so you know what is what."),
            sg.P(),
            sg.Button(image_filename="code/resources/images/play_small.png",image_size=(36,36),image_subsample=2,key=job.key+"-DO_JOB",button_color="white",tooltip="Save the changes and start the comparison job."),
            sg.Button(image_filename="code/resources/images/trash_small.png",image_size=(36,36),image_subsample=2,key=job.key+"-DELETE",button_color="white",tooltip="Delete this job. The configuration will be kept as a .deleted.json file in settings/jobqueue."),
            sg.Button(image_filename="code/resources/images/save_small.png",image_size=(36,36),image_subsample=2,key=job.key+"-SAVE_CHANGES",button_color="white",tooltip="Save the changes you made to the configuration."),
        ]
        
        input_template = [
            Bloc.browse_txt(job,"model","Input model",directories["diffusers"],size=15,expand_x=False,separated=True),
            Bloc.browse_txt(job,"vae","VAE",directories["diffusers"],size=15,expand_x=False,separated=True),
            Bloc.browse_txt(job,"tokenizer","Tokenizer",directories["diffusers"],size=15,expand_x=False,separated=True),
            Bloc.input(job,"resivision","Model revision",size=24,expand_x=False),
        ]
        output_template = [
            Bloc.browse(job,"output_dir","Output path",directories["output"]),
            Bloc.checkbox(job,"push_to_hub","Push to HF"),
            Bloc.input(job,"hub_token","HF token",expand_x=False,separated=True),
            Bloc.input(job,"hub_model_id","HF model",expand_x=False,separated=True),
        ]
        checkpoint_template = [
            # Bloc.input(job,"log_interval","Log every"),
            Bloc.input(job,"max_train_steps","Training steps",expand_x=False,separated=True),
            Bloc.input(job,"save_min_steps","Fist save on",expand_x=False,separated=True),
            Bloc.input(job,"save_interval","Save every",expand_x=False,separated=True),
            Bloc.input(job,"logging_dir","Log directory",expand_x=False,separated=True),
        ]
        samples_template = [
            Bloc.checkbox(job,"save_sample","Image sample during training"),
            Bloc.input(job,"save_sample_prompt","Prompt"),
            Bloc.input(job,"save_sample_negative_prompt","Negative prompt"),
            # Bloc.range(job,"sample_batch_size","Batch size",[i for i in range(1,8)]),
            Bloc.range(job,"n_save_sample","Total sample count",[i for i in range(1,20)]),
            Bloc.range(job,"save_infer_steps","Steps",[i for i in range(10,50,2)]),
            Bloc.input(job,"save_guidance_scale","CFG"),
        ]
        concepts_template = [
            Bloc.hook(job,"concept"),
            [
                Bloc.button(job,"add_concept","Add concept",as_line=False),
                Bloc.browse(job,"import_concept_list","Import concept list",directories["concepts"],visible_input=False,save_input=False,as_line=False),
                Bloc.browse(job,"export_concept_list","Export concept list",directories["concepts"],visible_input=False,save_input=False,as_line=False),
            ],
        ]
        dataset_template = [
            Bloc.input(job,"resolution","Image resolution"),
            Bloc.checkbox(job,"hflip","Horizontal flip"),
            Bloc.checkbox(job,"center_crop","Center crop"),
        ]
        prior_template = [
            Bloc.checkbox(job,"with_prior_preservation","Use prior preservation"),
            Bloc.input(job,"prior_loss_weight","Prior weight"),
            Bloc.range(job,"num_class_images","Class images",[i for i in range(200,2000,100)]),
        ]
        adam_template = [
            Bloc.checkbox(job,"use_8bit_adam","Use 8-bit Adam"),
            Bloc.input(job,"adam_beta1","Beta1"),
            Bloc.input(job,"adam_beta2","Beta2"),
            Bloc.input(job,"adam_weight_decay","Weight decay"),
            Bloc.input(job,"adam_epsilon","Epsilon value"),
        ]
        learning_template = [
            Bloc.checkbox(job,"train_text_encoder","Train the text encoder"),
            Bloc.input(job,"learning_rate","Learning rate"),
            Bloc.checkbox(job,"scale_lr","Scale LR"),
            Bloc.dropdown(job,"lr_scheduler","Scheduler",["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"]),
            Bloc.input(job,"lr_warmup_steps","Warmup steps"),
            # Bloc.input(job,"num_train_epochs","Epochs"),
            Bloc.input(job,"seed","Seed"),
        ]
        vram_template = [
            Bloc.checkbox(job,"gradient_checkpointing","Use gradient checkpointing"),
            Bloc.checkbox(job,"not_cache_latents","Don't cache latents"),
            Bloc.range(job,"train_batch_size","Train batch size",[i for i in range(1,12)]),
            Bloc.dropdown(job,"mixed_precision","Mixed precision",["no","fp16","bf16"]),
        ]
        no_idea_template = [
            Bloc.range(job,"gradient_accumulation_steps","Gradient accumulation steps",[i for i in range(1,12)]),
            Bloc.checkbox(job,"pad_tokens","Pad tokens to 77"),
            Bloc.input(job,"local_rank","local_rank"),
        ]
        
        
        return [
            title_row,
            [
                sg.Frame("Input",input_template,expand_y=True),
                sg.Frame("Output",output_template,expand_y=True),
                sg.Frame("Checkpoints",checkpoint_template,expand_y=True),
            ],
            [sg.Frame("Concepts to train",concepts_template,expand_x=True)],
            [
                sg.Col([
                    [sg.Frame("Dataset",dataset_template)],
                    [sg.Frame("Prior preservation",prior_template)],
                    [sg.Frame("No idea",no_idea_template)],
                ],vertical_alignment="top"),
                sg.Col([
                    [sg.Frame("Learning",learning_template)],
                    [sg.Frame("8bit_Adam",adam_template)],
                ],vertical_alignment="top"),
                sg.Col([
                    [sg.Frame("Samples",samples_template)],
                    [sg.Frame("VRAM",vram_template)],
                ],vertical_alignment="top"),
            ],
        ]
    #does nothing useful for now outside of updating the title, the rest isn't different from loading it when saved
    def update_layout(job):
        window[job.key+"-CHECKBOX-active"].update(text=job.params['title'])
        window[job.key+"-TAB"].update(title=job.params['title'])
        
    #called when an event with -CALLBACK- as subevent[2] is received
    #necessary for some UI parts specific to that job
    def callback(job,callback_type,event,values):
        return False
    
    def save_params(params):
        return params

    #layout parameters have autosave included and need a default value in the default_job_params
    def layout_parameters():
        return [
            ("title","INPUT"),
            ("active","CHECKBOX"),
        ]
    #all params used for a job of this type with their default values
    def default_job_params():
        return {
            'active':False,
            'output_dir':os.getcwd()+'/output/shivam/',
            'model':'',
            'resivision':'',
            'vae':'',
            'tokenizer':'',
            'push_to_hub':False,
            'hub_token':'',
            'hub_model_id':'',
            'log_interval':10,
            'save_min_steps':1000,
            'save_interval':250,
            'logging_dir':'log',
            'save_sample':False,
            'save_sample_prompt':'',
            'save_sample_negative_prompt':'',
            'sample_batch_size':4,
            'n_save_sample':4,
            'save_infer_steps':20,
            'save_guidance_scale':7.5,
            'resolution':512,
            'hflip':False,
            'center_crop':False,
            'with_prior_preservation':True,
            'prior_loss_weight':1.0,
            'num_class_images':1000,
            'use_8bit_adam':False,
            'adam_beta1':0.9,
            'adam_beta2':0.999,
            'adam_weight_decay':1e-2,
            'adam_epsilon':1e-08,
            'train_text_encoder':True,
            'max_train_steps':2000,
            'learning_rate':1e-6,
            'scale_lr':True,
            'lr_scheduler':'constant',
            'lr_warmup_steps':0,
            'num_train_epochs':1,
            'seed':-1,
            'gradient_checkpointing':True,
            'not_cache_latents':True,
            'train_batch_size':2,
            'mixed_precision':'fp16',
            'gradient_accumulation_steps':1,
            'pad_tokens':False,
            'local_rank':-1,
            'concept':[
                {
                    'instance':'Rick Roll',
                    'class':'A man',
                    'instance_path':'',
                    'class_path':''
                }
            ]
        }
    
    def check_and_start(job):
        print(window['test'].get_size())
        return False
        errors = []
        params = job.params
        
        if len(errors) > 0:
            sg.popup_error("Can't start the job "+params["title"],"\n".join(errors))
        else:
            return subprocess.Popen([executable, "code/scripts/doJob_Shivam.py","--jobJSON",job.saveJSON])
        return False
            