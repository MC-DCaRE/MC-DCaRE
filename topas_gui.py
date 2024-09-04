import os
import PySimpleGUI as sg
import subprocess
import shutil
from numpy import arange
import numpy as np
import multiprocessing as mp

#Useful functions###################################################
def my_arange(start, end, step):
	"""
	This is used instead of numpy arange due to numpy arange unstable length of
	output when floating numbers are used
	"""
	return np.linspace(start, end, num=round((end-start)/step), endpoint=False)

def stringindexreplacement(SearchString :str , TargetFile: str , ReplacementString: str):
    '''
    Targeted string replacement. 
    Function looks for the line that startes with SearchString at the file directory of TargetFile and replaces it with Replacement String. 
    Function will replace the entire line and any information trailing the SearchString will be lost in this process. 
    '''
    with open(TargetFile, 'r') as Rread_file:
        filecontent = Rread_file.readlines()
    with open(TargetFile, 'w') as Write_file:
        for lineIndex in range(len(filecontent)):
            if filecontent[lineIndex].startswith(SearchString):
                newline = SearchString + "=" +ReplacementString+'\n' 
                filecontent[lineIndex] = newline
                break #exits after the first instance of match. Saves compute. 
        Write_file.writelines( filecontent )

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
    stringindexreplacement(defaultforfloatorint.split('=')[0],path + '/generate_allproc.py', defaultforfloatorint.split('=')[1] )
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

# try
# path = os.getcwd()
# topas_application_path = 'Set your topas path'     #linux
# G4_Data = 'Set your G4 data path' #linux

# Fixed path for ease of user testing. User: JK
path = os.getcwd()
topas_application_path = '/root/topas/bin/topas '     #linux
dicom_path = '/root/nccs/Topas_wrapper/test/cherylair'
G4_Data ='/root/G4Data' #linux



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

#generate a dicom bat file from a boiler plate so we edit only that copy each time
original_file_path = path + '/dicom_boilerplate.bat'
duplicate_multiproc_file_name = "dicom.bat"
directory_path = os.path.dirname(original_file_path)
# duplicate_dicom_file_path = os.path.join(directory_path +"/runfolder" ,duplicate_multiproc_file_name)
duplicate_dicom_file_path = os.path.join(directory_path +"/test/sampledicom" ,duplicate_multiproc_file_name)
shutil.copy(original_file_path, duplicate_dicom_file_path)

from generate_allproc_boilerplate import selectcomponents

sg.theme('Reddit')

from guilayers import *
general_layer = gui_layer_generation(path, G4_Data, topas_application_path)

# Creating a tabbed menu 
main_layout = [[information_layer],
               [general_layer],
               [function_layer],
               [dicom_layer],
               [toggle_layer], 
               [runbuttons_layer]]

chamber_layout = [[CTDI_layer,ChamberPlugCentre_layer,ChamberPlugTop_layer],[ChamberPlugBottom_layer,ChamberPlugLeft_layer,ChamberPlugRight_layer]]

collimator_layout = [[Coll1_layer,Coll2_layer,Coll3_layer,Coll4_layer, CollimatorVerticalGroup_layer], 
                     [Coll1steel_layer,Coll2steel_layer,Coll3steel_layer,Coll4steel_layer,CollimatorHorizontalGroup_layer ]]

filter_layout = [[ TITFIL_layer, DemoFlat_layer,TopSideBox_layer,BottomSideBox_layer],
                  [DemoRTrap_layer,DemoLTrap_layer,TitaniumGroup_layer,Bowtie_layer]]

others_layout = [[Time_layer,Physics_layer, Scoring_layer,RotationGroup_layer], 
                 [Couch_layer,BeamGroup_layer,Beam_layer]]

layout = [[ sg.Text('Imaging Dose', size=(30,1),justification='center',font=('Helvetica 50 bold'), text_color='dark blue')],
          [sg.TabGroup([[sg.Tab( 'Main menu' , main_layout),
                        sg.Tab('Chamber menu' , chamber_layout, key= '-HIDETAB-', visible=False),
                        sg.Tab('Collimator menu', collimator_layout),
                        sg.Tab('Filter menu', filter_layout),
                        sg.Tab('Others menu', others_layout)]],
                        key='-TAB GROUP-', font=(40) ,expand_x=True, expand_y=True),
                        ]]

sg.set_options(scaling=1)

window = sg.Window(title= "Imaging Dose Simulation", layout=layout, finalize=True)
window.set_min_size(window.size)

from key_binds import *
key_binds(window) 

#default we will have 5 positions-chamberplugs and 3 quantities to score
#this variable has to be outside of the while loop because after the RUN event updates
#variable, the while loop continues to run and therefore it gets reassigned to 15 again
#interestingly, this means the while loop continues to loop (again and again) even as the  
#simulation subprocess is still running. if no other buttons get triggered while it loops
#then no if block statement will run. though when the subprocess runs, the GUI seems to block 
#all buttons and inputs
num_of_csvresult = 5 
DICOM_bool = USER_bool = False

while True:
    event,values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '-MAINFOLDERNAME-_ENTER':
        #default path
        path = values['-MAINFOLDERNAME-']
        # print(path)

    if event == '-GEN-':
        command = ["python3 generate_allproc.py"]
        subprocess.run(command, shell=True)
        # print(command)

    if event == '-G4FOLDERNAME-_ENTER':
        # print(str(values['-G4FOLDERNAME-']))
        # replacement_floatorint("G4DataDirectory = \'\""+G4_Data+"\"\'",
        #                        "G4DataDirectory = \'\""+str(values['-G4FOLDERNAME-'])+"\"\'")
        # Add a line search and replacement function here
        G4_Data = '\"' +str(values['-G4FOLDERNAME-'])+ '\"' 
        # stringindexreplacement(G4_Data, )

    if event == '-TOPAS-_ENTER':
        # Add a line search and replacement function here
        topas_application_path = values['-TOPAS-'] + " "

    if event == '-DICOM-_ENTER':
        # Add a line search and replacement function here
        dicom_path = values['-DICOM-'] + " "

    if event == '-DICOMACTIVATECHECK-':
        if USER_bool == False:
            DICOM_bool = not DICOM_bool
            window['-DICOMACTIVATE-'].update(visible=DICOM_bool)
            window['-BUTTONSACTIVATE-'].update(visible=DICOM_bool)
        else:
            sg.popup_error('Choose 1 option')
            window['-DICOMACTIVATECHECK-'].update(value=False)

    if event == '-USERACTIVATECHECK-':
        if DICOM_bool == False:
            USER_bool = not USER_bool
            window['-USERACTIVATE-'].update(visible=USER_bool)
            window['-HIDETAB-'].update(visible=USER_bool)
            window['-BUTTONSACTIVATE-'].update(visible=USER_bool)
        else:
            sg.popup_error('Choose 1 option')
            window['-USERACTIVATECHECK-'].update(value=False)

    if event == '-DUPGENPROC-':
        G4_Data = '\"' +str(values['-G4FOLDERNAME-'])+ '\"' 
        # Add code that dynamically pulls value from the input textboxes and replaced the newly generated files
        original_file_path = path + '/generate_allproc_boilerplate.py'
        duplicate_gen_file_name = "generate_allproc.py"
        directory_path = os.path.dirname(original_file_path)
        duplicate_gen_file_path = os.path.join(directory_path, duplicate_gen_file_name)
        shutil.copy(original_file_path, duplicate_gen_file_path)
        stringindexreplacement('G4DataDirectory', duplicate_gen_file_path, G4_Data)

    if event == '-DUPMULPROC-':
        topas_application_path = values['-TOPAS-'] + " "
        # Add code that dynamically pulls value from the input textboxes and replaced the newly generated files
        original_file_path = path + '/runfolder/topas_multiproc_boilerplate.py'
        duplicate_multiproc_file_name = "topas_multiproc.py"
        directory_path = os.path.dirname(original_file_path)
        duplicate_multiproc_file_path = os.path.join(directory_path, duplicate_multiproc_file_name)
        shutil.copy(original_file_path, duplicate_multiproc_file_path)
        stringindexreplacement('topas_directory', duplicate_multiproc_file_path, topas_application_path)

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
                                      "ChamberPlugCentre_RMin=\""+str(values['-CPC_RMIN-'])+"\"",
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
                                      "ChamberPlugTop_RMin=\""+str(values['-CPT_RMIN-'])+"\"",
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
                                      "ChamberPlugBottom_RMin=\""+str(values['-CPB_RMIN-'])+"\"",
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
                                      "ChamberPlugLeft_RMin=\""+str(values['-CPL_RMIN-'])+"\"",
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
                                      "ChamberPlugRight_RMin=\""+str(values['-CPR_RMIN-'])+"\"",

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

    if event == '-CPCTOG-':
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

    if event == '-GENRUN-':
        command = ["python3 generate_allproc.py"]
        subprocess.run(command, shell=True)
        print(command)
        command_topas = "python3 runfolder/topas_multiproc.py"
        command_progressbar = f"python3 progressbar.py {path} {num_of_csvresult}"
        commands = [command_topas,command_progressbar]
        #commands = [command_progressbar]
        procs = [subprocess.Popen(i,shell=True) for i in commands]
        for p in procs:
            #pass
            p.wait()
            
    if event == '-DICOMBAT-':
        #generate a dicom bat file from a boiler plate so we edit only that copy each time
        original_file_path = path + '/dicom_boilerplate.bat'
        duplicate_multiproc_file_name = "dicomtest.bat"
        directory_path = os.path.dirname(original_file_path)
        # duplicate_dicom_file_path = os.path.join(directory_path +"/runfolder" ,duplicate_multiproc_file_name)
        duplicate_dicom_file_path = os.path.join(directory_path +"/runfolder" ,duplicate_multiproc_file_name)
        shutil.copy(original_file_path, duplicate_dicom_file_path)

        G4_Data = '\"' +str(values['-G4FOLDERNAME-'])+ '\"' 
        DICOM = values['-DICOM-']         
        DICOM_image_path =  '\"' +str(values['-DICOM-'])+ '\"'
        DICOM_parent_directory = os.path.dirname(DICOM)
        stringindexreplacement('s:Ts/G4DataDirectory', duplicate_dicom_file_path, G4_Data)
        stringindexreplacement('s:Ge/Patient/DicomDirectory', duplicate_dicom_file_path, DICOM_image_path)
        stringindexreplacement( "includeFile", duplicate_dicom_file_path, "/root/nccs/Topas_wrapper/test/sampledicom/ConvertedTopasFile_head.txt /root/nccs/Topas_wrapper/test/sampledicom/HUtoMaterialSchneider.txt")
        stringindexreplacement("s:Sc/DoseOnRTGrid_tle100kz17/InputFile" , duplicate_dicom_file_path, "\"/root/nccs/Topas_wrapper/test/Muen.dat\"")
        command = [topas_application_path + ' ' + duplicate_dicom_file_path]
        # command = [topas_application_path + ' ' + DICOM_parent_directory +'/dicom.bat']

        print(command)
        print(DICOM)
        def run_topas(command):
            print(command)
            subprocess.run("cd test/sampledicom", shell=True)
            foo=os.getcwd() +"/test/sampledicom"
            subprocess.run(command, cwd= foo,shell =True)

        def run_topas_DICOM(x1): 
            print(x1)
            command = x1[0][0]
            DICOM = x1[1][0]
            print('command is' , command) 
            print('dicom is ', DICOM)
            subprocess.run('cd $home', shell=True)
            subprocess.run("cd " + DICOM, shell=True)
            subprocess.run(command, cwd= DICOM,shell =True)

        pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
        # pool.map_async(run_topas, command)
        pool.map_async(run_topas_DICOM, [(command, ["/root/nccs/Topas_wrapper/runfolder"])])
        pool.close()
        pool.join()
        
        # run_topas(command)
        pass
        
        

window.close()
