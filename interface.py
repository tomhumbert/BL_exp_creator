from ctypes import alignment
from sqlite3 import enable_callback_tracebacks
import PySimpleGUI as sg
import hypo_hyper_finder as hh
import tasklist_creator as tc
import os, shutil

# ------ Menu Definition ------ #      
menu_def = [['File', ['New Experiment', 'Open Experiment', 'Save + Exit', 'Exit']],      
                ['View', ['Overview', 'Other view', 'About']] ]      

def small_text(text):
    return sg.Text(text,  
                    justification='left',
                    font=('Courier 11'),
                    p=2,
                    auto_size_text=True )

def med_text(text, width = 25, key = None):
    words = text.split(' ')
    i = 1
    next_len = 0
    a_text = str.capitalize(words[0])
    lettercount = len(a_text)
    not_done = True
    if len(words) > 1:
        while not_done:
            try:
                next_len = len(words[i+1])
            except:
                not_done = False
            if next_len + lettercount > width:
                a_text += '\n'
                lettercount = 0
            else:
                a_text += ' '
            
            a_text +=  words[i]
            lettercount += len(words[i])
            i += 1

    return sg.Text(a_text, 
                    justification='left',
                    font=('Courier 14'),
                    p=2,
                    auto_size_text=True,
                    k=key
                     )

def big_text(text, key=None):
    words = text.split(' ')
    i = 1
    next_len = 0
    a_text = str.capitalize(words[0])
    lettercount = len(a_text)
    not_done = True
    if len(words) > 1:
        while not_done:
            try:
                next_len = len(words[i+1])
            except:
                not_done = False
            if next_len + lettercount > width:
                a_text += '\n'
                lettercount = 0
            else:
                a_text += ' '
            
            a_text +=  words[i]
            lettercount += len(words[i])
            i += 1
    return sg.Text(a_text,  
                    justification='left',
                    font=('Courier 20'),
                    p=2,
                    auto_size_text=True,
                    k=key )

def make_defbox(hyper,bl,synonyms, bl_def, hypo, hypo_syns, hypo_def, cert):
    hyper_layout = [
        [small_text(hyper)]
    ]
    bl_layout = [
        [big_text(bl)],
        [small_text("Expert annotator agreement:")],
        [med_text(f"Full agreement: {cert}")],
        [small_text("Synonyms:")],
        [med_text(synonyms)],
        [small_text("Definition:")],
        [med_text(bl_def)]
    ]
    hypo_layout = [
        [big_text(hypo, key='hypo')],
        [small_text("Synonyms:")],
        [med_text(hypo_syns, key='hypo_syns')],
        [small_text("Definition:")],
        [med_text(hypo_def, key="hypo_def")]
    ]

    hyperbox = sg.Frame("Hypernym", hyper_layout, font='Courier 12',expand_x=True, k='hyperbox',p=5,relief='sunken')
    blbox = False
    blbox = sg.Frame("Basic Level", bl_layout, font='Courier 12',  expand_y=True,expand_x=True, k='blbox',p=5,relief='sunken')
    hypobox = sg.Frame("Selected Hyponym", hypo_layout, font='Courier 12', expand_y=True,expand_x=True, k='hypobox',p=5,relief='sunken')
    defbox = sg.Column([[hyperbox],[blbox],[hypobox],[sg.Sizer(300,1)]], expand_y=True, expand_x=True)
    return defbox


def make_tree(tree, tree_data, root, i):
    text = tree_data[0].name()
    info = tree_data[0].definition()
    a_tree = tree
    e=i
    a_tree.insert(root, i, text, [info])
    
    for j in range(1,len(tree_data)):
        child = tree_data[j]
        e = e+1
        a_tree, e = make_tree(a_tree, child, i, e)
        
    return a_tree, e

def make_treebox(tree_data):
    tree = sg.TreeData()
    tree, tree_count = make_tree(tree, tree_data,'' ,0)
    box_layout = [
        [sg.Tree(tree, 
                expand_x=True,
                expand_y=True, 
                headings= ['Information',], 
                col0_heading='Taxonomy',
                enable_events=True,
                justification='left',
                show_expanded = True,
                font='Courier 10',
                auto_size_columns=True,
                k = tree),]
    ]
    treebox = sg.Frame('Hierarchy', box_layout, font='Courier 12', expand_y=True, expand_x= True,p=5)
    return treebox, tree

def make_actionbox():
    box_layout = [
        [sg.Button('Select Image', key='select_img', p=5), sg.Button('Continue', p=5)],
        [sg.Button('Save + Exit', p=5),sg.Button('Remove', p=5)]
    ]
    actbox = sg.Frame('Image + Actions', box_layout, font='Courier 12',  size=(500,100), expand_x=True,p=5)
    return actbox

def goto_overview(window, project):
    layout= [
        [sg.Menu(menu_def, key='menu')],
        [med_text("This is the overview of all the concepts. Click continue to simply continue the ongoing effort, or select a row and click Edit to change that specific entry.", 50)],
        [sg.Table(project.get_df_as_list(),
                            headings=["hypernym","bl","hyponym","hyponym_img"],
                            col_widths=10,
                            font=('Courier 12'),
                            expand_x= True,
                            expand_y=True,
                            enable_events=True,
                            p=2,
                            vertical_scroll_only=True,
                            justification='left',
                            k='table' )], 
        [sg.Button('Continue', k='o_cont'), sg.Button('Edit')]
        ]
    window.close()
    new_window = sg.Window("BLEXP Creator OVERVIEW", layout, default_element_size=(12, 1),auto_size_text=False, auto_size_buttons=False, default_button_element_size=(12, 1),size =(800,600), finalize=True)
    new_window.force_focus()
    return new_window

def goto_annotate(window, project):
    #index number of next item to be annotated
    info = project.get_def_info()
    hyper,bl_syn,bl_def,syns,bl_name, hypo, hypo_img, hypo_syns, hypo_def, certainty = str(info[0]),str(info[1]),str(info[2]),str(info[3]), str(info[4]), str(info[5]), str(info[6]), str(info[7]), str(info[8]), str(info[9])
    treedata = project.get_tree(bl_syn)

    img = os.path.join(project.cwd, "images", hypo_img)
    defbox = make_defbox(hyper,bl_name,syns,bl_def, hypo, hypo_syns, hypo_def, certainty)
    treebox, tree = make_treebox(treedata)
    actbox = make_actionbox()
    layout = [
        [sg.Menu(menu_def, key='menu')],
        [defbox, sg.Column([[treebox], [sg.Image(img,subsample=4,s=(100,100)),actbox],[sg.Sizer(400,1)]], expand_y=True, expand_x=True, justification='right')]
    ]
    window.close()
    new_window = sg.Window("BLEXP Creator Annotator", layout, default_element_size=(12, 1),auto_size_text=False, auto_size_buttons=False, default_button_element_size=(12, 1),size =(1000,600), finalize=True, resizable=True)
    new_window.force_focus()
    return new_window, tree

def main():
    sg.theme('DarkTeal6')      
    sg.set_options(element_padding=(0, 0))

    # +++++++++++++++++ Global Values +++++++++++++++++ #
    cwd = os.getcwd()
    project = False
    window = False

    # ------ Launch GUI Defintion ------ #      
    launch_layout = [
        [sg.Text("This is the Rosch 7 Experiment Creator tool. Please select an ongoing project or start a new one.", 
                    p=5, 
                    relief='sunken', 
                    expand_x=True, 
                    expand_y=True)],      
        [sg.Input(default_text=cwd, expand_x=True, p=2, k="dir", enable_events=True),sg.Button('Browse', key='browse', p=5)],
        [sg.Button('Open Experiment', p=2), sg.Button('New Experiment', p=2)]      
             ]  

    # --- Launch Window --- #
    window = sg.Window("B.L.EXP. Creator LAUNCHER", launch_layout, size=(600,100), default_element_size=(12, 1), auto_size_text=False, auto_size_buttons=False, default_button_element_size=(12, 1), finalize=True)
    window.force_focus()   

    # ------ Loop & Process button menu choices ------ #      
    while True:      
        event, values = window.read()     
        print("EVENT:",event,'\n\nVALUES:',values, '\n--------------\n\n') 
        current_hypo_tree = {}
        if event == sg.WIN_CLOSED or event == 'Exit':      
            break      
        
        # ------ Process menu choices ------ #     
        if event == 'About':      
            sg.popup('Version 1.0', 'Made by Tom Humbert at VU Amsterdam', title='About this program')  

        elif event == "table":
            index = values["table"][0]

        elif event == "Edit":
            try:
                index = values["table"][0]
                project.set_last_stored_pos(index)
                window, current_hypo_tree = goto_annotate(window, project)
            except:
                sg.PopupAnnoying("Select a row first!")

        elif type(event) == sg.TreeData:
            key = list(values.keys())[1]
            index=values[key][0]
            elements = [item.strip().split(':') for item in str(key).split("\n")]
            elements = dict([[item.strip() for item in group] for group in elements])
            selection = elements[str(index)].split(' ')[0]
            project.add_hypo(selection)
            info = project.get_hypo_info()
            hypo, syns, hypodef = str(info[0]),str(info[1]), str(info[2])
            window['hypo'].Update(hypo)
            window['hypo_syns'].Update(syns)
            window['hypo_def'].Update(hypodef)
            
        elif event == 'dir':
            event, values = window.read() 

        elif event == 'browse':
            p = sg.popup_get_folder("Choose folder", default_path=cwd, no_window=True)
            window.find_element('dir').Update(value=p)
            window.force_focus()

        elif event == 'New Experiment':        
            cwd = window.find_element('dir').Get()
            #pop-up asking for project name
            project_id = sg.popup_get_text("What would you like to call this project? The main CSV file will be called that way and the project folder will be called 'Rosch7_' + the name you enter here.")
            project = hh.BL_EXP(project_id, cwd)

            bl_input_filepath = sg.popup_get_file("Please select now the input file, containing the list of BL concepts to be evaluated. (2 columns; bl name and certainty)")
            project.initial_load(bl_input_filepath)

            window = goto_overview(window, project)

        elif event == 'Open Experiment':
            cwd = window.find_element('dir').Get()
            identifier = os.path.split(cwd)[1]
            identifier = identifier[7::]
            project = hh.BL_EXP(identifier, cwd, is_load=True)

            window = goto_overview(window, project)
            
        elif event == 'Save + Exit':
            project.store()
            break

        elif event == 'Overview':
            window = goto_overview(window, project)
            
        elif event == "o_cont":
            window, current_hypo_tree = goto_annotate(window, project)
            #print(current_hypo_tree)

        elif event == 'select_img':
            img_name = project.get_hypo_info()[0] + ".png"
            img_src = sg.popup_get_file("Select the image file.","Image Selection",project.cwd, "png")
            if len(img_src) > 0:
                img_dest = os.path.join(project.cwd, "images", img_name)
                shutil.copy(img_src, img_dest)
                project.add_img(img_name)
            window.refresh()

        elif event == "Remove":
            project.remove(project.last)
            window, current_hypo_tree = goto_annotate(window, project)

        elif event == "Continue":
            project.next()
            window, current_hypo_tree = goto_annotate(window, project)

if __name__ == "__main__":
    main()