import os
import PySimpleGUI as sg
import subprocess
import shutil
from numpy import arange
import copy
import numpy as np


#Useful functions###################################################
def my_arange(start, end, step):
	"""
	This is used instead of numpy arange due to numpy arange unstable length of
	output when floating numbers are used
	"""
	return np.linspace(start, end, num=round((end-start)/step), endpoint=False)

def replacement_floatorint(stringtoreplace,stringreplacement):

    replaced_content=""
    generate_proc = open(path + '/generate_allproc.py', "r")
    for line in generate_proc:
        line.strip()

        new_line = line.replace(stringtoreplace,stringreplacement)
        replaced_content = replaced_content + new_line 
    generate_proc.close()
    write_file = open(path + '/generate_allproc.py', "w")
    write_file.write(replaced_content)
    write_file.close()

def replacement_tuple(range_value,start,boundaries,boundaries_name,value):
    replaced_content = ""
    generate_proc = open(path + '/generate_allproc.py', "r")
    for line in generate_proc:
        line.strip()
        new_line = line.replace(start,start.replace("#","").replace("0,0,0",range_value))
        new_line = new_line.replace(boundaries,boundaries.replace("#",""))
        new_line = new_line.replace(boundaries_name,boundaries_name.replace("#",""))
        new_line = new_line.replace(value,value.replace("#",""))
        replaced_content = replaced_content + new_line 
    generate_proc.close()
    write_file = open(path + '/generate_allproc.py', "w")
    write_file.write(replaced_content)
    write_file.close()

def replacement_witherrorhandling (
        key_value,
        defaultforfloatorint,
        replaceforfloatorint,
        startfortuple,
        boundariesfortuple,
        boundariesnamefortuple,
        valuefortuple,
        ):
    if type(eval(key_value)) == float or type(eval(key_value)) == int: 
        replacement_floatorint(defaultforfloatorint,
                               replaceforfloatorint)
        

    elif type(eval(key_value)) == tuple:
        print(key_value)
        print(type(key_value))
        if len(eval(key_value)) == 3 and all(isinstance(n, int) or isinstance(n, float) for n in eval(key_value)):
            globals()['num_of_csvresult'] = globals()['num_of_csvresult']*len(my_arange(*eval(key_value)))
            replacement_tuple(key_value,
                              startfortuple,
                              boundariesfortuple,
                              boundariesnamefortuple,
                              valuefortuple)
        else:
            sg.popup_error("Something is wrong!","Either not all the inputs are integer/float or the number of elements entered is incorrect. Must be of the form: start,stop,step")
    else:
        sg.popup_error("Something is wrong!", "The input needs to be of the form :start,stop,step or single entry")

def replacement_witherrorhandling_forintegers(
        key_value,
        defaultforfloatorint,
        replaceforfloatorint,
        startfortuple,
        boundariesfortuple,
        boundariesnamefortuple,
        valuefortuple,
        ):
    if type(eval(key_value)) == int:
        replacement_floatorint(defaultforfloatorint,
                               replaceforfloatorint)

    elif type(eval(key_value)) == tuple:

        if len(eval(key_value)) == 3 and all(isinstance(n, int) for n in eval(key_value)):
            globals()['num_of_csvresult'] = globals()['num_of_csvresult']*len(arange(*eval(key_value)))
            print('this is triggered')
            replacement_tuple(key_value,
                              startfortuple,
                              boundariesfortuple,
                              boundariesnamefortuple,
                              valuefortuple)
        else:
            sg.popup_error("Something is wrong!","Either not all the inputs are integer/float or the number of elements entered is incorrect. Must be of the form: start,stop,step")
    else:
        sg.popup_error("Something is wrong!", "The input needs to be of the form :start,stop,step or single entry")
####################################################################

#default settings###################################################

# #path is directory of topas_gui.py  
# #path = '/Users/jacob/Desktop/NCCS/CBCT/gui/topaswrap_version3' #apple
# path='/root/nccs/Topas_wrapper'     #linux Figure out how to change this dynamically 

# # path = '__file__'.rstrip()

# #topas_application_path = '/Applications/topas/bin/topas'#apple
# topas_application_path='/root/topas/bin/topas'     #linux

# #replacing directory of G4Data
# G4_Data='/root/G4Data' #linux

# try
path = os.getcwd()
topas_application_path='Set your topas path'     #linux
G4_Data='Set your G4 data path' #linux


#generate a generate_allproc file from a boiler plate so we edit only that copy each time
original_file_path = path + '/generate_allproc_boilerplate.py'
duplicate_gen_file_name = "generate_allproc.py"
directory_path = os.path.dirname(original_file_path)
duplicate_gen_file_path = os.path.join(directory_path, duplicate_gen_file_name)
shutil.copy(original_file_path, duplicate_gen_file_path)

#generate a multi_allproc file from a boiler plate so we edit only that copy each time
original_file_path = path + '/runfolder/topas_multiproc_boilerplate.py'
duplicate_multiproc_file_name = "topas_multiproc.py"
directory_path = os.path.dirname(original_file_path)
duplicate_multiproc_file_path = os.path.join(directory_path, duplicate_multiproc_file_name)
shutil.copy(original_file_path, duplicate_multiproc_file_path)

replaced_content=""
multi_proc = open(path + '/runfolder/topas_multiproc.py', "r")
for line in multi_proc:
    line.strip()
    
    new_line  = line.replace(path,
                            f"{topas_application_path} ")
    replaced_content = replaced_content + new_line 
multi_proc.close()
write_file = open(path + '/runfolder/topas_multiproc.py', "w")
write_file.write(replaced_content)
write_file.close()

from generate_allproc_boilerplate import selectcomponents
#selectcomponents_local = copy.deepcopy(selectcomponents)
#####################################################################

sg.theme('Reddit')

general_layer = sg.Frame('General Settings',
                [ 
                  [sg.Text('Main Folder',size =(17,1),font=('Helvetica', 14),text_color='black'),
#                   sg.In(default_text='/home/businessit/Downloads/topaswrap_version2',key='-MAINFOLDERNAME-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FolderBrowse(font=('Helvetica', 14))],
                    sg.In(default_text=path,key='-MAINFOLDERNAME-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FolderBrowse(font=('Helvetica', 14))],
                  
                  [sg.Text('G4 Data Directory',size = (17,1),font=('Helvetica', 14), text_color='black'),
#                   sg.In(default_text='/home/businessit/G4Data',key='-G4FOLDERNAME-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FolderBrowse(font=('Helvetica', 14))],
                    sg.In(default_text=G4_Data,key='-G4FOLDERNAME-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FolderBrowse(font=('Helvetica', 14))],
                  [sg.Text('TOPAS Directory',size =(17,1),font=('Helvetica', 14),text_color='black'),
#                   sg.In(default_text='/home/businessit/topas/bin/topas',key='-TOPAS-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FileBrowse(font=('Helvetica', 14))],
                    sg.In(default_text=topas_application_path,key='-TOPAS-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FileBrowse(font=('Helvetica', 14))],
                  [sg.Button("Create generate_allproc file",enable_events=True, key='-DUPGENPROC-',disabled=False,font=('Helvetica', 14),disabled_button_color='grey',size=(35,1)),
                    sg.Text(' ', pad=(1, 1)),
                    sg.Button("Create multiproc file",enable_events=True,key='-DUPMULPROC-',disabled=False,font=('Helvetica', 14),disabled_button_color='grey',size=(35,1))],
                  [sg.Text('Seed',size =(9,1),font=('Helvetica', 14),text_color='black'),
                    sg.In(default_text='9',key='-SEED-',size=(10,1),font=('Helvetica', 14),enable_events=True)],
                  [sg.Text('Threads',size = (9,1),font=('Helvetica', 14),text_color='black'),
                    sg.In(default_text='4',key='-THREAD-',size=(10,1),font=('Helvetica',14),enable_events=True)],
                  [sg.Text('Histories',size = (9,1),font=('Helvetica',14),text_color='black'),
                    sg.In(default_text='100000',key='-HIST-',size=(10,1),font=('Helvetica',14),enable_events=True)]
                ])

#create a button menu with key that triggers an event 
#event that will fill up the dynamic for loop with range of values
#to simulate
#menu_def = ['Menu',['Menu item 1::savekey', 'Menu item 2']]

#range_generator_layer = sg.Frame('Range Generator',
                        # [  
                        #   [sg.Text('Component',size = (5,1), font=('Helvetica', 14), text_color='black'),
                        #     sg.ButtonMenu('select',menu_def,),
                        #     sg.Text('Start',size = (2,1),font=('Helvetica', 14), text_color='black')
                        #     sg.In(key='-START-',size=(2,1), font=('Helvetica', 14)),
                        #     sg.Text('Stop',size = (2,1),font=('Helvetica', 14), text_color='black')
                        #     sg.In(key='-STOP-',size=(2,1), font=('Helvetica', 14)),
                        #     sg.Text('Step',size = (2,1),font=('Helvetica', 14), text_color='black')
                        #     sg.In(key='-STEP-',size=(2,1), font=('Helvetica', 14))
                        #     sg.Button('Fill')
                        #     ]

                        # ])

# selectcomponents = {
# 'ChamberPlugCentre': 1,
# 'ChamberPlugTop': 1,
# 'ChamberPlugBottom': 1,
# 'ChamberPlugLeft': 1,
# 'ChamberPlugRight': 1,
# 'ChamberPlugDose_tle': 1,
# 'ChamberPlugDose_dtm': 1,
# 'ChamberPlugDose_dtw': 1,
# 'CollimatorsVertical': 1,
# 'CollimatorsHorizontal': 1,
# 'SteelFilter': 0,
# 'BowtieFilter': 0,
# 'Coll1': 1,
# 'Coll2': 1,
# 'Coll3': 1,
# 'Coll4': 1,
# 'DemoFlat': 0,
# 'DemoRTrap':0,
# 'DemoLTrap': 0,
# 'topsidebox': 0,
# 'bottomsidebox': 0,
# 'couch': 1
# }

CTDI_layer = sg.Frame('CTDI',
                    [
                      [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='TsCylinder',key='-CTDI_TYPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                      [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='PMMA',key='-CTDI_MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMin',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CTDI_RMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMax',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='8.0',key='-CTDI_RMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('HL',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='7.25',key='-CTDI_HL-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('SPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text="0.",key='-CTDI_SPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('DPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='360.',key='-CTDI_DPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.',key='-CTDI_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.',key='-CTDI_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.',key='-CTDI_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-90',key='-CTDI_RX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                    ])


ChamberPlugCentre_layer = sg.Frame('ChamberPlugCentre',
                    [
                      [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='TsCylinder',key='-CPC_TYPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                      [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='PMMA',key='-CPC_MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMin',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPC_RMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMax',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.655',key='-CPC_RMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('HL',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='5.0',key='-CPC_HL-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('SPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text="0.",key='-CPC_SPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('DPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='360.',key='-CPC_DPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPC_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPC_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPC_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-90',key='-CPC_RX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                    ])

ChamberPlugTop_layer = sg.Frame('ChamberPlugTop',
                    [
                      [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='TsCylinder',key='-CPT_TYPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                      [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='PMMA',key='-CPT_MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMin',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPT_RMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMax',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.655',key='-CPT_RMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('HL',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='5.0',key='-CPT_HL-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('SPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text="0.",key='-CPT_SPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('DPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='360.',key='-CPT_DPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPT_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPT_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-7.0',key='-CPT_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-90',key='-CPT_RX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                    ])

ChamberPlugBottom_layer = sg.Frame('ChamberPlugBottom',
                    [
                      [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='TsCylinder',key='-CPB_TYPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                      [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='PMMA',key='-CPB_MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMin',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPB_RMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMax',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.655',key='-CPB_RMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('HL',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='5.0',key='-CPB_HL-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('SPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text="0.",key='-CPB_SPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('DPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='360.',key='-CPB_DPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPB_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPB_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='7.0',key='-CPB_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-90',key='-CPB_RX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                    ])

ChamberPlugLeft_layer = sg.Frame('ChamberPlugLeft',
                    [
                      [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='TsCylinder',key='-CPL_TYPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                      [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='PMMA',key='-CPL_MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMin',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPL_RMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMax',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.655',key='-CPL_RMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('HL',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='5.0',key='-CPL_HL-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('SPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text="0.",key='-CPL_SPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('DPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='360.',key='-CPL_DPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-7.0',key='-CPL_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPL_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPL_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-90',key='-CPL_RX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                    ])

ChamberPlugRight_layer = sg.Frame('ChamberPlugRight',
                    [
                      [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='TsCylinder',key='-CPR_TYPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                      [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='PMMA',key='-CPR_MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMin',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPR_RMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RMax',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.655',key='-CPR_RMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('HL',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='5.0',key='-CPR_HL-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('SPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text="0.",key='-CPR_SPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('DPHI',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='360.',key='-CPR_DPHI-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='7.0',key='-CPR_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPR_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='0.0',key='-CPR_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text='-90',key='-CPR_RX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],

                    ])

Scoring_layer = sg.Frame("Scoring",
                [
                   [sg.Text('TLE_Zbins',size = (10,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='100',key='-TLEZB-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('DTM_Zbins',size = (10,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='100',key='-DTMZB-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('DTW_Zbins',size = (10,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='100',key='-DTWZB-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

Physics_layer = sg.Frame("Physics",
                [
                   [sg.Text('List',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Default',key='-PHYLST-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Process',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='False',key='-PHYPRO-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Default Type',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Geant4_Modular',key='-PHYDEFTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Default Modules',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='6 "g4em-standard_opt4" "g4h-phy_QGSP_BIC_HP" "g4decay" "g4ion-binarycascade" "g4h-elastic_HP" "g4stopping"',key='-PHYDEFMO-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('EMRangeMin',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='100.',key='-PHYEMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('EMRangeMax',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='521.',key='-PHYEMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

RotationGroup_layer = sg.Frame("Rotation Group",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Group',key='-ROTTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='World',key='-ROTPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-ROTROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Tf_Rotate_Value',key='-ROTROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-ROTROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-ROTTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-ROTTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-ROTTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

CollimatorVerticalGroup_layer = sg.Frame("Collimators Vertical Group",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Group',key='-COLLVERTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Rotation',key='-COLLVERPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-COLLVERROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-COLLVERROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-COLLVERROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='9.3',key='-COLLVERTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

CollimatorHorizontalGroup_layer = sg.Frame("Collimators Horizontal Group",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Group',key='-COLLHORTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsVertical',key='-COLLHORPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-COLLHORROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-COLLHORROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-COLLHORROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='1.4',key='-COLLHORTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

# SteelGroup_layer = sg.Frame("Steel Filter Group",
#               [
#                  [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='Group',key='-STEELTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='CollimatorsHorizontal',key='-STEELPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='1.59',key='-STEELTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#               ])

TitaniumGroup_layer = sg.Frame("Titanium Filter Group",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Group',key='-TITTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsHorizontal',key='-TITPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='1.59',key='-TITTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])
Bowtie_layer = sg.Frame("Bowtie Filter Group",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Group',key='-BFTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsHorizontal',key='-BFPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BFROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BFROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90.',key='-BFROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-BFTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-BFTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='3.85',key='-BFTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

Coll1_layer = sg.Frame("Collimator 1",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll1TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Lead',key='-Coll1MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsVertical',key='-Coll1PAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll1ROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90.',key='-Coll1ROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll1ROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll1TRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.27',key='-Coll1TRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll1TRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll1LZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.3',key='-Coll1LY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll1LX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='9.2',key='-Coll1LTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Coll2_layer = sg.Frame("Collimator 2",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll2TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Lead',key='-Coll2MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsVertical',key='-Coll2PAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90',key='-Coll2ROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='270.',key='-Coll2ROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll2ROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll2TRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-5.27',key='-Coll2TRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll2TRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll2LZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.3',key='-Coll2LY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll2LX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='9.2',key='-Coll2LTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])
	
Coll3_layer = sg.Frame("Collimator 3",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll3TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Lead',key='-Coll3MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsHorizontal',key='-Coll3PAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll3ROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='180.',key='-Coll3ROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll3ROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.27',key='-Coll3TRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-Coll3TRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-Coll3TRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll3LZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.3',key='-Coll3LY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll3LX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='9.2',key='-Coll3LTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Coll4_layer = sg.Frame("Collimator 4",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll4TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Lead',key='-Coll4MAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsHorizontal',key='-Coll4PAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll4ROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-Coll4ROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll4ROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-5.27',key='-Coll4TRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-Coll4TRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-Coll4TRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll4LZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.3',key='-Coll4LY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll4LX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='9.2',key='-Coll4LTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Coll1steel_layer = sg.Frame("Collimator Steel 1",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll1steelTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Steel',key='-Coll1steelMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsVertical',key='-Coll1steelPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll1steelROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90.',key='-Coll1steelROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll1steelROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll1steelTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll1steelTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-0.25',key='-Coll1steelTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll1steelLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll1steelLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll1steelLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll1steelLTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Coll2steel_layer = sg.Frame("Collimator Steel 2",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll2steelTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Steel',key='-Coll2steelMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsVertical',key='-Coll2steelPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll2steelROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='270.',key='-Coll2steelROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll2steelROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll2steelTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll2steelTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-0.25',key='-Coll2steelTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll2steelLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll2steelLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll2steelLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll2steelLTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Coll3steel_layer = sg.Frame("Collimator Steel 3",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll3steelTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Steel',key='-Coll3steelMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsHorizontal',key='-Coll3steelPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll3steelROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='180.',key='-Coll3steelROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll3steelROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll3steelTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll3steelTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-0.25',key='-Coll3steelTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll3steelLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll3steelLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll3steelLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll3steelLTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Coll4steel_layer = sg.Frame("Collimator Steel 4",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-Coll4steelTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Steel',key='-Coll4steelMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='CollimatorsHorizontal',key='-Coll4steelPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-Coll4steelROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-Coll4steelROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll4steelROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll4steelTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-Coll4steelTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-0.25',key='-Coll4steelTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='12.',key='-Coll4steelLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-Coll4steelLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll4steelLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-Coll4steelLTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])


# SteelFil_layer = sg.Frame("Steel Filter",
#               [
#                  [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='TsBox',key='-STEELFILTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='Steel',key='-STEELFILMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='SteelFilterGroup',key='-STEELFILPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELFILROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELFILROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELFILROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELFILTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELFILTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.',key='-STEELFILTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='0.01',key='-STEELFILHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='10.',key='-STEELFILHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
#                  [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
#                    sg.In(default_text='10.',key='-STEELFILHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
#               ])

TITFIL_layer = sg.Frame("Titanium Filter",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='TsBox',key='-TITFILTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Titanium',key='-TITFILMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='TitaniumFilterGroup',key='-TITFILPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITFILROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITFILROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITFILROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITFILTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITFILTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TITFILTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0445',key='-TITFILHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-TITFILHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='10.',key='-TITFILHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
                ])

DemoFlat_layer = sg.Frame("Demo Flat",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='TsBox',key='-DEMOFLATTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Aluminum',key='-DEMOFLATMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='BowtieFilter',key='-DEMOFLATPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-DEMOFLATROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-DEMOFLATROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-DEMOFLATROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-DEMOFLATTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-DEMOFLATTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-DEMOFLATTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='7.5',key='-DEMOFLATHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.4',key='-DEMOFLATHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='7.5',key='-DEMOFLATHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
                ])
TopSideBox_layer = sg.Frame("Top side box",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='TsBox',key='-TSBTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Aluminum',key='-TSBMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='BowtieFilter',key='-TSBPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TSBROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-TSBROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-TSBROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-TSBTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.0',key='-TSBTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='1.3',key='-TSBTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='7.5',key='-TSBHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='2.5',key='-TSBHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='1.4',key='-TSBHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
                ])

BottomSideBox_layer = sg.Frame("Bottom side box",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='TsBox',key='-BSBTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Aluminum',key='-BSBMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='BowtieFilter',key='-BSBPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BSBROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-90.',key='-BSBROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BSBROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-BSBTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-5.0',key='-BSBTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='1.3',key='-BSBTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='7.5',key='-BSBHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='2.5',key='-BSBHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='1.4',key='-BSBHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
                ])

DemoRTrap_layer = sg.Frame("Demo RTrap",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-DEMORTRAPTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Aluminum',key='-DEMORTRAPMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='BowtieFilter',key='-DEMORTRAPPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-DEMORTRAPROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90',key='-DEMORTRAPROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-DEMORTRAPROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-DEMORTRAPTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-2.5',key='-DEMORTRAPTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.65',key='-DEMORTRAPTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='15.',key='-DEMORTRAPLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.',key='-DEMORTRAPLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='2.8',key='-DEMORTRAPLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-DEMORTRAPLTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])
DemoLTrap_layer = sg.Frame("Demo LTrap",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='G4RTrap',key='-DEMOLTRAPTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Aluminum',key='-DEMOLTRAPMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='BowtieFilter',key='-DEMOLTRAPPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='180',key='-DEMOLTRAPROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='270',key='-DEMOLTRAPROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-DEMOLTRAPROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-DEMOLTRAPTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='2.5',key='-DEMOLTRAPTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.65',key='-DEMOLTRAPTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='15.',key='-DEMOLTRAPLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.0',key='-DEMOLTRAPLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='2.8',key='-DEMOLTRAPLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('LTX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.2',key='-DEMOLTRAPLTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Couch_layer = sg.Frame("Couch",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='TsBox',key='-COUCHTY-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                     sg.Text('Material',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Aluminum',key='-COUCHMAT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='World',key='-COUCHPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-COUCHTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.0',key='-COUCHTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Ge/couch/HLZ + Ge/CTDI/RMax',key='-COUCHTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.075',key='-COUCHHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='100.0',key='-COUCHHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='26.0',key='-COUCHHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
                ])

BeamGroup_layer = sg.Frame("Beam Group",
                [
                   [sg.Text('Type',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Group',key='-BEAMGRPTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Parent',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Rotation',key='-BEAMGRPPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BEAMGRPTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BEAMGRPTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='-100.',key='-BEAMGRPTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BEAMGRPROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BEAMGRPROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('RotZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.',key='-BEAMGRPROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                 
                ])

Beam_layer = sg.Frame("Beam",
                [   
                   [sg.Text('EnergySpec',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Continuous',key='-BEAMSPECTY-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('Type',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Beam',key='-BEAMTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Component',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='BeamPosition',key='-BEAMCOMPO-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('Particle',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='gamma',key='-BEAMPAR-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('PosDistro',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Gaussian',key='-BEAMPOSDISTRO-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('CutOffShape',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Rectangle',key='-BEAMPOSHAPE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('CutOffX',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.',key='-BEAMPOSCUTOFFX-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('CutOffY',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='5.',key='-BEAMPOSCUTTOFFY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('SpreadX',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.04246',key='-BEAMPOSSPRDX-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('SpreadY',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.04246',key='-BEAMPOSSPRDY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('AngDistro',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Gaussian',key='-BEAMSPOSANGDISTRO-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('AngCutoffX',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90',key='-BEAMPOSANGCUTOFFX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('AngCutoffY',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90',key='-BEAMPOSANGCUTOFFY-',size=(10,1), font=('Helvetica', 12), enable_events=True),
                    sg.Text('AngSpreadX',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='28',key='-BEAMPOSANGSPREADX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('AngSpreadY',size = (11,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='28',key='-BEAMPOSANGSPREADY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])

Time_layer = sg.Frame("Time Feature",
                [   
                   [sg.Text('Seq Time',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='501',key='-TIMESEQ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Verbosity',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0',key='-TIMEVERBO-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Timeline End',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='501.0',key='-TIMELINEEND-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Rotate Func',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='Linear deg',key='-TIMEROTFUNC-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Rotate Rate',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='0.4',key='-TIMEROTRATE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Rotate Start',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='90.0',key='-TIMEROTSTART-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('ShowHistoryInt',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text='100000',key='-TIMEHISTINT-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                     
                ])

toggle_layer = sg.Frame("ON/OFF",
                [   
                  [sg.Text('ChamberPlugCentre',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugCentre'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugCentre'] else 'white on red', key='-CPCTOG-'),
                    sg.Text('ChamberPlugTop',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugTop'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugTop'] else 'white on red', key='-CPTTOG-'),
                    sg.Text('ChamberPlugBottom',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugBottom'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugBottom'] else 'white on red', key='-CPBTOG-'),
                    sg.Text('ChamberPlugLeft',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugLeft'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugLeft'] else 'white on red', key='-CPLTOG-')],
                  [sg.Text('ChamberPlugRight',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugRight'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugRight'] else 'white on red', key='-CPRTOG-'),
                    sg.Text('ChamberPlugDose_tle',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugDose_tle'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugDose_tle'] else 'white on red', key='-TLETOG-'),
                    sg.Text('ChamberPlugDose_dtm',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugDose_dtm'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugDose_dtm'] else 'white on red', key='-DTMTOG-'),
                    sg.Text('ChamberPlugDose_dtw',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['ChamberPlugDose_dtw'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['ChamberPlugDose_dtw'] else 'white on red', key='-DTWTOG-')],
                  [sg.Text('CollimatorsVertical',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['CollimatorsVertical'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['CollimatorsVertical'] else 'white on red', key='-COLLVERTOG-'),
                    sg.Text('CollimatorsHorizontal',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['CollimatorsHorizontal'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['CollimatorsHorizontal'] else 'white on red', key='-COLLHORTOG-'),
                    sg.Text('TitaniumFilter',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['TitaniumFilter'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['TitaniumFilter'] else 'white on red', key='-TITFILTOG-'),
                    sg.Text('BowtieFilter',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['BowtieFilter'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['BowtieFilter'] else 'white on red', key='-BTFILTOG-')],
                  [sg.Text('Coll1',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['Coll1'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['Coll1'] else 'white on red', key='-COLL1TOG-'),
                    sg.Text('Coll2',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['Coll2'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['Coll2'] else 'white on red', key='-COLL2TOG-'),
                    sg.Text('Coll3',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['Coll3'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['Coll3'] else 'white on red', key='-COLL3TOG-'),
                    sg.Text('Coll4',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['Coll4'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['Coll4'] else 'white on red', key='-COLL4TOG-')],
                 
                  [sg.Text('DemoFlat',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['DemoFlat'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['DemoFlat'] else 'white on red', key='-DEMOFLATTOG-'),
                    sg.Text('DemoRTrap',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['DemoRTrap'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['DemoRTrap'] else 'white on red', key='-DEMORTRAPTOG-'),
                    sg.Text('DemoLTrap',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['DemoLTrap'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['DemoLTrap'] else 'white on red', key='-DEMOLTRAPTOG-')],
                  [sg.Text('topsidebox',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['topsidebox'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['topsidebox'] else 'white on red', key='-TSBTOG-'),
                    sg.Text('bottomsidebox',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['bottomsidebox'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['bottomsidebox'] else 'white on red', key='-BSBTOG-'),
                    sg.Text('couch',size = (21,1),font=('Helvetica', 12), text_color='black'),
                    sg.Button('On' if selectcomponents['couch'] else 'Off' , size=(3, 1), button_color='white on green' if selectcomponents['couch'] else 'white on red', key='-COHTOG-')]
                ])
	

#old menu
# layout = [[ sg.Text('Imaging Dose', size=(30,1),font=('Helvetica 28 bold'), text_color='dark blue')],
#             [general_layer,CTDI_layer,toggle_layer],
#             [ChamberPlugCentre_layer,ChamberPlugTop_layer,ChamberPlugBottom_layer,ChamberPlugLeft_layer,ChamberPlugRight_layer,TITFIL_layer,Coll1_layer,Coll2_layer,Coll3_layer,Coll4_layer,Scoring_layer],
#             [Coll1steel_layer,Coll2steel_layer,Coll3steel_layer,Coll4steel_layer,DemoFlat_layer,TopSideBox_layer,BottomSideBox_layer,DemoRTrap_layer,DemoLTrap_layer,Time_layer,Physics_layer],
#             [RotationGroup_layer,CollimatorVerticalGroup_layer,CollimatorHorizontalGroup_layer,TitaniumGroup_layer,Bowtie_layer,
# #           [DemoFlat_layer,TopSideBox_layer,BottomSideBox_layer,DemoRTrap_layer,DemoLTrap_layer],
#             Couch_layer,BeamGroup_layer,Beam_layer,
#              sg.Button("Generate Processes", enable_events=True, key='-GEN-', disabled=False, font=('Helvetica', 14), disabled_button_color='grey'),
#              sg.Button("Run", enable_events=True, key='-RUN-', disabled=False, font=('Helvetica', 14), disabled_button_color='grey')]
#          ]
#end old menu

# Creating a tabbed menu 
main_layout = [[general_layer],
               [toggle_layer], [
                sg.Button("Generate Processes", enable_events=True, key='-GEN-', disabled=False, font=('Helvetica', 14), disabled_button_color='grey'), 
                sg.Button("Run", enable_events=True, key='-RUN-', disabled=False, font=('Helvetica', 14), disabled_button_color='grey')] ]



chamber_layout = [[CTDI_layer,ChamberPlugCentre_layer,ChamberPlugTop_layer,ChamberPlugBottom_layer,ChamberPlugLeft_layer,ChamberPlugRight_layer]]

collimator_layout = [[Coll1_layer,Coll2_layer,Coll3_layer,Coll4_layer, CollimatorVerticalGroup_layer], 
                     [Coll1steel_layer,Coll2steel_layer,Coll3steel_layer,Coll4steel_layer,CollimatorHorizontalGroup_layer ]]

filter_layout = [[ TITFIL_layer, DemoFlat_layer,TopSideBox_layer,BottomSideBox_layer],
                  [DemoRTrap_layer,DemoLTrap_layer,TitaniumGroup_layer,Bowtie_layer]]

others_layout = [[Time_layer,Physics_layer, Scoring_layer,RotationGroup_layer], 
                 [Couch_layer,BeamGroup_layer,Beam_layer]]

layout = [[ sg.Text('Imaging Dose', size=(30,1),justification='center',font=('Helvetica 50 bold'), text_color='dark blue')],
          [sg.TabGroup([[sg.Tab( 'Main menu' , main_layout),
                        sg.Tab('Chamber menu' , chamber_layout),
                        sg.Tab('Collimator menu', collimator_layout),
                        sg.Tab('Filter menu', filter_layout),
                        sg.Tab('Others menu', others_layout)]],
                        key='-TAB GROUP-', font=(40) ,expand_x=True, expand_y=True),
                        ]]

sg.set_options(scaling=1)

window = sg.Window(title= "Imaging Dose Simulation", layout=layout, finalize=True)
window.set_min_size(window.size)
# End test tab menu

# my_width, my_height = 1920, 1080

# root = sg.tk.Tk()
# new_scaling = root.winfo_fpixels('1i')/72
# width, height = sg.Window.get_screen_size()
# scaling = new_scaling * min(width / my_width, height / my_height)




window["-MAINFOLDERNAME-"].bind("<Return>","_ENTER")
window["-G4FOLDERNAME-"].bind("<Return>","_ENTER")
window["-TOPAS-"].bind("<Return>","_ENTER")
window["-SEED-"].bind("<Return>","_ENTER")
window["-THREAD-"].bind("<Return>","_ENTER")
window["-HIST-"].bind("<Return>","_ENTER")
window["-CPC_TYPE-"].bind("<Return>","_ENTER")
window["-CPC_MAT-"].bind("<Return>","_ENTER")
window["-CPC_RMIN-"].bind("<Return>","_ENTER")
window["-CPC_RMAX-"].bind("<Return>","_ENTER")
window["-CPC_HL-"].bind("<Return>","_ENTER")
window["-CPC_RMAX-"].bind("<Return>","_ENTER") #Why is there a dupli?
window["-CPC_SPHI-"].bind("<Return>","_ENTER")
window["-CPC_DPHI-"].bind("<Return>","_ENTER")
window["-CPC_TX-"].bind("<Return>","_ENTER")
window["-CPC_TY-"].bind("<Return>","_ENTER")
window["-CPC_TZ-"].bind("<Return>","_ENTER")
window["-CPC_RX-"].bind("<Return>","_ENTER")

window["-CPT_TYPE-"].bind("<Return>","_ENTER")
window["-CPT_MAT-"].bind("<Return>","_ENTER")
window["-CPT_RMIN-"].bind("<Return>","_ENTER")
window["-CPT_RMAX-"].bind("<Return>","_ENTER")
window["-CPT_HL-"].bind("<Return>","_ENTER")
window["-CPT_RMAX-"].bind("<Return>","_ENTER")
window["-CPT_SPHI-"].bind("<Return>","_ENTER")
window["-CPT_DPHI-"].bind("<Return>","_ENTER")
window["-CPT_TX-"].bind("<Return>","_ENTER")
window["-CPT_TY-"].bind("<Return>","_ENTER")
window["-CPT_TZ-"].bind("<Return>","_ENTER")
window["-CPT_RX-"].bind("<Return>","_ENTER")

window["-CPB_TYPE-"].bind("<Return>","_ENTER")
window["-CPB_MAT-"].bind("<Return>","_ENTER")
window["-CPB_RMIN-"].bind("<Return>","_ENTER")
window["-CPB_RMAX-"].bind("<Return>","_ENTER")
window["-CPB_HL-"].bind("<Return>","_ENTER")
window["-CPB_RMAX-"].bind("<Return>","_ENTER")
window["-CPB_SPHI-"].bind("<Return>","_ENTER")
window["-CPB_DPHI-"].bind("<Return>","_ENTER")
window["-CPB_TX-"].bind("<Return>","_ENTER")
window["-CPB_TY-"].bind("<Return>","_ENTER")
window["-CPB_TZ-"].bind("<Return>","_ENTER")
window["-CPB_RX-"].bind("<Return>","_ENTER")

window["-CPL_TYPE-"].bind("<Return>","_ENTER")
window["-CPL_MAT-"].bind("<Return>","_ENTER")
window["-CPL_RMIN-"].bind("<Return>","_ENTER")
window["-CPL_RMAX-"].bind("<Return>","_ENTER")
window["-CPL_HL-"].bind("<Return>","_ENTER")
window["-CPL_RMAX-"].bind("<Return>","_ENTER")
window["-CPL_SPHI-"].bind("<Return>","_ENTER")
window["-CPL_DPHI-"].bind("<Return>","_ENTER")
window["-CPL_TX-"].bind("<Return>","_ENTER")
window["-CPL_TY-"].bind("<Return>","_ENTER")
window["-CPL_TZ-"].bind("<Return>","_ENTER")
window["-CPL_RX-"].bind("<Return>","_ENTER")

window["-CPR_TYPE-"].bind("<Return>","_ENTER")
window["-CPR_MAT-"].bind("<Return>","_ENTER")
window["-CPR_RMIN-"].bind("<Return>","_ENTER")
window["-CPR_RMAX-"].bind("<Return>","_ENTER")
window["-CPR_HL-"].bind("<Return>","_ENTER")
window["-CPR_RMAX-"].bind("<Return>","_ENTER")
window["-CPR_SPHI-"].bind("<Return>","_ENTER")
window["-CPR_DPHI-"].bind("<Return>","_ENTER")
window["-CPR_TX-"].bind("<Return>","_ENTER")
window["-CPR_TY-"].bind("<Return>","_ENTER")
window["-CPR_TZ-"].bind("<Return>","_ENTER")
window["-CPR_RX-"].bind("<Return>","_ENTER")

window["-TLEZB-"].bind("<Return>","_ENTER")
window["-DTMZB-"].bind("<Return>","_ENTER")
window["-DTWZB-"].bind("<Return>","_ENTER")
#window["-DTMDZB-"].bind("<Return>","_ENTER")

window["-PHYLST-"].bind("<Return>","_ENTER")
window["-PHYPRO-"].bind("<Return>","_ENTER")
window["-PHYDEFTY-"].bind("<Return>","_ENTER")
window["-PHYDEFMO-"].bind("<Return>","_ENTER")
window["-PHYEMIN-"].bind("<Return>","_ENTER")
window["-PHYEMAX-"].bind("<Return>","_ENTER")
window["-ROTTY-"].bind("<Return>","_ENTER")
window["-ROTPAR-"].bind("<Return>","_ENTER")

window["-ROTROTX-"].bind("<Return>","_ENTER")
window["-ROTROTY-"].bind("<Return>","_ENTER")
window["-ROTROTZ-"].bind("<Return>","_ENTER")
window["-ROTTRANSX-"].bind("<Return>","_ENTER")
window["-ROTTRANSY-"].bind("<Return>","_ENTER")
window["-ROTTRANSZ-"].bind("<Return>","_ENTER")
window["-COLLVERTY-"].bind("<Return>","_ENTER")
window["-COLLVERPAR-"].bind("<Return>","_ENTER")
window["-COLLVERROTX-"].bind("<Return>","_ENTER")
window["-COLLVERROTY-"].bind("<Return>","_ENTER")
window["-COLLVERROTZ-"].bind("<Return>","_ENTER")
window["-COLLVERTRANSZ-"].bind("<Return>","_ENTER")
window["-COLLHORPAR-"].bind("<Return>","_ENTER")
window["-COLLHORROTX-"].bind("<Return>","_ENTER")
window["-COLLHORROTY-"].bind("<Return>","_ENTER")
window["-COLLHORROTZ-"].bind("<Return>","_ENTER")
window["-COLLHORTRANSZ-"].bind("<Return>","_ENTER")

window["-TITTY-"].bind("<Return>","_ENTER")
window["-TITPAR-"].bind("<Return>","_ENTER")
window["-TITROTX-"].bind("<Return>","_ENTER")
window["-TITROTY-"].bind("<Return>","_ENTER")
window["-TITROTZ-"].bind("<Return>","_ENTER")
window["-TITTRANSZ-"].bind("<Return>","_ENTER")

window["-BFTY-"].bind("<Return>","_ENTER")
window["-BFPAR-"].bind("<Return>","_ENTER")
window["-BFROTX-"].bind("<Return>","_ENTER")
window["-BFROTY-"].bind("<Return>","_ENTER")
window["-BFROTZ-"].bind("<Return>","_ENTER")
window["-BFTRANSX-"].bind("<Return>","_ENTER")
window["-BFTRANSY-"].bind("<Return>","_ENTER")
window["-BFTRANSZ-"].bind("<Return>","_ENTER")

window["-Coll1TY-"].bind("<Return>","_ENTER")
window["-Coll1PAR-"].bind("<Return>","_ENTER")
window["-Coll1MAT-"].bind("<Return>","_ENTER")
window["-Coll1ROTX-"].bind("<Return>","_ENTER")
window["-Coll1ROTY-"].bind("<Return>","_ENTER")
window["-Coll1ROTZ-"].bind("<Return>","_ENTER")
window["-Coll1TRANSX-"].bind("<Return>","_ENTER")
window["-Coll1TRANSY-"].bind("<Return>","_ENTER")
window["-Coll1TRANSZ-"].bind("<Return>","_ENTER")
window["-Coll1LZ-"].bind("<Return>","_ENTER")
window["-Coll1LY-"].bind("<Return>","_ENTER")
window["-Coll1LX-"].bind("<Return>","_ENTER")
window["-Coll1LTX-"].bind("<Return>","_ENTER")

window["-Coll2TY-"].bind("<Return>","_ENTER")
window["-Coll2PAR-"].bind("<Return>","_ENTER")
window["-Coll2MAT-"].bind("<Return>","_ENTER")
window["-Coll2ROTX-"].bind("<Return>","_ENTER")
window["-Coll2ROTY-"].bind("<Return>","_ENTER")
window["-Coll2ROTZ-"].bind("<Return>","_ENTER")
window["-Coll2TRANSX-"].bind("<Return>","_ENTER")
window["-Coll2TRANSY-"].bind("<Return>","_ENTER")
window["-Coll2TRANSZ-"].bind("<Return>","_ENTER")
window["-Coll2LZ-"].bind("<Return>","_ENTER")
window["-Coll2LY-"].bind("<Return>","_ENTER")
window["-Coll2LX-"].bind("<Return>","_ENTER")
window["-Coll2LTX-"].bind("<Return>","_ENTER")

window["-Coll3TY-"].bind("<Return>","_ENTER")
window["-Coll3PAR-"].bind("<Return>","_ENTER")
window["-Coll3MAT-"].bind("<Return>","_ENTER")
window["-Coll3ROTX-"].bind("<Return>","_ENTER")
window["-Coll3ROTY-"].bind("<Return>","_ENTER")
window["-Coll3ROTZ-"].bind("<Return>","_ENTER")
window["-Coll3TRANSX-"].bind("<Return>","_ENTER")
window["-Coll3TRANSY-"].bind("<Return>","_ENTER")
window["-Coll3TRANSZ-"].bind("<Return>","_ENTER")
window["-Coll3LZ-"].bind("<Return>","_ENTER")
window["-Coll3LY-"].bind("<Return>","_ENTER")
window["-Coll3LX-"].bind("<Return>","_ENTER")
window["-Coll3LTX-"].bind("<Return>","_ENTER")

window["-Coll4TY-"].bind("<Return>","_ENTER")
window["-Coll4PAR-"].bind("<Return>","_ENTER")
window["-Coll4MAT-"].bind("<Return>","_ENTER")
window["-Coll4ROTX-"].bind("<Return>","_ENTER")
window["-Coll4ROTY-"].bind("<Return>","_ENTER")
window["-Coll4ROTZ-"].bind("<Return>","_ENTER")
window["-Coll4TRANSX-"].bind("<Return>","_ENTER")
window["-Coll4TRANSY-"].bind("<Return>","_ENTER")
window["-Coll4TRANSZ-"].bind("<Return>","_ENTER")
window["-Coll4LZ-"].bind("<Return>","_ENTER")
window["-Coll4LY-"].bind("<Return>","_ENTER")
window["-Coll4LX-"].bind("<Return>","_ENTER")
window["-Coll4LTX-"].bind("<Return>","_ENTER")

window["-Coll1steelMAT-"].bind("<Return>","_ENTER")
window["-Coll1steelPAR-"].bind("<Return>","_ENTER")
window["-Coll1steelTY-"].bind("<Return>","_ENTER")
window["-Coll1steelROTX-"].bind("<Return>","_ENTER")
window["-Coll1steelROTY-"].bind("<Return>","_ENTER")
window["-Coll1steelROTZ-"].bind("<Return>","_ENTER")
window["-Coll1steelTRANSX-"].bind("<Return>","_ENTER")
window["-Coll1steelTRANSY-"].bind("<Return>","_ENTER")
window["-Coll1steelTRANSZ-"].bind("<Return>","_ENTER")
window["-Coll1steelLZ-"].bind("<Return>","_ENTER")
window["-Coll1steelLY-"].bind("<Return>","_ENTER")
window["-Coll1steelLX-"].bind("<Return>","_ENTER")
window["-Coll1steelLTX-"].bind("<Return>","_ENTER")

window["-Coll2steelTY-"].bind("<Return>","_ENTER")
window["-Coll2steelPAR-"].bind("<Return>","_ENTER")
window["-Coll2steelMAT-"].bind("<Return>","_ENTER")
window["-Coll2steelROTX-"].bind("<Return>","_ENTER")
window["-Coll2steelROTY-"].bind("<Return>","_ENTER")
window["-Coll2steelROTZ-"].bind("<Return>","_ENTER")
window["-Coll2steelTRANSX-"].bind("<Return>","_ENTER")
window["-Coll2steelTRANSY-"].bind("<Return>","_ENTER")
window["-Coll2steelTRANSZ-"].bind("<Return>","_ENTER")
window["-Coll2steelLZ-"].bind("<Return>","_ENTER")
window["-Coll2steelLY-"].bind("<Return>","_ENTER")
window["-Coll2steelLX-"].bind("<Return>","_ENTER")
window["-Coll2steelLTX-"].bind("<Return>","_ENTER")

window["-Coll3steelTY-"].bind("<Return>","_ENTER")
window["-Coll3steelPAR-"].bind("<Return>","_ENTER")
window["-Coll3steelMAT-"].bind("<Return>","_ENTER")
window["-Coll3steelROTX-"].bind("<Return>","_ENTER")
window["-Coll3steelROTY-"].bind("<Return>","_ENTER")
window["-Coll3steelROTZ-"].bind("<Return>","_ENTER")
window["-Coll3steelTRANSX-"].bind("<Return>","_ENTER")
window["-Coll3steelTRANSY-"].bind("<Return>","_ENTER")
window["-Coll3steelTRANSZ-"].bind("<Return>","_ENTER")
window["-Coll3steelLZ-"].bind("<Return>","_ENTER")
window["-Coll3steelLY-"].bind("<Return>","_ENTER")
window["-Coll3steelLX-"].bind("<Return>","_ENTER")
window["-Coll3steelLTX-"].bind("<Return>","_ENTER")
window["-Coll4steelTY-"].bind("<Return>","_ENTER")
window["-Coll4steelPAR-"].bind("<Return>","_ENTER")
window["-Coll4steelMAT-"].bind("<Return>","_ENTER")
window["-Coll4steelROTX-"].bind("<Return>","_ENTER")
window["-Coll4steelROTY-"].bind("<Return>","_ENTER")
window["-Coll4steelROTZ-"].bind("<Return>","_ENTER")
window["-Coll4steelTRANSX-"].bind("<Return>","_ENTER")
window["-Coll4steelTRANSY-"].bind("<Return>","_ENTER")
window["-Coll4steelTRANSZ-"].bind("<Return>","_ENTER")
window["-Coll4steelLZ-"].bind("<Return>","_ENTER")
window["-Coll4steelLY-"].bind("<Return>","_ENTER")
window["-Coll4steelLX-"].bind("<Return>","_ENTER")
window["-Coll4steelLTX-"].bind("<Return>","_ENTER")

window["-TITFILTY-"].bind("<Return>","_ENTER")
window["-TITFILPAR-"].bind("<Return>","_ENTER")
window["-TITFILMAT-"].bind("<Return>","_ENTER")
window["-TITFILROTX-"].bind("<Return>","_ENTER")
window["-TITFILROTY-"].bind("<Return>","_ENTER")
window["-TITFILROTZ-"].bind("<Return>","_ENTER")
window["-TITFILTRANSX-"].bind("<Return>","_ENTER")
window["-TITFILTRANSY-"].bind("<Return>","_ENTER")
window["-TITFILTRANSZ-"].bind("<Return>","_ENTER")
window["-TITFILHLZ-"].bind("<Return>","_ENTER")
window["-TITFILHLY-"].bind("<Return>","_ENTER")
window["-TITFILHLX-"].bind("<Return>","_ENTER")

window["-DEMOFLATTY-"].bind("<Return>","_ENTER")
window["-DEMOFLATPAR-"].bind("<Return>","_ENTER")
window["-DEMOFLATMAT-"].bind("<Return>","_ENTER")
window["-DEMOFLATROTX-"].bind("<Return>","_ENTER")
window["-DEMOFLATROTY-"].bind("<Return>","_ENTER")
window["-DEMOFLATROTZ-"].bind("<Return>","_ENTER")
window["-DEMOFLATTRANSX-"].bind("<Return>","_ENTER")
window["-DEMOFLATTRANSY-"].bind("<Return>","_ENTER")
window["-DEMOFLATTRANSZ-"].bind("<Return>","_ENTER")
window["-DEMOFLATHLZ-"].bind("<Return>","_ENTER")
window["-DEMOFLATHLY-"].bind("<Return>","_ENTER")
window["-DEMOFLATHLX-"].bind("<Return>","_ENTER")

window["-TSBTY-"].bind("<Return>","_ENTER")
window["-TSBPAR-"].bind("<Return>","_ENTER")
window["-TSBMAT-"].bind("<Return>","_ENTER")
window["-TSBROTX-"].bind("<Return>","_ENTER")
window["-TSBROTY-"].bind("<Return>","_ENTER")
window["-TSBROTZ-"].bind("<Return>","_ENTER")
window["-TSBTRANSX-"].bind("<Return>","_ENTER")
window["-TSBTRANSY-"].bind("<Return>","_ENTER")
window["-TSBTRANSZ-"].bind("<Return>","_ENTER")
window["-TSBHLZ-"].bind("<Return>","_ENTER")
window["-TSBHLY-"].bind("<Return>","_ENTER")
window["-TSBHLX-"].bind("<Return>","_ENTER")

window["-BSBTY-"].bind("<Return>","_ENTER")
window["-BSBPAR-"].bind("<Return>","_ENTER")
window["-BSBMAT-"].bind("<Return>","_ENTER")
window["-BSBROTX-"].bind("<Return>","_ENTER")
window["-BSBROTY-"].bind("<Return>","_ENTER")
window["-BSBROTZ-"].bind("<Return>","_ENTER")
window["-BSBTRANSX-"].bind("<Return>","_ENTER")
window["-BSBTRANSY-"].bind("<Return>","_ENTER")
window["-BSBTRANSZ-"].bind("<Return>","_ENTER")
window["-BSBHLZ-"].bind("<Return>","_ENTER")
window["-BSBHLY-"].bind("<Return>","_ENTER")
window["-BSBHLX-"].bind("<Return>","_ENTER")

window["-COUCHTY-"].bind("<Return>","_ENTER")
window["-COUCHPAR-"].bind("<Return>","_ENTER")
window["-COUCHMAT-"].bind("<Return>","_ENTER")
window["-COUCHTRANSX-"].bind("<Return>","_ENTER")
window["-COUCHTRANSY-"].bind("<Return>","_ENTER")
window["-COUCHTRANSZ-"].bind("<Return>","_ENTER")
window["-COUCHHLZ-"].bind("<Return>","_ENTER")
window["-COUCHHLY-"].bind("<Return>","_ENTER")
window["-COUCHHLX-"].bind("<Return>","_ENTER")

window["-BEAMGRPTY-"].bind("<Return>","_ENTER")
window["-BEAMGRPPAR-"].bind("<Return>","_ENTER")
window["-BEAMGRPTRANSX-"].bind("<Return>","_ENTER")
window["-BEAMGRPTRANSY-"].bind("<Return>","_ENTER")
window["-BEAMGRPTRANSZ-"].bind("<Return>","_ENTER")
window["-BEAMGRPROTZ-"].bind("<Return>","_ENTER")
window["-BEAMGRPROTY-"].bind("<Return>","_ENTER")
window["-BEAMGRPROTX-"].bind("<Return>","_ENTER")

window["-BEAMSPECTY-"].bind("<Return>","_ENTER")
window["-BEAMTY-"].bind("<Return>","_ENTER")
window["-BEAMCOMPO-"].bind("<Return>","_ENTER")
window["-BEAMPAR-"].bind("<Return>","_ENTER")
window["-BEAMGRPTRANSZ-"].bind("<Return>","_ENTER")
window["-BEAMPOSDISTRO-"].bind("<Return>","_ENTER")
window["-BEAMPOSHAPE-"].bind("<Return>","_ENTER")
window["-BEAMSPOSANGDISTRO-"].bind("<Return>","_ENTER")
window["-BEAMPOSCUTOFFX-"].bind("<Return>","_ENTER")
window["-BEAMPOSCUTTOFFY-"].bind("<Return>","_ENTER")
window["-BEAMPOSSPRDX-"].bind("<Return>","_ENTER")
window["-BEAMPOSSPRDY-"].bind("<Return>","_ENTER")
window["-BEAMPOSANGCUTOFFX-"].bind("<Return>","_ENTER")
window["-BEAMPOSANGCUTOFFY-"].bind("<Return>","_ENTER")
window["-BEAMPOSANGSPREADX-"].bind("<Return>","_ENTER")
window["-BEAMPOSANGSPREADY-"].bind("<Return>","_ENTER")
window["-TIMEROTFUNC-"].bind("<Return>","_ENTER")
window["-TIMESEQ-"].bind("<Return>","_ENTER")
window["-TIMELINEEND-"].bind("<Return>","_ENTER")
window["-COUCHTRANSZ-"].bind("<Return>","_ENTER")
window["-TIMEROTRATE-"].bind("<Return>","_ENTER")
window["-TIMEROTSTART-"].bind("<Return>","_ENTER")
window["-TIMEHISTINT-"].bind("<Return>","_ENTER")
#default we will have 5 positions-chamberplugs and 3 quantities to score
#this variable has to be outside of the while loop because after the RUN event updates
#variable, the while loop continues to run and therefore it gets reassigned to 15 again
#interestingly, this means the while loop continues to loop (again and again) even as the  
#simulation subprocess is still running. if no other buttons get triggered while it loops
#then no if block statement will run. though when the subprocess runs, the GUI seems to block 
#all buttons and inputs
num_of_csvresult = 15 

while True:
    event,values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '-MAINFOLDERNAME-_ENTER':
        #default path
        path = values['-MAINFOLDERNAME-']
        print(path)

    if event == '-GEN-':
        command = ["python3 generate_allproc.py"]
        subprocess.run(command, shell=True)
        print(command)

    if event == '-G4FOLDERNAME-_ENTER':
        # print(str(values['-G4FOLDERNAME-']))
        # replacement_floatorint("G4DataDirectory = \'\""+G4_Data+"\"\'",
        #                        "G4DataDirectory = \'\""+str(values['-G4FOLDERNAME-'])+"\"\'")
        G4_Data = values['-G4FOLDERNAME-'] 

    if event == '-DUPGENPROC-':
        original_file_path = path + '/generate_allproc_boilerplate.py'
        duplicate_gen_file_name = "generate_allproc.py"
        directory_path = os.path.dirname(original_file_path)
        duplicate_gen_file_path = os.path.join(directory_path, duplicate_gen_file_name)
        shutil.copy(original_file_path, duplicate_gen_file_path)

        replaced_content=""
        all_proc = open(path + '/generate_allproc.py', "r")
        for line in all_proc:
            line.strip()
            
            new_line  = line.replace("test_boilerplate_path_change_G4",
                                    f"{G4_Data}")
            replaced_content = replaced_content + new_line 
        all_proc.close()
        write_file = open(path + '/generate_allproc.py', "w")
        write_file.write(replaced_content)
        write_file.close()
        # This code is inefficient, runs more lines than required 

    if event == '-DUPMULPROC-':
        original_file_path = path + '/runfolder/topas_multiproc_boilerplate.py'
        duplicate_multiproc_file_name = "topas_multiproc.py"
        directory_path = os.path.dirname(original_file_path)
        duplicate_multiproc_file_path = os.path.join(directory_path, duplicate_multiproc_file_name)
        shutil.copy(original_file_path, duplicate_multiproc_file_path)

        replaced_content=""
        multi_proc = open(path + '/runfolder/topas_multiproc.py', "r")
        for line in multi_proc:
            line.strip()
            
            new_line  = line.replace("test_boilerplate_path_change_topas",
                                    f"{topas_application_path}")
            replaced_content = replaced_content + new_line 
        multi_proc.close()
        write_file = open(path + '/runfolder/topas_multiproc.py', "w")
        write_file.write(replaced_content)
        write_file.close()
        # This code is inefficient, runs more lines than required 

    if event == '-TOPAS-_ENTER':
        topas_application_path = values['-TOPAS-'] + " "

    if event == '-SEED-_ENTER':
        replacement_witherrorhandling_forintegers(values['-SEED-'],
                                                  "Seed = \'9\'",
                                                  "Seed = "+"\'"+str(values['-SEED-'])+"\'",
                                                  "#Seed_start,Seed_stop,Seed_step = 0,0,0",
                                                  "#boundaries_list.append([Seed_start",
                                                  "#boundaries_name_list.append(['Seed'])+",
                                                  "#Seed,i=str(int(values[i])),i+1")

    if event == '-THREAD-_ENTER':
        replacement_witherrorhandling_forintegers(values['-THREAD-'],
                                                  "NumberOfThreads = \'4\'",
                                                  "NumberOfThreads = \'"+str(values['-THREAD-'])+"\'",
                                                  "#NumberOfThreads_start,NumberOfThreads_stop,NumberOfThreads_step = 0,0,0",
                                                  "#boundaries_list.append([NumberOfThreads_start",
                                                  "#boundaries_name_list.append(['NumberOfThreads'])+",
                                                  "#NumberOfThreads,i=str(int(values[i])),i+1")
        
    if event == '-HIST-_ENTER':
        replacement_witherrorhandling_forintegers(values['-HIST-'],
                                                  "beam_NumberOfHistoriesInRun=\"100000\"",
                                                  "beam_NumberOfHistoriesInRun=\""+str(values['-HIST-'])+"\"",
                                                  "#beam_NumberOfHistoriesInRun_start,beam_NumberOfHistoriesInRun_stop,beam_NumberOfHistoriesInRun_step = 0,0,0",
                                                  "#boundaries_list.append([beam_NumberOfHistoriesInRun_start",
                                                  "#boundaries_name_list.append(['beam_NumberOfHistoriesInRun'])+",
                                                  "#beam_NumberOfHistoriesInRun,i=str(int(values[i])),i+1")
    if event == '-CPC_TYPE-_ENTER':
        try:
            int(values['-CPC_TYPE-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except:
            replacement_floatorint("ChamberPlugCentre_Type=\'\"TsCylinder\"\'",
                               "ChamberPlugCentre_Type=\'\""+str(values['-CPC_TYPE-'])+"\"\'")

    if event == '-CPC_MAT-_ENTER':
        try:
            int(values['-CPC_MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("ChamberPlugCentre_Material=\'\"PMMA\"\'",
                                   "ChamberPlugCentre_Material=\'\""+str(values['-CPC_MAT-'])+"\"\'")

    if event == '-CPC_RMIN-_ENTER':
        replacement_witherrorhandling(values['-CPC_RMIN-'],
                                      "ChamberPlugCentre_RMin=\"0.0\"",
                                      "ChamberPlugCentre_RMin=\""+str(values['-CPC_RMIN-'])+"\""
                                      "#ChamberPlugCentre_RMin_start,ChamberPlugCentre_RMin_stop,ChamberPlugCentre_RMin_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_RMin_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_RMin']",
                                      "#ChamberPlugCentre_RMin,i=str(values[i]),i+1")
        
    if event == '-CPC_RMAX-_ENTER':
        replacement_witherrorhandling(values['-CPC_RMAX-'],
                                      "ChamberPlugCentre_RMax=\"0.655\"",
                                      "ChamberPlugCentre_RMax=\""+str(values['-CPC_RMAX-'])+"\"",
                                      "#ChamberPlugCentre_RMax_start,ChamberPlugCentre_RMax_stop,ChamberPlugCentre_RMax_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_RMax_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_RMax']",
                                      "#ChamberPlugCentre_RMax,i=str(values[i]),i+1")
        
    if event == '-CPC_HL-_ENTER':
        replacement_witherrorhandling(values['-CPC_HL-'],
                                      "ChamberPlugCentre_HL=\"5.0\"",
                                      "ChamberPlugCentre_HL=\""+str(values['-CPC_HL-'])+"\"",
                                      "#ChamberPlugCentre_HL_start,ChamberPlugCentre_HL_stop,ChamberPlugCentre_HL_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_HL_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_HL']",
                                      "#ChamberPlugCentre_HL,i=str(values[i]),i+1")

    if event == '-CPC_SPHI-_ENTER':
        replacement_witherrorhandling(values['-CPC_SPHI-'],
                                      "ChamberPlugCentre_SPhi=\"0.\"",
                                      "ChamberPlugCentre_SPhi=\""+str(values['-CPC_SPHI-'])+"\"",
                                      "#ChamberPlugCentre_SPhi_start,ChamberPlugCentre_SPhi_stop,ChamberPlugCentre_SPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_SPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_SPhi']",
                                      "#ChamberPlugCentre_SPhi,i=str(values[i]),i+1")

    if event == '-CPC_DPHI-_ENTER':
        replacement_witherrorhandling(values['-CPC_DPHI-'],
                                      "ChamberPlugCentre_DPhi=\"360.\"",
                                      "ChamberPlugCentre_DPhi=\""+str(values['-CPC_DPHI-'])+"\"",
                                      "#ChamberPlugCentre_DPhi_start,ChamberPlugCentre_DPhi_stop,ChamberPlugCentre_DPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_DPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_DPhi'])+",
                                      "#ChamberPlugCentre_DPhi,i=str(values[i]),i+1")

    if event == '-CPC_TX-_ENTER':
        replacement_witherrorhandling(values['-CPC_TX-'],
                                      "ChamberPlugCentre_TransX=\"0.0\"",
                                      "ChamberPlugCentre_TransX=\""+str(values['-CPC_TX-'])+"\"",
                                      "#ChamberPlugCentre_TransX_start,ChamberPlugCentre_TransX_stop,ChamberPlugCentre_TransX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_TransX_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_TransX'])+",
                                      "#ChamberPlugCentre_TransX,i=str(values[i]),i+1")

    if event == '-CPC_TY-_ENTER':
        replacement_witherrorhandling(values['-CPC_TY-'],
                                      "ChamberPlugCentre_TransY=\"0.0\"",
                                      "ChamberPlugCentre_TransY=\""+str(values['-CPC_TY-'])+"\"",
                                      "#ChamberPlugCentre_TransY_start,ChamberPlugCentre_TransY_stop,ChamberPlugCentre_TransY_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_TransY_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_TransY'])+",
                                      "#ChamberPlugCentre_TransY,i=str(values[i]),i+1")

    if event == '-CPC_TZ-_ENTER':
        replacement_witherrorhandling(values['-CPC_TZ-'],
                                      "ChamberPlugCentre_TransZ=\"0.0\"",
                                      "ChamberPlugCentre_TransZ=\""+str(values['-CPC_TZ-'])+"\"",
                                      "#ChamberPlugCentre_TransZ_start,ChamberPlugCentre_TransZ_stop,ChamberPlugCentre_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_TransZ_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_TransZ'])+",
                                      "#ChamberPlugCentre_TransZ,i=str(values[i]),i+1")

    if event == '-CPC_RX-_ENTER':
        replacement_witherrorhandling(values['-CPC_RX-'],
                                      "ChamberPlugCentre_RotX=\"-90\"",
                                      "ChamberPlugCentre_RotX=\""+str(values['-CPC_RX-'])+"\"",
                                      "#ChamberPlugCentre_RotX_start,ChamberPlugCentre_RotX_stop,ChamberPlugCentre_RotX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugCentre_RotX_start",
                                      "#boundaries_name_list.append(['ChamberPlugCentre_RotX'])+",
                                      "#ChamberPlugCentre_RotX,i=str(values[i]),i+1")

    if event == '-CPT_TYPE-_ENTER':
        try:
            int(values['-CPT_TYPE-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except:
            replacement_floatorint("ChamberPlugTop_Type=\'\"TsCylinder\"\'",
                               "ChamberPlugTop_Type=\'\""+str(values['-CPT_TYPE-'])+"\"\'")

    if event == '-CPT_MAT-_ENTER':
        try:
            int(values['-CPT_MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("ChamberPlugTop_Material=\'\"PMMA\"\'",
                                   "ChamberPlugTop_Material=\'\""+str(values['-CPT_MAT-'])+"\"\'")

    if event == '-CPT_RMIN-_ENTER':
        replacement_witherrorhandling(values['-CPT_RMIN-'],
                                      "ChamberPlugTop_RMin=\"0.0\"",
                                      "ChamberPlugTop_RMin=\""+str(values['-CPT_RMIN-'])+"\""
                                      "#ChamberPlugTop_RMin_start,ChamberPlugTop_RMin_stop,ChamberPlugTop_RMin_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_RMin_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_RMin']",
                                      "#ChamberPlugTop_RMin,i=str(values[i]),i+1")
        
    if event == '-CPT_RMAX-_ENTER':
        replacement_witherrorhandling(values['-CPT_RMAX-'],
                                      "ChamberPlugTop_RMax=\"0.655\"",
                                      "ChamberPlugTop_RMax=\""+str(values['-CPT_RMAX-'])+"\"",
                                      "#ChamberPlugTop_RMax_start,ChamberPlugTop_RMax_stop,ChamberPlugTop_RMax_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_RMax_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_RMax']",
                                      "#ChamberPlugTop_RMax,i=str(values[i]),i+1")
        
    if event == '-CPT_HL-_ENTER':
        replacement_witherrorhandling(values['-CPT_HL-'],
                                      "ChamberPlugTop_HL=\"5.0\"",
                                      "ChamberPlugTop_HL=\""+str(values['-CPT_HL-'])+"\"",
                                      "#ChamberPlugTop_HL_start,ChamberPlugTop_HL_stop,ChamberPlugTop_HL_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_HL_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_HL']",
                                      "#ChamberPlugTop_HL,i=str(values[i]),i+1")

    if event == '-CPT_SPHI-_ENTER':
        replacement_witherrorhandling(values['-CPT_SPHI-'],
                                      "ChamberPlugTop_SPhi=\"0.\"",
                                      "ChamberPlugTop_SPhi=\""+str(values['-CPT_SPHI-'])+"\"",
                                      "#ChamberPlugTop_SPhi_start,ChamberPlugTop_SPhi_stop,ChamberPlugTop_SPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_SPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_SPhi']",
                                      "#ChamberPlugTop_SPhi,i=str(values[i]),i+1")

    if event == '-CPT_DPHI-_ENTER':
        replacement_witherrorhandling(values['-CPT_DPHI-'],
                                      "ChamberPlugTop_DPhi=\"360.\"",
                                      "ChamberPlugTop_DPhi=\""+str(values['-CPT_DPHI-'])+"\"",
                                      "#ChamberPlugTop_DPhi_start,ChamberPlugTop_DPhi_stop,ChamberPlugTop_DPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_DPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_DPhi'])+",
                                      "#ChamberPlugTop_DPhi,i=str(values[i]),i+1")

    if event == '-CPT_TX-_ENTER':
        replacement_witherrorhandling(values['-CPT_TX-'],
                                      "ChamberPlugTop_TransX=\"0.0\"",
                                      "ChamberPlugTop_TransX=\""+str(values['-CPT_TX-'])+"\"",
                                      "#ChamberPlugTop_TransX_start,ChamberPlugTop_TransX_stop,ChamberPlugTop_TransX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_TransX_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_TransX'])+",
                                      "#ChamberPlugTop_TransX,i=str(values[i]),i+1")

    if event == '-CPT_TY-_ENTER':
        replacement_witherrorhandling(values['-CPT_TY-'],
                                      "ChamberPlugTop_TransY=\"0.0\"",
                                      "ChamberPlugTop_TransY=\""+str(values['-CPT_TY-'])+"\"",
                                      "#ChamberPlugTop_TransY_start,ChamberPlugTop_TransY_stop,ChamberPlugTop_TransY_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_TransY_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_TransY'])+",
                                      "#ChamberPlugTop_TransY,i=str(values[i]),i+1")

    if event == '-CPT_TZ-_ENTER':
        replacement_witherrorhandling(values['-CPT_TZ-'],
                                      "ChamberPlugTop_TransZ=\"-7.0\"",
                                      "ChamberPlugTop_TransZ=\""+str(values['-CPT_TZ-'])+"\"",
                                      "#ChamberPlugTop_TransZ_start,ChamberPlugTop_TransZ_stop,ChamberPlugTop_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_TransZ_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_TransZ'])+",
                                      "#ChamberPlugTop_TransZ,i=str(values[i]),i+1")

    if event == '-CPT_RX-_ENTER':
        replacement_witherrorhandling(values['-CPT_RX-'],
                                      "ChamberPlugTop_RotX=\"-90\"",
                                      "ChamberPlugTop_RotX=\""+str(values['-CPT_RX-'])+"\"",
                                      "#ChamberPlugTop_RotX_start,ChamberPlugTop_RotX_stop,ChamberPlugTop_RotX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugTop_RotX_start",
                                      "#boundaries_name_list.append(['ChamberPlugTop_RotX'])+",
                                      "#ChamberPlugTop_RotX,i=str(values[i]),i+1")
    if event == '-CPB_TYPE-_ENTER':
        try:
            int(values['-CPB_TYPE-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except:
            replacement_floatorint("ChamberPlugBottom_Type=\'\"TsCylinder\"\'",
                               "ChamberPlugBottom_Type=\'\""+str(values['-CPB_TYPE-'])+"\"\'")

    if event == '-CPB_MAT-_ENTER':
        try:
            int(values['-CPB_MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("ChamberPlugBottom_Material=\'\"PMMA\"\'",
                                   "ChamberPlugBottom_Material=\'\""+str(values['-CPB_MAT-'])+"\"\'")

    if event == '-CPB_RMIN-_ENTER':
        replacement_witherrorhandling(values['-CPB_RMIN-'],
                                      "ChamberPlugBottom_RMin=\"0.0\"",
                                      "ChamberPlugBottom_RMin=\""+str(values['-CPB_RMIN-'])+"\""
                                      "#ChamberPlugBottom_RMin_start,ChamberPlugBottom_RMin_stop,ChamberPlugBottom_RMin_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_RMin_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_RMin']",
                                      "#ChamberPlugBottom_RMin,i=str(values[i]),i+1")
        
    if event == '-CPB_RMAX-_ENTER':
        replacement_witherrorhandling(values['-CPB_RMAX-'],
                                      "ChamberPlugBottom_RMax=\"0.655\"",
                                      "ChamberPlugBottom_RMax=\""+str(values['-CPB_RMAX-'])+"\"",
                                      "#ChamberPlugBottom_RMax_start,ChamberPlugBottom_RMax_stop,ChamberPlugBottom_RMax_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_RMax_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_RMax']",
                                      "#ChamberPlugBottom_RMax,i=str(values[i]),i+1")
        
    if event == '-CPB_HL-_ENTER':
        replacement_witherrorhandling(values['-CPB_HL-'],
                                      "ChamberPlugBottom_HL=\"5.0\"",
                                      "ChamberPlugBottom_HL=\""+str(values['-CPB_HL-'])+"\"",
                                      "#ChamberPlugBottom_HL_start,ChamberPlugBottom_HL_stop,ChamberPlugBottom_HL_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_HL_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_HL']",
                                      "#ChamberPlugBottom_HL,i=str(values[i]),i+1")

    if event == '-CPB_SPHI-_ENTER':
        replacement_witherrorhandling(values['-CPB_SPHI-'],
                                      "ChamberPlugBottom_SPhi=\"0.\"",
                                      "ChamberPlugBottom_SPhi=\""+str(values['-CPB_SPHI-'])+"\"",
                                      "#ChamberPlugBottom_SPhi_start,ChamberPlugBottom_SPhi_stop,ChamberPlugBottom_SPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_SPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_SPhi']",
                                      "#ChamberPlugBottom_SPhi,i=str(values[i]),i+1")

    if event == '-CPB_DPHI-_ENTER':
        replacement_witherrorhandling(values['-CPB_DPHI-'],
                                      "ChamberPlugBottom_DPhi=\"360.\"",
                                      "ChamberPlugBottom_DPhi=\""+str(values['-CPB_DPHI-'])+"\"",
                                      "#ChamberPlugBottom_DPhi_start,ChamberPlugBottom_DPhi_stop,ChamberPlugBottom_DPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_DPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_DPhi'])+",
                                      "#ChamberPlugBottom_DPhi,i=str(values[i]),i+1")

    if event == '-CPB_TX-_ENTER':
        replacement_witherrorhandling(values['-CPB_TX-'],
                                      "ChamberPlugBottom_TransX=\"0.0\"",
                                      "ChamberPlugBottom_TransX=\""+str(values['-CPB_TX-'])+"\"",
                                      "#ChamberPlugBottom_TransX_start,ChamberPlugBottom_TransX_stop,ChamberPlugBottom_TransX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_TransX_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_TransX'])+",
                                      "#ChamberPlugBottom_TransX,i=str(values[i]),i+1")

    if event == '-CPB_TY-_ENTER':
        replacement_witherrorhandling(values['-CPB_TY-'],
                                      "ChamberPlugBottom_TransY=\"0.0\"",
                                      "ChamberPlugBottom_TransY=\""+str(values['-CPB_TY-'])+"\"",
                                      "#ChamberPlugBottom_TransY_start,ChamberPlugBottom_TransY_stop,ChamberPlugBottom_TransY_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_TransY_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_TransY'])+",
                                      "#ChamberPlugBottom_TransY,i=str(values[i]),i+1")

    if event == '-CPB_TZ-_ENTER':
        replacement_witherrorhandling(values['-CPB_TZ-'],
                                      "ChamberPlugBottom_TransZ=\"7.0\"",
                                      "ChamberPlugBottom_TransZ=\""+str(values['-CPB_TZ-'])+"\"",
                                      "#ChamberPlugBottom_TransZ_start,ChamberPlugBottom_TransZ_stop,ChamberPlugBottom_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_TransZ_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_TransZ'])+",
                                      "#ChamberPlugBottom_TransZ,i=str(values[i]),i+1")

    if event == '-CPB_RX-_ENTER':
        replacement_witherrorhandling(values['-CPB_RX-'],
                                      "ChamberPlugBottom_RotX=\"-90\"",
                                      "ChamberPlugBottom_RotX=\""+str(values['-CPB_RX-'])+"\"",
                                      "#ChamberPlugBottom_RotX_start,ChamberPlugBottom_RotX_stop,ChamberPlugBottom_RotX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugBottom_RotX_start",
                                      "#boundaries_name_list.append(['ChamberPlugBottom_RotX'])+",
                                      "#ChamberPlugBottom_RotX,i=str(values[i]),i+1")
    if event == '-CPL_TYPE-_ENTER':
        try:
            int(values['-CPL_TYPE-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except:
            replacement_floatorint("ChamberPlugLeft_Type=\'\"TsCylinder\"\'",
                               "ChamberPlugLeft_Type=\'\""+str(values['-CPL_TYPE-'])+"\"\'")

    if event == '-CPL_MAT-_ENTER':
        try:
            int(values['-CPL_MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("ChamberPlugLeft_Material=\'\"PMMA\"\'",
                                   "ChamberPlugLeft_Material=\'\""+str(values['-CPL_MAT-'])+"\"\'")

    if event == '-CPL_RMIN-_ENTER':
        replacement_witherrorhandling(values['-CPL_RMIN-'],
                                      "ChamberPlugLeft_RMin=\"0.0\"",
                                      "ChamberPlugLeft_RMin=\""+str(values['-CPL_RMIN-'])+"\""
                                      "#ChamberPlugLeft_RMin_start,ChamberPlugLeft_RMin_stop,ChamberPlugLeft_RMin_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_RMin_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_RMin']",
                                      "#ChamberPlugLeft_RMin,i=str(values[i]),i+1")
        
    if event == '-CPL_RMAX-_ENTER':
        replacement_witherrorhandling(values['-CPL_RMAX-'],
                                      "ChamberPlugLeft_RMax=\"0.655\"",
                                      "ChamberPlugLeft_RMax=\""+str(values['-CPL_RMAX-'])+"\"",
                                      "#ChamberPlugLeft_RMax_start,ChamberPlugLeft_RMax_stop,ChamberPlugLeft_RMax_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_RMax_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_RMax']",
                                      "#ChamberPlugLeft_RMax,i=str(values[i]),i+1")
        
    if event == '-CPL_HL-_ENTER':
        replacement_witherrorhandling(values['-CPL_HL-'],
                                      "ChamberPlugLeft_HL=\"5.0\"",
                                      "ChamberPlugLeft_HL=\""+str(values['-CPL_HL-'])+"\"",
                                      "#ChamberPlugLeft_HL_start,ChamberPlugLeft_HL_stop,ChamberPlugLeft_HL_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_HL_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_HL']",
                                      "#ChamberPlugLeft_HL,i=str(values[i]),i+1")

    if event == '-CPL_SPHI-_ENTER':
        replacement_witherrorhandling(values['-CPL_SPHI-'],
                                      "ChamberPlugLeft_SPhi=\"0.\"",
                                      "ChamberPlugLeft_SPhi=\""+str(values['-CPL_SPHI-'])+"\"",
                                      "#ChamberPlugLeft_SPhi_start,ChamberPlugLeft_SPhi_stop,ChamberPlugLeft_SPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_SPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_SPhi']",
                                      "#ChamberPlugLeft_SPhi,i=str(values[i]),i+1")

    if event == '-CPL_DPHI-_ENTER':
        replacement_witherrorhandling(values['-CPL_DPHI-'],
                                      "ChamberPlugLeft_DPhi=\"360.\"",
                                      "ChamberPlugLeft_DPhi=\""+str(values['-CPL_DPHI-'])+"\"",
                                      "#ChamberPlugLeft_DPhi_start,ChamberPlugLeft_DPhi_stop,ChamberPlugLeft_DPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_DPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_DPhi'])+",
                                      "#ChamberPlugLeft_DPhi,i=str(values[i]),i+1")

    if event == '-CPL_TX-_ENTER':
        replacement_witherrorhandling(values['-CPL_TX-'],
                                      "ChamberPlugLeft_TransX=\"-7.0\"",
                                      "ChamberPlugLeft_TransX=\""+str(values['-CPL_TX-'])+"\"",
                                      "#ChamberPlugLeft_TransX_start,ChamberPlugLeft_TransX_stop,ChamberPlugLeft_TransX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_TransX_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_TransX'])+",
                                      "#ChamberPlugLeft_TransX,i=str(values[i]),i+1")

    if event == '-CPL_TY-_ENTER':
        replacement_witherrorhandling(values['-CPL_TY-'],
                                      "ChamberPlugLeft_TransY=\"0.0\"",
                                      "ChamberPlugLeft_TransY=\""+str(values['-CPL_TY-'])+"\"",
                                      "#ChamberPlugLeft_TransY_start,ChamberPlugLeft_TransY_stop,ChamberPlugLeft_TransY_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_TransY_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_TransY'])+",
                                      "#ChamberPlugLeft_TransY,i=str(values[i]),i+1")

    if event == '-CPL_TZ-_ENTER':
        replacement_witherrorhandling(values['-CPL_TZ-'],
                                      "ChamberPlugLeft_TransZ=\"0.0\"",
                                      "ChamberPlugLeft_TransZ=\""+str(values['-CPL_TZ-'])+"\"",
                                      "#ChamberPlugLeft_TransZ_start,ChamberPlugLeft_TransZ_stop,ChamberPlugLeft_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_TransZ_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_TransZ'])+",
                                      "#ChamberPlugLeft_TransZ,i=str(values[i]),i+1")

    if event == '-CPL_RX-_ENTER':
        replacement_witherrorhandling(values['-CPL_RX-'],
                                      "ChamberPlugLeft_RotX=\"-90\"",
                                      "ChamberPlugLeft_RotX=\""+str(values['-CPL_RX-'])+"\"",
                                      "#ChamberPlugLeft_RotX_start,ChamberPlugLeft_RotX_stop,ChamberPlugLeft_RotX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugLeft_RotX_start",
                                      "#boundaries_name_list.append(['ChamberPlugLeft_RotX'])+",
                                      "#ChamberPlugLeft_RotX,i=str(values[i]),i+1")

    if event == '-CPR_TYPE-_ENTER':
        try:
            int(values['-CPR_TYPE-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except:
            replacement_floatorint("ChamberPlugRight_Type=\'\"TsCylinder\"\'",
                               "ChamberPlugRight_Type=\'\""+str(values['-CPR_TYPE-'])+"\"\'")

    if event == '-CPR_MAT-_ENTER':
        try:
            int(values['-CPR_MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("ChamberPlugRight_Material=\'\"PMMA\"\'",
                                   "ChamberPlugRight_Material=\'\""+str(values['-CPR_MAT-'])+"\"\'")

    if event == '-CPR_RMIN-_ENTER':
        replacement_witherrorhandling(values['-CPR_RMIN-'],
                                      "ChamberPlugRight_RMin=\"0.0\"",
                                      "ChamberPlugRight_RMin=\""+str(values['-CPR_RMIN-'])+"\""
                                      "#ChamberPlugRight_RMin_start,ChamberPlugRight_RMin_stop,ChamberPlugRight_RMin_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_RMin_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_RMin']",
                                      "#ChamberPlugRight_RMin,i=str(values[i]),i+1")
        
    if event == '-CPR_RMAX-_ENTER':
        replacement_witherrorhandling(values['-CPR_RMAX-'],
                                      "ChamberPlugRight_RMax=\"0.655\"",
                                      "ChamberPlugRight_RMax=\""+str(values['-CPR_RMAX-'])+"\"",
                                      "#ChamberPlugRight_RMax_start,ChamberPlugRight_RMax_stop,ChamberPlugRight_RMax_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_RMax_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_RMax']",
                                      "#ChamberPlugRight_RMax,i=str(values[i]),i+1")
        
    if event == '-CPR_HL-_ENTER':
        replacement_witherrorhandling(values['-CPR_HL-'],
                                      "ChamberPlugRight_HL=\"5.0\"",
                                      "ChamberPlugRight_HL=\""+str(values['-CPR_HL-'])+"\"",
                                      "#ChamberPlugRight_HL_start,ChamberPlugRight_HL_stop,ChamberPlugRight_HL_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_HL_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_HL']",
                                      "#ChamberPlugRight_HL,i=str(values[i]),i+1")

    if event == '-CPR_SPHI-_ENTER':
        replacement_witherrorhandling(values['-CPR_SPHI-'],
                                      "ChamberPlugRight_SPhi=\"0.\"",
                                      "ChamberPlugRight_SPhi=\""+str(values['-CPR_SPHI-'])+"\"",
                                      "#ChamberPlugRight_SPhi_start,ChamberPlugRight_SPhi_stop,ChamberPlugRight_SPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_SPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_SPhi']",
                                      "#ChamberPlugRight_SPhi,i=str(values[i]),i+1")

    if event == '-CPR_DPHI-_ENTER':
        replacement_witherrorhandling(values['-CPR_DPHI-'],
                                      "ChamberPlugRight_DPhi=\"360.\"",
                                      "ChamberPlugRight_DPhi=\""+str(values['-CPR_DPHI-'])+"\"",
                                      "#ChamberPlugRight_DPhi_start,ChamberPlugRight_DPhi_stop,ChamberPlugRight_DPhi_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_DPhi_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_DPhi'])",
                                      "#ChamberPlugRight_DPhi,i=str(values[i]),i+1")

    if event == '-CPR_TX-_ENTER':
        replacement_witherrorhandling(values['-CPR_TX-'],
                                      "ChamberPlugRight_TransX=\"7.0\"",
                                      "ChamberPlugRight_TransX=\""+str(values['-CPR_TX-'])+"\"",
                                      "#ChamberPlugRight_TransX_start,ChamberPlugRight_TransX_stop,ChamberPlugRight_TransX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_TransX_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_TransX'])",
                                      "#ChamberPlugRight_TransX,i=str(values[i]),i+1")

    if event == '-CPR_TY-_ENTER':
        replacement_witherrorhandling(values['-CPR_TY-'],
                                      "ChamberPlugRight_TransY=\"0.0\"",
                                      "ChamberPlugRight_TransY=\""+str(values['-CPR_TY-'])+"\"",
                                      "#ChamberPlugRight_TransY_start,ChamberPlugRight_TransY_stop,ChamberPlugRight_TransY_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_TransY_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_TransY'])",
                                      "#ChamberPlugRight_TransY,i=str(values[i]),i+1")

    if event == '-CPR_TZ-_ENTER':
        replacement_witherrorhandling(values['-CPR_TZ-'],
                                      "ChamberPlugRight_TransZ=\"0.0\"",
                                      "ChamberPlugRight_TransZ=\""+str(values['-CPR_TZ-'])+"\"",
                                      "#ChamberPlugRight_TransZ_start,ChamberPlugRight_TransZ_stop,ChamberPlugRight_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_TransZ_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_TransZ'])",
                                      "#ChamberPlugRight_TransZ,i=str(values[i]),i+1")

    if event == '-CPR_RX-_ENTER':
        replacement_witherrorhandling(values['-CPR_RX-'],
                                      "ChamberPlugRight_RotX=\"-90\"",
                                      "ChamberPlugRight_RotX=\""+str(values['-CPR_RX-'])+"\"",
                                      "#ChamberPlugRight_RotX_start,ChamberPlugRight_RotX_stop,ChamberPlugRight_RotX_step = 0,0,0",
                                      "#boundaries_list.append([ChamberPlugRight_RotX_start",
                                      "#boundaries_name_list.append(['ChamberPlugRight_RotX'])",
                                      "#ChamberPlugRight_RotX,i=str(values[i]),i+1")


    if event == '-TLEZB-_ENTER':
        replacement_witherrorhandling_forintegers(values['-TLEZB-'],
                                                  "ChamberPlugDose_tle_ZBins=\"100\"",
                                                  "ChamberPlugDose_tle_ZBins="+"\""+str(values['-TLEZB-'])+"\"",
                                                  "#ChamberPlugDose_tle_ZBins_start,ChamberPlugDose_tle_ZBins_stop,ChamberPlugDose_tle_ZBins_step = 0,0,0",
                                                  "#boundaries_list.append([ChamberPlugDose_tle_ZBins_start,",
                                                  "#boundaries_name_list.append(['ChamberPlugDose_tle_Zbins'])",
                                                  "#ChamberPlugDose_tle_Zbins,i=str(int(values[i])),i+1")
    if event == '-DTMZB-_ENTER':
        replacement_witherrorhandling_forintegers(values['-DTMZB-'],
                                                  "ChamberPlugDose_dtm_ZBins=\"100\"",
                                                  "ChamberPlugDose_dtm_ZBins="+"\""+str(values['-DTMZB-'])+"\"",
                                                  "#ChamberPlugDose_dtm_ZBins_start,ChamberPlugDose_dtm_ZBins_stop,ChamberPlugDose_dtm_ZBins_step = 0,0,0",
                                                  "#boundaries_list.append([ChamberPlugDose_dtm_ZBins_start,",
                                                  "#boundaries_name_list.append(['ChamberPlugDose_dtm_Zbins'])",
                                                  "#ChamberPlugDose_dtm_Zbins,i=str(int(values[i])),i+1")
    if event == '-DTWZB-_ENTER':
        replacement_witherrorhandling_forintegers(values['-DTWZB-'],
                                                  "ChamberPlugDose_dtw_ZBins=\"100\"",
                                                  "ChamberPlugDose_dtw_ZBins="+"\""+str(values['-DTWZB-'])+"\"",
                                                  "#ChamberPlugDose_dtw_ZBins_start,ChamberPlugDose_dtw_ZBins_stop,ChamberPlugDose_dtw_ZBins_step = 0,0,0",
                                                  "#boundaries_list.append([ChamberPlugDose_dtw_ZBins_start,",
                                                  "#boundaries_name_list.append(['ChamberPlugDose_dtw_Zbins'])",
                                                  "#ChamberPlugDose_dtw_Zbins,i=str(int(values[i])),i+1")
    if event == '-DTMDZB-_ENTER':
        replacement_witherrorhandling_forintegers(values['-DTMDZB-'],
                                                  "ChamberPlugDose_dtmd_ZBins=\"100\"",
                                                  "ChamberPlugDose_dtmd_ZBins="+"\""+str(values['-DTMDZB-'])+"\"",
                                                  "#ChamberPlugDose_dtmd_ZBins_start,ChamberPlugDose_dtmd_ZBins_stop,ChamberPlugDose_dtmd_ZBins_step = 0,0,0",
                                                  "#boundaries_list.append([ChamberPlugDose_dtmd_ZBins_start,",
                                                  "#boundaries_name_list.append(['ChamberPlugDose_dtmd_Zbins'])",
                                                  "#ChamberPlugDose_dtmd_Zbins,i=str(int(values[i])),i+1")

    if event == '-PHYLST-_ENTER':
        try:
            int(values['-PHYLST-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Name=\'\"Default\"\'",
                                   "Ph_ListName=\'\""+str(values['-PHYLST-'])+"\"\'")

    if event == '-PHYPRO-_ENTER':
        try:
            int(values['-PHYPRO-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Ph_ListProcesses=\'\"False\"\'",
                                   "Ph_ListProcesses=\'\""+str(values['-PHYPRO-'])+"\"\'")

    if event == '-PHYDEFTY-_ENTER':
        try:
            int(values['-PHYDEFTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Ph_Default_Type=\'\"Geant4_Modular\"\'",
                                   "Ph_Default_Type=\'\""+str(values['-PHYDEFTY-'])+"\"\'")
    if event == '-PHYDEFMO-_ENTER':
        try:
            int(values['-PHYDEFMO-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Ph_Default_Modules=\'6 \"g4em-standard_opt4\" \"g4h-phy_QGSP_BIC_HP\" \"g4decay\" \"g4ion-binarycascade\" \"g4h-elastic_HP\" \"g4stopping\"\'",
                                   "Ph_Default_Modules=\'6 "+str(values['-PHYDEFMO-']))

    if event == '-PHYEMIN-_ENTER':
        replacement_witherrorhandling(values['-PHYEMIN-'],
                                      "Ph_Default_EMRangeMin=\"100.\"",
                                      "Ph_Default_EMRangeMin=\""+str(values['-PHYEMIN-'])+"\"",
                                      "#Ph_Default_EMRangeMin_start,Ph_Default_EMRangeMin_stop,Ph_Default_EMRangeMin_step = 0,0,0",
                                      "#boundaries_list.append([Ph_Default_EMRangeMin_start",
                                      "#boundaries_name_list.append(['Ph_Default_EMRangeMin']",
                                      "#Ph_Default_EMRangeMin,i=str(values[i]),i+1")
    if event == '-PHYEMAX-_ENTER':
        replacement_witherrorhandling(values['-PHYEMAX-'],
                                      "Ph_Default_EMRangeMax=\"521.\"",
                                      "Ph_Default_EMRangeMax=\""+str(values['-PHYEMAX-'])+"\"",
                                      "#Ph_Default_EMRangeMax_start,Ph_Default_EMRangeMax_stop,Ph_Default_EMRangeMax_step = 0,0,0",
                                      "#boundaries_list.append([Ph_Default_EMRangeMax_start",
                                      "#boundaries_name_list.append(['Ph_Default_EMRangeMax']",
                                      "#Ph_Default_EMRangeMax,i=str(values[i]),i+1")

    if event == '-ROTTY-_ENTER':
        try:
            int(values['-ROTTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Rotation_Type=\'\"Group\"\'",
                                   "Rotation_Type=\'\""+str(values['-ROTTY-'])+"\"\'")

    if event == '-ROTPAR-_ENTER':
        try:
            int(values['-ROTPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Rotation_Parent=\'\"World\"\'",
                                   "Rotation_Parent=\'\""+str(values['-ROTPAR-'])+"\"\'")

    if event == '-ROTROTX-_ENTER':
        replacement_witherrorhandling(values['-ROTROTX-'],
                                      "Rotation_RotX=\"0.\"",
                                      "Rotation_RotX=\""+str(values['-ROTROTX-'])+"\"",
                                      "#Rotation_RotX_start,Rotation_RotX_stop,Rotation_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Rotation_RotX_start",
                                      "#boundaries_name_list.append(['Rotation_RotX']",
                                      "#Rotation_RotX,i=str(values[i]),i+1")
    if event == '-ROTROTY-_ENTER':
        replacement_witherrorhandling(values['-ROTROTY-'],
                                      "Rotation_RotY=\"0.\"",
                                      "Rotation_RotY=\""+str(values['-ROTROTY-'])+"\"",
                                      "#Rotation_RotY_start,Rotation_RotY_stop,Rotation_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Rotation_RotY_start",
                                      "#boundaries_name_list.append(['Rotation_RotY']",
                                      "#Rotation_RotY,i=str(values[i]),i+1")
    if event == '-ROTROTZ-_ENTER':
        replacement_witherrorhandling(values['-ROTROTZ-'],
                                      "Rotation_RotZ=\"0.\"",
                                      "Rotation_RotZ=\""+str(values['-ROTROTZ-'])+"\"",
                                      "#Rotation_RotZ_start,Rotation_RotZ_stop,Rotation_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Rotation_RotZ_start",
                                      "#boundaries_name_list.append(['Rotation_RotZ']",
                                      "#Rotation_RotZ,i=str(values[i]),i+1")
    if event == '-ROTTRANSX-_ENTER':
        replacement_witherrorhandling(values['-ROTTRANSX-'],
                                      "Rotation_TransX=\"0.\"",
                                      "Rotation_TransX=\""+str(values['-ROTTRANSX-'])+"\"",
                                      "#Rotation_TransX_start,Rotation_TransX_stop,Rotation_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Rotation_TransX_start",
                                      "#boundaries_name_list.append(['Rotation_TransX']",
                                      "#Rotation_TransX,i=str(values[i]),i+1")
    if event == '-ROTTRANSY-_ENTER':
        replacement_witherrorhandling(values['-ROTTRANSY-'],
                                      "Rotation_TransY=\"0.\"",
                                      "Rotation_TransY=\""+str(values['-ROTTRANSY-'])+"\"",
                                      "#Rotation_TransY_start,Rotation_TransY_stop,Rotation_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Rotation_TransY_start",
                                      "#boundaries_name_list.append(['Rotation_TransY']",
                                      "#Rotation_TransY,i=str(values[i]),i+1")
    if event == '-ROTTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-ROTTRANSZ-'],
                                      "Rotation_TransZ=\"0.\"",
                                      "Rotation_TransZ=\""+str(values['-ROTTRANSZ-'])+"\"",
                                      "#Rotation_TransZ_start,Rotation_TransZ_stop,Rotation_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Rotation_TransZ_start",
                                      "#boundaries_name_list.append(['Rotation_TransZ']",
                                      "#Rotation_TransZ,i=str(values[i]),i+1")

    if event == '-COLLVERTY-_ENTER':
        try:
            int(values['-COLLVERTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("CollimatorsVertical_Type=\'\"Group\"\'",
                                   "CollimatorsVertical_Type=\'\""+str(values['-COLLVERTY-'])+"\"\'")
    if event == '-COLLVERPAR-_ENTER':
        try:
            int(values['-COLLVERPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("CollimatorsVertical_Parent=\'\"World\"\'",
                                   "CollimatorsVertical_Parent=\'\""+str(values['-COLLVERPAR-'])+"\"\'")

    if event == '-COLLVERROTX-_ENTER':
        replacement_witherrorhandling(values['-COLLVERROTX-'],
                                      "CollimatorsVertical_RotX=\"0.\"",
                                      "CollimatorsVertical_RotX=\""+str(values['-COLLVERROTX-'])+"\"",
                                      "#CollimatorsVertical_RotX_start,CollimatorsVertical_RotX_stop,CollimatorsVertical_RotX_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsVertical_RotX_start",
                                      "#boundaries_name_list.append(['CollimatorsVertical_RotX']",
                                      "#CollimatorsVertical_RotX,i=str(values[i]),i+1")
    if event == '-COLLVERROTY-_ENTER':
        replacement_witherrorhandling(values['-COLLVERROTY-'],
                                      "CollimatorsVertical_RotY=\"0.\"",
                                      "CollimatorsVertical_RotY=\""+str(values['-COLLVERROTY-'])+"\"",
                                      "#CollimatorsVertical_RotY_start,CollimatorsVertical_RotY_stop,CollimatorsVertical_RotY_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsVertical_RotY_start",
                                      "#boundaries_name_list.append(['CollimatorsVertical_RotY']",
                                      "#CollimatorsVertical_RotY,i=str(values[i]),i+1")
    if event == '-COLLVERROTZ-_ENTER':
        replacement_witherrorhandling(values['-COLLVERROTZ-'],
                                      "CollimatorsVertical_RotZ=\"0.\"",
                                      "CollimatorsVertical_RotZ=\""+str(values['-COLLVERROTZ-'])+"\"",
                                      "#CollimatorsVertical_RotZ_start,CollimatorsVertical_RotZ_stop,CollimatorsVertical_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsVertical_RotZ_start",
                                      "#boundaries_name_list.append(['CollimatorsVertical_RotZ']",
                                      "#CollimatorsVertical_RotZ,i=str(values[i]),i+1")

    if event == '-COLLVERTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-COLLVERTRANSZ-'],
                                      "CollimatorsVertical_TransZ=\"8.75\"",
                                      "CollimatorsVertical_TransZ=\""+str(values['-COLLVERTRANSZ-'])+"\"",
                                      "#CollimatorsVertical_TransZ_start,CollimatorsVertical_TransZ_stop,CollimatorsVertical_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsVertical_TransZ_start",
                                      "#boundaries_name_list.append(['CollimatorsVertical_TransZ']",
                                      "#CollimatorsVertical_TransZ,i=str(values[i]),i+1")

    if event == '-COLLHORTY-_ENTER':
        try:
            int(values['-COLLHORTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("CollimatorsHorizontal_Type=\'\"Group\"\'",
                                   "CollimatorsHorizontal_Type=\'\""+str(values['-COLLHORTY-'])+"\"\'")
    if event == '-COLLHORPAR-_ENTER':
        try:
            int(values['-COLLHORPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("CollimatorsHorizontal_Parent=\'\"CollimatorsVertical\"\'",
                                   "CollimatorsHorizontal_Parent=\'\""+str(values['-COLLHORPAR-'])+"\"\'")

    if event == '-COLLHORROTX-_ENTER':
        replacement_witherrorhandling(values['-COLLHORROTX-'],
                                      "CollimatorsHorizontal_RotX=\"0.\"",
                                      "CollimatorsHorizontal_RotX=\""+str(values['-COLLHORROTX-'])+"\"",
                                      "#CollimatorsHorizontal_RotX_start,CollimatorsHorizontal_RotX_stop,CollimatorsHorizontal_RotX_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsHorizontal_RotX_start",
                                      "#boundaries_name_list.append(['CollimatorsHorizontal_RotX']",
                                      "#CollimatorsHorizontal_RotX,i=str(values[i]),i+1")
    if event == '-COLLHORROTY-_ENTER':
        replacement_witherrorhandling(values['-COLLHORROTY-'],
                                      "CollimatorsHorizontal_RotY=\"0.\"",
                                      "CollimatorsHorizontal_RotY=\""+str(values['-COLLHORROTY-'])+"\"",
                                      "#CollimatorsHorizontal_RotY_start,CollimatorsHorizontal_RotY_stop,CollimatorsHorizontal_RotY_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsHorizontal_RotY_start",
                                      "#boundaries_name_list.append(['CollimatorsHorizontal_RotY']",
                                      "#CollimatorsHorizontal_RotY,i=str(values[i]),i+1")
    if event == '-COLLHORROTZ-_ENTER':
        replacement_witherrorhandling(values['-COLLHORROTZ-'],
                                      "CollimatorsHorizontal_RotZ=\"0.\"",
                                      "CollimatorsHorizontal_RotZ=\""+str(values['-COLLHORROTZ-'])+"\"",
                                      "#CollimatorsHorizontal_RotZ_start,CollimatorsHorizontal_RotZ_stop,CollimatorsHorizontal_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsHorizontal_RotZ_start",
                                      "#boundaries_name_list.append(['CollimatorsHorizontal_RotZ']",
                                      "#CollimatorsHorizontal_RotZ,i=str(values[i]),i+1")

    if event == '-COLLHORTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-COLLHORTRANSZ-'],
                                      "CollimatorsHorizontal_TransZ=\"Ge/Coll1/LY\"",
                                      "CollimatorsHorizontal_TransZ=\""+str(values['-COLLHORTRANSZ-'])+"\"",
                                      "#CollimatorsHorizontal_TransZ_start,CollimatorsHorizontal_TransZ_stop,CollimatorsHorizontal_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([CollimatorsHorizontal_TransZ_start",
                                      "#boundaries_name_list.append(['CollimatorsHorizontal_TransZ']",
                                      "#CollimatorsHorizontal_TransZ,i=str(values[i]),i+1")
    if event == '-TITTY-_ENTER':
        try:
            int(values['-TITTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("TitaniumFilterGroup_Type=\'\"Group\"\'",
                                   "TitaniumFilterGroup_Type=\'\""+str(values['-TITTY-'])+"\"\'")
    if event == '-TITPAR-_ENTER':
        try:
            int(values['-TITPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("TitaniumFilterGroup_Parent=\'\"CollimatorsHorizontal\"\'",
                                   "TitaniumFilterGroup_Parent=\'\""+str(values['-TITPAR-'])+"\"\'")

    if event == '-TITROTX-_ENTER':
        replacement_witherrorhandling(values['-TITROTX-'],
                                      "TitaniumFilterGroup_RotX=\"0.\"",
                                      "TitaniumFilterGroup_RotX=\""+str(values['-TITROTX-'])+"\"",
                                      "#TitaniumFilterGroup_RotX_start,TitaniumFilterGroup_RotX_stop,TitaniumFilterGroup_RotX_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilterGroup_RotX_start",
                                      "#boundaries_name_list.append(['TitaniumFilterGroup_RotX']",
                                      "#TitaniumFilterGroup_RotX,i=str(values[i]),i+1")
    if event == '-TITROTY-_ENTER':
        replacement_witherrorhandling(values['-TITROTY-'],
                                      "TitaniumFilterGroup_RotY=\"0.\"",
                                      "TitaniumFilterGroup_RotY=\""+str(values['-TITROTY-'])+"\"",
                                      "#TitaniumFilterGroup_RotY_start,TitaniumFilterGroup_RotY_stop,TitaniumFilterGroup_RotY_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilterGroup_RotY_start",
                                      "#boundaries_name_list.append(['TitaniumFilterGroup_RotY']",
                                      "#TitaniumFilterGroup_RotY,i=str(values[i]),i+1")
    if event == '-TITROTZ-_ENTER':
        replacement_witherrorhandling(values['-TITROTZ-'],
                                      "TitaniumFilterGroup_RotZ=\"0.\"",
                                      "TitaniumFilterGroup_RotZ=\""+str(values['-TITROTZ-'])+"\"",
                                      "#TitaniumFilterGroup_RotZ_start,TitaniumFilterGroup_RotZ_stop,TitaniumFilterGroup_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilterGroup_RotZ_start",
                                      "#boundaries_name_list.append(['TitaniumFilterGroup_RotZ']",
                                      "#TitaniumFilterGroup_RotZ,i=str(values[i]),i+1")

    if event == '-TITTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-TITTRANSZ-'],
                                      "TitaniumFilterGroup_TransZ=\"1.59\"",
                                      "TitaniumFilterGroup_TransZ=\""+str(values['-TITTRANSZ-'])+"\"",
                                      "#TitaniumFilterGroup_TransZ_start,TitaniumFilterGroup_TransZ_stop,TitaniumFilterGroup_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilterGroup_TransZ_start",
                                      "#boundaries_name_list.append(['TitaniumFilterGroup_TransZ']",
                                      "#TitaniumFilterGroup_TransZ,i=str(values[i]),i+1")
    if event == '-BFTY-_ENTER':
        try:
            int(values['-BFTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("BowtieFilter_Type=\'\"Group\"\'",
                                   "BowtieFilter_Type=\'\""+str(values['-BFTY-'])+"\"\'")
    if event == '-BFPAR-_ENTER':
        try:
            int(values['-BFPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("BowtieFilter_Parent=\'\"CollimatorsVertical\"\'",
                                   "BowtieFilter_Parent=\'\""+str(values['-BFPAR-'])+"\"\'")

    if event == '-BFROTX-_ENTER':
        replacement_witherrorhandling(values['-BFROTX-'],
                                      "BowtieFilter_RotX=\"0.\"",
                                      "BowtieFilter_RotX=\""+str(values['-BFROTX-'])+"\"",
                                      "#BowtieFilter_RotX_start,BowtieFilter_RotX_stop,BowtieFilter_RotX_step = 0,0,0",
                                      "#boundaries_list.append([BowtieFilter_RotX_start",
                                      "#boundaries_name_list.append(['BowtieFilter_RotX']",
                                      "#BowtieFilter_RotX,i=str(values[i]),i+1")
    if event == '-BFROTY-_ENTER':
        replacement_witherrorhandling(values['-BFROTY-'],
                                      "BowtieFilter_RotY=\"0.\"",
                                      "BowtieFilter_RotY=\""+str(values['-BFROTY-'])+"\"",
                                      "#BowtieFilter_RotY_start,BowtieFilter_RotY_stop,BowtieFilter_RotY_step = 0,0,0",
                                      "#boundaries_list.append([BowtieFilter_RotY_start",
                                      "#boundaries_name_list.append(['BowtieFilter_RotY']",
                                      "#BowtieFilter_RotY,i=str(values[i]),i+1")
    if event == '-BFROTZ-_ENTER':
        replacement_witherrorhandling(values['-BFROTZ-'],
                                      "BowtieFilter_RotZ=\"90.\"",
                                      "BowtieFilter_RotZ=\""+str(values['-BFROTZ-'])+"\"",
                                      "#BowtieFilter_RotZ_start,BowtieFilter_RotZ_stop,BowtieFilter_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([BowtieFilter_RotZ_start",
                                      "#boundaries_name_list.append(['BowtieFilter_RotZ']",
                                      "#BowtieFilter_RotZ,i=str(values[i]),i+1")
    if event == '-BFTRANSX-_ENTER':
        replacement_witherrorhandling(values['-BFTRANSX-'],
                                      "BowtieFilter_TransX=\"0.0\"",
                                      "BowtieFilter_TransX=\""+str(values['-BFTRANSX-'])+"\"",
                                      "#BowtieFilter_TransX_start,BowtieFilter_TransX_stop,BowtieFilter_TransX_step = 0,0,0",
                                      "#boundaries_list.append([BowtieFilter_TransX_start",
                                      "#boundaries_name_list.append(['BowtieFilter_TransX']",
                                      "#BowtieFilter_TransX,i=str(values[i]),i+1")
    if event == '-BFTRANSY-_ENTER':
        replacement_witherrorhandling(values['-BFTRANSY-'],
                                      "BowtieFilter_TransY=\"0.0\"",
                                      "BowtieFilter_TransY=\""+str(values['-BFTRANSY-'])+"\"",
                                      "#BowtieFilter_TransY_start,BowtieFilter_TransY_stop,BowtieFilter_TransY_step = 0,0,0",
                                      "#boundaries_list.append([BowtieFilter_TransY_start",
                                      "#boundaries_name_list.append(['BowtieFilter_TransY']",
                                      "#BowtieFilter_TransY,i=str(values[i]),i+1")
    if event == '-BFTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-BFTRANSZ-'],
                                      "BowtieFilter_TransZ=\"3.85\"",
                                      "BowtieFilter_TransZ=\""+str(values['-BFTRANSZ-'])+"\"",
                                      "#BowtieFilter_TransZ_start,BowtieFilter_TransZ_stop,BowtieFilter_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([BowtieFilter_TransZ_start",
                                      "#boundaries_name_list.append(['BowtieFilter_TransZ']",
                                      "#BowtieFilter_TransZ,i=str(values[i]),i+1")

    if event == '-Coll1TY-_ENTER':
        try:
            int(values['-Coll1TY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll1_Type=\'\"G4RTrap\"\'",
                                   "Coll1_Type=\'\""+str(values['-Coll1TY-'])+"\"\'")
    if event == '-Coll1PAR-_ENTER':
        try:
            int(values['-Coll1PAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll1_Parent=\'\"CollimatorsVertical\"\'",
                                   "Coll1_Parent=\'\""+str(values['-Coll1PAR-'])+"\"\'")
    if event == '-Coll1MAT-_ENTER':
        try:
            int(values['-Coll1MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll1_Material=\'\"Lead\"\'",
                                   "Coll1_Material=\'\""+str(values['-Coll1MAT-'])+"\"\'")
    if event == '-Coll1ROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll1ROTX-'],
                                      "Coll1_RotX=\"-90.\"",
                                      "Coll1_RotX=\""+str(values['-Coll1ROTX-'])+"\"",
                                      "#Coll1_RotX_start,Coll1_RotX_stop,Coll1_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_RotX_start",
                                      "#boundaries_name_list.append(['Coll1_RotX']",
                                      "#Coll1_RotX,i=str(values[i]),i+1")
    if event == '-Coll1ROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll1ROTY-'],
                                      "Coll1_RotY=\"90.\"",
                                      "Coll1_RotY=\""+str(values['-Coll1ROTY-'])+"\"",
                                      "#Coll1_RotY_start,Coll1_RotY_stop,Coll1_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_RotY_start",
                                      "#boundaries_name_list.append(['Coll1_RotY']",
                                      "#Coll1_RotY,i=str(values[i]),i+1")
    if event == '-Coll1ROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll1ROTZ-'],
                                      "Coll1_RotZ=\"0\"",
                                      "Coll1_RotZ=\""+str(values['-Coll1ROTZ-'])+"\"",
                                      "#Coll1_RotZ_start,Coll1_RotZ_stop,Coll1_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_RotZ_start",
                                      "#boundaries_name_list.append(['Coll1_RotZ']",
                                      "#Coll1_RotZ,i=str(values[i]),i+1")
    if event == '-Coll1TRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll1TRANSX-'],
                                      "Coll1_TransX=\"0\"",
                                      "Coll1_TransX=\""+str(values['-Coll1TRANSX-'])+"\"",
                                      "#Coll1_TransX_start,Coll1_TransX_stop,Coll1_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_TransX_start",
                                      "#boundaries_name_list.append(['Coll1_TransX']",
                                      "#Coll1_TransX,i=str(values[i]),i+1")
    if event == '-Coll1TRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll1TRANSY-'],
                                      "Coll1_TransY=\"5.5\"",
                                      "Coll1_TransY=\""+str(values['-Coll1TRANSY-'])+"\"",
                                      "#Coll1_TransY_start,Coll1_TransY_stop,Coll1_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_TransY_start",
                                      "#boundaries_name_list.append(['Coll1_TransY']",
                                      "#Coll1_TransY,i=str(values[i]),i+1")
    if event == '-Coll1TRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll1TRANSZ-'],
                                      "Coll1_TransZ=\"0\"",
                                      "Coll1_TransZ=\""+str(values['-Coll1TRANSZ-'])+"\"",
                                      "#Coll1_TransZ_start,Coll1_TransZ_stop,Coll1_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_TransZ_start",
                                      "#boundaries_name_list.append(['Coll1_TransZ']",
                                      "#Coll1_TransZ,i=str(values[i]),i+1")
    if event == '-Coll1LZ-_ENTER':
        replacement_witherrorhandling(values['-Coll1LZ-'],
                                      "Coll1_LZ=\"12.\"",
                                      "Coll1_LZ=\""+str(values['-Coll1LZ-'])+"\"",
                                      "#Coll1_LZ_start,Coll1_LZ_stop,Coll1_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_LZ_start",
                                      "#boundaries_name_list.append(['Coll1_LZ']",
                                      "#Coll1_LZ,i=str(values[i]),i+1")
    if event == '-Coll1LY-_ENTER':
        replacement_witherrorhandling(values['-Coll1LY-'],
                                      "Coll1_LY=\"1.7\"",
                                      "Coll1_LY=\""+str(values['-Coll1LY-'])+"\"",
                                      "#Coll1_LY_start,Coll1_LY_stop,Coll1_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_LY_start",
                                      "#boundaries_name_list.append(['Coll1_LY']",
                                      "#Coll1_LY,i=str(values[i]),i+1")
    if event == '-Coll1LX-_ENTER':
        replacement_witherrorhandling(values['-Coll1LX-'],
                                      "Coll1_LX=\"10.\"",
                                      "Coll1_LX=\""+str(values['-Coll1LX-'])+"\"",
                                      "#Coll1_LX_start,Coll1_LX_stop,Coll1_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_LX_start",
                                      "#boundaries_name_list.append(['Coll1_LX']",
                                      "#Coll1_LX,i=str(values[i]),i+1")

    if event == '-Coll1LTX-_ENTER':
        replacement_witherrorhandling(values['-Coll1LTX-'],
                                      "Coll1_LTX=\"9.2\"",
                                      "Coll1_LTX=\""+str(values['-Coll1LTX-'])+"\"",
                                      "#Coll1_LTX_start,Coll1_LTX_stop,Coll1_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1_LTX_start",
                                      "#boundaries_name_list.append(['Coll1_LTX']",
                                      "#Coll1_LTX,i=str(values[i]),i+1")
    if event == '-Coll2TY-_ENTER':
        try:
            int(values['-Coll2TY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll2_Type=\'\"G4RTrap\"\'",
                                   "Coll2_Type=\'\""+str(values['-Coll2TY-'])+"\"\'")
    if event == '-Coll2PAR-_ENTER':
        try:
            int(values['-Coll2PAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll2_Parent=\'\"CollimatorsVertical\"\'",
                                   "Coll2_Parent=\'\""+str(values['-Coll2PAR-'])+"\"\'")
    if event == '-Coll2MAT-_ENTER':
        try:
            int(values['-Coll2MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll2_Material=\'\"Lead\"\'",
                                   "Coll2_Material=\'\""+str(values['-Coll2MAT-'])+"\"\'")
    if event == '-Coll2ROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll2ROTX-'],
                                      "Coll2_RotX=\"-90.\"",
                                      "Coll2_RotX=\""+str(values['-Coll2ROTX-'])+"\"",
                                      "#Coll2_RotX_start,Coll2_RotX_stop,Coll2_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_RotX_start",
                                      "#boundaries_name_list.append(['Coll2_RotX']",
                                      "#Coll2_RotX,i=str(values[i]),i+1")
    if event == '-Coll2ROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll2ROTY-'],
                                      "Coll2_RotY=\"270.\"",
                                      "Coll2_RotY=\""+str(values['-Coll2ROTY-'])+"\"",
                                      "#Coll2_RotY_start,Coll2_RotY_stop,Coll2_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_RotY_start",
                                      "#boundaries_name_list.append(['Coll2_RotY']",
                                      "#Coll2_RotY,i=str(values[i]),i+1")
    if event == '-Coll2ROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll2ROTZ-'],
                                      "Coll2_RotZ=\"0\"",
                                      "Coll2_RotZ=\""+str(values['-Coll2ROTZ-'])+"\"",
                                      "#Coll2_RotZ_start,Coll2_RotZ_stop,Coll2_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_RotZ_start",
                                      "#boundaries_name_list.append(['Coll2_RotZ']",
                                      "#Coll2_RotZ,i=str(values[i]),i+1")
    if event == '-Coll2TRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll2TRANSX-'],
                                      "Coll2_TransX=\"0\"",
                                      "Coll2_TransX=\""+str(values['-Coll2TRANSX-'])+"\"",
                                      "#Coll2_TransX_start,Coll2_TransX_stop,Coll2_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_TransX_start",
                                      "#boundaries_name_list.append(['Coll2_TransX']",
                                      "#Coll2_TransX,i=str(values[i]),i+1")
    if event == '-Coll2TRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll2TRANSY-'],
                                      "Coll2_TransY=\"-5.5\"",
                                      "Coll2_TransY=\""+str(values['-Coll2TRANSY-'])+"\"",
                                      "#Coll2_TransY_start,Coll2_TransY_stop,Coll2_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_TransY_start",
                                      "#boundaries_name_list.append(['Coll2_TransY']",
                                      "#Coll2_TransY,i=str(values[i]),i+1")
    if event == '-Coll2TRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll2TRANSZ-'],
                                      "Coll2_TransZ=\"0\"",
                                      "Coll2_TransZ=\""+str(values['-Coll2TRANSZ-'])+"\"",
                                      "#Coll2_TransZ_start,Coll2_TransZ_stop,Coll2_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_TransZ_start",
                                      "#boundaries_name_list.append(['Coll2_TransZ']",
                                      "#Coll2_TransZ,i=str(values[i]),i+1")
    if event == '-Coll2LZ-_ENTER':
        replacement_witherrorhandling(values['-Coll2LZ-'],
                                      "Coll2_LZ=\"12.\"",
                                      "Coll2_LZ=\""+str(values['-Coll2LZ-'])+"\"",
                                      "#Coll2_LZ_start,Coll2_LZ_stop,Coll2_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_LZ_start",
                                      "#boundaries_name_list.append(['Coll2_LZ']",
                                      "#Coll2_LZ,i=str(values[i]),i+1")
    if event == '-Coll2LY-_ENTER':
        replacement_witherrorhandling(values['-Coll2LY-'],
                                      "Coll2_LY=\"1.7\"",
                                      "Coll2_LY=\""+str(values['-Coll2LY-'])+"\"",
                                      "#Coll2_LY_start,Coll2_LY_stop,Coll2_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_LY_start",
                                      "#boundaries_name_list.append(['Coll2_LY']",
                                      "#Coll2_LY,i=str(values[i]),i+1")
    if event == '-Coll2LX-_ENTER':
        replacement_witherrorhandling(values['-Coll2LX-'],
                                      "Coll2_LX=\"10.\"",
                                      "Coll2_LX=\""+str(values['-Coll2LX-'])+"\"",
                                      "#Coll2_LX_start,Coll2_LX_stop,Coll2_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_LX_start",
                                      "#boundaries_name_list.append(['Coll2_LX']",
                                      "#Coll2_LX,i=str(values[i]),i+1")

    if event == '-Coll2LTX-_ENTER':
        replacement_witherrorhandling(values['-Coll2LTX-'],
                                      "Coll2_LTX=\"9.2\"",
                                      "Coll2_LTX=\""+str(values['-Coll2LTX-'])+"\"",
                                      "#Coll2_LTX_start,Coll2_LTX_stop,Coll2_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2_LTX_start",
                                      "#boundaries_name_list.append(['Coll2_LTX']",
                                      "#Coll2_LTX,i=str(values[i]),i+1")
    if event == '-Coll3TY-_ENTER':
        try:
            int(values['-Coll3TY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll3_Type=\'\"G4RTrap\"\'",
                                   "Coll3_Type=\'\""+str(values['-Coll3TY-'])+"\"\'")
    if event == '-Coll3PAR-_ENTER':
        try:
            int(values['-Coll3PAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll3_Parent=\'\"CollimatorsHorizontal\"\'",
                                   "Coll3_Parent=\'\""+str(values['-Coll3PAR-'])+"\"\'")
    if event == '-Coll3MAT-_ENTER':
        try:
            int(values['-Coll3MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll3_Material=\'\"Lead\"\'",
                                   "Coll3_Material=\'\""+str(values['-Coll3MAT-'])+"\"\'")
    if event == '-Coll3ROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll3ROTX-'],
                                      "Coll3_RotX=\"-90.\"",
                                      "Coll3_RotX=\""+str(values['-Coll3ROTX-'])+"\"",
                                      "#Coll3_RotX_start,Coll3_RotX_stop,Coll3_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_RotX_start",
                                      "#boundaries_name_list.append(['Coll3_RotX']",
                                      "#Coll3_RotX,i=str(values[i]),i+1")
    if event == '-Coll3ROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll3ROTY-'],
                                      "Coll3_RotY=\"180.\"",
                                      "Coll3_RotY=\""+str(values['-Coll3ROTY-'])+"\"",
                                      "#Coll3_RotY_start,Coll3_RotY_stop,Coll3_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_RotY_start",
                                      "#boundaries_name_list.append(['Coll3_RotY']",
                                      "#Coll3_RotY,i=str(values[i]),i+1")
    if event == '-Coll3ROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll3ROTZ-'],
                                      "Coll3_RotZ=\"0\"",
                                      "Coll3_RotZ=\""+str(values['-Coll3ROTZ-'])+"\"",
                                      "#Coll3_RotZ_start,Coll3_RotZ_stop,Coll3_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_RotZ_start",
                                      "#boundaries_name_list.append(['Coll3_RotZ']",
                                      "#Coll3_RotZ,i=str(values[i]),i+1")
    if event == '-Coll3TRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll3TRANSX-'],
                                      "Coll3_TransX=\"5.5\"",
                                      "Coll3_TransX=\""+str(values['-Coll3TRANSX-'])+"\"",
                                      "#Coll3_TransX_start,Coll3_TransX_stop,Coll3_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_TransX_start",
                                      "#boundaries_name_list.append(['Coll3_TransX']",
                                      "#Coll3_TransX,i=str(values[i]),i+1")
    if event == '-Coll3TRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll3TRANSY-'],
                                      "Coll3_TransY=\"0.\"",
                                      "Coll3_TransY=\""+str(values['-Coll3TRANSY-'])+"\"",
                                      "#Coll3_TransY_start,Coll3_TransY_stop,Coll3_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_TransY_start",
                                      "#boundaries_name_list.append(['Coll3_TransY']",
                                      "#Coll3_TransY,i=str(values[i]),i+1")
    if event == '-Coll3TRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll3TRANSZ-'],
                                      "Coll3_TransZ=\"0.\"",
                                      "Coll3_TransZ=\""+str(values['-Coll3TRANSZ-'])+"\"",
                                      "#Coll3_TransZ_start,Coll3_TransZ_stop,Coll3_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_TransZ_start",
                                      "#boundaries_name_list.append(['Coll3_TransZ']",
                                      "#Coll3_TransZ,i=str(values[i]),i+1")
    if event == '-Coll3LZ-_ENTER':
        replacement_witherrorhandling(values['-Coll3LZ-'],
                                      "Coll3_LZ=\"12.\"",
                                      "Coll3_LZ=\""+str(values['-Coll3LZ-'])+"\"",
                                      "#Coll3_LZ_start,Coll3_LZ_stop,Coll3_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_LZ_start",
                                      "#boundaries_name_list.append(['Coll3_LZ']",
                                      "#Coll3_LZ,i=str(values[i]),i+1")
    if event == '-Coll3LY-_ENTER':
        replacement_witherrorhandling(values['-Coll3LY-'],
                                      "Coll3_LY=\"1.7\"",
                                      "Coll3_LY=\""+str(values['-Coll3LY-'])+"\"",
                                      "#Coll3_LY_start,Coll3_LY_stop,Coll3_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_LY_start",
                                      "#boundaries_name_list.append(['Coll3_LY']",
                                      "#Coll3_LY,i=str(values[i]),i+1")
    if event == '-Coll3LX-_ENTER':
        replacement_witherrorhandling(values['-Coll3LX-'],
                                      "Coll3_LX=\"10.\"",
                                      "Coll3_LX=\""+str(values['-Coll3LX-'])+"\"",
                                      "#Coll3_LX_start,Coll3_LX_stop,Coll3_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_LX_start",
                                      "#boundaries_name_list.append(['Coll3_LX']",
                                      "#Coll3_LX,i=str(values[i]),i+1")

    if event == '-Coll3LTX-_ENTER':
        replacement_witherrorhandling(values['-Coll3LTX-'],
                                      "Coll3_LTX=\"9.2\"",
                                      "Coll3_LTX=\""+str(values['-Coll3LTX-'])+"\"",
                                      "#Coll3_LTX_start,Coll3_LTX_stop,Coll3_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3_LTX_start",
                                      "#boundaries_name_list.append(['Coll3_LTX']",
                                      "#Coll3_LTX,i=str(values[i]),i+1")
    if event == '-Coll4TY-_ENTER':
        try:
            int(values['-Coll4TY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll4_Type=\'\"G4RTrap\"\'",
                                   "Coll4_Type=\'\""+str(values['-Coll4TY-'])+"\"\'")
    if event == '-Coll4PAR-_ENTER':
        try:
            int(values['-Coll4PAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll4_Parent=\'\"CollimatorsHorizontal\"\'",
                                   "Coll4_Parent=\'\""+str(values['-Coll4PAR-'])+"\"\'")
    if event == '-Coll4MAT-_ENTER':
        try:
            int(values['-Coll4MAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll4_Material=\'\"Lead\"\'",
                                   "Coll4_Material=\'\""+str(values['-Coll4MAT-'])+"\"\'")
    if event == '-Coll4ROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll4ROTX-'],
                                      "Coll4_RotX=\"-90.\"",
                                      "Coll4_RotX=\""+str(values['-Coll4ROTX-'])+"\"",
                                      "#Coll4_RotX_start,Coll4_RotX_stop,Coll4_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_RotX_start",
                                      "#boundaries_name_list.append(['Coll4_RotX']",
                                      "#Coll4_RotX,i=str(values[i]),i+1")
    if event == '-Coll4ROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll4ROTY-'],
                                      "Coll4_RotY=\"0.\"",
                                      "Coll4_RotY=\""+str(values['-Coll4ROTY-'])+"\"",
                                      "#Coll4_RotY_start,Coll4_RotY_stop,Coll4_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_RotY_start",
                                      "#boundaries_name_list.append(['Coll4_RotY']",
                                      "#Coll4_RotY,i=str(values[i]),i+1")
    if event == '-Coll4ROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll4ROTZ-'],
                                      "Coll4_RotZ=\"0\"",
                                      "Coll4_RotZ=\""+str(values['-Coll4ROTZ-'])+"\"",
                                      "#Coll4_RotZ_start,Coll4_RotZ_stop,Coll4_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_RotZ_start",
                                      "#boundaries_name_list.append(['Coll4_RotZ']",
                                      "#Coll4_RotZ,i=str(values[i]),i+1")
    if event == '-Coll4TRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll4TRANSX-'],
                                      "Coll4_TransX=\"-5.5\"",
                                      "Coll4_TransX=\""+str(values['-Coll4TRANSX-'])+"\"",
                                      "#Coll4_TransX_start,Coll4_TransX_stop,Coll4_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_TransX_start",
                                      "#boundaries_name_list.append(['Coll4_TransX']",
                                      "#Coll4_TransX,i=str(values[i]),i+1")
    if event == '-Coll4TRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll4TRANSY-'],
                                      "Coll4_TransY=\"0.\"",
                                      "Coll4_TransY=\""+str(values['-Coll4TRANSY-'])+"\"",
                                      "#Coll4_TransY_start,Coll4_TransY_stop,Coll4_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_TransY_start",
                                      "#boundaries_name_list.append(['Coll4_TransY']",
                                      "#Coll4_TransY,i=str(values[i]),i+1")
    if event == '-Coll4TRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll4TRANSZ-'],
                                      "Coll4_TransZ=\"0.\"",
                                      "Coll4_TransZ=\""+str(values['-Coll4TRANSZ-'])+"\"",
                                      "#Coll4_TransZ_start,Coll4_TransZ_stop,Coll4_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_TransZ_start",
                                      "#boundaries_name_list.append(['Coll4_TransZ']",
                                      "#Coll4_TransZ,i=str(values[i]),i+1")
    if event == '-Coll4LZ-_ENTER':
        replacement_witherrorhandling(values['-Coll4LZ-'],
                                      "Coll4_LZ=\"12.\"",
                                      "Coll4_LZ=\""+str(values['-Coll4LZ-'])+"\"",
                                      "#Coll4_LZ_start,Coll4_LZ_stop,Coll4_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_LZ_start",
                                      "#boundaries_name_list.append(['Coll4_LZ']",
                                      "#Coll4_LZ,i=str(values[i]),i+1")
    if event == '-Coll4LY-_ENTER':
        replacement_witherrorhandling(values['-Coll4LY-'],
                                      "Coll4_LY=\"1.7\"",
                                      "Coll4_LY=\""+str(values['-Coll4LY-'])+"\"",
                                      "#Coll4_LY_start,Coll4_LY_stop,Coll4_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_LY_start",
                                      "#boundaries_name_list.append(['Coll4_LY']",
                                      "#Coll4_LY,i=str(values[i]),i+1")
    if event == '-Coll4LX-_ENTER':
        replacement_witherrorhandling(values['-Coll4LX-'],
                                      "Coll4_LX=\"10.\"",
                                      "Coll4_LX=\""+str(values['-Coll4LX-'])+"\"",
                                      "#Coll4_LX_start,Coll4_LX_stop,Coll4_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_LX_start",
                                      "#boundaries_name_list.append(['Coll4_LX']",
                                      "#Coll4_LX,i=str(values[i]),i+1")
    if event == '-Coll4LTX-_ENTER':
        replacement_witherrorhandling(values['-Coll4LTX-'],
                                      "Coll4_LTX=\"9.2\"",
                                      "Coll4_LTX=\""+str(values['-Coll4LTX-'])+"\"",
                                      "#Coll4_LTX_start,Coll4_LTX_stop,Coll4_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4_LTX_start",
                                      "#boundaries_name_list.append(['Coll4_LTX']",
                                      "#Coll4_LTX,i=str(values[i]),i+1")

    if event == '-Coll1steelPAR-_ENTER':
        try:
            int(values['-Coll1steelPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll1steel_Parent=\'\"CollimatorsVertical\"\'",
                                   "Coll1steel_Parent=\'\""+str(values['-Coll1steelPAR-'])+"\"\'")
    if event == '-Coll1steelTY-_ENTER':
        try:
            int(values['-Coll1steelTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll1steel_Type=\'\"G4RTrap\"\'",
                                   "Coll1steel_Type=\'\""+str(values['-Coll1steelTY-'])+"\"\'")
    if event == '-Coll1steelMAT-_ENTER':
        try:
            int(values['-Coll1steelMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll1steel_Material=\'\"Steel\"\'",
                                   "Coll1steel_Material=\'\""+str(values['-Coll1steelMAT-'])+"\"\'")
    if event == '-Coll1steelROTX-_ENTER':
            replacement_witherrorhandling(values['-Coll1steelROTX-'],
                                      "Coll1steel_RotX=\"-90.\"",
                                      "Coll1steel_RotX=\""+str(values['-Coll1steelROTX-'])+"\"",
                                      "#Coll1steel_RotX_start,Coll1steel_RotX_stop,Coll1steel_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_RotX_start",
                                      "#boundaries_name_list.append(['Coll1steel_RotX']",
                                      "#Coll1steel_RotX,i=str(values[i]),i+1")
    if event == '-Coll1steelROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelROTY-'],
                                      "Coll1steel_RotY=\"90.\"",
                                      "Coll1steel_RotY=\""+str(values['-Coll1steelROTY-'])+"\"",
                                      "#Coll1steel_RotY_start,Coll1steel_RotY_stop,Coll1steel_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_RotY_start",
                                      "#boundaries_name_list.append(['Coll1steel_RotY']",
                                      "#Coll1steel_RotY,i=str(values[i]),i+1")
    if event == '-Coll1steelROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelROTZ-'],
                                      "Coll1steel_RotZ=\"0\"",
                                      "Coll1steel_RotZ=\""+str(values['-Coll1steelROTZ-'])+"\"",
                                      "#Coll1steel_RotZ_start,Coll1steel_RotZ_stop,Coll1steel_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_RotZ_start",
                                      "#boundaries_name_list.append(['Coll1steel_RotZ']",
                                      "#Coll1steel_RotZ,i=str(values[i]),i+1")
    if event == '-Coll1steelTRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelTRANSX-'],
                                      "Coll1steel_TransX=\"0\"",
                                      "Coll1steel_TransX=\""+str(values['-Coll1steelTRANSX-'])+"\"",
                                      "#Coll1steel_TransX_start,Coll1steel_TransX_stop,Coll1steel_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_TransX_start",
                                      "#boundaries_name_list.append(['Coll1steel_TransX']",
                                      "#Coll1steel_TransX,i=str(values[i]),i+1")
    if event == '-Coll1steelTRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelTRANSY-'],
                                      "Coll1steel_TransY=\"0.2\"",
                                      "Coll1steel_TransY=\""+str(values['-Coll1steelTRANSY-'])+"\"",
                                      "#Coll1steel_TransY_start,Coll1steel_TransY_stop,Coll1steel_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_TransY_start",
                                      "#boundaries_name_list.append(['Coll1steel_TransY']",
                                      "#Coll1steel_TransY,i=str(values[i]),i+1")
    if event == '-Coll1steelTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelTRANSZ-'],
                                      "Coll1steel_TransZ=\"-0.25\"",
                                      "Coll1steel_TransZ=\""+str(values['-Coll1steelTRANSZ-'])+"\"",
                                      "#Coll1steel_TransZ_start,Coll1steel_TransZ_stop,Coll1steel_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_TransZ_start",
                                      "#boundaries_name_list.append(['Coll1steel_TransZ']",
                                      "#Coll1steel_TransZ,i=str(values[i]),i+1")
    if event == '-Coll1steelLZ-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelLZ-'],
                                      "Coll1steel_LZ=\"12.\"",
                                      "Coll1steel_LZ=\""+str(values['-Coll1steelLZ-'])+"\"",
                                      "#Coll1steel_LZ_start,Coll1steel_LZ_stop,Coll1steel_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_LZ_start",
                                      "#boundaries_name_list.append(['Coll1steel_LZ']",
                                      "#Coll1steel_LZ,i=str(values[i]),i+1")
    if event == '-Coll1steelLY-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelLY-'],
                                      "Coll1steel_LY=\"0.2\"",
                                      "Coll1steel_LY=\""+str(values['-Coll1steelLY-'])+"\"",
                                      "#Coll1steel_LY_start,Coll1steel_LY_stop,Coll1steel_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_LY_start",
                                      "#boundaries_name_list.append(['Coll1steel_LY']",
                                      "#Coll1steel_LY,i=str(values[i]),i+1")
    if event == '-Coll1steelLX-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelLX-'],
                                      "Coll1steel_LX=\"10.\"",
                                      "Coll1steel_LX=\""+str(values['-Coll1steelLX-'])+"\"",
                                      "#Coll1steel_LX_start,Coll1steel_LX_stop,Coll1steel_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_LX_start",
                                      "#boundaries_name_list.append(['Coll1steel_LX']",
                                      "#Coll1steel_LX,i=str(values[i]),i+1")

    if event == '-Coll1steelLTX-_ENTER':
        replacement_witherrorhandling(values['-Coll1steelLTX-'],
                                      "Coll1steel_LTX=\"10.\"",
                                      "Coll1steel_LTX=\""+str(values['-Coll1steelLTX-'])+"\"",
                                      "#Coll1steel_LTX_start,Coll1steel_LTX_stop,Coll1steel_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll1steel_LTX_start",
                                      "#boundaries_name_list.append(['Coll1steel_LTX']",
                                      "#Coll1steel_LTX,i=str(values[i]),i+1")

    if event == '-Coll2steelTY-_ENTER':
        try:
            int(values['-Coll2steelTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll2steel_Type=\'\"G4RTrap\"\'",
                                   "Coll2steel_Type=\'\""+str(values['-Coll2steelTY-'])+"\"\'")
    if event == '-Coll2steelPAR-_ENTER':
        try:
            int(values['-Coll2steelPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll2steel_Parent=\'\"CollimatorsVertical\"\'",
                                   "Coll2steel_Parent=\'\""+str(values['-Coll2steelPAR-'])+"\"\'")
    if event == '-Coll2steelMAT-_ENTER':
        try:
            int(values['-Coll2steelMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll2steel_Material=\'\"Steel\"\'",
                                   "Coll2steel_Material=\'\""+str(values['-Coll2steelMAT-'])+"\"\'")
    if event == '-Coll2steelROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelROTX-'],
                                      "Coll2steel_RotX=\"-90.\"",
                                      "Coll2steel_RotX=\""+str(values['-Coll2steelROTX-'])+"\"",
                                      "#Coll2steel_RotX_start,Coll2steel_RotX_stop,Coll2steel_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_RotX_start",
                                      "#boundaries_name_list.append(['Coll2steel_RotX']",
                                      "#Coll2steel_RotX,i=str(values[i]),i+1")
    if event == '-Coll2steelROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelROTY-'],
                                      "Coll2steel_RotY=\"270.\"",
                                      "Coll2steel_RotY=\""+str(values['-Coll2steelROTY-'])+"\"",
                                      "#Coll2steel_RotY_start,Coll2steel_RotY_stop,Coll2steel_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_RotY_start",
                                      "#boundaries_name_list.append(['Coll2steel_RotY']",
                                      "#Coll2steel_RotY,i=str(values[i]),i+1")
    if event == '-Coll2steelROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelROTZ-'],
                                      "Coll2steel_RotZ=\"0\"",
                                      "Coll2steel_RotZ=\""+str(values['-Coll2steelROTZ-'])+"\"",
                                      "#Coll2steel_RotZ_start,Coll2steel_RotZ_stop,Coll2steel_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_RotZ_start",
                                      "#boundaries_name_list.append(['Coll2steel_RotZ']",
                                      "#Coll2steel_RotZ,i=str(values[i]),i+1")
    if event == '-Coll2steelTRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelTRANSX-'],
                                      "Coll2steel_TransX=\"0\"",
                                      "Coll2steel_TransX=\""+str(values['-Coll2steelTRANSX-'])+"\"",
                                      "#Coll2steel_TransX_start,Coll2steel_TransX_stop,Coll2steel_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_TransX_start",
                                      "#boundaries_name_list.append(['Coll2steel_TransX']",
                                      "#Coll2steel_TransX,i=str(values[i]),i+1")
    if event == '-Coll2steelTRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelTRANSY-'],
                                      "Coll2steel_TransY=\"0.2\"",
                                      "Coll2steel_TransY=\""+str(values['-Coll2steelTRANSY-'])+"\"",
                                      "#Coll2steel_TransY_start,Coll2steel_TransY_stop,Coll2steel_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_TransY_start",
                                      "#boundaries_name_list.append(['Coll2steel_TransY']",
                                      "#Coll2steel_TransY,i=str(values[i]),i+1")
    if event == '-Coll2steelTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelTRANSZ-'],
                                      "Coll2steel_TransZ=\"-0.25\"",
                                      "Coll2steel_TransZ=\""+str(values['-Coll2steelTRANSZ-'])+"\"",
                                      "#Coll2steel_TransZ_start,Coll2steel_TransZ_stop,Coll2steel_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_TransZ_start",
                                      "#boundaries_name_list.append(['Coll2steel_TransZ']",
                                      "#Coll2steel_TransZ,i=str(values[i]),i+1")
    if event == '-Coll2steelLZ-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelLZ-'],
                                      "Coll2steel_LZ=\"12.\"",
                                      "Coll2steel_LZ=\""+str(values['-Coll2steelLZ-'])+"\"",
                                      "#Coll2steel_LZ_start,Coll2steel_LZ_stop,Coll2steel_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_LZ_start",
                                      "#boundaries_name_list.append(['Coll2steel_LZ']",
                                      "#Coll2steel_LZ,i=str(values[i]),i+1")
    if event == '-Coll2steelLY-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelLY-'],
                                      "Coll2steel_LY=\"0.2\"",
                                      "Coll2steel_LY=\""+str(values['-Coll2steelLY-'])+"\"",
                                      "#Coll2steel_LY_start,Coll2steel_LY_stop,Coll2steel_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_LY_start",
                                      "#boundaries_name_list.append(['Coll2steel_LY']",
                                      "#Coll2steel_LY,i=str(values[i]),i+1")
    if event == '-Coll2steelLX-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelLX-'],
                                      "Coll2steel_LX=\"10.\"",
                                      "Coll2steel_LX=\""+str(values['-Coll2steelLX-'])+"\"",
                                      "#Coll2steel_LX_start,Coll2steel_LX_stop,Coll2steel_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_LX_start",
                                      "#boundaries_name_list.append(['Coll2steel_LX']",
                                      "#Coll2steel_LX,i=str(values[i]),i+1")

    if event == '-Coll2steelLTX-_ENTER':
        replacement_witherrorhandling(values['-Coll2steelLTX-'],
                                      "Coll2steel_LTX=\"10.\"",
                                      "Coll2steel_LTX=\""+str(values['-Coll2steelLTX-'])+"\"",
                                      "#Coll2steel_LTX_start,Coll2steel_LTX_stop,Coll2steel_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll2steel_LTX_start",
                                      "#boundaries_name_list.append(['Coll2steel_LTX']",
                                      "#Coll2steel_LTX,i=str(values[i]),i+1")

    if event == '-Coll3steelTY-_ENTER':
        try:
            int(values['-Coll3steelTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll3steel_Type=\'\"G4RTrap\"\'",
                                   "Coll3steel_Type=\'\""+str(values['-Coll3steelTY-'])+"\"\'")
    if event == '-Coll3steelPAR-_ENTER':
        try:
            int(values['-Coll3steelPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll3steel_Parent=\'\"CollimatorsHorizontal\"\'",
                                   "Coll3steel_Parent=\'\""+str(values['-Coll3steelPAR-'])+"\"\'")
    if event == '-Coll3steelMAT-_ENTER':
        try:
            int(values['-Coll3steelMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll3steel_Material=\'\"Steel\"\'",
                                   "Coll3steel_Material=\'\""+str(values['-Coll3steelMAT-'])+"\"\'")
    if event == '-Coll3steelROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelROTX-'],
                                      "Coll3steel_RotX=\"-90.\"",
                                      "Coll3steel_RotX=\""+str(values['-Coll3steelROTX-'])+"\"",
                                      "#Coll3steel_RotX_start,Coll3steel_RotX_stop,Coll3steel_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_RotX_start",
                                      "#boundaries_name_list.append(['Coll3steel_RotX']",
                                      "#Coll3steel_RotX,i=str(values[i]),i+1")
    if event == '-Coll3steelROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelROTY-'],
                                      "Coll3steel_RotY=\"180.\"",
                                      "Coll3steel_RotY=\""+str(values['-Coll3steelROTY-'])+"\"",
                                      "#Coll3steel_RotY_start,Coll3steel_RotY_stop,Coll3steel_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_RotY_start",
                                      "#boundaries_name_list.append(['Coll3steel_RotY']",
                                      "#Coll3steel_RotY,i=str(values[i]),i+1")
    if event == '-Coll3steelROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelROTZ-'],
                                      "Coll3steel_RotZ=\"0\"",
                                      "Coll3steel_RotZ=\""+str(values['-Coll3steelROTZ-'])+"\"",
                                      "#Coll3steel_RotZ_start,Coll3steel_RotZ_stop,Coll3steel_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_RotZ_start",
                                      "#boundaries_name_list.append(['Coll3steel_RotZ']",
                                      "#Coll3steel_RotZ,i=str(values[i]),i+1")
    if event == '-Coll3steelTRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelTRANSX-'],
                                      "Coll3steel_TransX=\"0.2\"",
                                      "Coll3steel_TransX=\""+str(values['-Coll3steelTRANSX-'])+"\"",
                                      "#Coll3steel_TransX_start,Coll3steel_TransX_stop,Coll3steel_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_TransX_start",
                                      "#boundaries_name_list.append(['Coll3steel_TransX']",
                                      "#Coll3steel_TransX,i=str(values[i]),i+1")
    if event == '-Coll3steelTRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelTRANSY-'],
                                      "Coll3steel_TransY=\"0\"",
                                      "Coll3steel_TransY=\""+str(values['-Coll3steelTRANSY-'])+"\"",
                                      "#Coll3steel_TransY_start,Coll3steel_TransY_stop,Coll3steel_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_TransY_start",
                                      "#boundaries_name_list.append(['Coll3steel_TransY']",
                                      "#Coll3steel_TransY,i=str(values[i]),i+1")
    if event == '-Coll3steelTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelTRANSZ-'],
                                      "Coll3steel_TransZ=\"-0.25\"",
                                      "Coll3steel_TransZ=\""+str(values['-Coll3steelTRANSZ-'])+"\"",
                                      "#Coll3steel_TransZ_start,Coll3steel_TransZ_stop,Coll3steel_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_TransZ_start",
                                      "#boundaries_name_list.append(['Coll3steel_TransZ']",
                                      "#Coll3steel_TransZ,i=str(values[i]),i+1")
    if event == '-Coll3steelLZ-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelLZ-'],
                                      "Coll3steel_LZ=\"12.\"",
                                      "Coll3steel_LZ=\""+str(values['-Coll3steelLZ-'])+"\"",
                                      "#Coll3steel_LZ_start,Coll3steel_LZ_stop,Coll3steel_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_LZ_start",
                                      "#boundaries_name_list.append(['Coll3steel_LZ']",
                                      "#Coll3steel_LZ,i=str(values[i]),i+1")
    if event == '-Coll3steelLY-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelLY-'],
                                      "Coll3steel_LY=\"0.2\"",
                                      "Coll3steel_LY=\""+str(values['-Coll3steelLY-'])+"\"",
                                      "#Coll3steel_LY_start,Coll3steel_LY_stop,Coll3steel_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_LY_start",
                                      "#boundaries_name_list.append(['Coll3steel_LY']",
                                      "#Coll3steel_LY,i=str(values[i]),i+1")
    if event == '-Coll3steelLX-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelLX-'],
                                      "Coll3steel_LX=\"10.\"",
                                      "Coll3steel_LX=\""+str(values['-Coll3steelLX-'])+"\"",
                                      "#Coll3steel_LX_start,Coll3steel_LX_stop,Coll3steel_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_LX_start",
                                      "#boundaries_name_list.append(['Coll3steel_LX']",
                                      "#Coll3steel_LX,i=str(values[i]),i+1")

    if event == '-Coll3steelLTX-_ENTER':
        replacement_witherrorhandling(values['-Coll3steelLTX-'],
                                      "Coll3steel_LTX=\"10.\"",
                                      "Coll3steel_LTX=\""+str(values['-Coll3steelLTX-'])+"\"",
                                      "#Coll3steel_LTX_start,Coll3steel_LTX_stop,Coll3steel_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll3steel_LTX_start",
                                      "#boundaries_name_list.append(['Coll3steel_LTX']",
                                      "#Coll3steel_LTX,i=str(values[i]),i+1")

    if event == '-Coll4steelTY-_ENTER':
        try:
            int(values['-Coll4steelTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll4steel_Type=\'\"G4RTrap\"\'",
                                   "Coll4steel_Type=\'\""+str(values['-Coll4steelTY-'])+"\"\'")
    if event == '-Coll4steelPAR-_ENTER':
        try:
            int(values['-Coll4steelPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll4steel_Parent=\'\"CollimatorsHorizontal\"\'",
                                   "Coll4steel_Parent=\'\""+str(values['-Coll4steelPAR-'])+"\"\'")
    if event == '-Coll4steelMAT-_ENTER':
        try:
            int(values['-Coll4steelMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("Coll4steel_Material=\'\"Steel\"\'",
                                   "Coll4steel_Material=\'\""+str(values['-Coll4steelMAT-'])+"\"\'")
    if event == '-Coll4steelROTX-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelROTX-'],
                                      "Coll4steel_RotX=\"-90.\"",
                                      "Coll4steel_RotX=\""+str(values['-Coll4steelROTX-'])+"\"",
                                      "#Coll4steel_RotX_start,Coll4steel_RotX_stop,Coll4steel_RotX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_RotX_start",
                                      "#boundaries_name_list.append(['Coll4steel_RotX']",
                                      "#Coll4steel_RotX,i=str(values[i]),i+1")
    if event == '-Coll4steelROTY-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelROTY-'],
                                      "Coll4steel_RotY=\"0.\"",
                                      "Coll4steel_RotY=\""+str(values['-Coll4steelROTY-'])+"\"",
                                      "#Coll4steel_RotY_start,Coll4steel_RotY_stop,Coll4steel_RotY_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_RotY_start",
                                      "#boundaries_name_list.append(['Coll4steel_RotY']",
                                      "#Coll4steel_RotY,i=str(values[i]),i+1")
    if event == '-Coll4steelROTZ-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelROTZ-'],
                                      "Coll4steel_RotZ=\"0\"",
                                      "Coll4steel_RotZ=\""+str(values['-Coll4steelROTZ-'])+"\"",
                                      "#Coll4steel_RotZ_start,Coll4steel_RotZ_stop,Coll4steel_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_RotZ_start",
                                      "#boundaries_name_list.append(['Coll4steel_RotZ']",
                                      "#Coll4steel_RotZ,i=str(values[i]),i+1")
    if event == '-Coll4steelTRANSX-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelTRANSX-'],
                                      "Coll4steel_TransX=\"0.2\"",
                                      "Coll4steel_TransX=\""+str(values['-Coll4steelTRANSX-'])+"\"",
                                      "#Coll4steel_TransX_start,Coll4steel_TransX_stop,Coll4steel_TransX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_TransX_start",
                                      "#boundaries_name_list.append(['Coll4steel_TransX']",
                                      "#Coll4steel_TransX,i=str(values[i]),i+1")
    if event == '-Coll4steelTRANSY-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelTRANSY-'],
                                      "Coll4steel_TransY=\"0\"",
                                      "Coll4steel_TransY=\""+str(values['-Coll4steelTRANSY-'])+"\"",
                                      "#Coll4steel_TransY_start,Coll4steel_TransY_stop,Coll4steel_TransY_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_TransY_start",
                                      "#boundaries_name_list.append(['Coll4steel_TransY']",
                                      "#Coll4steel_TransY,i=str(values[i]),i+1")
    if event == '-Coll4steelTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelTRANSZ-'],
                                      "Coll4steel_TransZ=\"-0.25\"",
                                      "Coll4steel_TransZ=\""+str(values['-Coll4steelTRANSZ-'])+"\"",
                                      "#Coll4steel_TransZ_start,Coll4steel_TransZ_stop,Coll4steel_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_TransZ_start",
                                      "#boundaries_name_list.append(['Coll4steel_TransZ']",
                                      "#Coll4steel_TransZ,i=str(values[i]),i+1")
    if event == '-Coll4steelLZ-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelLZ-'],
                                      "Coll4steel_LZ=\"12.\"",
                                      "Coll4steel_LZ=\""+str(values['-Coll4steelLZ-'])+"\"",
                                      "#Coll4steel_LZ_start,Coll4steel_LZ_stop,Coll4steel_LZ_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_LZ_start",
                                      "#boundaries_name_list.append(['Coll4steel_LZ']",
                                      "#Coll4steel_LZ,i=str(values[i]),i+1")
    if event == '-Coll4steelLY-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelLY-'],
                                      "Coll4steel_LY=\"0.2\"",
                                      "Coll4steel_LY=\""+str(values['-Coll4steelLY-'])+"\"",
                                      "#Coll4steel_LY_start,Coll4steel_LY_stop,Coll4steel_LY_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_LY_start",
                                      "#boundaries_name_list.append(['Coll4steel_LY']",
                                      "#Coll4steel_LY,i=str(values[i]),i+1")
    if event == '-Coll4steelLX-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelLX-'],
                                      "Coll4steel_LX=\"10.\"",
                                      "Coll4steel_LX=\""+str(values['-Coll4steelLX-'])+"\"",
                                      "#Coll4steel_LX_start,Coll4steel_LX_stop,Coll4steel_LX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_LX_start",
                                      "#boundaries_name_list.append(['Coll4steel_LX']",
                                      "#Coll4steel_LX,i=str(values[i]),i+1")

    if event == '-Coll4steelLTX-_ENTER':
        replacement_witherrorhandling(values['-Coll4steelLTX-'],
                                      "Coll4steel_LTX=\"10.\"",
                                      "Coll4steel_LTX=\""+str(values['-Coll4steelLTX-'])+"\"",
                                      "#Coll4steel_LTX_start,Coll4steel_LTX_stop,Coll4steel_LTX_step = 0,0,0",
                                      "#boundaries_list.append([Coll4steel_LTX_start",
                                      "#boundaries_name_list.append(['Coll4steel_LTX']",
                                      "#Coll4steel_LTX,i=str(values[i]),i+1")

    if event == '-STEELFILTY-_ENTER':
        try:
            int(values['-STEELFILTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("SteelFilter_Type=\'\"TsBox\"\'",
                                   "SteelFilter_Type=\'\""+str(values['-STEELFILTY-'])+"\"\'")
    if event == '-STEELFILPAR-_ENTER':
        try:
            int(values['-STEELFILPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("SteelFilter_Parent=\'\"SteelFilterGroup\"\'",
                                   "SteelFilter_Parent=\'\""+str(values['-STEELFILPAR-'])+"\"\'")
    if event == '-STEELFILMAT-_ENTER':
        try:
            int(values['-STEELFILMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("SteelFilter_Material=\'\"Steel\"\'",
                                   "SteelFilter_Material=\'\""+str(values['-STEELFILMAT-'])+"\"\'")
    if event == '-STEELFILROTX-_ENTER':
        replacement_witherrorhandling(values['-STEELFILROTX-'],
                                      "SteelFilter_RotX=\"-90.\"",
                                      "SteelFilter_RotX=\""+str(values['-STEELFILROTX-'])+"\"",
                                      "#SteelFilter_RotX_start,SteelFilter_RotX_stop,SteelFilter_RotX_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_RotX_start",
                                      "#boundaries_name_list.append(['SteelFilter_RotX']",
                                      "#SteelFilter_RotX,i=str(values[i]),i+1")
    if event == '-STEELFILROTY-_ENTER':
        replacement_witherrorhandling(values['-STEELFILROTY-'],
                                      "SteelFilter_RotY=\"0.\"",
                                      "SteelFilter_RotY=\""+str(values['-STEELFILROTY-'])+"\"",
                                      "#SteelFilter_RotY_start,SteelFilter_RotY_stop,SteelFilter_RotY_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_RotY_start",
                                      "#boundaries_name_list.append(['SteelFilter_RotY']",
                                      "#SteelFilter_RotY,i=str(values[i]),i+1")
    if event == '-STEELFILROTZ-_ENTER':
        replacement_witherrorhandling(values['-STEELFILROTZ-'],
                                      "SteelFilter_RotZ=\"0\"",
                                      "SteelFilter_RotZ=\""+str(values['-STEELFILROTZ-'])+"\"",
                                      "#SteelFilter_RotZ_start,SteelFilter_RotZ_stop,SteelFilter_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_RotZ_start",
                                      "#boundaries_name_list.append(['SteelFilter_RotZ']",
                                      "#SteelFilter_RotZ,i=str(values[i]),i+1")
    if event == '-STEELFILTRANSX-_ENTER':
        replacement_witherrorhandling(values['-STEELFILTRANSX-'],
                                      "SteelFilter_TransX=\"-5.5\"",
                                      "SteelFilter_TransX=\""+str(values['-STEELFILTRANSX-'])+"\"",
                                      "#SteelFilter_TransX_start,SteelFilter_TransX_stop,SteelFilter_TransX_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_TransX_start",
                                      "#boundaries_name_list.append(['SteelFilter_TransX']",
                                      "#SteelFilter_TransX,i=str(values[i]),i+1")
    if event == '-STEELFILTRANSY-_ENTER':
        replacement_witherrorhandling(values['-STEELFILTRANSY-'],
                                      "SteelFilter_TransY=\"0.\"",
                                      "SteelFilter_TransY=\""+str(values['-STEELFILTRANSY-'])+"\"",
                                      "#SteelFilter_TransY_start,SteelFilter_TransY_stop,SteelFilter_TransY_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_TransY_start",
                                      "#boundaries_name_list.append(['SteelFilter_TransY']",
                                      "#SteelFilter_TransY,i=str(values[i]),i+1")
    if event == '-STEELFILTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-STEELFILTRANSZ-'],
                                      "SteelFilter_TransZ=\"0.\"",
                                      "SteelFilter_TransZ=\""+str(values['-STEELFILTRANSZ-'])+"\"",
                                      "#SteelFilter_TransZ_start,SteelFilter_TransZ_stop,SteelFilter_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_TransZ_start",
                                      "#boundaries_name_list.append(['SteelFilter_TransZ']",
                                      "#SteelFilter_TransZ,i=str(values[i]),i+1")
    if event == '-STEELFILHLZ-_ENTER':
        replacement_witherrorhandling(values['-STEELFILHLZ-'],
                                      "SteelFilter_HLZ=\"0.01\"",
                                      "SteelFilter_HLZ=\""+str(values['-STEELFILHLZ-'])+"\"",
                                      "#SteelFilter_HLZ_start,SteelFilter_HLZ_stop,SteelFilter_HLZ_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_HLZ_start",
                                      "#boundaries_name_list.append(['SteelFilter_HLZ']",
                                      "#SteelFilter_HLZ,i=str(values[i]),i+1")
    if event == '-STEELFILHLY-_ENTER':
        replacement_witherrorhandling(values['-STEELFILHLY-'],
                                      "SteelFilter_HLY=\"10.\"",
                                      "SteelFilter_HLY=\""+str(values['-STEELFILHLY-'])+"\"",
                                      "#SteelFilter_HLY_start,SteelFilter_HLY_stop,SteelFilter_HLY_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_HLY_start",
                                      "#boundaries_name_list.append(['SteelFilter_HLY']",
                                      "#SteelFilter_HLY,i=str(values[i]),i+1")
    if event == '-STEELFILHLX-_ENTER':
        replacement_witherrorhandling(values['-STEELFILHLX-'],
                                      "SteelFilter_HLX=\"10.\"",
                                      "SteelFilter_HLX=\""+str(values['-STEELFILHLX-'])+"\"",
                                      "#SteelFilter_HLX_start,SteelFilter_HLX_stop,SteelFilter_HLX_step = 0,0,0",
                                      "#boundaries_list.append([SteelFilter_HLX_start",
                                      "#boundaries_name_list.append(['SteelFilter_HLX']",
                                      "#SteelFilter_HLX,i=str(values[i]),i+1")

    if event == '-TITFILPAR-_ENTER':
        try:
            int(values['-TITFILPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("TitaniumFilter_Parent=\'\"TitaniumFilterGroup\"\'",
                                   "TitaniumFilter_Parent=\'\""+str(values['-TITFILPAR-'])+"\"\'")

    if event == '-TITFILTY-_ENTER':
        try:
            int(values['-TITFILTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except:
            replacement_floatorint("TitaniumFilter_Type=\'\"TsBox\"\'",
                                   "TitaniumFilter_Type=\'\""+str(values['-TITFILTY-'])+"\"\'")
    if event == '-TITFILMAT-_ENTER':
        try:
            int(values['-TITFILMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("TitaniumFilter_Material=\'\"Titanium\"\'",
                                   "TitaniumFilter_Material=\'\""+str(values['-TITFILMAT-'])+"\"\'")
    if event == '-TITFILROTX-_ENTER':
        replacement_witherrorhandling(values['-TITFILROTX-'],
                                      "TitaniumFilter_RotX=\"0.\"",
                                      "TitaniumFilter_RotX=\""+str(values['-TITFILROTX-'])+"\"",
                                      "#TitaniumFilter_RotX_start,TitaniumFilter_RotX_stop,TitaniumFilter_RotX_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_RotX_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_RotX']",
                                      "#TitaniumFilter_RotX,i=str(values[i]),i+1")
    if event == '-TITFILROTY-_ENTER':
        replacement_witherrorhandling(values['-TITFILROTY-'],
                                      "TitaniumFilter_RotY=\"0.\"",
                                      "TitaniumFilter_RotY=\""+str(values['-TITFILROTY-'])+"\"",
                                      "#TitaniumFilter_RotY_start,TitaniumFilter_RotY_stop,TitaniumFilter_RotY_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_RotY_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_RotY']",
                                      "#TitaniumFilter_RotY,i=str(values[i]),i+1")
    if event == '-TITFILROTZ-_ENTER':
        replacement_witherrorhandling(values['-TITFILROTZ-'],
                                      "TitaniumFilter_RotZ=\"0\"",
                                      "TitaniumFilter_RotZ=\""+str(values['-TITFILROTZ-'])+"\"",
                                      "#TitaniumFilter_RotZ_start,TitaniumFilter_RotZ_stop,TitaniumFilter_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_RotZ_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_RotZ']",
                                      "#TitaniumFilter_RotZ,i=str(values[i]),i+1")
    if event == '-TITFILTRANSX-_ENTER':
        replacement_witherrorhandling(values['-TITFILTRANSX-'],
                                      "TitaniumFilter_TransX=\"0.\"",
                                      "TitaniumFilter_TransX=\""+str(values['-TITFILTRANSX-'])+"\"",
                                      "#TitaniumFilter_TransX_start,TitaniumFilter_TransX_stop,TitaniumFilter_TransX_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_TransX_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_TransX']",
                                      "#TitaniumFilter_TransX,i=str(values[i]),i+1")
    if event == '-TITFILTRANSY-_ENTER':
        replacement_witherrorhandling(values['-TITFILTRANSY-'],
                                      "TitaniumFilter_TransY=\"0.\"",
                                      "TitaniumFilter_TransY=\""+str(values['-TITFILTRANSY-'])+"\"",
                                      "#TitaniumFilter_TransY_start,TitaniumFilter_TransY_stop,TitaniumFilter_TransY_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_TransY_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_TransY']",
                                      "#TitaniumFilter_TransY,i=str(values[i]),i+1")
    if event == '-TITFILTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-TITFILTRANSZ-'],
                                      "TitaniumFilter_TransZ=\"0.\"",
                                      "TitaniumFilter_TransZ=\""+str(values['-TITFILTRANSZ-'])+"\"",
                                      "#TitaniumFilter_TransZ_start,TitaniumFilter_TransZ_stop,TitaniumFilter_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_TransZ_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_TransZ']",
                                      "#TitaniumFilter_TransZ,i=str(values[i]),i+1")
    if event == '-TITFILHLZ-_ENTER':
        replacement_witherrorhandling(values['-TITFILHLZ-'],
                                      "TitaniumFilter_HLZ=\"0.0445\"",
                                      "TitaniumFilter_HLZ=\""+str(values['-TITFILHLZ-'])+"\"",
                                      "#TitaniumFilter_HLZ_start,TitaniumFilter_HLZ_stop,TitaniumFilter_HLZ_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_HLZ_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_HLZ']",
                                      "#TitaniumFilter_HLZ,i=str(values[i]),i+1")
    if event == '-TITFILHLY-_ENTER':
        replacement_witherrorhandling(values['-TITFILHLY-'],
                                      "TitaniumFilter_HLY=\"10.\"",
                                      "TitaniumFilter_HLY=\""+str(values['-TITFILHLY-'])+"\"",
                                      "#TitaniumFilter_HLY_start,TitaniumFilter_HLY_stop,TitaniumFilter_HLY_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_HLY_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_HLY']",
                                      "#TitaniumFilter_HLY,i=str(values[i]),i+1")
    if event == '-TITFILHLX-_ENTER':
        replacement_witherrorhandling(values['-TITFILHLX-'],
                                      "TitaniumFilter_HLX=\"10.\"",
                                      "TitaniumFilter_HLX=\""+str(values['-TITFILHLX-'])+"\"",
                                      "#TitaniumFilter_HLX_start,TitaniumFilter_HLX_stop,TitaniumFilter_HLX_step = 0,0,0",
                                      "#boundaries_list.append([TitaniumFilter_HLX_start",
                                      "#boundaries_name_list.append(['TitaniumFilter_HLX']",
                                      "#TitaniumFilter_HLX,i=str(values[i]),i+1")


    if event == '-DEMOFLATTY-_ENTER':
        try:
            int(values['-DEMOFLATTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("DemoFlat_Type=\'\"TsBox\"\'",
                                   "DemoFlat_Type=\'\""+str(values['-DEMOFLATTY-'])+"\"\'")
    if event == '-DEMOFLATPAR-_ENTER':
        try:
            int(values['-DEMOFLATPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("DemoFlat_Parent=\'\"BowtieFilter\"\'",
                                   "DemoFlat_Parent=\'\""+str(values['-DEMOFLATPAR-'])+"\"\'")
    if event == '-DEMOFLATMAT-_ENTER':
        try:
            int(values['-DEMOFLATMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("DemoFlat_Material=\'\"Aluminum\"\'",
                                   "DemoFlat_Material=\'\""+str(values['-DEMOFLATMAT-'])+"\"\'")
    if event == '-DEMOFLATROTX-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATROTX-'],
                                      "DemoFlat_RotX=\"0.\"",
                                      "DemoFlat_RotX=\""+str(values['-DEMOFLATROTX-'])+"\"",
                                      "#DemoFlat_RotX_start,DemoFlat_RotX_stop,DemoFlat_RotX_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_RotX_start",
                                      "#boundaries_name_list.append(['DemoFlat_RotX']",
                                      "#DemoFlat_RotX,i=str(values[i]),i+1")
    if event == '-DEMOFLATROTY-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATROTY-'],
                                      "DemoFlat_RotY=\"-90.\"",
                                      "DemoFlat_RotY=\""+str(values['-DEMOFLATROTY-'])+"\"",
                                      "#DemoFlat_RotY_start,DemoFlat_RotY_stop,DemoFlat_RotY_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_RotY_start",
                                      "#boundaries_name_list.append(['DemoFlat_RotY']",
                                      "#DemoFlat_RotY,i=str(values[i]),i+1")
    if event == '-DEMOFLATROTZ-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATROTZ-'],
                                      "DemoFlat_RotZ=\"0.\"",
                                      "DemoFlat_RotZ=\""+str(values['-DEMOFLATROTZ-'])+"\"",
                                      "#DemoFlat_RotZ_start,DemoFlat_RotZ_stop,DemoFlat_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_RotZ_start",
                                      "#boundaries_name_list.append(['DemoFlat_RotZ']",
                                      "#DemoFlat_RotZ,i=str(values[i]),i+1")
    if event == '-DEMOFLATTRANSX-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATTRANSX-'],
                                      "DemoFlat_TransX=\"0.0\"",
                                      "DemoFlat_TransX=\""+str(values['-DEMOFLATTRANSX-'])+"\"",
                                      "#DemoFlat_TransX_start,DemoFlat_TransX_stop,DemoFlat_TransX_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_TransX_start",
                                      "#boundaries_name_list.append(['DemoFlat_TransX']",
                                      "#DemoFlat_TransX,i=str(values[i]),i+1")
    if event == '-DEMOFLATTRANSY-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATTRANSY-'],
                                      "DemoFlat_TransY=\"0.\"",
                                      "DemoFlat_TransY=\""+str(values['-DEMOFLATTRANSY-'])+"\"",
                                      "#DemoFlat_TransY_start,DemoFlat_TransY_stop,DemoFlat_TransY_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_TransY_start",
                                      "#boundaries_name_list.append(['DemoFlat_TransY']",
                                      "#DemoFlat_TransY,i=str(values[i]),i+1")
    if event == '-DEMOFLATTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATTRANSZ-'],
                                      "DemoFlat_TransZ=\"Ge/DemoFlat/HLX\""
                                      "DemoFlat_TransZ=\""+str(values['-DEMOFLATTRANSZ-'])+"\"",
                                      "#DemoFlat_TransZ_start,DemoFlat_TransZ_stop,DemoFlat_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_TransZ_start",
                                      "#boundaries_name_list.append(['DemoFlat_TransZ']",
                                      "#DemoFlat_TransZ,i=str(values[i]),i+1")
    if event == '-DEMOFLATHLZ-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATHLZ-'],
                                      "DemoFlat_HLZ=\"7.5\"",
                                      "DemoFlat_HLZ=\""+str(values['-DEMOFLATHLZ-'])+"\"",
                                      "#DemoFlat_HLZ_start,DemoFlat_HLZ_stop,DemoFlat_HLZ_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_HLZ_start",
                                      "#boundaries_name_list.append(['DemoFlat_HLZ']",
                                      "#DemoFlat_HLZ,i=str(values[i]),i+1")
    if event == '-DEMOFLATHLY-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATHLY-'],
                                      "DemoFlat_HLY=\"0.4\"",
                                      "DemoFlat_HLY=\""+str(values['-DEMOFLATHLY-'])+"\"",
                                      "#DemoFlat_HLY_start,DemoFlat_HLY_stop,DemoFlat_HLY_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_HLY_start",
                                      "#boundaries_name_list.append(['DemoFlat_HLY']",
                                      "#DemoFlat_HLY,i=str(values[i]),i+1")
    if event == '-DEMOFLATHLX-_ENTER':
        replacement_witherrorhandling(values['-DEMOFLATHLX-'],
                                      "DemoFlat_HLX=\"0.1\"",
                                      "DemoFlat_HLX=\""+str(values['-DEMOFLATHLX-'])+"\"",
                                      "#DemoFlat_HLX_start,DemoFlat_HLX_stop,DemoFlat_HLX_step = 0,0,0",
                                      "#boundaries_list.append([DemoFlat_HLX_start",
                                      "#boundaries_name_list.append(['DemoFlat_HLX']",
                                      "#DemoFlat_HLX,i=str(values[i]),i+1")
    if event == '-TSBTY-_ENTER':
        try:
            int(values['-TSBTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("topsidebox_Type=\'\"TsBox\"\'",
                                   "topsidebox_Type=\'\""+str(values['-TSBTY-'])+"\"\'")
    if event == '-TSBPAR-_ENTER':
        try:
            int(values['-TSBPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("topsidebox_Parent=\'\"BowtieFilter\"\'",
                                   "topsidebox_Parent=\'\""+str(values['-TSBPAR-'])+"\"\'")
    if event == '-TSBMAT-_ENTER':
        try:
            int(values['-TSBMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("topsidebox_Material=\'\"Aluminum\"\'",
                                   "topsidebox_Material=\'\""+str(values['-TSBMAT-'])+"\"\'")
    if event == '-TSBROTX-_ENTER':
        replacement_witherrorhandling(values['-TSBROTX-'],
                                      "topsidebox_RotX=\"0.\"",
                                      "topsidebox_RotX=\""+str(values['-TSBROTX-'])+"\"",
                                      "#topsidebox_RotX_start,topsidebox_RotX_stop,topsidebox_RotX_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_RotX_start",
                                      "#boundaries_name_list.append(['topsidebox_RotX']",
                                      "#topsidebox_RotX,i=str(values[i]),i+1")
    if event == '-TSBROTY-_ENTER':
        replacement_witherrorhandling(values['-TSBROTY-'],
                                      "topsidebox_RotY=\"-90.\"",
                                      "topsidebox_RotY=\""+str(values['-TSBROTY-'])+"\"",
                                      "#topsidebox_RotY_start,topsidebox_RotY_stop,topsidebox_RotY_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_RotY_start",
                                      "#boundaries_name_list.append(['topsidebox_RotY']",
                                      "#topsidebox_RotY,i=str(values[i]),i+1")
    if event == '-TSBROTZ-_ENTER':
        replacement_witherrorhandling(values['-TSBROTZ-'],
                                      "topsidebox_RotZ=\"0\"",
                                      "topsidebox_RotZ=\""+str(values['-TSBROTZ-'])+"\"",
                                      "#topsidebox_RotZ_start,topsidebox_RotZ_stop,topsidebox_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_RotZ_start",
                                      "#boundaries_name_list.append(['topsidebox_RotZ']",
                                      "#topsidebox_RotZ,i=str(values[i]),i+1")
    if event == '-TSBTRANSX-_ENTER':
        replacement_witherrorhandling(values['-TSBTRANSX-'],
                                      "topsidebox_TransX=\"0.0\"",
                                      "topsidebox_TransX=\""+str(values['-TSBTRANSX-'])+"\"",
                                      "#topsidebox_TransX_start,topsidebox_TransX_stop,topsidebox_TransX_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_TransX_start",
                                      "#boundaries_name_list.append(['topsidebox_TransX']",
                                      "#topsidebox_TransX,i=str(values[i]),i+1")
    if event == '-TSBTRANSY-_ENTER':
        replacement_witherrorhandling(values['-TSBTRANSY-'],
                                      "topsidebox_TransY=\"5.0\"",
                                      "topsidebox_TransY=\""+str(values['-TSBTRANSY-'])+"\"",
                                      "#topsidebox_TransY_start,topsidebox_TransY_stop,topsidebox_TransY_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_TransY_start",
                                      "#boundaries_name_list.append(['topsidebox_TransY']",
                                      "#topsidebox_TransY,i=str(values[i]),i+1")
    if event == '-TSBTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-TSBTRANSZ-'],
                                      "topsidebox_TransZ=\"2.6\"",
                                      "topsidebox_TransZ=\""+str(values['-TSBTRANSZ-'])+"\"",
                                      "#topsidebox_TransZ_start,topsidebox_TransZ_stop,topsidebox_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_TransZ_start",
                                      "#boundaries_name_list.append(['topsidebox_TransZ']",
                                      "#topsidebox_TransZ,i=str(values[i]),i+1")
    if event == '-TSBHLZ-_ENTER':
        replacement_witherrorhandling(values['-TSBHLZ-'],
                                      "topsidebox_HLZ=\"7.5\"",
                                      "topsidebox_HLZ=\""+str(values['-TSBHLZ-'])+"\"",
                                      "#topsidebox_HLZ_start,topsidebox_HLZ_stop,topsidebox_HLZ_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_HLZ_start",
                                      "#boundaries_name_list.append(['topsidebox_HLZ']",
                                      "#topsidebox_HLZ,i=str(values[i]),i+1")
    if event == '-TSBHLY-_ENTER':
        replacement_witherrorhandling(values['-TSBHLY-'],
                                      "topsidebox_HLY=\"2.5\"",
                                      "topsidebox_HLY=\""+str(values['-TSBHLY-'])+"\"",
                                      "#topsidebox_HLY_start,topsidebox_HLY_stop,topsidebox_HLY_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_HLY_start",
                                      "#boundaries_name_list.append(['topsidebox_HLY']",
                                      "#topsidebox_HLY,i=str(values[i]),i+1")
    if event == '-TSBHLX-_ENTER':
        replacement_witherrorhandling(values['-TSBHLX-'],
                                      "topsidebox_HLX=\"2.75\"",
                                      "topsidebox_HLX=\""+str(values['-TSBHLX-'])+"\"",
                                      "#topsidebox_HLX_start,topsidebox_HLX_stop,topsidebox_HLX_step = 0,0,0",
                                      "#boundaries_list.append([topsidebox_HLX_start",
                                      "#boundaries_name_list.append(['topsidebox_HLX']",
                                      "#topsidebox_HLX,i=str(values[i]),i+1")

    if event == '-BSBTY-_ENTER':
        try:
            int(values['-BSBTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("bottomsidebox_Type=\'\"TsBox\"\'",
                                   "bottomsidebox_Type=\'\""+str(values['-BSBTY-'])+"\"\'")
    if event == '-BSBPAR-_ENTER':
        try:
            int(values['-BSBPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("bottomsidebox_Parent=\'\"BowtieFilter\"\'",
                                   "bottomsidebox_Parent=\'\""+str(values['-BSBPAR-'])+"\"\'")
    if event == '-BSBMAT-_ENTER':
        try:
            int(values['-BSBMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("bottomsidebox_Material=\'\"Aluminum\"\'",
                                   "bottomsidebox_Material=\'\""+str(values['-BSBMAT-'])+"\"\'")
    if event == '-BSBROTX-_ENTER':
        replacement_witherrorhandling(values['-BSBROTX-'],
                                      "bottomsidebox_RotX=\"-90.\"",
                                      "bottomsidebox_RotX=\""+str(values['-BSBROTX-'])+"\"",
                                      "#bottomsidebox_RotX_start,bottomsidebox_RotX_stop,bottomsidebox_RotX_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_RotX_start",
                                      "#boundaries_name_list.append(['bottomsidebox_RotX']",
                                      "#bottomsidebox_RotX,i=str(values[i]),i+1")
    if event == '-BSBROTY-_ENTER':
        replacement_witherrorhandling(values['-BSBROTY-'],
                                      "bottomsidebox_RotY=\"0.\"",
                                      "bottomsidebox_RotY=\""+str(values['-BSBROTY-'])+"\"",
                                      "#bottomsidebox_RotY_start,bottomsidebox_RotY_stop,bottomsidebox_RotY_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_RotY_start",
                                      "#boundaries_name_list.append(['bottomsidebox_RotY']",
                                      "#bottomsidebox_RotY,i=str(values[i]),i+1")
    if event == '-BSBROTZ-_ENTER':
        replacement_witherrorhandling(values['-BSBROTZ-'],
                                      "bottomsidebox_RotZ=\"0\"",
                                      "bottomsidebox_RotZ=\""+str(values['-BSBROTZ-'])+"\"",
                                      "#bottomsidebox_RotZ_start,bottomsidebox_RotZ_stop,bottomsidebox_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_RotZ_start",
                                      "#boundaries_name_list.append(['bottomsidebox_RotZ']",
                                      "#bottomsidebox_RotZ,i=str(values[i]),i+1")
    if event == '-BSBTRANSX-_ENTER':
        replacement_witherrorhandling(values['-BSBTRANSX-'],
                                      "bottomsidebox_TransX=\"-5.5\"",
                                      "bottomsidebox_TransX=\""+str(values['-BSBTRANSX-'])+"\"",
                                      "#bottomsidebox_TransX_start,bottomsidebox_TransX_stop,bottomsidebox_TransX_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_TransX_start",
                                      "#boundaries_name_list.append(['bottomsidebox_TransX']",
                                      "#bottomsidebox_TransX,i=str(values[i]),i+1")
    if event == '-BSBTRANSY-_ENTER':
        replacement_witherrorhandling(values['-BSBTRANSY-'],
                                      "bottomsidebox_TransY=\"-5.0 cm + Ge/DemoRTrap/\"",
                                      "bottomsidebox_TransY=\""+str(values['-BSBTRANSY-'])+"\"",
                                      "#bottomsidebox_TransY_start,bottomsidebox_TransY_stop,bottomsidebox_TransY_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_TransY_start",
                                      "#boundaries_name_list.append(['bottomsidebox_TransY']",
                                      "#bottomsidebox_TransY,i=str(values[i]),i+1")
    if event == '-BSBTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-BSBTRANSZ-'],
                                      "bottomsidebox_TransZ=\"Ge/bottomsidebox/HLX\"",
                                      "bottomsidebox_TransZ=\""+str(values['-BSBTRANSZ-'])+"\"",
                                      "#bottomsidebox_TransZ_start,bottomsidebox_TransZ_stop,bottomsidebox_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_TransZ_start",
                                      "#boundaries_name_list.append(['bottomsidebox_TransZ']",
                                      "#bottomsidebox_TransZ,i=str(values[i]),i+1")
    if event == '-BSBHLZ-_ENTER':
        replacement_witherrorhandling(values['-BSBHLZ-'],
                                      "bottomsidebox_HLZ=\"0.01\"",
                                      "bottomsidebox_HLZ=\""+str(values['-BSBHLZ-'])+"\"",
                                      "#bottomsidebox_HLZ_start,bottomsidebox_HLZ_stop,bottomsidebox_HLZ_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_HLZ_start",
                                      "#boundaries_name_list.append(['bottomsidebox_HLZ']",
                                      "#bottomsidebox_HLZ,i=str(values[i]),i+1")
    if event == '-BSBHLY-_ENTER':
        replacement_witherrorhandling(values['-BSBHLY-'],
                                      "bottomsidebox_HLY=\"10.\"",
                                      "bottomsidebox_HLY=\""+str(values['-BSBHLY-'])+"\"",
                                      "#bottomsidebox_HLY_start,bottomsidebox_HLY_stop,bottomsidebox_HLY_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_HLY_start",
                                      "#boundaries_name_list.append(['bottomsidebox_HLY']",
                                      "#bottomsidebox_HLY,i=str(values[i]),i+1")
    if event == '-BSBHLX-_ENTER':
        replacement_witherrorhandling(values['-BSBHLX-'],
                                      "bottomsidebox_HLX=\"10.\"",
                                      "bottomsidebox_HLX=\""+str(values['-BSBHLX-'])+"\"",
                                      "#bottomsidebox_HLX_start,bottomsidebox_HLX_stop,bottomsidebox_HLX_step = 0,0,0",
                                      "#boundaries_list.append([bottomsidebox_HLX_start",
                                      "#boundaries_name_list.append(['bottomsidebox_HLX']",
                                      "#bottomsidebox_HLX,i=str(values[i]),i+1")

    if event == '-COUCHTY-_ENTER':
        try:
            int(values['-COUCHTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("couch_Type=\'\"TsBox\"\'",
                                   "couch_Type=\'\""+str(values['-COUCHTY-'])+"\"\'")
    if event == '-COUCHPAR-_ENTER':
        try:
            int(values['-COUCHPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("couch_Parent=\'\"World\"\'",
                                   "couch_Parent=\'\""+str(values['-COUCHPAR-'])+"\"\'")
    if event == '-COUCHMAT-_ENTER':
        try:
            int(values['-COUCHMAT-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("couch_Material=\'\"Aluminum\"\'",
                                   "couch_Material=\'\""+str(values['-COUCHMAT-'])+"\"\'")
    if event == '-COUCHTRANSX-_ENTER':
        replacement_witherrorhandling(values['-COUCHTRANSX-'],
                                      "couch_TransX=\"0.0\"",
                                      "couch_TransX=\""+str(values['-COUCHTRANSX-'])+"\"",
                                      "#couch_TransX_start,couch_TransX_stop,couch_TransX_step = 0,0,0",
                                      "#boundaries_list.append([couch_TransX_start",
                                      "#boundaries_name_list.append(['couch_TransX']",
                                      "#couch_TransX,i=str(values[i]),i+1")
    if event == '-COUCHTRANSY-_ENTER':
        replacement_witherrorhandling(values['-COUCHTRANSY-'],
                                      "couch_TransY=\"0.0\"",
                                      "couch_TransY=\""+str(values['-COUCHTRANSY-'])+"\"",
                                      "#couch_TransY_start,couch_TransY_stop,couch_TransY_step = 0,0,0",
                                      "#boundaries_list.append([couch_TransY_start",
                                      "#boundaries_name_list.append(['couch_TransY']",
                                      "#couch_TransY,i=str(values[i]),i+1")
    if event == '-COUCHTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-COUCHTRANSZ-'],
                                      "couch_TransZ=\"Ge/couch/HLZ + Ge/CTDI/RMax\"",
                                      "couch_TransZ=\""+str(values['-COUCHTRANSZ-'])+"\"",
                                      "#couch_TransZ_start,couch_TransZ_stop,couch_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([couch_TransZ_start",
                                      "#boundaries_name_list.append(['couch_TransZ']",
                                      "#couch_TransZ,i=str(values[i]),i+1")
    if event == '-COUCHHLZ-_ENTER':
        replacement_witherrorhandling(values['-COUCHHLZ-'],
                                      "couch_HLZ=\"0.075\"",
                                      "couch_HLZ=\""+str(values['-COUCHHLZ-'])+"\"",
                                      "#couch_HLZ_start,couch_HLZ_stop,couch_HLZ_step = 0,0,0",
                                      "#boundaries_list.append([couch_HLZ_start",
                                      "#boundaries_name_list.append(['couch_HLZ']",
                                      "#couch_HLZ,i=str(values[i]),i+1")
    if event == '-COUCHHLY-_ENTER':
        replacement_witherrorhandling(values['-COUCHHLY-'],
                                      "couch_HLY=\"100.0\"",
                                      "couch_HLY=\""+str(values['-COUCHHLY-'])+"\"",
                                      "#couch_HLY_start,couch_HLY_stop,couch_HLY_step = 0,0,0",
                                      "#boundaries_list.append([couch_HLY_start",
                                      "#boundaries_name_list.append(['couch_HLY']",
                                      "#couch_HLY,i=str(values[i]),i+1")
    if event == '-COUCHHLX-_ENTER':
        replacement_witherrorhandling(values['-COUCHHLX-'],
                                      "couch_HLX=\"26.0\"",
                                      "couch_HLX=\""+str(values['-COUCHHLX-'])+"\"",
                                      "#couch_HLX_start,couch_HLX_stop,couch_HLX_step = 0,0,0",
                                      "#boundaries_list.append([couch_HLX_start",
                                      "#boundaries_name_list.append(['couch_HLX']",
                                      "#couch_HLX,i=str(values[i]),i+1")

    if event == '-BEAMGRPTY-_ENTER':
        try:
            int(values['-BEAMGRPTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("BeamPosition_Type=\'\"Group\"\'",
                                   "BeamPosition_Type=\'\""+str(values['-BEAMGRPTY-'])+"\"\'")
    if event == '-BEAMGRPPAR-_ENTER':
        try:
            int(values['-BEAMGRPPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("BeamPosition_Parent=\'\"Rotation\"\'",
                                   "BeamPosition_Parent=\'\""+str(values['-BEAMGRPPAR-'])+"\"\'")
            
    if event == '-BEAMGRPTRANSX-_ENTER':
        replacement_witherrorhandling(values['-BEAMGRPTRANSX-'],
                                      "BeamPosition_TransX=\"0.\"",
                                      "BeamPosition_TransX=\""+str(values['-BEAMGRPTRANSX-'])+"\"",
                                      "#BeamPosition_TransX_start,BeamPosition_TransX_stop,BeamPosition_TransX_step = 0,0,0",
                                      "#boundaries_list.append([BeamPosition_TransX_start",
                                      "#boundaries_name_list.append(['BeamPosition_TransX']",
                                      "#BeamPosition_TransX,i=str(values[i]),i+1")
    if event == '-BEAMGRPTRANSY-_ENTER':
        replacement_witherrorhandling(values['-BEAMGRPTRANSY-'],
                                      "BeamPosition_TransY=\"0.\"",
                                      "BeamPosition_TransY=\""+str(values['-BEAMGRPTRANSY-'])+"\"",
                                      "#BeamPosition_TransY_start,BeamPosition_TransY_stop,BeamPosition_TransY_step = 0,0,0",
                                      "#boundaries_list.append([BeamPosition_TransY_start",
                                      "#boundaries_name_list.append(['BeamPosition_TransY']",
                                      "#BeamPosition_TransY,i=str(values[i]),i+1")
    if event == '-BEAMGRPTRANSZ-_ENTER':
        replacement_witherrorhandling(values['-BEAMGRPTRANSZ-'],
                                      "BeamPosition_TransZ=\"-100.\"",
                                      "BeamPosition_TransZ=\""+str(values['-BEAMGRPTRANSZ-'])+"\"",
                                      "#BeamPosition_TransZ_start,BeamPosition_TransZ_stop,BeamPosition_TransZ_step = 0,0,0",
                                      "#boundaries_list.append([BeamPosition_TransZ_start",
                                      "#boundaries_name_list.append(['BeamPosition_TransZ']",
                                      "#BeamPosition_TransZ,i=str(values[i]),i+1")
    if event == '-BEAMGRPROTZ-_ENTER':
        replacement_witherrorhandling(values['-BEAMGRPROTZ-'],
                                      "BeamPosition_RotZ=\"0.\"",
                                      "BeamPosition_RotZ=\""+str(values['-BEAMGRPROTZ-'])+"\"",
                                      "#BeamPosition_RotZ_start,BeamPosition_RotZ_stop,BeamPosition_RotZ_step = 0,0,0",
                                      "#boundaries_list.append([BeamPosition_RotZ_start",
                                      "#boundaries_name_list.append(['BeamPosition_RotZ']",
                                      "#BeamPosition_RotZ,i=str(values[i]),i+1")
    if event == '-BEAMGRPROTY-_ENTER':
        replacement_witherrorhandling(values['-BEAMGRPROTY-'],
                                      "BeamPosition_RotY=\"0.\"",
                                      "BeamPosition_RotY=\""+str(values['-BEAMGRPROTY-'])+"\"",
                                      "#BeamPosition_RotY_start,BeamPosition_RotY_stop,BeamPosition_RotY_step = 0,0,0",
                                      "#boundaries_list.append([BeamPosition_RotY_start",
                                      "#boundaries_name_list.append(['BeamPosition_RotY']",
                                      "#BeamPosition_RotY,i=str(values[i]),i+1")
    if event == '-BEAMGRPROTX-_ENTER':
        replacement_witherrorhandling(values['-BEAMGRPROTX-'],
                                      "BeamPosition_RotX=\"0.\"",
                                      "BeamPosition_RotX=\""+str(values['-BEAMGRPROTX-'])+"\"",
                                      "#BeamPosition_RotX_start,BeamPosition_RotX_stop,BeamPosition_RotX_step = 0,0,0",
                                      "#boundaries_list.append([BeamPosition_RotX_start",
                                      "#boundaries_name_list.append(['BeamPosition_RotX']",
                                      "#BeamPosition_RotX,i=str(values[i]),i+1")

    if event == '-BEAMSPECTY-_ENTER':
        try:
            int(values['-BEAMSPECTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("BeamEnergySpectrumType=\'\"Continuous\"\'",
                                   "BeamEnergySpectrumType=\'\""+str(values['-BEAMSPECTY-'])+"\"\'")
    if event == '-BEAMTY-_ENTER':
        try:
            int(values['-BEAMTY-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("beam_Type=\'\"Beam\"\'",
                                   "beam_Type=\'\""+str(values['-BEAMTY-'])+"\"\'")
    if event == '-BEAMCOMPO-_ENTER':
        try:
            int(values['-BEAMCOMPO-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("beam_Component=\'\"BeamPosition\"\'",
                                   "beam_Component=\'\""+str(values['-BEAMCOMPO-'])+"\"\'")
    if event == '-BEAMPAR-_ENTER':
        try:
            int(values['-BEAMPAR-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("beam_BeamParticle=\'\"gamma\"\'",
                                   "beam_BeamParticle=\'\""+str(values['-BEAMPAR-'])+"\"\'")
    if event == '-BEAMPOSDISTRO-_ENTER':
        try:
            int(values['-BEAMPOSDISTRO-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("beam_BeamPositionDistribution=\'\"Gaussian\"\'",
                                   "beam_BeamPositionDistribution=\'\""+str(values['-BEAMPOSDISTRO-'])+"\"\'")
    if event == '-BEAMPOSHAPE-_ENTER':
        try:
            int(values['-BEAMPOSHAPE-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("beam_BeamPositionCutoffShape=\'\"Rectangle\"\'",
                                   "beam_BeamPositionCutoffShape=\'\""+str(values['-BEAMPOSHAPE-'])+"\"\'")
    if event == '-BEAMSPOSANGDISTRO-_ENTER':
        try:
            int(values['-BEAMSPOSANGDISTRO-'])
            sg.popup_error("Something is wrong!","This is suppose to be a string and not a number!")
        except: 
            replacement_floatorint("beam_BeamAngularDistribution=\'\"Gaussian\"\'",
                                   "beam_BeamAngularDistribution=\'\""+str(values['-BEAMSPOSANGDISTRO-'])+"\"\'")

    if event == '-BEAMPOSCUTOFFX-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSCUTOFFX-'],
                                      "beam_BeamPositionCutoffX=\"5.\"",
                                      "beam_BeamPositionCutoffX=\""+str(values['-BEAMPOSCUTOFFX-'])+"\"",
                                      "#beam_BeamPositionCutoffX_start,beam_BeamPositionCutoffX_stop,beam_BeamPositionCutoffX_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamPositionCutoffX_start",
                                      "#boundaries_name_list.append(['beam_BeamPositionCutoffX']",
                                      "#beam_BeamPositionCutoffX,i=str(values[i]),i+1")
    if event == '-BEAMPOSCUTTOFFY-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSCUTOFFY-'],
                                      "beam_BeamPositionCutoffY=\"5.\"",
                                      "beam_BeamPositionCutoffY=\""+str(values['-BEAMPOSCUTOFFY-'])+"\"",
                                      "#beam_BeamPositionCutoffY_start,beam_BeamPositionCutoffY_stop,beam_BeamPositionCutoffY_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamPositionCutoffY_start",
                                      "#boundaries_name_list.append(['beam_BeamPositionCutoffY']",
                                      "#beam_BeamPositionCutoffY,i=str(values[i]),i+1")
    if event == '-BEAMPOSSPRDX-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSSPRDX-'],
                                      "beam_BeamPositionSpreadX=\"0.04246\"",
                                      "beam_BeamPositionSpreadX=\""+str(values['-BEAMPOSSPRDX-'])+"\"",
                                      "#beam_BeamPositionSpreadX_start,beam_BeamPositionSpreadX_stop,beam_BeamPositionSpreadX_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamPositionSpreadX_start",
                                      "#boundaries_name_list.append(['beam_BeamPositionSpreadX']",
                                      "#beam_BeamPositionSpreadX,i=str(values[i]),i+1")

    if event == '-BEAMPOSSPRDY-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSSPRDY-'],
                                      "beam_BeamPositionSpreadY=\"0.04246\"",
                                      "beam_BeamPositionSpreadY=\""+str(values['-BEAMPOSSPRDY-'])+"\"",
                                      "#beam_BeamPositionSpreadY_start,beam_BeamPositionSpreadY_stop,beam_BeamPositionSpreadY_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamPositionSpreadY_start",
                                      "#boundaries_name_list.append(['beam_BeamPositionSpreadY']",
                                      "#beam_BeamPositionSpreadY,i=str(values[i]),i+1")

    if event == '-BEAMPOSANGCUTOFFX-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSANGCUTOFFX-'],
                                      "beam_BeamAngularCutoffX=\"90\"",
                                      "beam_BeamAngularCutoffX=\""+str(values['-BEAMPOSANGCUTOFFX-'])+"\"",
                                      "#beam_BeamAngularCutoffX_start,beam_BeamAngularCutoffX_stop,beam_BeamAngularCutoffX_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamAngularCutoffX_start",
                                      "#boundaries_name_list.append(['beam_BeamAngularCutoffX']",
                                      "#beam_BeamAngularCutoffX,i=str(values[i]),i+1")
    if event == '-BEAMPOSANGCUTOFFY-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSANGCUTOFFY-'],
                                      "beam_BeamAngularCutoffY=\"90\"",
                                      "beam_BeamAngularCutoffY=\""+str(values['-BEAMPOSANGCUTOFFY-'])+"\"",
                                      "#beam_BeamAngularCutoffY_start,beam_BeamAngularCutoffY_stop,beam_BeamAngularCutoffY_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamAngularCutoffY_start",
                                      "#boundaries_name_list.append(['beam_BeamAngularCutoffY']",
                                      "#beam_BeamAngularCutoffY,i=str(values[i]),i+1")
    if event == '-BEAMPOSANGSPREADX-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSANGSPREADX-'],
                                      "beam_BeamAngularSpreadX=\"10\"",
                                      "beam_BeamAngularSpreadX=\""+str(values['-BEAMPOSANGSPREADX-'])+"\"",
                                      "#beam_BeamAngularSpreadX_start,beam_BeamAngularSpreadX_stop,beam_BeamAngularSpreadX_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamAngularSpreadX_start",
                                      "#boundaries_name_list.append(['beam_BeamAngularSpreadX']",
                                      "#beam_BeamAngularSpreadX,i=str(values[i]),i+1")
    if event == '-BEAMPOSANGSPREADY-_ENTER':
        replacement_witherrorhandling(values['-BEAMPOSANGSPREADY-'],
                                      "beam_BeamAngularSpreadY=\"10\"",
                                      "beam_BeamAngularSpreadY=\""+str(values['-BEAMPOSANGSPREADY-'])+"\"",
                                      "#beam_BeamAngularSpreadY_start,beam_BeamAngularSpreadY_stop,beam_BeamAngularSpreadY_step = 0,0,0",
                                      "#boundaries_list.append([beam_BeamAngularSpreadY_start",
                                      "#boundaries_name_list.append(['beam_BeamAngularSpreadY']",
                                      "#beam_BeamAngularSpreadY,i=str(values[i]),i+1")
    if event == '-TIMEROTFUNC-_ENTER':
        replacement_witherrorhandling(values['-TIMEROTFUNC-'],
                                      "Rotate_Function=\'\"Linear deg\"\'",
                                      "Rotate_Function=\'\""+str(values['-TIMEROTFUNC-'])+"\"\'",
                                      "#Rotate_Function_start,Rotate_Function_stop,Rotate_Function_step = 0,0,0",
                                      "#boundaries_list.append([Rotate_Function_start",
                                      "#boundaries_name_list.append(['Rotate_Function']",
                                      "#Rotate_Function,i=str(values[i]),i+1")
    if event == '-TIMESEQ-_ENTER':
        replacement_witherrorhandling(values['-TIMESEQ-'],
                                      "NumberOfSequentialTimes=\"501\"",
                                      "NumberOfSequentialTimes=\""+str(values['-TIMESEQ-'])+"\"",
                                      "#NumberOfSequentialTimes_start,NumberOfSequentialTimes_stop,NumberOfSequentialTimes_step = 0,0,0",
                                      "#boundaries_list.append([NumberOfSequentialTimes_start",
                                      "#boundaries_name_list.append(['NumberOfSequentialTimes']",
                                      "#NumberOfSequentialTimes,i=str(values[i]),i+1")
    # if event == '-TIMEVERBO-':
    #   replacement_witherrorhandling(values['-TIMEVERBO-'],
    #                                 "Verbosity=\"0\"",
    #                                 "Verbosity=\""+str(values['-TIMEVERBO-'])+"\"",
    #                                 "#Verbosity_start,Verbosity_stop,Verbosity_step = 0,0,0",
    #                                 "#boundaries_list.append([Verbosity_start",
    #                                 "#boundaries_name_list.append(['Verbosity']",
    #                                 "#Verbosity,i=str(values[i]),i+1")
    if event == '-TIMELINEEND-_ENTER':
        replacement_witherrorhandling(values['-TIMELINEEND-'],
                                      "TimelineEnd=\"501.0s\"",
                                      "TimelineEnd=\""+str(values['-TIMELINEEND-'])+"\"",
                                      "#TimelineEnd_start,TimelineEnd_stop,TimelineEnd_step = 0,0,0",
                                      "#boundaries_list.append([TimelineEnd_start",
                                      "#boundaries_name_list.append(['TimelineEnd']",
                                      "#TimelineEnd,i=str(values[i]),i+1")

    if event == '-TIMEROTRATE-_ENTER':
        replacement_witherrorhandling(values['-TIMEROTRATE-'],
                                      "Rotate_Rate=\"0.4\"",
                                      "Rotate_Rate=\""+str(values['-TIMEROTRATE-'])+"\"",
                                      "#Rotate_Rate_start,Rotate_Rate_stop,Rotate_Rate_step = 0,0,0",
                                      "#boundaries_list.append([Rotate_Rate_start",
                                      "#boundaries_name_list.append(['Rotate_Rate']",
                                      "#Rotate_Rate,i=str(values[i]),i+1")
    if event == '-TIMEROTSTART-_ENTER':
        replacement_witherrorhandling(values['-TIMEROTSTART-'],
                                      "Rotate_StartValue=\"90.0\"",
                                      "Rotate_StartValue=\""+str(values['-TIMEROTSTART-'])+"\"",
                                      "#Rotate_StartValue_start,Rotate_StartValue_stop,Rotate_StartValue_step = 0,0,0",
                                      "#boundaries_list.append([Rotate_StartValue_start",
                                      "#boundaries_name_list.append(['Rotate_StartValue']",
                                      "#Rotate_StartValue,i=str(values[i]),i+1")
    if event == '-TIMEHISTINT-_ENTER':
        replacement_witherrorhandling(values['-TIMEHISTINT-'],
                                      "ShowHistoryCountAtInterval=\"100000\"",
                                      "ShowHistoryCountAtInterval=\""+str(values['-TIMEHISTINT-'],)+"\"",
                                      "#ShowHistoryCountAtInterval_start,ShowHistoryCountAtInterval_stop,ShowHistoryCountAtInterval_step = 0,0,0",
                                      "#boundaries_list.append([ShowHistoryCountAtInterval_start",
                                      "#boundaries_name_list.append(['ShowHistoryCountAtInterval']",
                                      "#ShowHistoryCountAtInterval,i=str(values[i]),i+1")
    if event == '-CPCTOG-':
        down = not bool(selectcomponents['ChamberPlugCentre'])
        window['-CPCTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugCentre': 0","'ChamberPlugCentre': 1")
            selectcomponents['ChamberPlugCentre'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugCentre': 1","'ChamberPlugCentre': 0")
            selectcomponents['ChamberPlugCentre'] = 0

    if event == '-CPTTOG-':
        down = not bool(selectcomponents['ChamberPlugTop'])
        window['-CPCTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugTop': 0","'ChamberPlugTop': 1")
            selectcomponents['ChamberPlugTop'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugTop': 1","'ChamberPlugTop': 0")
            selectcomponents['ChamberPlugTop'] = 0

    if event == '-CPBTOG-':
        down = not bool(selectcomponents['ChamberPlugBottom'])
        window['-CPBTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugBottom': 0","'ChamberPlugBottom': 1")
            selectcomponents['ChamberPlugBottom'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugBottom': 1","'ChamberPlugBottom': 0")
            selectcomponents['ChamberPlugBottom'] = 0

    if event == '-CPLTOG-':
        down = not bool(selectcomponents['ChamberPlugLeft'])
        window['-CPLTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugLeft': 0","'ChamberPlugLeft': 1")
            selectcomponents['ChamberPlugLeft'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugLeft': 1","'ChamberPlugLeft': 0")
            selectcomponents['ChamberPlugLeft'] = 0

    if event == '-CPRTOG-':
        down = not bool(selectcomponents['ChamberPlugRight'])
        window['-CPRTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugRight': 0","'ChamberPlugRight': 1")
            selectcomponents['ChamberPlugRight'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugRight': 1","'ChamberPlugRight': 0")
            selectcomponents['ChamberPlugRight'] = 0

    if event == '-TLETOG-':
        down = not bool(selectcomponents['ChamberPlugDose_tle'])
        window['-TLETOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugDose_tle': 0","'ChamberPlugDose_tle': 1")
            selectcomponents['ChamberPlugDose_tle'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugDose_tle': 1","'ChamberPlugDose_tle': 0")
            selectcomponents['ChamberPlugDose_tle'] = 0

    if event == '-DTMTOG-':
        down = not bool(selectcomponents['ChamberPlugDose_dtm'])
        window['-DTMTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugDose_dtm': 0","'ChamberPlugDose_dtm': 1")
            selectcomponents['ChamberPlugDose_dtm'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugDose_dtm': 1","'ChamberPlugDose_dtm': 0")
            selectcomponents['ChamberPlugDose_dtm'] = 0

    if event == '-DTWTOG-':
        down = not bool(selectcomponents['ChamberPlugDose_dtw'])
        window['-DTWTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'ChamberPlugDose_dtw': 0","'ChamberPlugDose_dtw': 1")
            selectcomponents['ChamberPlugDose_dtw'] = 1
        elif not down:
            replacement_floatorint("'ChamberPlugDose_dtw': 1","'ChamberPlugDose_dtw': 0")
            selectcomponents['ChamberPlugDose_dtw'] = 0

    if event == '-COLLVERTOG-':
        down = not bool(selectcomponents['CollimatorsVertical'])
        window['-COLLVERTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'CollimatorsVertical': 0","'CollimatorsVertical': 1")
            selectcomponents['CollimatorsVertical'] = 1
        elif not down:
            replacement_floatorint("'CollimatorsVertical': 1","'CollimatorsVertical': 0")
            selectcomponents['CollimatorsVertical'] = 0

    if event == '-COLLHORTOG-':
        down = not bool(selectcomponents['CollimatorsHorizontal'])
        window['-COLLHORTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'CollimatorsHorizontal': 0","'CollimatorsHorizontal': 1")
            selectcomponents['CollimatorsHorizontal'] = 1
        elif not down:
            replacement_floatorint("'CollimatorsHorizontal': 1","'CollimatorsHorizontal': 0")
            selectcomponents['CollimatorsHorizontal'] = 0

    if event == '-STEELFILTOG-':
        down = not bool(selectcomponents['SteelFilter'])
        window['-STEELFILTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'SteelFilter': 0","'SteelFilter': 1")
            selectcomponents['SteelFilter'] = 1
        elif not down:
            replacement_floatorint("'SteelFilter': 1","'SteelFilter': 0")
            selectcomponents['SteelFilter'] = 0

    if event == '-BTFILTOG-':
        down = not bool(selectcomponents['BowtieFilter'])
        window['-BTFILTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'BowtieFilter': 0","'BowtieFilter': 1")
            selectcomponents['BowtieFilter'] = 1
        elif not down:
            replacement_floatorint("'BowtieFilter': 1","'BowtieFilter': 0")
            selectcomponents['BowtieFilter'] = 0

    if event == '-COLL1TOG-':
        down = not bool(selectcomponents['Coll1'])
        window['-COLL1TOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'Coll1': 0","'Coll1': 1")
            selectcomponents['Coll1'] = 1
        elif not down:
            replacement_floatorint("'Coll1': 1","'Coll1': 0")
            selectcomponents['Coll1'] = 0

    if event == '-COLL2TOG-':
        down = not bool(selectcomponents['Coll2'])
        window['-COLL2TOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'Coll2': 0","'Coll2': 1")
            selectcomponents['Coll2'] = 1
        elif not down:
            replacement_floatorint("'Coll2': 1","'Coll2': 0")
            selectcomponents['Coll2'] = 0

    if event == '-COLL3TOG-':
        down = not bool(selectcomponents['Coll3'])
        window['-COLL3TOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'Coll3': 0","'Coll3': 1")
            selectcomponents['Coll3'] = 1
        elif not down:
            replacement_floatorint("'Coll3': 1","'Coll3': 0")
            selectcomponents['Coll3'] = 0

    if event == '-COLL4TOG-':
        down = not bool(selectcomponents['Coll4'])
        window['-COLL4TOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'Coll4': 0","'Coll4': 1")
            selectcomponents['Coll4'] = 1
        elif not down:
            replacement_floatorint("'Coll4': 1","'Coll4': 0")
            selectcomponents['Coll4'] = 0

    if event == '-DEMOFLATTOG-':
        down = not bool(selectcomponents['DemoFlat'])
        window['-DEMOFLATTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'DemoFlat': 0","'DemoFlat': 1")
            selectcomponents['DemoFlat'] = 1
        elif not down:
            replacement_floatorint("'DemoFlat': 1","'DemoFlat': 0")
            selectcomponents['DemoFlat'] = 0
        
    if event == '-DEMORTRAPTOG-':
        down = not bool(selectcomponents['DemoRTrap'])
        window['-DEMORTRAPTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'DemoRTrap': 0","'DemoRTrap': 1")
            selectcomponents['DemoRTrap'] = 1
        elif not down:
            replacement_floatorint("'DemoRTrap': 1","'DemoRTrap': 0")
            selectcomponents['DemoRTrap'] = 0

    if event == '-DEMOLTRAPTOG-':
        down = not bool(selectcomponents['DemoLTrap'])
        window['-DEMOLTRAPTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'DemoLTrap': 0","'DemoLTrap': 1")
            selectcomponents['DemoLTrap'] = 1
        elif not down:
            replacement_floatorint("'DemoLTrap': 1","'DemoLTrap': 0")
            selectcomponents['DemoLTrap'] = 0

    if event == '-TSBTOG-':
        down = not bool(selectcomponents['topsidebox'])
        window['-TSBTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'topsidebox': 0","'topsidebox': 1")
            selectcomponents['topsidebox'] = 1
        elif not down:
            replacement_floatorint("'topsidebox': 1","'topsidebox': 0")
            selectcomponents['topsidebox'] = 0

    if event == '-BSBTOG-':
        down = not bool(selectcomponents['bottomsidebox'])
        window['-BSBTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'bottomsidebox': 0","'bottomsidebox': 1")
            selectcomponents['bottomsidebox'] = 1
        elif not down:
            replacement_floatorint("'bottomsidebox': 1","'bottomsidebox': 0")
            selectcomponents['bottomsidebox'] = 0

    if event == '-COHTOG-':
        down = not bool(selectcomponents['couch'])
        window['-COHTOG-'].update(text='On' if down else 'Off', button_color='white on green' if down else 'white on red')
        if down:
            replacement_floatorint("'couch': 0","'couch': 1")
            selectcomponents['couch'] = 1
        elif not down:
            replacement_floatorint("'couch': 1","'couch': 0")
            selectcomponents['couch'] = 0

    if event == '-RUN-':

        command_topas = "python3 runfolder/topas_multiproc.py"
        command_progressbar = f"python3 progressbar.py {path} {num_of_csvresult}"
        commands = [command_topas,command_progressbar]
        #commands = [command_progressbar]
        procs = [subprocess.Popen(i,shell=True) for i in commands]
        for p in procs:
            #pass
            p.wait()

window.close()
