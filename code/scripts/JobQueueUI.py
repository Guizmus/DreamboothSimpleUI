import os
from sys import executable, path
import PySimpleGUI as sg
import subprocess
path.insert(1, 'code/scripts/lib/')
from DiffusersComparator import DiffusersComparator

devmode = False
# devmode = True
visivility_queue = devmode

sg.theme('Dark Black')
# innerTheme='Dark Green 3'

# sg.theme_previewer()

#list of the types of jobs
TypesLayouts={
    "DiffusersComparator" : DiffusersComparator
}
dropdown_options = ['-NEW JOB-']
menu_options = []

for type in TypesLayouts:
    dropdown_options.append(type)
    menu_options.append(type+"::JOBQUEUE-MENU-"+type)


#general UI layout
JobQueue=sg.Col([
    [sg.Text("Job Queue")],
    [sg.Combo(dropdown_options,default_value='-NEW JOB-',enable_events=True,key="JOBQUEUE-DROPDOWN",size=(15,1))],
],key="HOOK-jobqueue_col",visible=visivility_queue)

TabZone=[[
    sg.TabGroup([[]],key="HOOK-jobtabs_tabgroup",tab_location="topleft",expand_y=True,expand_x=True,size=(590,500))
]]

menu_def=[['&New job',menu_options]]


  
layout = [
    [sg.Menu(menu_def)],
    [
        sg.vtop(JobQueue),
        sg.vtop(sg.Col(TabZone,expand_y=True,expand_x=True))
    ],
    [sg.VPush()],
    [sg.StatusBar("",key='-STATUSBAR-',expand_x=True,size=(74,1))]
]

#we initialize the window empty and force loading to simplify UI building a little
window = sg.Window('Training job queue', layout, finalize=True)
for type in TypesLayouts:
    TypesLayouts[type].set_window(window)
    
# a job controls everything specific to that task and its UI
# this class is the bridge and interface to the different types of layouts
class Job:
    def __init__(self,i,type,fromParams=False):
        self.i=i
        self.type=type
        self.key="JOB-"+str(i)
        if not fromParams:
            self.params= TypesLayouts[type].default_job_params()
            self.params['title']=type
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