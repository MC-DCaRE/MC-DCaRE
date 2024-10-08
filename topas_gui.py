import os
import FreeSimpleGUI as sg
import shutil
from pydicom import dcmread
from src.runtime_handler import log_output
from src.edits_handler import editor
from src.guilayers import *

#Useful functions###################################################
def reset_tmp():
    '''
    Helper function that resets the temporary files after each run to ensure smooth operation. 
    '''
    path = os.getcwd()
    #generate a headsource file from a boiler plate so we edit only that copy each time
    original_headsource_file_path = path + '/src/boilerplates/headsourcecode_boilerplate.txt'
    duplicate_headsource_file_path = path + "/tmp/headsourcecode.txt"
    shutil.copy(original_headsource_file_path, duplicate_headsource_file_path)

    #generate a dicom includefile from a boiler plate so we edit only that copy each time
    original_dicom_file_path = path + '/src/boilerplates/TOPAS_includeFiles/patientDICOM.txt'
    duplicate_dicom_file_path = path + "/tmp/patientDICOM.txt"
    shutil.copy(original_dicom_file_path, duplicate_dicom_file_path)

    #generate a CTDI 16cm includefile from a boiler plate so we edit only that copy each time
    original_CTDI_16_file_path = path + '/src/boilerplates/TOPAS_includeFiles/CTDIphantom_16.txt'
    duplicate_CTDI_16_file_path = path + "/tmp/CTDIphantom_16.txt"
    shutil.copy(original_CTDI_16_file_path, duplicate_CTDI_16_file_path)

    #generate a CTDI 32cm includefile from a boiler plate so we edit only that copy each time
    original_CTDI_32_file_path = path + '/src/boilerplates/TOPAS_includeFiles/CTDIphantom_32.txt'
    duplicate_CTDI_32_file_path = path + "/tmp/CTDIphantom_32.txt"
    shutil.copy(original_CTDI_32_file_path, duplicate_CTDI_32_file_path)


####################################################################

#Seting up the GUI layout ##########################################
main_layout = [[main_menu_information_layer],
               [general_layer],
               [function_layer]]

chamber_layout = [[CTDI_information_layer],
                  [CTDI_layer, Couch_layer],
                  [CTDI_run_layer]]

dicom_layout = [[dicom_information_layer], 
                [dicom_file_layer],
                [sg.Text('')],
                [dicom_patient_layer, dicom_planned_layer, dicom_graphics_layer]]


others_layout = [[settings_information_layout],
                 [Time_layer, Scoring_layer], 
                 [imaging_protocol_layer, imaging_scan_layer]]

layout = [[ sg.Text('Monte Carlo - Dose Calculation for Risk Evaluation', justification='center', text_color='dark blue', font=('',40,'bold'))],
          [sg.TabGroup([[sg.Tab('Main menu' , main_layout),
                         sg.Tab('Simulation settings', others_layout),
                         sg.Tab('DICOM adjustments menu', dicom_layout, key= '-DICOM_TAB-', visible=False),
                         sg.Tab('CTDI phantom menu' , chamber_layout, key= '-CTDI_TAB-', visible=False),
                         ]],
                         key='-TAB GROUP-' ,expand_x=True, expand_y=True),
                        ]]

sg.set_options(scaling=1)
window = sg.Window(title= "MC-DCaRE", layout=layout, finalize=True, auto_size_text=True, font = ('', 15))

# Defining some required values
path = os.getcwd()
initiate = True
reset_tmp()
window["-G4FOLDERNAME-"].bind("<Return>","_ENTER") # for quick and dirty debuggin with G4 enter, remove for actual release

while True:
    event,values = window.read()

    if initiate == True: 
        # Sets up default values for resetting to default parameters
        values_default = values
        # Brute force work around as reseting all parameter will clear the default 'Browse' string on the buttons
        values_default['Browse'] =values_default['Browse0']=values_default['Browse1']=values_default['Browse2']= "Browse"
        initiate = False
    
    if event == '-RESET-':
        # HAS TO BE A LOOPED FUNCTION CAUSE PYSIMPLEGUI
        for i in values: 
            window[i].update(values_default[i])
        window['-CTDI_TAB-'].update(visible=False)
        window['-DICOM_TAB-'].update(visible=False)
        pass

    if event == '-G4FOLDERNAME-_ENTER':
        # THIS IS A PLACEHOLDER FOR QUICK AND DIRTY DEBUGGING

        # DUMP all values into a text file
        f = open('dump.txt', 'w')
        f.write( 'dict = '+repr(values)+ '\n')
        f.close()

    if event == '-FUNCTION_CHECK-':
        # Turns on or off visibility of the tab when checkbox is selected
        if values['-FUNCTION_CHECK-'] == 'DICOM':
            window['-DICOM_TAB-'].update(visible=True)
            window['-CTDI_TAB-'].update(visible=False)
        elif values['-FUNCTION_CHECK-'] == 'CTDI validation':
            window['-CTDI_TAB-'].update(visible=True)
            window['-DICOM_TAB-'].update(visible=False)
            
    if event == '-DICOM-':
        # Takes DICOM imageset location and checks it for CT images and pulls relevant data tags
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

    if event == '-DICOMRP-':
        # Takes DICOM RT plan and checks patientID match and pulls out isocentre data. 
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
            tmp_headsource_file_path = path + '/tmp/headsourcecode.txt'
            editor(values, tmp_headsource_file_path, 'main')
            tmp_patient_file_path = path + '/tmp/patientDICOM.txt'
            editor(values, tmp_patient_file_path, 'sub')
            topas_application_path = values['-TOPAS-'] + " "
            run_status = log_output(tmp_headsource_file_path, 'dicom', topas_application_path, values['-FAN-'])
            reset_tmp()
            sg.popup(run_status)
        except:
            sg.popup_error("Ensure that you have specified a valid DICOM folder and file")
    
    if event == '-RUN-':
        # When users try to simulate CTDI , this block will run. 
        # Code will activate the editor() function to edit the tmp file
        # Runtimehandler will then form the timestamp folder and drop the outputs there
        tmp_headsource_file_path = path + '/tmp/headsourcecode.txt'
        editor(values, tmp_headsource_file_path, 'main')
        topas_application_path = values['-TOPAS-'] + " "
        if values['-CTDI_PHANTOM-'] == '16 cm': 
            tmp_16cm_file_path = path + '/tmp/CTDIphantom_16.txt'
            editor(values, tmp_16cm_file_path, 'sub')
            run_status = log_output(tmp_headsource_file_path, 'ctdi16', topas_application_path, values['-FAN-'])
            reset_tmp()
            sg.popup(run_status)        
        elif values['-CTDI_PHANTOM-'] == '32 cm': 
            tmp_32cm_file_path = path + '/tmp/CTDIphantom_32.txt'
            editor(values, tmp_32cm_file_path, 'sub')
            run_status = log_output(tmp_headsource_file_path, 'ctdi32', topas_application_path, values['-FAN-'])
            reset_tmp()
            sg.popup(run_status)

    if event == '-IMAGEMODE-':
        # When users select the image protocol, this block will run and input the imaging parameteres
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
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
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
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
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
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
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
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
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
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
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
            values['-BLADE_X1-'] = '1 mm'
            values['-BLADE_X2-'] = '2 mm'
            values['-BLADE_Y1-'] = '3 mm'
            values['-BLADE_Y2-'] = '4 mm'
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
    
    if event == '-DIRECTROT-':
        # This switches the direction of rotation depending on mode 
        if values['-DIRECTROT-'] == 'CBCT Clockwise':
            values['-TIMEROTRATE-'] = '0.4 deg/s'
            window['-TIMEROTRATE-'].update(values['-TIMEROTRATE-'])
        elif values['-DIRECTROT-'] == 'CBCT Anticlockwise':
            values['-TIMEROTRATE-'] = '-0.4 deg/s'
            window['-TIMEROTRATE-'].update(values['-TIMEROTRATE-'])
        elif values['-DIRECTROT-'] == 'kVkV':
            values['-TIMEROTRATE-'] = '0 deg/s'
            window['-TIMEROTRATE-'].update(values['-TIMEROTRATE-'])
    if event == '-COUCH_TOG-':
        window['-COUCH-'].update(visible=values['-COUCH_TOG-'])

    if event == sg.WIN_CLOSED:
        break

        
        

window.close()
