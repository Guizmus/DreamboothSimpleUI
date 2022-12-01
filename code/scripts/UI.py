from os import path, startfile
import subprocess
import PySimpleGUI as sg

sg.theme('Dark Black')

scripts = [
    ["Training UI : Diffusers Comparison","code\\scripts\\installDiffusers.bat","code\\resources\\diffusers\\"],
    ["Training : ShivamShrirao","code\\scripts\\installShivam.bat","code\\resources\\shivam\\"],
    ["Training : EveryDream","code\\scripts\\installEveryDream.bat","code\\resources\\everydream\\"],
    ["Diffusers : 1.5 diffusers with updated VAE","code\\scripts\\installDiffusers1-5.bat","data\\diffusers\\SD-1.5-VAE\\"],
    ["Diffusers : 2.0 diffusers (512)","code\\scripts\\installDiffusers2-0-512.bat","data\\diffusers\\SD-2.0-512\\"],
    ["Diffusers : 2.0 diffusers (768)","code\\scripts\\installDiffusers2-0-768.bat","data\\diffusers\\SD-2.0-768\\"],
    ["Diffusers : 2.0 diffusers (4xUp)","code\\scripts\\installDiffusers2-0-4xUpscaler.bat","data\\diffusers\\SD-2.0-4xUpscaler\\"],
    ["Example run dataset","code\\scripts\\installExample.bat","data\\datasets\\example\\"],
]

c1=[]
c2=[]
i = 0
for script in scripts:
    isInstalled = path.isdir(script[2])
    c1.append([
        sg.Checkbox(script[0],key='INSTALL-'+str(i),default=isInstalled,disabled=isInstalled)
    ])
    c2.append([
        sg.Button("Open folder",key='OPEN-'+str(i),disabled=not isInstalled)
    ])
    i = i + 1
layout=[[sg.Col(c1),sg.Col(c2)]]
layout.append([
    sg.Button("Install checked resources",key='START')
]) 
layout.append([
    [sg.StatusBar("",key='STATUSBAR',size=(40,1))]
])

window = sg.Window('DreamboothSimpleUI Installer', layout)

runningInstall=False
currentProcess=None
currentScript=0
tried_jobs = []
while True:
    event, values = window.read(timeout=500 if runningInstall else None)
    if (event == None) or (event == sg.WIN_CLOSED):
        break
    
    subevent = event.split('-')
    if subevent[0] == "OPEN":
        script = scripts[int(subevent[1])]
        startfile(script[2])
    elif subevent[0] == "START":
        runningInstall=True
        window['START'](disabled=True)
        
    if runningInstall:
        if not (currentProcess is None): #if a process is running
            if not (currentProcess.poll() is None):
                tried_jobs.append(currentScript)
                if path.isdir(scripts[currentScript][2]):
                    window['INSTALL-'+str(currentScript)](disabled=True,value=True)
                    window['OPEN-'+str(currentScript)](disabled=False)
                else:
                    window['INSTALL-'+str(currentScript)](disabled=False,value=False)
                    window['STATUSBAR']("Install failed : "+scripts[currentScript][0])
                currentProcess = None
                currentScript = 0
        if currentProcess is None: #if no process is running
            next_script = None
            for i in range(len(scripts)):
                script = scripts[i]
                if (window['INSTALL-'+str(i)].get()) and not i in tried_jobs:
                    isInstalled = path.isdir(script[2])
                    if not isInstalled:
                        next_script = i
                        break
            if next_script is None:#nothing to install
                runningInstall=False
                tried_jobs = []
                window['START'](disabled=False)
            else:
                currentScript = next_script
                window['INSTALL-'+str(currentScript)](disabled=True)
                window['STATUSBAR']("Installing  "+scripts[currentScript][0])
                currentProcess = subprocess.Popen([scripts[currentScript][1]])

window.close()