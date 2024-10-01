import os
import PySimpleGUI as sg
import shutil
from pydicom import dcmread
from src.runtime_handler import log_output
from src.edits_handler import editor
from src.guilayers import *
import numpy as np

#Useful functions###################################################
def reset_tmp():
    '''
    Helper function that resets the temporary files after each run to ensure smooth operation. 
    '''
    path = os.getcwd()
    #generate a generate_allproc file from a boiler plate so we edit only that copy each time
    original_gen_file_path = path + '/src/boilerplates/generate_allproc_boilerplate.py'
    duplicate_gen_file_path = path + "/tmp/generate_allproc.py"
    shutil.copy(original_gen_file_path, duplicate_gen_file_path)

    #generate a headsource file from a boiler plate so we edit only that copy each time
    original_headsource_file_path = path + '/src/boilerplates/headsourcecode_boilerplate.bat'
    duplicate_headsource_file_path = path + "/tmp/headsourcecode.bat"
    shutil.copy(original_headsource_file_path, duplicate_headsource_file_path)

    #generate a multi_allproc file from a boiler plate so we edit only that copy each time
    original_multiproc_file_path = path + '/src/boilerplates/topas_multiproc_boilerplate.py'
    duplicate_multiproc_file_path = path + "/tmp/topas_multiproc.py"
    shutil.copy(original_multiproc_file_path, duplicate_multiproc_file_path)

    #generate a dicom bat file from a boiler plate so we edit only that copy each time
    original_dicom_file_path = path + '/src/boilerplates/dicom_boilerplate.bat'
    duplicate_dicom_file_path = path +"/tmp/dicom.bat"
    shutil.copy(original_dicom_file_path, duplicate_dicom_file_path)


####################################################################

#Seting up the GUI layout ##########################################
main_layout = [[main_menu_information_layer],
               [general_layer],
               [function_layer],
               [dicom_file_layer],
               [runbuttons_layer]]

chamber_layout = [[CTDI_information_layer],
                  [CTDI_layer,Couch_layer]]

dicom_layout = [[dicom_information_layer], 
                [dicom_patient_layer,dicom_planned_layer], ]


others_layout = [[Time_layer,Physics_layer, Scoring_layer], 
                 [Beam_layer],
                 [imaging_protocol_layer, imaging_scan_layer]]

layout = [[ sg.Text('Monte Carlo - Dose Calculation for Risk Evaluation', justification='center',font=('Helvetica 30 bold'), text_color='dark blue')],
          [sg.TabGroup([[sg.Tab('Main menu' , main_layout),
                         sg.Tab('DICOM adjustments menu', dicom_layout, key= '-HIDEDICOMTAB-', visible=False),
                         sg.Tab('CTDI phantom menu' , chamber_layout, key= '-HIDESIMUTAB-', visible=False),
                         sg.Tab('Others menu', others_layout)]],
                         key='-TAB GROUP-', font=(40) ,expand_x=True, expand_y=True),
                        ]]

sg.set_options(scaling=1)
window = sg.Window(title= "MC-DCaRE", layout=layout, finalize=True, auto_size_text=True, font ='Helvetica' ,debugger_enabled= True)
# window.set_min_size(window.size) #might not be needed

# Defining some required values
path = os.getcwd()
DICOM_bool = USER_bool = False
initiate =couch_bool_change = True
reset_tmp()
window["-G4FOLDERNAME-"].bind("<Return>","_ENTER") # for quick and dirty debuggin with G4 enter, remove for actual release

while True:
    event,values = window.read()

    if initiate == True: 
        # Sets up default values for resetting to default parameters
        values_default = values
        # Brute force work around as reseting all parameter will clear the default 'Browse' string
        values_default['Browse'] =values_default['Browse0']=values_default['Browse1']=values_default['Browse2']= "Browse"
        initiate = False
    
    if event == '-RESET-':
        # HAS TO BE A LOOPED FUNCTION CAUSE PYSIMPLEGUI
        for i in values: 
            window[i].update(values_default[i])
        pass

    if event == '-G4FOLDERNAME-_ENTER':
        # THIS IS A PLACEHOLDER FOR QUICK AND DIRTY DEBUGGING

        # DUMP all values into a text file
        f = open('dump.txt', 'w')
        f.write( 'dict = '+repr(values)+ '\n')
        f.close()

        # print(str(values['-G4FOLDERNAME-']))
        # Add a line search and replacement function here
        # G4_Data = '\"' +str(values['-G4FOLDERNAME-'])+ '\"' 

    if event == '-TOPAS-':
        # Add a line search and replacement function here
        topas_application_path = values['-TOPAS-'] + " "

    if event == '-DICOM-':
        # Add a line search and replacement function here
        count_of_CT_images = 0
        try:    
            DICOM_PATH = values['-DICOM-']
            list_of_files = os.listdir(DICOM_PATH)
            for files in list_of_files: 
                if  dcmread(os.path.join(DICOM_PATH,files)).Modality == 'CT':
                    count_of_CT_images += 1
                    patient_ID = dcmread(os.path.join(DICOM_PATH,files)).PatientID
            values['-PATID-'] = patient_ID
            window['-PATID-'].update(values['-PATID-'])
            sg.popup("Number of CT images found" , count_of_CT_images , auto_close= True, non_blocking=True)
        except: 
            sg.popup_error("No CT images found in the folder")

    if event == '-DICOMACTIVATECHECK-':
        if USER_bool == False:
            DICOM_bool = not DICOM_bool
            window['-DICOMACTIVATE-'].update(visible=DICOM_bool)
            window['-HIDEDICOMTAB-'].update(visible=DICOM_bool)
            
        else:
            sg.popup_error('Choose 1 option')
            window['-DICOMACTIVATECHECK-'].update(value=False)

    if event == '-USERACTIVATECHECK-':
        if DICOM_bool == False:
            USER_bool = not USER_bool
            window['-HIDESIMUTAB-'].update(visible=USER_bool)
            window['-BUTTONSACTIVATE-'].update(visible=USER_bool)
        else:
            sg.popup_error('Choose 1 option')
            window['-USERACTIVATECHECK-'].update(value=False)
        
    if event == '-RUN-':
        # add code to edit the tmp file
        tmp_file_path = path + '/tmp/generate_allproc.py'
        topas_application_path = values['-TOPAS-'] + " "
        editor(values, tmp_file_path, 'CTDI')
        run_status = log_output(tmp_file_path, 'generate_allproc.py', topas_application_path)
        reset_tmp()
        sg.popup(run_status)

    if event == '-DICOMRP-':
        if dcmread(values['-DICOMRP-']).PatientID == values['-PATID-']: 
            try:    
                isocentre_coors = dcmread(values['-DICOMRP-']).BeamSequence[0].ControlPointSequence[0].IsocenterPosition
                values['-DICOM_ISOX-'] = str(round(isocentre_coors[0], 5)) + ' mm' #figure out how to get units form dicom 
                values['-DICOM_ISOY-'] = str(round(isocentre_coors[1], 5)) + ' mm'
                values['-DICOM_ISOZ-'] = str(round(isocentre_coors[2], 5)) + ' mm'
                window['-DICOM_ISOX-'].update(values['-DICOM_ISOX-'])
                window['-DICOM_ISOY-'].update(values['-DICOM_ISOY-'])
                window['-DICOM_ISOZ-'].update(values['-DICOM_ISOZ-'])
            except: 
                sg.popup_error("No isocentre found")
        else: 
            sg.popup_error('Patient ID for the CT image set and treatment plan does not match')


    if event == '-DICOMBAT-':
        # When users try to simulate DICOM imaging, this block will run. 
        # Code will activate the editor() function to edit the tmp file
        # Runtimehandler will then form the timestamp folder and drop the outputs there
        try: 
            tmp_file_path = path + '/tmp/dicom.bat'
            topas_application_path = values['-TOPAS-'] + " "
            editor(values, tmp_file_path, 'DICOM')
            run_status = log_output(tmp_file_path, 'dicom.bat', topas_application_path)
            reset_tmp()
            sg.popup(run_status)
        except:
            sg.popup_error("Ensure that you have specified a DICOM folder and file")
    
    if event == '-IMAGEMODE-':
        # When users select the image protocol, this block will run and put input the imaging parameteres
        # Hardcoded values for image protocol
        if values['-IMAGEMODE-'] == 'Image Gently':
            values['-FAN-'] = 'Full Fan'
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '80 kV'
            values['-BEAMCURRENT-'] = '100 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Head':
            values['-FAN-'] = 'Full Fan'
            values['-X1-'] = '1 mm'
            values['-X2-'] = '2 mm'
            values['-Y1-'] = '3 mm'
            values['-Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '100 kV'
            values['-BEAMCURRENT-'] = '150 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Short Thorax':
            values['-FAN-'] = 'Full Fan'
            values['-X1-'] = '1 mm'
            values['-X2-'] = '2 mm'
            values['-Y1-'] = '3 mm'
            values['-Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '125 kV'
            values['-BEAMCURRENT-'] = '210 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Spotlight':
            values['-FAN-'] = 'Full Fan'
            values['-X1-'] = '1 mm'
            values['-X2-'] = '2 mm'
            values['-Y1-'] = '3 mm'
            values['-Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '125 kV'
            values['-BEAMCURRENT-'] = '750 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Thorax':
            values['-FAN-'] = 'Half Fan'
            values['-X1-'] = '1 mm'
            values['-X2-'] = '2 mm'
            values['-Y1-'] = '3 mm'
            values['-Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '270 kV'
            values['-BEAMCURRENT-'] = '1080 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Pelvis':
            values['-FAN-'] = 'Half Fan'
            values['-X1-'] = '1 mm'
            values['-X2-'] = '2 mm'
            values['-Y1-'] = '3 mm'
            values['-Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '140 kV'
            values['-BEAMCURRENT-'] = '1688 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Pelvis Large':
            values['-FAN-'] = 'Half Fan'
            values['-X1-'] = '1 mm'
            values['-X2-'] = '2 mm'
            values['-Y1-'] = '3 mm'
            values['-Y2-'] = '4 mm'
            values['-IMAGEVOLTAGE-'] = '125 kV'
            values['-BEAMCURRENT-'] = '672 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-BLADE_X1-'].update(values['-BLADE_X1-'])
            window['-BLADE_X2-'].update(values['-BLADE_X2-'])
            window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
            window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])
            window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
            window['-BEAMCURRENT-'].update(values['-BEAMCURRENT-'])

        else: 
            pass
    
    if event == '-COUCH_TOG-':
        window['-COUCH-'].update(visible=values['-COUCH_TOG-'])

    if event == sg.WIN_CLOSED:
        break

        
        

window.close()
