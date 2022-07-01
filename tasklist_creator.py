import sys, os, random
import pandas as pd
from colorama import Fore, Back, Style

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

def capitalize(word):
    label = word.split('.')[0]
    label = label.replace("_", " ").capitalize()
    return  label

def select_files(list):
    selection = []
    prRed(50*"=_")
    print("These files are available for conversion:")
    prList(list)
    print("\nWrite either 'all' or list the exact names of the files, seperated by spaces, you would like to convert to a psytoolkit task table:")
    ans = input("> ")

    if ans == "all":
        selection = list
    else:
        selection = ans.split(" ")

    prRed(50*"=-")
    return selection

def create_tt(dfs, lvl):
    tasktable = "#-image--label--condition(img,group,label,ans)--correct_response-#"
    unique_labels = []
    #first run of all the correct labels
    for df in dfs:
        unique_labels.append(df.hypernym.unique())
        for index, row in df.iterrows(): 
            img = row["hyponym_img"]
            label = row[lvl]
            condition = f"\'{img} {lvl} {label} True\'"
            label = capitalize(label)
            label = f"\'{label}\'"
            newline = f"\n{img} {label} {condition} 1"
            tasktable = tasktable + newline

    #now create false labels
    for df in dfs:
        for index, row in df.iterrows(): 
            img = row["hyponym_img"]
            lb_candidates = df[df["hypernym"] != row["hypernym"]]
            label = lb_candidates[lvl].tolist()[random.randint(0,(len(lb_candidates)-1))]
            condition = f"\'{img} {lvl} {label} False\'"
            label = capitalize(label)
            label = f"\'{label}\'"
            newline = f"\n{img} {label} {condition} 2"
            tasktable = tasktable + newline

    prGreen(f"Finished creating the tasktable for {lvl} lvl")
    print()
    return tasktable

def store(folder, filename, content):
    os.chdir(folder)
    success = False
    try:
        with open(filename, "w") as file:
            file.write(content)
        success = True
    except:
        prRed("The file could not be saved.")

    os.chdir("..")
    return success

def create_image_list_file():
    image_list = ""

    return store("Rosch7", "image_list.txt", image_list)

def write_exp_code(taskgroups):
    blocks={"block1":{  "length": len(taskgroups['hypernym'].split("\n"))-1,
                        "true_rows": "(",
                        "false_rows": "("},
            "block2":{  "length": len(taskgroups['bl'].split("\n"))-1,
                        "true_rows": "(",
                        "false_rows": "("},
            "block3": {"length": len(taskgroups['hyponym'].split("\n"))-1,
                        "true_rows": "(",
                        "false_rows": "("}
    }

    for key in blocks.keys():
        length = blocks[key]['length']
        for i in range(length):
            if i == (length/2)-1:
                blocks[key]['true_rows'] += f"c1 == {i} ) && c5 == 1"
            elif i == length-1:
                blocks[key]['false_rows'] += f"c1 == {i} ) && c5 == 1"
            elif i < (length-1)/2:
                blocks[key]['true_rows'] += f"c1 == {i} ||"
            else:
                blocks[key]['false_rows'] += f"c1 == {i} ||"
    
    content = f"""#In the original Rosch experiment(7) 15 people participated in judging superordinate names of objects.
options
    background color white
    bitmapdir images

bitmaps
    include image_list.txt
    mistake
    intro
    intro2
    outro

fonts
    arial 20
    bahn BAHNSCHRIFT.TTF 40

table hypernym_tasks
    include tasklist_hypernym.txt

table bl_tasks
    include tasklist_bl.txt

table hyponym_tasks
    include tasklist_hyponym.txt

task hypernyms
    font bahn
    table hypernym_tasks
    keys 1 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 5000
    clear 1 2
    if STATUS != CORRECT                   # if you make an error
        show bitmap mistake                # show an error message at screen center
        delay 500                          # for 500 ms
        clear 3                            # and then clear
    fi                                     # end of if statement
    delay 500                              
    save TABLEROW @3 STATUS RT             # save data to file

task bl
    font bahn
    table bl_tasks
    keys 1 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 5000
    clear 1 2
    if STATUS != CORRECT                   # if you make an error
        show bitmap mistake                # show an error message at screen center
        delay 500                          # for 500 ms
        clear 3                            # and then clear
    fi                                     # end of if statement
    delay 500                              
    save TABLEROW @3 STATUS RT             # save data to file


task hyponyms
    font bahn
    table hyponym_tasks
    keys 1 0
    show text @2 0 -200 0 0 0
    delay 500
    show bitmap @1 0 100
    readkey @4 5000
    clear 1 2
    if STATUS != CORRECT                   # if you make an error
        show bitmap mistake                # show an error message at screen center
        delay 500                          # for 500 ms
        clear 3                            # and then clear
    fi                                     # end of if statement
    delay 500                              
    save TABLEROW @3 STATUS RT             # save data to file


message intro
message intro2

block group1 
    delay 1000
    tasklist
        hypernyms {blocks["block1"]['length']} all_before_repeat
    end
    feedback
        text color black
        text align left
        set &RTtrue mean c6 ; select {blocks["block1"]["true_rows"]}
        set &RTfalse mean c6 ; select {blocks["block1"]["false_rows"]}
        text -350 -200 "Average response times (without wrong answers)"
        text -350 -100 &RTtrue ; prefix "RT for true labels: " ; postfix " ms"
        text -350 0 &RTfalse ; prefix "RT for false labels: " ; postfix " ms"
        text -350 200 "Press space to continue."
    end

message intro2

block group2 
    delay 1000
    tasklist
        bl {blocks["block2"]['length']} all_before_repeat
    end
    feedback
        text color black
        text align left
        set &RTtrue mean c6 ; select {blocks["block2"]["true_rows"]}
        set &RTfalse mean c6 ; select {blocks["block2"]["false_rows"]}
        text -350 -200 "Average response times (without wrong answers)"
        text -350 -100 &RTtrue ; prefix "RT for true labels: " ; postfix " ms"
        text -350 0 &RTfalse ; prefix "RT for false labels: " ; postfix " ms"
        text -350 200 "Press space to continue."
    end

message intro2

block group3 
    delay 1000
    tasklist
        hyponyms {blocks["block3"]['length']} all_before_repeat
    end
    feedback
        text color black
        text align left
        set &RTtrue mean c6 ; select {blocks["block3"]["true_rows"]}
        set &RTfalse mean c6 ; select {blocks["block3"]["false_rows"]}
        text -350 -200 "Average response times (without wrong answers)"
        text -350 -100 &RTtrue ; prefix "RT for true labels: " ; postfix " ms"
        text -350 0 &RTfalse ; prefix "RT for false labels: " ; postfix " ms"
        text -350 200 "Press space to continue."
    end

message outro
 """

    return store("Rosch7", "code.psy", content)

def main():
    cwd = os.getcwd()
    exp_input_folder = "exp_selection"
    exp_folder = "Rosch7"
    img_folder = os.path.join(exp_folder,"images")

    if not os.path.isdir(exp_folder):
        os.mkdir(exp_folder)

    if not os.path.isdir(img_folder):
        os.mkdir(img_folder)

    files = os.listdir(exp_input_folder)
    exp_files = select_files(files)
    dataframes = []
    taskgroups = {'hypernym':"",'bl':"",'hyponym':""}

    for file in exp_files:
        df = pd.read_csv(os.path.join(exp_input_folder, file))
        dataframes.append(df)

    for lvl in taskgroups.keys():
        taskgroups[lvl] = create_tt(dataframes, lvl)
        if store(exp_folder, f"tl_{lvl}.txt", taskgroups[lvl]):
            prGreen(f"The {lvl} taskgroup has been created in the Rosch7 experiment folder.")
    
    prYellow("Do you also want the code for the experiment automatically generated?")
    cont_program = input("(y/n)? >")
    if cont_program == 'y':
        code = write_exp_code(taskgroups)

    #Need to paste a copy of the 'publish' folder with files into exp_folder

    prGreen(30*'+')
    prGreen("The process has concluded.")
    prGreen(30*'+')
    print()
    print("If it hasn't existed yet, the experiment folder was created with the images and publish folders inside.")
    prYellow("The folder should now contain:")
    prList(["Three tasklist files","A file listing all images","The main code.psy file","An 'images' folder", "A 'publish' folder"])
    print()
    print(30*"~")
    prRed("Do not forget to paste the images in the images folder, with the exact names as they are listed in the experiment input file.")
    prYellow("All images should have white background, depict only the object and be 400x400 pixels in size.")
    print(30*"~")

if __name__ == "__main__":
    main()