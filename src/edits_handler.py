# This script is used to handle all the edits that must be made to the .batch and python files.

def stringindexreplacement(SearchString :str , TargetList: str , ReplacementString :str = None):
    '''
    Targeted string replacement for a list. 
    Function looks for the line that startes with SearchString in the list and replaces it with Replacement String. 
    Function will replace the entire line and any information trailing the SearchString and replacement string will be lost in this process. 
    Untested, but should be faster
    If no replacement string is given in the arguements, the entire line is removed 
    '''
    for lineIndex in range(len(TargetList)):
        if TargetList[lineIndex].startswith(SearchString):
            if ReplacementString == None:
                TargetList[lineIndex] = '' 
                break #exits after the first instance of match. Saves compute. 
            else:
                TargetList[lineIndex] = SearchString + " = " + ReplacementString + '\n' 
                break #exits after the first instance of match. Saves compute. 



def editor(change_dictionary: dict,  TargetFile: str, filetype:str):
    '''
    Main function that handles the editting and changing of parameter files. 
    As the user inputs are saved in the values dictionary, this is passed in as change_dictionary and we can use the associated key to reference it and pull the data. 
    The function opens the Targetfile and saves it as a list on memory to be editted before rewriting after all edits are done on the list. 
    All edits must be hardcoded here. 
    
    :filetype str: either "main" or "sub" ; "main" is for the mainheadscript and "sub" is for includefiles
    '''
    with open(TargetFile, 'r') as Rread_file:
        filecontent = Rread_file.readlines()

    if filetype == 'main':
        # Edits for mainheadsource
        stringindexreplacement('s:Ts/G4DataDirectory', filecontent , '\"'+change_dictionary['-G4FOLDERNAME-']+'\"') 
        stringindexreplacement('i:Tf/NumberOfSequentialTimes', filecontent , change_dictionary['-TIMESEQ-']) 
        stringindexreplacement('i:Tf/Verbosity', filecontent , change_dictionary['-TIMEVERBO-']) 
        stringindexreplacement('d:Tf/TimelineEnd', filecontent , change_dictionary['-TIMELINEEND-']) 
        stringindexreplacement('d:Tf/Rotate/Rate', filecontent , change_dictionary['-TIMEROTRATE-']) 
        stringindexreplacement('d:Tf/Rotate/StartValue', filecontent , change_dictionary['-STARTANGLEROT-']) 
        stringindexreplacement('i:Ts/Seed', filecontent , change_dictionary['-SEED-']) 
        stringindexreplacement('i:Ts/NumberOfThreads', filecontent , change_dictionary['-THREAD-']) 
        stringindexreplacement('i:So/beam/NumberOfHistoriesInRun', filecontent , change_dictionary['-HIST-']) 

            
        if change_dictionary['-FAN-'] == 'Full Fan':
            ### Removes the includeFile line for half bowtie
            stringindexreplacement('includeFile = halffan.txt', filecontent , ) 
            # ADD EDITS TO THE BOWTIE GEOMETRY 
        elif change_dictionary['-FAN-'] == 'Half Fan':
            ### Removes the includeFile line for full bowtie
            stringindexreplacement('includeFile = fullfan.txt', filecontent , )

        if change_dictionary['-FUNCTION_CHECK-'] == 'DICOM':
            ### Removes both CTDI phantom includeFile
            stringindexreplacement('includeFile = CTDIphantom_16.txt', filecontent , )
            stringindexreplacement('includeFile = CTDIphantom_32.txt', filecontent , )
            stringindexreplacement('sv:Ph/Default/LayeredMassGeometryWorlds', filecontent , )
            if change_dictionary['-DICOM_GRAPHICS-'] ==False: 
                ### Removes graphics 
                stringindexreplacement('Ts/UseQt', filecontent , ) 
                stringindexreplacement('s:Gr/ViewA/Type', filecontent , ) 
                stringindexreplacement('b:Gr/Enable', filecontent , ) 

        elif change_dictionary['-FUNCTION_CHECK-'] == 'CTDI validation':
            ### Removes DICOM includeFile and the other phantom file
            stringindexreplacement('includeFile = patientDICOM.txt', filecontent , )
            if change_dictionary['-CTDI_GRAPHICS-'] ==False: 
                ### Removes graphics 
                stringindexreplacement('Ts/UseQt', filecontent , ) 
                stringindexreplacement('s:Gr/ViewA/Type', filecontent , ) 
                stringindexreplacement('b:Gr/Enable', filecontent , ) 

            if change_dictionary['-CTDI_PHANTOM-'] == '16 cm': 
                stringindexreplacement('includeFile = CTDIphantom_32.txt', filecontent , )
            elif change_dictionary['-CTDI_PHANTOM-'] == '32 cm': 
                stringindexreplacement('includeFile = CTDIphantom_16.txt', filecontent , )


    if filetype == 'sub':
        # Edits related to includeFiles 
        if change_dictionary['-FUNCTION_CHECK-'] == 'DICOM':
            stringindexreplacement('d:Ge/Patient/RotX', filecontent , change_dictionary['-DICOM_ROTX-']) 
            stringindexreplacement('d:Ge/Patient/RotY', filecontent , change_dictionary['-DICOM_ROTY-']) 
            stringindexreplacement('d:Ge/Patient/RotZ', filecontent , change_dictionary['-DICOM_ROTZ-']) 
            stringindexreplacement('s:Ge/Patient/DicomDirectory', filecontent , '\"'+change_dictionary['-DICOM-']+'\"') 

            stringindexreplacement('dc:Ge/IsocenterX', filecontent , change_dictionary['-DICOM_ISOX-'])  
            stringindexreplacement('dc:Ge/IsocenterY', filecontent , change_dictionary['-DICOM_ISOY-'])  
            stringindexreplacement('dc:Ge/IsocenterZ', filecontent , change_dictionary['-DICOM_ISOZ-'])  

            stringindexreplacement('dc:Ge/Patient/UserTransX', filecontent , change_dictionary['-DICOM_TX-'])
            stringindexreplacement('dc:Ge/Patient/UserTransY', filecontent , change_dictionary['-DICOM_TY-'])
            stringindexreplacement('dc:Ge/Patient/UserTransZ', filecontent , change_dictionary['-DICOM_TZ-'])

            stringindexreplacement('s:Sc/DoseOnRTGrid100kz17/OutputFile', filecontent , '\"' +change_dictionary['-PATID-'] + '_DOSE_PTV' +'\"') 
            
        elif change_dictionary['-FUNCTION_CHECK-'] == 'CTDI validation':
            if change_dictionary['-COUCH_TOG-'] == False: 
                # by removing the parent group link, the component is removed
                stringindexreplacement( 's:Ge/couch/Parent="couchgroup"', filecontent,  )
            stringindexreplacement( 'd:Ge/couch/HLX', filecontent, change_dictionary['-COUCHHLX-'] )
            stringindexreplacement( 'd:Ge/couch/HLY', filecontent, change_dictionary['-COUCHHLY-'] )
            stringindexreplacement( 'd:Ge/couch/HLZ', filecontent, change_dictionary['-COUCHHLZ-'] )
            stringindexreplacement( 'i:Sc/ChamberPlugDose_dtm/ZBins', filecontent , change_dictionary['-DTMZB-']) 
            stringindexreplacement( 'i:Sc/ChamberPlugDose_tle/ZBins', filecontent , change_dictionary['-TLEZB-']) 
            stringindexreplacement( 'i:Sc/ChamberPlugDose_dtw/ZBins', filecontent , change_dictionary['-DTWZB-']) 



    with open(TargetFile, 'w') as Write_file:
        Write_file.writelines( filecontent )

    pass 

if __name__== '__main__':
    editor()