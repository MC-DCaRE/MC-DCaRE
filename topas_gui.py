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

def iso_finder(dicomdirectory,dicomRPdirectory): 
    slice_start = 100000000
    slice_end = -100000000
    for file in os.listdir(dicomdirectory):
        try:
            dcmct = dcmread(os.path.join(dicomdirectory , file))
            if dcmct.Modality == 'CT':
                if dcmct.SliceLocation > slice_end: 
                    slice_end = dcmct.SliceLocation
                if dcmct.SliceLocation < slice_start: 
                    slice_start = dcmct.SliceLocation
                known_CT_file = file
        except:
            pass
    DCMRP=dcmread(dicomRPdirectory)        
    if DCMRP.Modality == 'RTPLAN':
        plan_iso = DCMRP.BeamSequence[0].ControlPointSequence[0].IsocenterPosition
    dcm = dcmread(os.path.join(dicomdirectory , known_CT_file))
    arbi_iso_x = (dcm.ImagePositionPatient[0]+(dcm.ReconstructionDiameter/2))/2
    arbi_iso_y = (dcm.ImagePositionPatient[1]+(dcm.ReconstructionDiameter/2))
    arbi_iso_z = (slice_end+slice_start)/2
    correction_shift_x = arbi_iso_x - plan_iso[0]
    correction_shift_y = arbi_iso_y - plan_iso[1]
    correction_shift_z = arbi_iso_z - plan_iso[2]
    return correction_shift_x, correction_shift_y, correction_shift_z

####################################################################

#Seting up the GUI layout ##########################################
main_layout = [[main_menu_information_layer],
               [general_layer],
               [function_layer],
               [dicom_file_layer],
               [toggle_layer], 
               [runbuttons_layer]]

chamber_layout = [[CTDI_information_layer],
                  [CTDI_layer,ChamberPlugCentre_layer,ChamberPlugTop_layer],
                  [ChamberPlugBottom_layer,ChamberPlugLeft_layer,ChamberPlugRight_layer]]

dicom_layout = [[dicom_information_layer], 
                [dicom_patient_layer,dicom_scan_layer], 
                [dicom_protocol_layer,dicom_planned_layer]]
                # [dicom_hidden_layer]]

collimator_layout = [[Coll1_layer,Coll2_layer,Coll3_layer,Coll4_layer, CollimatorVerticalGroup_layer], 
                     [Coll1steel_layer,Coll2steel_layer,Coll3steel_layer,Coll4steel_layer,CollimatorHorizontalGroup_layer ]]

filter_layout = [[TITFIL_layer, DemoFlat_layer,TopSideBox_layer,BottomSideBox_layer],
                 [DemoRTrap_layer,DemoLTrap_layer,TitaniumGroup_layer,Bowtie_layer]]

others_layout = [[Time_layer,Physics_layer, Scoring_layer,RotationGroup_layer], 
                 [Couch_layer,BeamGroup_layer,Beam_layer]]

layout = [[ sg.Text('Imaging Dose', size=(30,1),justification='center',font=('Helvetica 50 bold'), text_color='dark blue')],
          [sg.TabGroup([[sg.Tab('Main menu' , main_layout),
                         sg.Tab('DICOM adjustments menu', dicom_layout, key= '-HIDEDICOMTAB-', visible=False),
                         sg.Tab('CTDI phantom menu' , chamber_layout, key= '-HIDESIMUTAB-', visible=False),
                         sg.Tab('Collimator menu', collimator_layout),
                         sg.Tab('Filter menu', filter_layout),
                         sg.Tab('Others menu', others_layout)]],
                         key='-TAB GROUP-', font=(40) ,expand_x=True, expand_y=True),
                        ]]

sg.set_options(scaling=1)
window = sg.Window(title= "Imaging Dose Simulation", layout=layout, finalize=True, auto_size_text=True, font ='Helvetica' ,debugger_enabled= True)
# window.set_min_size(window.size) #might not be needed

# Defining some required values
path = os.getcwd()
DICOM_bool = USER_bool = False
initiate = True
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
            window['-USERACTIVATE-'].update(visible=USER_bool)
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
                # correction_shift_x, correction_shift_y, correction_shift_z = iso_finder(values['-DICOM-'],values['-DICOMRP-'])
                # values['-DICOM_X_CORRECTION-'] = str(correction_shift_x) + ' mm'
                # values['-DICOM_Y_CORRECTION-'] = str(correction_shift_y) + ' mm'
                # values['-DICOM_Z_CORRECTION-'] = str(correction_shift_z) + ' mm'
                # window['-DICOM_X_CORRECTION-'].update(values['-DICOM_X_CORRECTION-'])
                # window['-DICOM_Y_CORRECTION-'].update(values['-DICOM_Y_CORRECTION-'])
                # window['-DICOM_Z_CORRECTION-'].update(values['-DICOM_Z_CORRECTION-'])
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
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '80 kV'
            values['-DICOM_BEAMCURRENT-'] = '100 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Head':
            values['-FAN-'] = 'Full Fan'
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '100 kV'
            values['-DICOM_BEAMCURRENT-'] = '150 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Short Thorax':
            values['-FAN-'] = 'Full Fan'
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '125 kV'
            values['-DICOM_BEAMCURRENT-'] = '210 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Spotlight':
            values['-FAN-'] = 'Full Fan'
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '125 kV'
            values['-DICOM_BEAMCURRENT-'] = '750 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Thorax':
            values['-FAN-'] = 'Half Fan'
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '270 kV'
            values['-DICOM_BEAMCURRENT-'] = '1080 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Pelvis':
            values['-FAN-'] = 'Half Fan'
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '140 kV'
            values['-DICOM_BEAMCURRENT-'] = '1688 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        elif values['-IMAGEMODE-'] == 'Pelvis Large':
            values['-FAN-'] = 'Half Fan'
            values['-DICOM_X1-'] = '1 mm'
            values['-DICOM_X2-'] = '2 mm'
            values['-DICOM_Y1-'] = '3 mm'
            values['-DICOM_Y2-'] = '4 mm'
            values['-DICOM_IMAGEVOLTAGE-'] = '125 kV'
            values['-DICOM_BEAMCURRENT-'] = '672 mAs'
            window['-FAN-'].update(values['-FAN-'])
            window['-DICOM_X1-'].update(values['-DICOM_X1-'])
            window['-DICOM_X2-'].update(values['-DICOM_X2-'])
            window['-DICOM_Y1-'].update(values['-DICOM_Y1-'])
            window['-DICOM_Y2-'].update(values['-DICOM_Y2-'])
            window['-DICOM_IMAGEVOLTAGE-'].update(values['-DICOM_IMAGEVOLTAGE-'])
            window['-DICOM_BEAMCURRENT-'].update(values['-DICOM_BEAMCURRENT-'])

        else: 
            pass
    
    if event == sg.WIN_CLOSED:
        break

        
        

window.close()
