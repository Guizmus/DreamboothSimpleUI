from os import path, startfile
from time import sleep
import subprocess
import PySimpleGUI as sg
sg.theme('Topanga')

scripts = [
    ["ShivamShrirao","code\\scripts\\installShivam.bat","code\\resources\\shivam\\"],
    ["1.5 diffusers with updated VAE","code\\scripts\\installDiffusers1-5.bat","data\\diffusers\\SD-1.5-VAE\\"],
    ["2.0 diffusers (512)","code\\scripts\\installDiffusers2-0.bat","data\\diffusers\\SD-2.0\\"],
    ["Example run dataset","code\\scripts\\installExample.bat","data\\datasets\\example\\"]
]

c1=[]
c2=[]
i = 0
for script in scripts:
    isInstalled = path.isdir(script[2])
    c1.append([
        sg.Checkbox(script[0],key='-INSTALL-'+str(i)+'-',default=isInstalled,disabled=isInstalled)
    ])
    c2.append([
        sg.Button("Open folder",key='-OPEN-'+str(i)+'-',disabled=not isInstalled)
    ])
    i = i + 1
layout=[[sg.Col(c1),sg.Col(c2)]]
layout.append([
    sg.Button("Install checked resources",key='-START-INSTALL-')
]) 
layout.append([
    [sg.StatusBar("",key='-STATUSBAR-',size=(40,1))]
])

window = sg.Window('DreamboothSimpleUI Installer', layout)

while True:
    event, values = window.read()
    if event != None:
        subevent = event.split('-')
        
        if subevent[1] == "OPEN":
            script = scripts[int(subevent[2])]
            startfile(script[2])
                
    if event == "-START-INSTALL-":
        i=0
        confirmtext="Are you sure you want to install :\n"
        installlist=[]
        for script in scripts:
            isInstalled = path.isdir(script[2])
            isChecked = window['-INSTALL-'+str(i)+'-'].get()
            if (not isInstalled) and isChecked:
                confirmtext = confirmtext+"- "+script[0]+"\n"
                installlist.append(i)
            i=i+1
        if len(installlist) > 0:
            if (sg.popup_yes_no(confirmtext,title="Intall confim")) == "Yes":
                window['-START-INSTALL-'](disabled=True)
                report = ""
                for i in installlist:
                    script=scripts[i]
                    print("Executing script : "+script[1])
                    status = "Installing "+script[0]
                    currentInstall = subprocess.Popen([script[1]])
                    j=""
                    while currentInstall.poll() == None:
                    # while True:
                        j=j+"."
                        if len(j)>3:
                            j="."
                        window['-STATUSBAR-'](status+j)
                        window.refresh()
                        sleep(1)
                    if path.isdir(script[2]):
                        window['-INSTALL-'+str(i)+'-'](disabled=True,value=True)
                        window['-OPEN-'+str(i)+'-'](disabled=False)
                        window['-STATUSBAR-']("Installed "+script[0])
                        report = report + script[0]+":Success "
                    else:
                        window['-STATUSBAR-']("Failed installation : "+script[0])
                        report = report + script[0]+":Fail "
                    window.refresh()
                window['-START-INSTALL-'](disabled=False)
                window['-STATUSBAR-'](report)
                window.refresh()
        else:
            sg.popup("Nothing to install.\nCheck the boxes in front of the items you want to install first.",title="Nothing to install")
            
    if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
        break

window.close()