from nltk.corpus import wordnet as wn
import pandas as pd
import numpy as np
from colorama import Fore, Back, Style
import sys, os, re

#=============================================================================
# Classes
#=============================================================================
class synset:
    def __init__(self):
        pass

class BL_EXP:
    pre = "Rosch7_"
    id = ""
    df = False
    cwd = os.path.abspath(".")
    exp_triplets = []
    one_hypo_per_bl = True
    last = "awl.n.01"

    def __init__(self, identifier, cwd, is_load = False):
        self.id = identifier
        if is_load:
            try:
                self.df = pd.read_csv(os.path.join(cwd, self.id+".csv"))
            except:
                raise Exception("This is not a valid project folder")
            self.cwd = cwd

        elif os.path.isdir(os.path.join(cwd, self.pre+self.id)):
            self.cwd = os.path.join(cwd, self.pre+self.id)
            self.df = pd.read_csv(os.path.join(self.cwd, self.id+".csv"))

        else:
            self.cwd = os.path.join(cwd, self.pre+self.id)
            os.mkdir(self.cwd)
        return None

    def add_hypo(self, hypo):
        ind = self.get_bl_index(self.last)
        self.df.at[ind,'hyponym'] = hypo
        self.df.at[ind,'hyponym_def'] = wn.synset(hypo).definition()
        return True

    def initial_load(self, BLlist_filepath):
        ret = False
        input = pd.read_csv(BLlist_filepath)
        if  self.create_new_df(input):
            self.store()
            ret =  True
        else:
            raise Exception("The initial dataframe creation failed")
        return ret

    def create_new_df(self, bl_list):
        l = len(bl_list.index)
        empty_col = ['missing' for i in range(l)]
        cols = {"hypernym":bl_list.get('hyper').tolist(), 
                "bl":bl_list.get('synset').tolist(),
                "bl_name":empty_col,
                "bl_certainty":bl_list.get('bl_certain').tolist(), 
                "hyponym":empty_col, 
                "hypernym_def":empty_col, 
                "bl_def":empty_col, 
                "hyponym_def":empty_col, 
                "hyponym_img":empty_col}
        try:
            self.df = pd.DataFrame(data=cols).astype('string')
            print(self.df)
            self.fill_df_generic()
        except:
            raise Exception('Dataframe creation failed.')
        return True

    def fill_df_generic(self):
        self.last = self.df.at[0,'bl']
        for i in range(len(self.df)):
            bl = self.df.at[i,'bl']
            syn = wn.synset(bl)
            name = syn.lemma_names()[0]
            bldef = syn.definition()
            self.df.at[i,'bl_name'] = name
            self.df.at[i,'bl_def'] = bldef
        return True

    def store(self):
        '''Takes the current dataframe and new filename and stores the dataframe in the working directory. Returns True.'''
        self.df.to_csv(os.path.join(self.cwd, self.id+".csv"))
        return True

    def get_df_as_list(self):
        table = self.df.loc[:,["hypernym","bl","hyponym","hyponym_img"]].to_numpy().tolist()
        return table

    def next(self):
        last_index = self.get_bl_index(self.last)
        index = last_index+1
        self.last = self.df["bl"][index]
        return self.last

    def get_def_info(self):
        index = self.get_bl_index(self.last)
        row = self.df.iloc[[index]].to_dict()
        hyper = list(row.get('hypernym').values())[0]
        bl_name = list(row.get('bl_name').values())[0]
        bl_syn = list(row.get('bl').values())[0]
        bl_def = list(row.get('bl_def').values())[0]
        syns = wn.synset(bl_syn).lemma_names()
        self.last = bl_syn
        return [hyper,bl_syn,bl_def,syns,bl_name]

    def get_hypo_info(self):
        index = self.get_bl_index(self.last)
        row = self.df.iloc[[index]].to_dict()
        hypo = list(row.get('hyponym').values())[0]
        hypodef = list(row.get('hyponym_def').values())[0]
        print(hypo)
        syns = wn.synset(hypo).lemma_names()
        return [hypo, syns, hypodef]

    def get_children(self, name):
        syn = get_synset(name)
        children = [str(hypo.name()) for hypo in syn.hyponyms()]
        return children


    def get_tree(self, root):
        tree = wn.synset(root).tree(lambda s:s.hyponyms())
        return tree

    def get_bl_index(self, name):
        index = self.df.index[self.df['bl']==name].tolist()[0]
        return index

    def remove(self, bl_name):
        index = self.get_bl_index(bl_name)
        self.df = self.df.drop([index])
        self.last = self.df["bl"][index+1]
        print(self.last)
        return True

#=============================================================================
# Functions
#=============================================================================

def get_synset(name):
    '''Takes full synset name string. E.g. "apple.n.01".
    Returns synset structure. If not the exact name is given,
    but the word exists, the first option is selected. If none applies, it returns False'''
    syn = False
    if len(name.split('.')) > 1:
        syn = wn.synset(name)
    else:
        search = wn.synsets(name)
        if len(search) > 0:
            syn = wn.synset(search[0])
    
    return syn

def get_hypos(name):
    '''Takes full synset name string.
    Returns list of all direct hyponyms.'''
    syn = get_synset(name)
    return [str(hypo.name()) for hypo in syn.hyponyms()]

def get_hypers(name):
    '''Takes full synset name string.
    Returns list of all direct hypernyms.'''
    syn = get_synset(name)
    return [str(hyper.name()) for hyper in syn.hypernyms()]

def get_lemmas(name):
    '''Takes full synset name string.
    Returns list of all lemmas (synonyms).'''
    syn = get_synset(name)
    return [str(lemma.name()) for lemma in syn.lemmas()]

def get_definition(name):
    '''Takes full synset name string.
    Returns definition of concept.'''
    syn = get_synset(name)
    return syn.definition()

def get_all_hypos(name):
    tree = []

def select_hypo(hypos):
    '''Takes list of hyponyms. Starts interactive hyponym selection routine.
    Returns name of selected concept.'''
    choices = list(hypos)
    prRed(f"\nThese are the hyponyms (subordinate concepts):")
    for s in hypos:
        sub = get_hypos(s)
        choices += sub
        prYellow(f"{s} -")
        prList(sub)
    
    prGreen(f"Which concept do you want to register as the hyponym? (write complete name)")
    while True:
        try:
            hypo = input(">")
            if(hypo in choices):
                print(f"You chose {hypo}")
                break
            else:
                print("Your selection is not listed.")
                pass
        except:
            print("Your selection is invalid, try again.")
            pass
            
    return hypo
    
def select_hyper(hypers):
    '''Takes list of hypernyms. Starts interactive hypernym selection routine.
    Returns name of selected concept.'''
    prRed(f"These are the hypernyms (superordinate concepts):")
    hyper_max_i = len(hypers)
    selection = hypers[0]
    prList(hypers)
    if len(hypers) < 2:
        print(f"There is only one hypernym to choose from. {selection} has been selected as hypernym.")

    else:
        prGreen(f"Which concept do you want to register as the hypernym? 1 to {hyper_max_i}")
        while True:
            try:
                hyper_index = int(input(">"))
                if(hyper_index in range(1,hyper_max_i+1)):
                    selection = hypers[hyper_index-1]
                    print(f"You chose {selection}")
                    break
                else:
                    print("Your selection is invalid, try again.")
                    pass

            except:
                print("Your selection is not an integer, try again.")
                pass

            
    return selection

def select_img(name):
    '''Takes full synset name string.
    Renames and moves the img to the appropriate experiment folder.
    Returns new path of img file.'''
    prYellow(f"Paste the file path of an image for the hyponym {name} here. It will be copied into the folder 'hypo_imgs' in the current working directory.")
    filepath = input()
    while True:
        try:
            open(filepath)
            break
        except:
            prRed("This is not a valid file path.")
            filepath = input()
            
    filename = os.path.basename(os.path.abspath(filepath))
    fileext = filename.split(".")[-1]
    currentpath = os.getcwd()

    if not "hyper_imgs" in os.listdir():
        os.mkdir("hyper_imgs")

    imagefolder = os.path.join(currentpath, "hyper_imgs")
    newfilename = f"img_{name}.{fileext}"
    newfilenamepath = os.path.join(imagefolder, newfilename)
    

    os.replace(filepath, newfilenamepath)
    print(f"\nThe file {filepath} is now called {newfilename} and was put in the folder {newfilenamepath}.\n")
    return os.path.join("hyper_imgs", newfilename)

def df_create():
    '''Creates and returns the correctly shaped experiment dataframe.'''
    cols = {"index":[], "hypernym":[], "bl":[], "hyponym":[], "hypernym_def":[], "bl_def":[], "hyponym_def":[], "hyponym_img":[]}
    df = pd.DataFrame(data=cols)
    return df

def df_new_entry(df, hyper, bl, hypo, img):
    '''Takes the current dataframe state, bl concept, image, hyper- and hyponym.
    Adds a new row in the dataframe.
    Returns the modified dataframe.'''
    entry = False
    ind = len(df.index)
    hyper_def = get_definition(hyper)
    bl_def = get_definition(bl)
    hypo_def = get_definition(hypo)
    new_row = [ind, hyper, bl, hypo, hyper_def, bl_def, hypo_def, img]
    df.loc[ind] = new_row
    print("A new row has been added to the dataframe:")
    prList(new_row)
    return df

def df_store(df, filename):
    '''Takes the current dataframe and new filename and stores the dataframe in the working directory. Returns True.'''
    df.to_csv(filename)
    prCyan(f"The file {filename} has been saved.")
    return True

#Various colored console output methods.
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))

def prList(list):
    '''Takes any list.
    Pretty prints it in the console.
    Returns True.'''
    count = 1
    for li in list:
        print(f"    {count}) {li}")
        count +=1

    print()
    return True

def interactive_selector(df):
    '''Takes input dataframe containing bl concepts and their certainty value.
    Creates new dataframe.
    Iterates over all rows of input file and starts the interactive selection routines.
    Populates new dataframe.
    Returns finished experiment dataframe.
    '''
    exp_dataset = df_create()
    df = df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        bl_name = row[1]
        bl_certainty = row[2]
        bl_lemmas = get_lemmas(bl_name)
        bl_definition = get_definition(bl_name)

        hypers = get_hypers(bl_name)
        hypers_lemmas = [get_lemmas(name) for name in hypers]
        hypers_defs = [get_definition(name) for name in hypers]
        

        hypos = get_hypos(bl_name)
        hypos_lemmas = [get_lemmas(name) for name in hypos]
        hypos_defs = [get_definition(name) for name in hypos]       

        if len(hypos)>0:
            prLightGray(50*"_")

            prRed(50*"=")
            prRed(f"\n\n\nConcept number {index}: {bl_name}")
            prRed(50*"=")
            print(f"With the synonyms:")
            prList(bl_lemmas)
            print(f"Meaning: {bl_definition}\n")

            selected_hyper = select_hyper(hypers)
            selected_hypo = select_hypo(hypos)
            selected_img = select_img(selected_hypo)

            exp_dataset = df_new_entry(exp_dataset, selected_hyper, bl_name, selected_hypo, selected_img)
            
            prLightGray(50*"_")
            print()

        else:
            prPurple(50*"=")
            name = bl_lemmas[0].replace("_", " ").capitalize()
            prLightPurple(f"\nNumber {index}: {name} has no hyponym and is therefore skipped.\n")
            prPurple(50*"=")

    print(exp_dataset.head)
    return exp_dataset

def main(file):
    '''Main execution loop.'''
    was_success = False
    exp_file = "gen_"+file
    bl_df = False
    try:
        bl_df = pd.read_csv(file)
        try:
            exp_df = interactive_selector(bl_df)
            try:
                was_success = df_store(exp_df, exp_file)
            except:
                prRed("Somthing went wrong during the storage routine of the new dataset.")
        except:
            prRed("The interactive selection failed. You might want to check the input file.")
    except:
        print(f"The file named '{file}' wasn't found in this folder.")

    return was_success
    


#=============================================================================
# Execution
#=============================================================================

if __name__ == "__main__":
    #Either the user specifies the input file in the terminal as an additional
    #argument or they may just call the program and select the input file
    #during the execution.
    tryagain = True
    second_try = False
    arguments = sys.argv
    files = arguments[1:]
    failed_files = []

    clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
    clearConsole()

    while tryagain:
        if second_try:
            bl_file = input("Which csv file? (Needs column 'synset' and 'certainty')")
            prCyan(50*"-")
            prCyan(50*"-")
            print(f"Starting process on {bl_file}")
            prCyan(50*"-")
            prCyan(50*"-")
            tryagain = not main(bl_file)
        
        elif len(files) == 1:
            prCyan(50*"-")
            prCyan(50*"-")
            print(f"Starting process on {files[0]}")
            prCyan(50*"-")
            prCyan(50*"-")
            second_try = True
            tryagain = not main(files[0])

        elif len(files) > 1 and not second_try:
            for file in files:
                
                prCyan(50*"-")
                prCyan(50*"-")
                print(f"Starting process on {file}")
                prCyan(50*"-")
                prCyan(50*"-")
                tryagain = not main(file)
                if tryagain: failed_files.append(file)
            
            if len(failed_files)>0:
                prRed("These files failed during processing.")
                prList(failed_files)
                tryagain = False

        else:
            bl_file = input("Which csv file? (Needs column 'synset' and 'certainty')")
            prCyan(50*"-")
            prCyan(50*"-")
            print(f"Starting process on {bl_file}")
            prCyan(50*"-")
            prCyan(50*"-")
            tryagain = not main(bl_file)
                

            