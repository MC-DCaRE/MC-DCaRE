# Helper script to set up the GUI elements. Edits to elements should be made here. Another daughter script called defaultvalues.py is used to store all the default parameters. 
import PySimpleGUI as sg
sg.theme('Reddit')
from src.defaultvalues import *

general_layer = sg.Frame('General Settings',
                [ 
                  [sg.Text('G4 Data Directory',size = (17,1),font=('Helvetica', 14), text_color='black'),
                    sg.In(default_text=default_G4_Directory,key='-G4FOLDERNAME-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FolderBrowse(button_text= "Browse", key= 'Browse' , font=('Helvetica', 14))],
                  [sg.Text('TOPAS Directory',size =(17,1),font=('Helvetica', 14),text_color='black'),
                    sg.In(default_text=default_TOPAS_Directory,key='-TOPAS-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FileBrowse(button_text= "Browse", key= 'Browse0',font=('Helvetica', 14))],
                  [sg.Button(button_text='Reset all parameters to default', key='-RESET-')],
              ])

main_menu_information_layer = sg.Frame('Instructions on the usage of the GUI', 
                             [ 
                               [sg.Text('Select your Topas and G4 data directories. Next, select the function you would like to enable. ')],
                               [sg.Text('   DICOM allows the user to specify a patient DICOM CT image folder to run simulations on')],
                               [sg.Text('   CTDI validation if for running simulations on CTDI phantom')],
                               [sg.Text('In the following pages, type in your desired value with the units. ')],
                               [sg.Text('By default all lengths are in units of mm and all angles are in units of degrees.')],
                             ]) 

CTDI_run_layer= sg.Frame('Activate CTDI simulation', 
                           [
                             [sg.Checkbox("Graphics toggle", enable_events=True, key='-GRAPHICS-', default= False)],
                             [sg.Button("Run", enable_events=True, key='-RUN-', disabled=False, font=('Helvetica', 14), disabled_button_color='grey')],
                            ], key ='-BUTTONSACTIVATE-', 
                              visible = False)

function_layer = sg.Frame('Choose your function',
                          [
                            [sg.Checkbox('Use DICOM', enable_events=True, key='-DICOMACTIVATECHECK-'),
                             sg.Checkbox('CTDI validation', enable_events=True , key='-USERACTIVATECHECK-')
                             ],
                          ])

dicom_file_layer = sg.pin(sg.Frame("DICOM inputs",
                              [ 
                                [sg.Text('DICOM Directory',size =(17,1),font=('Helvetica', 14),text_color='black'),
                                 sg.In(default_text=default_DICOM_Directory,key='-DICOM-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FolderBrowse(button_text= "Browse", key= 'Browse1' ,font=('Helvetica', 14))
                                ],
                                [sg.Text('Loaded patient ID:',size =(17,1),font=('Helvetica', 14),text_color='black'),
                                 sg.In(default_text = '', key = '-PATID-' ,size =(17,1),font=('Helvetica', 14),text_color='black', background_color='light grey', enable_events=True, readonly= True)],
                                [sg.Text('DICOM RP file',size =(17,1),font=('Helvetica', 14),text_color='black'),
                                 sg.In(default_text=default_DICOM_RP_file,key='-DICOMRP-',size=(50,1),font=('Helvetica', 14),enable_events=True),sg.FileBrowse(button_text= "Browse", key= 'Browse2' ,file_types= (("DICOM File",'*.dcm'),) ,font=('Helvetica', 14))
                                ],
                                [sg.Button("Run set up imaging dose simulation",enable_events=True, key='-DICOMBAT-',font=('Helvetica', 14),size=(35,1))],
                              ],
                              key ='-DICOMACTIVATE-', 
                              visible = False
                              ) )

dicom_information_layer = sg.Frame('Instructions on the usage of the DICOM adjustments', 
                             [ 
                               [sg.Text('The programme automatically shifts the patient such that the isocentre of the treatment plan is matched to the isocentre of the beam.')],
                               [sg.Text('In the next page, make any adjustments relative to the ioscentre of the treatment plan.')],
                               [sg.Text('Use the other tabs to make edits to other parameters like collimator openings and beam current. ')],
                             ]) 

dicom_patient_layer = sg.Frame('Patient set up adjustments',
                    [
                        [sg.Text('TransX',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_TRANS_X,key='-DICOM_TX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransY',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_TRANS_Y,key='-DICOM_TY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('TransZ',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_TRANS_Z,key='-DICOM_TZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('RotX',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_ROT_X,key='-DICOM_ROTX-',size=(10,1), font=('Helvetica', 12), enable_events=True)], 
                        [sg.Text('RotY',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_ROT_Y,key='-DICOM_ROTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)], 
                        [sg.Text('RotZ',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_ROT_Z,key='-DICOM_ROTZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)], 
                    ])

imaging_protocol_layer = sg.Frame('Imaging protocol',
                      [ [sg.Text('Imaging mode',size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.Combo(['Image Gently', 'Head', 'Short Thorax', 'Spotlight', 'Thorax', 'Pelvis', 'Pelvis Large'],default_value=None, key='-IMAGEMODE-', readonly=True ,enable_events=True)],
                        [sg.Text('Fan mode selection',size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text='Full fan', key='-FAN-',size = (15,1),font=('Helvetica', 12), text_color='black', enable_events=True,  readonly=True )],
                        [sg.Text('Collimate X1', size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text= "0 mm", key = '-BLADE_X1-',size = (15,1),font=('Helvetica', 12), text_color='black', enable_events=True, readonly=True)],
                        [sg.Text('Collimate X2', size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text= "0 mm", key = '-BLADE_X2-',size = (15,1),font=('Helvetica', 12), text_color='black', enable_events=True, readonly=True)],
                        [sg.Text('Collimate Y1', size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text= "0 mm", key = '-BLADE_Y1-',size = (15,1),font=('Helvetica', 12), text_color='black', enable_events=True, readonly=True)],
                        [sg.Text('Collimate Y2', size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text= "0 mm", key = '-BLADE_Y2-',size = (15,1),font=('Helvetica', 12), text_color='black', enable_events=True, readonly=True)],
                      ])

imaging_scan_layer = sg.Frame('Set up imaging parameters', 
                      [ [sg.Text('Start angle',size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text=default_DICOM_IMAGE_START_ANGLE,key='-STARTROT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('Stop angle',size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.In(default_text=default_DICOM_IMAGE_STOP_ANGLE,key='-STOPROT-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                        [sg.Text('Direction of rotation',size = (15,1),font=('Helvetica', 12), text_color='black'),
                         sg.Combo(['Clockwise', 'Anticlockwise'], default_value='Clockwise' ,key='-DIRECTROT-', readonly=True )],
                        [sg.Text('kVp',size = (15,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_IMAGE_VOLTAGE,key='-IMAGEVOLTAGE-',size=(10,1), font=('Helvetica', 12), enable_events=True)], 
                        [sg.Text('Beam current',size = (15,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_BEAM_CURRENT,key='-BEAMCURRENT-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                        ])

dicom_planned_layer = sg.Frame('Treatment plan parameters',
                    [
                        [sg.Text('Isocenter X',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text= default_DICOM_ISOCENTER_X, key='-DICOM_ISOX-',size=(10,1), font=('Helvetica', 12), enable_events=True, readonly=True)],
                        [sg.Text('Isocenter Y',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_ISOCENTER_Y, key='-DICOM_ISOY-',size=(10,1), font=('Helvetica', 12), enable_events=True, readonly=True)],
                        [sg.Text('Isocenter Z',size = (10,1),font=('Helvetica', 12), text_color='black'),
                        sg.In(default_text=default_DICOM_ISOCENTER_Z, key='-DICOM_ISOZ-',size=(10,1), font=('Helvetica', 12), enable_events=True, readonly=True)],
                    ])


CTDI_information_layer = sg.Frame('Instructions on the usage of the CTDI phantom parameters', 
                             [ 
                               [sg.Text('Select the CTDI phantom used for the CTDI validation. The phantom will be automatically centered at isocenter.')],
                               [sg.Text('Simulation will automatically generate and run 5 CTDI simulations for all 5 possible detector position.')],
                               [sg.Text('Use the other tabs to make edits to other parameters like collimator openings and beam current. ')],
                               [sg.Text('Use the couch toggle to select or remove the couch from the simulation, the phantom is automatically placed on top of the couch.')],
                               [sg.Text('You can also choose to change the thickeness of the couch in terms of its aluminium thickness.')]
                             ]) 

CTDI_layer = sg.Frame('CTDI phantom',
                    [
                      [sg.Text('CTDI phantom used',size = (15,1),font=('Helvetica', 12), text_color='black'),
                       sg.Combo(['16 cm', '32 cm'], default_value='16 cm' ,key='-CTDI_PHANTOM-', readonly=True )],
                      [sg.Checkbox("Couch toggle", enable_events=True, key='-COUCH_TOG-', default= True)],
                      [sg.Text('5 Chamber plugs ')]
                    ], vertical_alignment='top')




Scoring_layer = sg.Frame("Scoring",
                [
                  [sg.Text('Seed',size =(10,1),font=('Helvetica', 12),text_color='black'),
                   sg.In(default_text=default_Seed,key='-SEED-',size=(10,1),font=('Helvetica', 12),enable_events=True)],
                  [sg.Text('Threads',size = (10,1),font=('Helvetica', 12),text_color='black'),
                   sg.In(default_text=default_Threads,key='-THREAD-',size=(10,1),font=('Helvetica',12),enable_events=True)],
                  [sg.Text('Histories',size = (10,1),font=('Helvetica',12),text_color='black'),
                   sg.In(default_text=default_Histories,key='-HIST-',size=(10,1),font=('Helvetica',12),enable_events=True)],
                  [sg.Text('DTM_Zbins',size = (10,1),font=('Helvetica', 12), text_color='black'),
                   sg.In(default_text=default_DTM_Zbins,key='-DTMZB-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                  [sg.Text('TLE_Zbins',size = (10,1),font=('Helvetica', 12), text_color='black'),
                   sg.In(default_text=default_TLE_Zbins,key='-TLEZB-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                  [sg.Text('DTW_Zbins',size = (10,1),font=('Helvetica', 12), text_color='black'),
                   sg.In(default_text='100',key='-DTWZB-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                ])

Physics_layer = sg.Frame("Physics",
                [
                   [sg.Text('List',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_PHYSICS_LIST,key='-PHYLST-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Process',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_PHYSICS_PROCESS,key='-PHYPRO-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Default Type',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_PHYSICS_TYPE,key='-PHYDEFTY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Default Modules',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_PHYSICS_MODULES,key='-PHYDEFMO-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('EMRangeMin',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_PHYSICS_EM_MIN,key='-PHYEMIN-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('EMRangeMax',size = (15,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_PHYSICS_EM_MAX,key='-PHYEMAX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                ])


Couch_layer = sg.Frame("Couch",
                [
                   [sg.Text('TransX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_COUCH_TRANS_X,key='-COUCHTRANSX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_COUCH_TRANS_Y,key='-COUCHTRANSY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('TransZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_COUCH_TRANS_Z,key='-COUCHTRANSZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLZ',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_COUCH_HLZ,key='-COUCHHLZ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLY',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_COUCH_HLY,key='-COUCHHLY-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('HLX',size = (8,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_COUCH_HLX,key='-COUCHHLX-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   
                ], key='-COUCH-', visible= True )

Time_layer = sg.Frame("Time Feature",
                [   
                   [sg.Text('Seq Time',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_SEQ_TIME,key='-TIMESEQ-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Verbosity',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_VERBOSITY,key='-TIMEVERBO-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Timeline End',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_TIME_END,key='-TIMELINEEND-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Rotate Func',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_ROT_FUNC,key='-TIMEROTFUNC-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Rotate Rate',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_ROT_RATE,key='-TIMEROTRATE-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('Rotate Start',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_ROT_START,key='-TIMEROTSTART-',size=(10,1), font=('Helvetica', 12), enable_events=True)],
                   [sg.Text('ShowHistoryInt',size = (14,1),font=('Helvetica', 12), text_color='black'),
                     sg.In(default_text=default_TIME_ROT_HISTORY,key='-TIMEHISTINT-',size=(10,1), font=('Helvetica', 12), enable_events=True)]
                     
                ])

settings_layout = sg.Frame("General settings", 
                           [
                               [sg.Text('This page contains general settings used for all simulations.')],
                               [sg.Text('You will be able to control the granularity of the simulations along with the scan parameters here')],
                               [sg.Text('')],
                           ])                