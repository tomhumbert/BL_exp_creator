# BL_exp_creator
A tool to select wordnet categories and transform it into an Psytoolkit experiment folder, ready for upload. The experiment is a recreation of the experiments done by Rosch in 1976.

## Creating a new experiment:
0) Launch interface.py
1) Select working directory
2) Click 'New Experiment'
3) Enter project name (folder name)
4) Select basic level name list (example csv is included)
5) The Overview is generated, see how to continue in the next section.

## Continue annotation
0) Launch interface.py
1) Select Experiment folder
2) Click 'Open Experiment'
3) Click 'Continue' on the Overview screen
4) Select hyponym from the taxonomy tree
5) The selected entry will be saved when clicking 'Continue' or 'Save + Exit'
6) The entire dataset row is deleted when clicking 'Remove'

## To-do
- Image selection, update and storage (Should create Experiment upload folder already).
- Top option menu : Currently only 'Overview' and 'Exit' work.
- Saving last position when exiting the program, so that the overview continue button does not start on the top.
  - Actually, the program should continue annotating from the row selected in the overview table.
