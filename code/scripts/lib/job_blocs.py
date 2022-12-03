import PySimpleGUI as sg

class Bloc:
    def browse_txt(job,param_name,title,initial_directory,visible_input=True,as_line=True,save_input=True,expand_x=True,size=10,separated=False):
        size = (size,1)
        out = [sg.T(title)]
        if separated:
            out.append(sg.P())
        out += [
            sg.In("" if not save_input else job.params[param_name],key=job.key+"-INPUT-"+param_name,visible=visible_input,size=size,expand_x=expand_x),
            sg.FolderBrowse("Browse",initial_folder=initial_directory),
        ]
        return out if as_line else sg.Col([out])
    def browse(job,param_name,title,initial_directory,visible_input=True,as_line=True,save_input=True,expand_x=True,size=10,separated=False):
        size = (size,1)
        out = [sg.In("" if not save_input else job.params[param_name],key=job.key+"-INPUT-"+param_name,visible=visible_input,size=size,expand_x=expand_x)]
        if separated:
            out.append(sg.P())
        out += [
            sg.FolderBrowse(title,initial_folder=initial_directory),
        ]
        return out if as_line else sg.Col([out])
    def input(job,param_name,title,as_line=True,expand_x=True,size=10,separated=False):
        size = (size,1)
        out = [sg.T(title)]
        if separated:
            out.append(sg.P())
        out += [
            sg.In(job.params[param_name],key=job.key+"-INPUT-"+param_name,size=size,expand_x=expand_x),
        ]
        return out if as_line else sg.Col([out])
    def checkbox(job,param_name,title,as_line=True,expand_x=True):
        out = sg.Checkbox(title,key=job.key+"-CHECKBOX-"+param_name,default=job.params[param_name],expand_x=expand_x)
        return [out] if as_line else out
    def button(job,param_name,title,as_line=True,expand_x=False):
        out = sg.Button(title,key=job.key+"-BUTTON-"+param_name,expand_x=expand_x)
        return [out] if as_line else out
    def range(job,param_name,title,r,as_line=True,expand_x=True,separated=False):
        out = [sg.T(title)]
        if separated:
            out.append(sg.P())
        out += [
            sg.Spin(r,initial_value=job.params[param_name],key=job.key+"-INPUT-"+param_name,expand_x=expand_x),
        ]
        return out if as_line else sg.Col([out])
    def dropdown(job,param_name,title,values,as_line=True,expand_x=True,separated=False):
        out = [sg.T(title)]
        if separated:
            out.append(sg.P())
        out += [
            sg.Combo(values,default_value=job.params[param_name],enable_events=True,key=job.key+"-DROPDOWN-"+param_name,expand_x=expand_x)
        ]
        return out if as_line else sg.Col([out])
    def hook(job,param_name,as_line=True,expand_x=True):
        out = sg.Col([[]],key=job.key+"-HOOK-"+param_name,expand_x=expand_x)
        return [out] if as_line else out