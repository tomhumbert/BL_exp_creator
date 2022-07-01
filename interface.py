import PySimpleGUI as sg
import hypo_hyper_finder as hh
import tasklist_creator as tc
import os

# ------ Menu Definition ------ #      
menu_def = [['File', ['New Experiment', 'Open Experiment', 'Save + Exit', 'Exit']],      
                ['View', ['Overview', 'Other view', 'About']] ]      

def check_savefile():
    return False

def load_rows():
    return rows

def small_text(text):
    return sg.Text(text,  
                    justification='left', 
                    expand_x=True,
                    font=('Courier 12'),
                    p=2 )

def med_text(text):
    return sg.Text(text, 
                    justification='left', 
                    expand_x=True,
                    font=('Courier 17'),
                    p=2 )

def big_text(text):
    return sg.Text(text,  
                    justification='left', 
                    expand_x=True,
                    font=('Courier 24'),
                    p=2 )

def make_defbox(hyper,bl,synonyms, bl_def):
    box_layout = [
        [small_text("Hypernym: ")],
        [small_text(hyper)],
        [small_text("Basic Level:")],
        [big_text(bl)],
        [small_text("Synonyms:")],
        [med_text(synonyms)],
        [small_text("Definition:")],
        [med_text(bl_def)]
    ]
    defbox = sg.Frame('Concept definition', box_layout, font='Courier 12', title_color='blue', size=(300,600))
    return defbox

def make_tree(project, root):
    tree = sg.TreeData()
    children = project.get_tree(root)
    tree.insert('', 0, f"{root}",[])
    
    for child in children:
        if type(child) == list: 
            c = child.name()
            tree.insert(0, c, c, [])
        else:
           pass 

    print(tree)
    return tree

def make_treebox(project, bl):
    tree = make_tree(project, bl)
    box_layout = [
        [sg.Tree(tree)]
    ]
    treebox = sg.Frame('Hierarchy', box_layout, font='Courier 12', title_color='blue', size=(500,400))
    return treebox

def make_actionbox():
    box_layout = [
        [sg.Input(default_text="Select an image for the chosen hyponym", expand_x=True, p=2, k="dir", enable_events=True),sg.Button('Browse', key='browse', p=2)],
        [sg.Button('Continue', p=2), sg.Button('Save + Exit', p=2)]
    ]
    actbox = defbox = sg.Frame('Image + Actions', box_layout, font='Courier 12', title_color='blue', size=(500,200))
    return actbox

def goto_overview(window, project):
    layout= [
        [sg.Menu(menu_def, key='menu')],
        [sg.Table(project.get_df_as_list(),
                            headings=["hypernym","bl","hyponym","hyponym_img"],
                            col_widths=10, 
                            background_color='white', 
                            font=('Courier 12'),
                            expand_x= True,
                            expand_y=True,
                            enable_events=True,
                            p=2,
                            vertical_scroll_only=True,
                            justification='left',
                            k='table' )], 
        [med_text("This is the overview of all the concepts.\nClick continue to simply continue the ongoing effort,\nor select a row and click Edit to change\nthat specific entry")],
        [sg.Button('Continue', k='o_cont'), sg.Button('Edit')]
        ]
    window.close()
    new_window = sg.Window("BLEXP Creator OVERVIEW", layout, default_element_size=(12, 1),auto_size_text=False, auto_size_buttons=False, default_button_element_size=(12, 1),size =(800,600), finalize=True)
    new_window.force_focus()
    return new_window

def goto_annotate(window, project):
    #index number of next item to be annotated
    tobe_annotated = project.next()
    info = project.get_bl_info(tobe_annotated)
    hyper,bl,bl_def,syns = str(info[0]),str(info[1]),str(info[2]),str(info[3])
    print(bl)

    defbox = make_defbox(hyper,bl,syns,bl_def)
    treebox = make_treebox(project, bl)
    actbox = make_actionbox()
    layout = [
        [sg.Menu(menu_def, key='menu')],
        [defbox, sg.Column([[treebox], [actbox]])]
        
    ]

    window.close()
    new_window = sg.Window("BLEXP Creator Annotator", layout, default_element_size=(12, 1),auto_size_text=False, auto_size_buttons=False, default_button_element_size=(12, 1),size =(800,600), finalize=True)
    new_window.force_focus()
    return new_window

def main():
    sg.theme('LightGreen')      
    sg.set_options(element_padding=(0, 0))

    # +++++++++++++++++ Global Values +++++++++++++++++ #
    cwd = os.getcwd()
    project = False
    window = False

    # ------ Launch GUI Defintion ------ #      
    launch_layout = [
        [sg.Text("This is the Rosch 7 Experiment Creator tool. Please select an ongoing project or start a new one.", 
                    p=2, 
                    relief='sunken', 
                    expand_x=True, 
                    expand_y=True)],      
        [sg.Input(default_text=cwd, expand_x=True, p=2, k="dir", enable_events=True),sg.Button('Browse', key='browse', p=2)],
        [sg.VerticalSeparator(p=2, color='white')],
        [sg.Button('Open Experiment', p=2), sg.Button('New Experiment', p=2)]      
             ]  

    # --- Launch Window --- #
    window = sg.Window("B.L.EXP. Creator LAUNCHER", launch_layout, size=(600,100), default_element_size=(12, 1), auto_size_text=False, auto_size_buttons=False, default_button_element_size=(12, 1), finalize=True)
    window.force_focus()   

    # ------ Loop & Process button menu choices ------ #      
    while True:      
        event, values = window.read()      
        if event == sg.WIN_CLOSED or event == 'Exit':      
            break      
        
        # ------ Process menu choices ------ #      
        if event == 'About':      
            sg.popup('Version 1.0', 'Made by Tom Humbert at VU Amsterdam', title='About this program')  

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
            print(cwd)
            identifier = os.path.split(cwd)[1]
            print(identifier)
            identifier = identifier[7::]
            project = hh.BL_EXP(identifier, cwd, is_load=True)

            window = goto_overview(window, project)
            
        elif event == 'Save + Exit':
            project.store()
            break

        elif event == 'Overview':
            window = goto_overview(window, project)
            
        elif event == "o_cont":
            window = goto_annotate(window, project)

if __name__ == "__main__":
    main()