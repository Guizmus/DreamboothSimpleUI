import os
from sys import executable
import PySimpleGUI as sg
import subprocess

devmode = False
# devmode = True
visivility_queue = devmode

sg.theme('Dark Black')
# innerTheme='Dark Green 3'

# sg.theme_previewer()
#general UI layout
JobQueue=[
    [sg.Text("Job Queue",visible=visivility_queue)],
    [sg.Combo(['-NEW JOB-', 'Diffusers Comparator'],default_value='-NEW JOB-',enable_events=True,key="JOBQUEUE-DROPDOWN",size=(15,1),visible=visivility_queue)],
]
# 
TabZone=[[
    sg.TabGroup([[]],key="HOOK-jobtabs_tabgroup",tab_location="topleft",expand_y=True,expand_x=True,size=(590,500))
]]

menu_def=[
    # ['&Queue',['!Start','!Stop after this job','!Stop now','!Clear finished Jobs','!Clear all jobs',]],
    ['&New job',['Diffusers Comparison::JOBQUEUE-MENU-DiffusersComparator',]]
]

layout = [
    [sg.Menu(menu_def)],
    [
        sg.vtop(sg.Col(JobQueue,key="HOOK-jobqueue_col")),
        # sg.P(),
        sg.vtop(sg.Col(TabZone,expand_y=True,expand_x=True))
    ],
    [sg.VPush()],
    [sg.StatusBar("",key='-STATUSBAR-',expand_x=True,size=(74,1))]
]

#we initialize the window empty and force loading to simplify UI building a little
window = sg.Window('Diffusers comparator', layout, finalize=True)

#Firs type of job and its layout, Diffusers comparator
class DiffusersComparator:
    #used in the jobqueue, needed
    def layout_card(job):
        return [[
            sg.Checkbox(job.params['title'],key=job.key+"-CHECKBOX-active",tooltip="If checked, this job will be run when the queue reaches it",default=job.params['active'],visible=visivility_queue),
        ]]
    #used for the content of the job tab, needed
    def layout_tab(job):
        
        titleRow = [
            sg.Text("Job name : ",tooltip="The name of the job, so you know what is what."),
            sg.Input(job.params['title'],key=job.key+"-INPUT-title",expand_x=True,justification="center",tooltip="The name of the job, so you know what is what."),
            sg.P(),
            sg.Button(image_filename="code/resources/images/play_small.png",image_size=(36,36),image_subsample=2,key=job.key+"-DO_JOB",button_color="white",tooltip="Save the changes and start the comparison job."),
            sg.Button(image_filename="code/resources/images/trash_small.png",image_size=(36,36),image_subsample=2,key=job.key+"-DELETE",button_color="white",tooltip="Delete this job. The configuration will be kept as a .deleted.json file in settings/jobqueue."),
            sg.Button(image_filename="code/resources/images/save_small.png",image_size=(36,36),image_subsample=2,key=job.key+"-SAVE_CHANGES",button_color="white",tooltip="Save the changes you made to the configuration.")
        ]
        
        imageParametersFrame = sg.Frame("Images parameters",[
            [
                sg.P(),
                sg.Spin([i for i in range(1,20)], initial_value=job.params['n_samples'],tooltip="Number of pictures to make per same prompt/configuration",key=job.key+"-SPIN-n_samples",size=(2,1)),
                sg.T("samples",tooltip="Number of pictures to make per same prompt/configuration"),
                sg.P(),
                sg.Spin([i for i in range(1,9)], initial_value=job.params['batch_size'],tooltip="Number of pictures to make per batch maximum. This has only a VRAM impact, use the previous setting to change the pictures per prompt.",key=job.key+"-SPIN-batch_size",size=(2,1)),
                sg.T("batch size",tooltip="Number of pictures to make per batch maximum. This has only a VRAM impact, use the previous setting to change the pictures per prompt."),
                sg.P()
            ],
            [
                sg.T("Size :",pad=(10,5)),
                sg.P(),
                sg.Radio("512",job.key+"-RADIO-size",default=job.params["size"]=="512",key=job.key+"-RADIO-size-512",tooltip="512x512"),
                sg.P(),
                sg.Radio("768",job.key+"-RADIO-size",default=job.params["size"]=="768",key=job.key+"-RADIO-size-768",tooltip="768x768"),
                sg.P(),
            ],
            [
                sg.P(),
                sg.Radio("",job.key+"-RADIO-size",default=job.params["size"]=="custom",pad=0,key=job.key+"-RADIO-size-custom",tooltip="Custom size, choose height and width."),
                sg.P(),
                sg.T("Height",tooltip="Custum height to use for images to generate"),
                sg.Input(job.params["height"],key=job.key+"-INPUT-height",size=(4,1),tooltip="Custom height to use for images to generate."),
                sg.P(),
                sg.T("Width",tooltip="Custum width to use for images to generate"),
                sg.Input(job.params["width"],key=job.key+"-INPUT-width",size=(4,1),tooltip="Custum width to use for images to generate"),
                sg.P(),
            ]
        ],expand_x=True,expand_y=True)
        
        saveParametersFrame = sg.Frame("Save parameters",[
            [
                sg.T("Output folder",tooltip="Defaults to output/images, folder where the pictures and the grid will be saved"),
                sg.FolderBrowse(initial_folder=job.params['output'],target=job.key+"-TEXT-output",tooltip="Defaults to output/images, folder where the pictures and the grid will be saved"),
                sg.T(job.params['output'],key=job.key+"-TEXT-output",size=(15,1),justification="right",tooltip="Defaults to output/images, folder where the pictures and the grid will be saved")
            ],
            [
                sg.P(),
                sg.Checkbox("Save grid",key=job.key+"-CHECKBOX-save_grid",tooltip="If checked, a grid of pictures will be saved.",default=job.params['save_grid']),
                sg.P(),
                sg.Checkbox("Save pictures",key=job.key+"-CHECKBOX-save_pics",tooltip="If checked, all pictures will be saved.",default=job.params['save_pics']),
                sg.P(),
            ],
            [
                sg.P(),
                sg.T("Max grid size",tooltip="If the configurations you want to test get bigger, the grid will get split in multiple grids."),
                sg.T("Height",tooltip="Max pictures height of a grid."),
                sg.Spin([i for i in range(2,30)],initial_value=job.params["grid_height"],key=job.key+"-SPIN-grid_height",size=(2,1),tooltip="Max pictures height of a grid."),
                sg.P(),
                sg.T("Width",tooltip="Max pictures width of a grid."),
                sg.Spin([i for i in range(2,30)],initial_value=job.params["grid_width"],key=job.key+"-SPIN-grid_width",size=(2,1),tooltip="Max pictures width of a grid."),
                sg.P(),
            ]
        ],expand_x=True,expand_y=True)
        
        variatingParametersFrame = sg.Frame("Variating parameters",[
            [
                sg.P(),
                sg.Text("Scheduler : ",tooltip="Enter different samplers to try separated by \",\" :\nddpm\nddim\npndm\nlms\neuler_a\neuler\ndpm"),
                # sg.P(),
                sg.Input(job.params['scheduler'],key=job.key+"-INPUT-scheduler",size=(30,1),tooltip="Enter different samplers to try separated by \",\" :\nddpm\nddim\npndm\nlms\neuler_a\neuler\ndpm"),
            ],
            [
                sg.P(),
                sg.Text("Seed : ",tooltip="Enter different seeds to try separated by \",\".\nUsing the seed -1 will apply the same random seed to each configuration.\nUsing the seed None will apply a new random seed to each configuration."),
                # sg.P(),
                sg.Input(job.params['seed'],key=job.key+"-INPUT-seed",size=(30,1),tooltip="Enter different seeds to try separated by \",\".\nUsing the seed -1 will apply the same random seed to each configuration.\nUsing the seed None will apply a new random seed to each configuration."),
            ],
            [
                sg.P(),
                sg.Text("CFGS : ",tooltip="Enter different CFGS values to try separated by \",\""),
                # sg.P(),
                sg.Input(job.params['cfgs'],key=job.key+"-INPUT-cfgs",size=(30,1),tooltip="Enter different CFGS values to try separated by \",\""),
            ],
            [
                sg.P(),
                sg.Text("Steps : ",tooltip="Enter different step count to try separated by \",\""),
                # sg.P(),
                sg.Input(job.params['steps'],key=job.key+"-INPUT-steps",size=(30,1),tooltip="Enter different step count to try separated by \",\""),
            ],
            [
                sg.P(),
                sg.Text("Negative prompt : ",tooltip="Enter different negative prompts to try separated by \"|\""),
                # sg.P(),
                sg.Input(job.params['negative_prompt'],key=job.key+"-INPUT-negative_prompt",size=(30,1),tooltip="Enter different negative prompts to try separated by \"|\""),
            ]
        ],expand_x=True)
        
        #the frame with the prompt and the alias in it
        prompt_alias_list = []
        job.counters["prompt_alias"] = len(job.params['prompt_alias'])
        for i in range(job.counters["prompt_alias"]): #building alias rows from saved values
            alias = job.params['prompt_alias'][i]
            prompt_alias_list.append(DiffusersComparator.row_prompt_alias(job,i,alias["key"],alias["val"]))
        promptFrame = sg.Frame("Prompt",[
            [
                sg.Text("Template : ",tooltip="Choose the form your prompt should have, using [word] to test the values set for the alias \"word\""),
                sg.Input(job.params['prompt_template'],key=job.key+"-INPUT-prompt_template",size=(40,1),expand_x=True,tooltip="Choose the form your prompt should have, using [word] to test the values set for the alias \"word\""),
            ],
            [
                sg.Col(prompt_alias_list,key=job.key+"-HOOK-prompt_alias_list",expand_x=True) #the hook for more alias
            ],
            [
                sg.P(),
                sg.Button(image_filename="code/resources/images/plus_small.png",key=job.key+"-CALLBACK-prompt_alias_add",image_size=(20,20),image_subsample=4,button_color="white",pad=((10,5),(5,5)),tooltip="Add a new alias to the list."),
                sg.In("",key=job.key+"-CALLBACK-prompt_import",enable_events=True,visible=False),
                sg.FileBrowse("Import",key=job.key+"-BROWSE-prompt_import_browse",initial_folder=prompts_export_path,file_types=(('Prompt template files','*.prompt_template.json',),),visible=False),
                sg.Button(image_filename="code/resources/images/import_small.png",key=job.key+"-CALLBACK-prompt_import_image",image_size=(20,20),image_subsample=4,button_color="white",pad=(5,5),tooltip="Import a prompt template and the alias that goes with it from a .prompt_template.json file."),
                sg.In("",visible=False,key=job.key+"-CALLBACK-prompt_export",enable_events=True),
                sg.FileSaveAs(button_text="Export",key=job.key+"-BROWSE-prompt_export_browse",initial_folder=prompts_export_path,file_types=(('Prompt template files','*.prompt_template.json',),),visible=False),
                sg.Button(image_filename="code/resources/images/export_small.png",key=job.key+"-CALLBACK-prompt_export_image",image_size=(20,20),image_subsample=4,button_color="white",pad=(5,5),tooltip="Export the current prompt template and the alias that goes with it to a .prompt_template.json file."),
                sg.P(),
            ],
            [
                
            ]
        ],expand_x=True,expand_y=True)
        
        diffusers_list = []
        job.counters["diffusers_list"] = len(job.params['diffusers_list'])
        for i in range(job.counters["diffusers_list"]):
            diffusers_list.append(DiffusersComparator.row_diffusers(job,i,job.params['diffusers_list'][i]))
        modelsFrame = sg.Frame("Models",[
            [
                sg.T("Path to diffusers",tooltip="The sets of diffusers to compare should be listed here."),
                sg.In("",visible=False,key=job.key+"-CALLBACK-diffusers_add",enable_events=True),
                sg.FolderBrowse("Add",initial_folder='data/diffusers',key=job.key+"-BUTTON-diffusers_browse",visible=False),
                sg.Button(image_filename="code/resources/images/plus_small.png",image_size=(20,20),image_subsample=4,button_color="white",pad=(5,5),key=job.key+"-CALLBACK-diffusers_add_image-"+str(i),tooltip="Add a new set of diffusers to test to the list."),
            ],
            [
                sg.Col(diffusers_list,key=job.key+"-HOOK-diffusers_list") #the hook for more diffusers
            ]
        ],expand_y=True)
        
        return [
            titleRow,
            [
                sg.Col([
                    [
                        saveParametersFrame,
                        imageParametersFrame,
                    ],
                    [
                        variatingParametersFrame,
                        modelsFrame,
                    ],
                    [
                        promptFrame,
                    ],
                ],expand_x=True)
            ]
        ]
    #rows used during template generation
    def row_diffusers(job,i,value):
        path_parts = value.split("/")
        path_len = len(path_parts)
        simplified_value=path_parts[path_len-2]+"/"+path_parts[path_len-1]
        return [
            sg.T(simplified_value,tooltip=value+"\nClick to remove this set of diffusers from the list.",key=job.key+"-CALLBACK-diffusers_list_delete-"+str(i),enable_events=True)
        ]
    #rows used during template generation
    def row_prompt_alias(job,i,key,val):
        return [
            sg.In(key,key=job.key+"-CALLBACK-prompt_alias_key-"+str(i),size=(10,1),justification="center",enable_events=True,tooltip="An alias, a word that should be used in your prompt template inside []."),
            sg.In(val,key=job.key+"-CALLBACK-prompt_alias_val-"+str(i),size=(30,1),enable_events=True,expand_x=True,tooltip="The values that the alias should take, separated by \",\"."),
            sg.In("",visible=False,key=job.key+"-CALLBACK-prompt_alias_import-"+str(i),enable_events=True),
            sg.FileBrowse("Import",key=job.key+"-BROWSE-prompt_alias_import_browse-"+str(i),initial_folder=prompts_export_path,file_types=(('Alias files','*.alias.json',),),visible=False),
            sg.Button(image_filename="code/resources/images/import_small.png",image_size=(20,20),image_subsample=4,button_color="white",pad=(5,5),key=job.key+"-CALLBACK-prompt_alias_import_image-"+str(i),tooltip="Import an alias and its values from a .alias.json file."),
            sg.In("",visible=False,key=job.key+"-CALLBACK-prompt_alias_export-"+str(i),enable_events=True),
            sg.FileSaveAs(button_text="Export",key=job.key+"-BROWSE-prompt_alias_export_browse-"+str(i),initial_folder=prompts_export_path,file_types=(('Alias files','*.alias.json',),),visible=False),
            sg.Button(image_filename="code/resources/images/export_small.png",image_size=(20,20),image_subsample=4,button_color="white",pad=(5,5),key=job.key+"-CALLBACK-prompt_alias_export_image-"+str(i),tooltip="Export this alias and its values to a .alias.json file."),
            sg.Button(image_filename="code/resources/images/trash_small.png",image_size=(20,20),image_subsample=4,button_color="white",pad=(5,5),key=job.key+"-CALLBACK-prompt_alias_delete-"+str(i),tooltip="Remove this alias.")
        ]
    #does nothing useful for now outside of updating the title, the rest isn't different from loading it when saved
    def update_layout(job):
        window[job.key+"-CHECKBOX-active"].update(text=job.params['title'])
        window[job.key+"-TAB"].update(title=job.params['title'])
        
    #called when an event with -CALLBACK- as subevent[2] is received
    #necessary for some UI parts specific to that job
    def callback(job,callback_type,event,values):
    
        if callback_type == "prompt_export_image":
            window[job.key+"-BROWSE-prompt_export_browse"].click()
        if callback_type == "prompt_export":
            value = values[event]
            output=[]
            for i in range(len(job.params["prompt_alias"])):
                alias = job.params["prompt_alias"][i]
                if alias != None:
                    alias_data = DiffusersComparator.read_alias(job.key,i)
                    output.append({
                        "alias":alias_data["key"],
                        "values":alias_data["val"],
                    })
            promptFile = sg.UserSettings(filename=value)
            promptFile.set("prompt_template",window[job.key+"-INPUT-prompt_template"].get())
            promptFile.set("concept_list",output)
            promptFile.save()
            window['-STATUSBAR-']("Concept list exported as JSON.")
            
        if callback_type == "prompt_import_image":
            window[job.key+"-BROWSE-prompt_import_browse"].click()
        if callback_type == "prompt_import":
            value = values[event]
            promptFile = sg.UserSettings(filename=value)
            window[job.key+"-INPUT-prompt_template"].update(value=promptFile.get("prompt_template"))
            for i in range(len(job.params["prompt_alias"])):
               DiffusersComparator.prompt_alias_delete(job,i)
            concept_list = promptFile.get("concept_list")
            for i in range(len(concept_list)):
               DiffusersComparator.prompt_alias_add(job,concept_list[i]['alias'],concept_list[i]['values'])
            window['-STATUSBAR-']("Concept list imported from JSON.")
            
        if callback_type == "diffusers_add_image":
            window[job.key+"-BUTTON-diffusers_browse"].click()
            
        if callback_type == "diffusers_add":
            value = values[event]
            job.params['diffusers_list'].append(value)
            window.extend_layout(
                window[job.key+"-HOOK-diffusers_list"],
                [DiffusersComparator.row_diffusers(job,job.counters["diffusers_list"],value)]
            )
            job.counters["diffusers_list"] += 1
            
        if callback_type == "diffusers_list_delete":
            i = int(event.split("-")[4])
            window[event].hide_row()
            job.params['diffusers_list'][i] = None
            
        if callback_type == "prompt_alias_add":
            DiffusersComparator.prompt_alias_add(job,"","")
            
        if callback_type == "prompt_alias_delete":
            i = int(event.split("-")[4])
            DiffusersComparator.prompt_alias_delete(job,i)
            
        if callback_type == "prompt_alias_key":
            new_value = values[event]
            i = int(event.split("-")[4])
            prev_value = job.params['prompt_alias'][i]["key"]
            job.params['prompt_alias'][i]["key"]=new_value
            #we update the prompt live with change in alias keys
            prompt_template = window[job.key+"-INPUT-prompt_template"]
            new_prompt=prompt_template.get().replace("["+prev_value+"]","["+new_value+"]")
            prompt_template.update(value=new_prompt)
            
        if callback_type == "prompt_alias_val":
            value = values[event]
            i = int(event.split("-")[4])
            job.params['prompt_alias'][i]["val"]=value
            
        if callback_type == "prompt_alias_import_image":
            i = int(event.split("-")[4])
            window[job.key+"-BROWSE-prompt_alias_import_browse-"+str(i)].click()
            
        if callback_type == "prompt_alias_import":
            value = values[event]
            i = int(event.split("-")[4])
            aliasFile = sg.UserSettings(filename=value)
            window[job.key+"-CALLBACK-prompt_alias_key-"+str(i)].update(value=aliasFile.get("alias"))
            window[job.key+"-CALLBACK-prompt_alias_val-"+str(i)].update(value=aliasFile.get("values"))
            job.params["prompt_alias"][i] = {"key":aliasFile.get("alias"),"val":aliasFile.get("values")}
            window['-STATUSBAR-']("Alias imported from JSON.")
            
        if callback_type == "prompt_alias_export_image":
            i = int(event.split("-")[4])
            window[job.key+"-BROWSE-prompt_alias_export_browse-"+str(i)].click()
            
        if callback_type == "prompt_alias_export":
            value = values[event]
            i = int(event.split("-")[4])
            alias=DiffusersComparator.read_alias(job.key,i)
            aliasFile = sg.UserSettings(filename=value)
            aliasFile.set("alias",alias["key"])
            aliasFile.set("values",alias["val"])
            aliasFile.save()
            window['-STATUSBAR-']("Alias exported to JSON.")
            
    def read_alias(jobkey,i):
        return {
            "key": window[jobkey+"-CALLBACK-prompt_alias_key-"+str(i)].get(),
            "val": window[jobkey+"-CALLBACK-prompt_alias_val-"+str(i)].get()
        }
    def prompt_alias_add(job,key,val):
        job.params['prompt_alias'].append({"key":key,"val":val})
        window.extend_layout(
            window[job.key+"-HOOK-prompt_alias_list"],
            [DiffusersComparator.row_prompt_alias(job,job.counters["prompt_alias"],key,val)]
        )
        job.counters["prompt_alias"] += 1
    def prompt_alias_delete(job,i):
        window[job.key+"-CALLBACK-prompt_alias_delete-"+str(i)].hide_row()
        job.params['prompt_alias'][i] = None
    
    def save_params(params):
        output = params.copy()
        output["diffusers_list"] = [i for i in params["diffusers_list"] if i is not None]
        output["prompt_alias"] = [i for i in params["prompt_alias"] if i is not None]
        return output

    #layout parameters have autosave included and need a default value in the default_job_params
    def layout_parameters():
        return [
            ("title","INPUT"),
            ("active","CHECKBOX"),
            ("output","TEXT"),
            ("n_samples","SPIN"),
            ("batch_size","SPIN"),
            ("size","RADIO",["512","768","custom"]),
            ("height","INPUT"),
            ("width","INPUT"),
            ("scheduler","INPUT"),
            ("seed","INPUT"),
            ("cfgs","INPUT"),
            ("steps","INPUT"),
            ("negative_prompt","INPUT"),
            ("prompt_template","INPUT"),
            ("grid_height","SPIN"),
            ("grid_width","SPIN"),
        ]
    #all params used for a job of this type with their default values
    def default_job_params():
        return {
            'active':False,
            'output':os.getcwd()+'/output/images/',
            'save_grid':True,
            'grid_height':8,
            'grid_width':8,
            'save_pics':False,
            'size':"512",
            'height':"",
            'width':"",
            'n_samples':1,
            'batch_size':4,
            'scheduler':"euler_a",
            'seed':"-1",
            'cfgs':"7.5",
            'steps':"20",
            'negative_prompt':"",
            'diffusers_list':[],
            'prompt_template':"a [Color] [Subject]",
            'prompt_alias':[
                {"key":"Subject","val":"cat,dog"},
                {"key":"Color","val":"red,blue"},
            ],
        }
    
    def check_and_start(job):
        errors = []
        params = job.params
        
        if (not params['save_grid']) and (not params['save_pics']):
            errors.append("- You need to either save the grid or the pictures.")
            
        if (params['size'] == "custom") and ( (params['height'] == '') or (params['width'] == '') ):
            errors.append("- If you use custom size, you need to choose a height and width to go with it.")
            
        schedulers = params['scheduler'].split(',')
        for scheduler in schedulers:
            if not (scheduler in ["ddpm","ddim","pndm","lms","euler_a","euler","dpm"]):
                errors.append("- Scheduler "+scheduler+" not supported.")
                
        seeds = params['seed'].split(',')
        for seed in seeds:
            if (seed != "None"):
                try:
                    int(seed)
                except ValueError as error:
                    errors.append("- Seed \""+seed+"\" unsupported. It needs to be an integer or 'None'.")
                    
        cfgs = params['cfgs'].split(',')
        for cfg in cfgs:
            try:
                float(cfg)
            except ValueError as error:
                errors.append("- CFGS value \""+cfg+"\" unsupported. It needs to be a float value.")
                
        steps = params['steps'].split(',')
        for step in steps:
            try:
                int(step)
            except ValueError as error:
                errors.append("- Step value \""+step+"\" unsupported. It needs to be an integer.")
        
        if len(params['diffusers_list']) == 0:
            errors.append("- You need to choose at least one set of diffusers.")
        
        if len(errors) > 0:
            sg.popup_error("Can't start the job "+params["title"],"\n".join(errors))
        else:
            # if sg.popup_ok_cancel("Are you sure you want to start this job ?") == 'ok':
            return subprocess.Popen([executable, "code/scripts/doJob_DiffusersComparator.py","--jobJSON",job.saveJSON])
        return False
            

#creating alias folder for import/export function
prompts_export_path = "settings/prompts"
try:
    os.makedirs(prompts_export_path, exist_ok=True)
except OSError as error:
    print("")
        
#list of the types of jobs
TypesLayouts={
    "DiffusersComparator" : DiffusersComparator
}

# a job controls everything specific to that task and its UI
# this class is the bridge and interface to the different types of layouts
class Job:
    def __init__(self,i,type,fromParams=False):
        self.i=i
        self.type=type
        self.key="JOB-"+str(i)
        if not fromParams:
            self.params= TypesLayouts[type].default_job_params()
            self.params['title']="#"+str(i)
            self.params['active']=False
            self.saveJSON=self.key+"_"+str(len(os.listdir(settings_path)))+".queue.json"
            self.UserSettings = sg.UserSettings(filename=settings_path+"/"+self.saveJSON)
            self.save()
        else:
            self.UserSettings = sg.UserSettings(filename=settings_path+"/"+fromParams)
            self.params = TypesLayouts[type].default_job_params()
            savedParams = self.UserSettings.get("params")
            for k in savedParams:
                self.params[k]=savedParams[k]
            self.saveJSON=fromParams
        self.counters = {}
    def save(self):
        self.UserSettings.set("type",self.type)
        params = TypesLayouts[self.type].save_params(self.params)
        self.UserSettings.set("params",params)
        self.UserSettings.save()
    def layout_parameters(self):
        return TypesLayouts[self.type].layout_parameters()
    def update_layout(self):
        return TypesLayouts[self.type].update_layout(self)
    def layout_card(self):
        return TypesLayouts[self.type].layout_card(self)
    def layout_tab(self):
        return TypesLayouts[self.type].layout_tab(self)
    def callback(self,callback_type,event,values):
        TypesLayouts[self.type].callback(self,callback_type,event,values)
    def check_and_start(self):
        return TypesLayouts[self.type].check_and_start(self)

# the joblist is the Object that manages all jobs save/load and distributes events
# it also manages the queue
jobTotal=0
class JobList:
    def __init__(self,listKey,tabKey):
        self.listKey=listKey
        self.tabKey=tabKey
        self.list = []
        self.processList=[]
    def new(self,jobType,fromParams=False):
        global jobTotal
        jobTotal += 1
        newJob=Job(jobTotal,jobType,fromParams)
        self.list.append(newJob)
        window.extend_layout(window[self.listKey],newJob.layout_card())
        window[self.tabKey].add_tab(sg.Tab(
            title=newJob.params['title'],
            layout=[[sg.Col(
                newJob.layout_tab(),
                scrollable=True,vertical_scroll_only=True,
                expand_x=True,expand_y=True,
            )]],
            key=newJob.key+"-TAB",
            expand_y=True,expand_x=True,
        ))
        return newJob
    def get(self,i):
        return self.list[i-1]
    def saveChanges(self,i):
        job=self.get(i)
        for lp in job.layout_parameters():
            if lp[1] == "RADIO":
                for v in lp[2]:
                    if window[job.key+"-"+lp[1]+"-"+lp[0]+"-"+v].get():
                        newvalue = v
            else:
                newvalue=window[job.key+"-"+lp[1]+"-"+lp[0]].get()
            job.params[lp[0]]=newvalue
        job.update_layout()
        job.save()
        return job
    def check_and_start(self,i):
        job = jobs.saveChanges(i)
        processID = job.check_and_start()
        if processID:
            window[job.key+"-DO_JOB"].update(disabled=True)
            self.processList.append(processID)
            window['-STATUSBAR-']("Job is running")
        else:
            print("An error occured while starting the job.")
    def update_process(self):
        for i in range(len(self.processList)):
            poll = self.processList[i].poll()
            if not (poll is None):#job complete
                window[job.key+"-DO_JOB"].update(disabled=False)
                self.processList.pop(i)
                os.startfile(job.params['output'])
                window['-STATUSBAR-']("Job has ended")
    def deleteJob(self,i):
        job=self.get(i)
        self.list[i-1]=None
        window[job.key+"-TAB"](visible=False)
        window[job.key+"-CHECKBOX-active"].hide_row()
        filename=job.UserSettings.get_filename()
        os.rename(filename,filename.replace(".queue.json",".deleted.json"))
        
jobs = JobList("HOOK-jobqueue_col","HOOK-jobtabs_tabgroup")
    
# loading all the existing jobs
settings_path = "settings/jobqueue"
try:
  os.makedirs(settings_path, exist_ok=True)
except OSError as error:
    print("")
for file in os.listdir(settings_path):
    if file.endswith(".queue.json"):
        settings = sg.UserSettings(filename=settings_path+"/"+file)
        jobs.new(settings.get("type"),fromParams=file) #adding them to layout

#Event loop    
while True:
    event, values = window.read(timeout=500 if len(jobs.processList)>0 else None)
    if event == "__TIMEOUT__":
        jobs.update_process()
    else:
        if event is None:
            break
        elif event == sg.WIN_CLOSED:
            break
        elif event.find("::") != -1:
            event = event.split("::")[1]
            
        subevent = event.split('-')
        if devmode:
            print("Event : ",event)
        
        if subevent[0] == "JOBQUEUE":#jobqueue management
            if subevent[1]=="MENU":#top menu
                job = jobs.new(subevent[2])
                window['-STATUSBAR-']("New job created : "+job.params['title'])
            elif subevent[1]=="DROPDOWN":#dropdown on top of the jobs list
                jobType = values[event].replace(" ","")
                if TypesLayouts[jobType]:
                    job = jobs.new(jobType)
                    window[event].update(set_to_index=0)
                    window['-STATUSBAR-']("New job created : "+job.params['title'])
        
        elif subevent[0] == "JOB": #tabs management
            i = int(subevent[1])
            job = jobs.get(i)
            if subevent[2]=="SAVE_CHANGES":#save button in tab
                job = jobs.saveChanges(i)
                window['-STATUSBAR-']("Job saved as "+job.saveJSON)
            elif subevent[2]=="DELETE":#trash button in tab
                file = settings_path+"/"+(job.saveJSON)
                if sg.popup_ok_cancel("Are you sure you want to delete this job from the queue ?"):
                    jobs.deleteJob(i)
                    window['-STATUSBAR-']("Job deleted")
            elif subevent[2] == "CALLBACK":
                job.callback(subevent[3],event,values)
            elif subevent[2] == "DO_JOB":
                jobs.check_and_start(i)
window.close()