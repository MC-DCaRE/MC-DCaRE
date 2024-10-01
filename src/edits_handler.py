# This script is used to handle all the edits that must be made to the .batch and python files.

def stringindexreplacement(SearchString :str , TargetList: str , ReplacementString :str = None):
    '''
    Targeted string replacement for a list. 
    Function looks for the line that startes with SearchString at the file directory of TargetFile and replaces it with Replacement String. 
    Function will replace the entire line and any information trailing the SearchString will be lost in this process. 
    Untested, but should be faster
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
    Uses the values and selectcomponent dictionary to reference for keys and value to replace. 

    :filetype str: either "DICOM" or "CTDI"
    '''
    with open(TargetFile, 'r') as Rread_file:
        filecontent = Rread_file.readlines()


    stringindexreplacement('i:Ts/Seed', filecontent , change_dictionary['-SEED-']) 
    stringindexreplacement('i:Ts/NumberOfThreads', filecontent , change_dictionary['-THREAD-']) 
    stringindexreplacement('s:Ts/G4DataDirectory', filecontent , '\"'+change_dictionary['-G4FOLDERNAME-']+'\"') 

    stringindexreplacement('i:Sc/DoseOnRTGrid100kz17/ZBins', filecontent , change_dictionary['-DTMZB-']) 
    stringindexreplacement('i:Sc/DoseOnRTGrid_tle100kz17/ZBins', filecontent , change_dictionary['-TLEZB-']) 

    stringindexreplacement('d:Ph/Default/EMRangeMin', filecontent , change_dictionary['-PHYEMIN-']) 
    stringindexreplacement('d:Ph/Default/EMRangeMax', filecontent , change_dictionary['-PHYEMAX-']) 
    stringindexreplacement('s:Ge/BeamPosition/Type', filecontent , '\"'+change_dictionary['-BEAMGRPTY-']+'\"') 
    stringindexreplacement('d:Ge/BeamPosition/TransX', filecontent , change_dictionary['-BEAMGRPTRANSX-']) 
    stringindexreplacement('d:Ge/BeamPosition/TransY', filecontent , change_dictionary['-BEAMGRPTRANSY-']) 
    stringindexreplacement('d:Ge/BeamPosition/TransZ', filecontent , change_dictionary['-BEAMGRPTRANSZ-']) 
    stringindexreplacement('d:Ge/BeamPosition/RotX', filecontent , change_dictionary['-BEAMGRPROTX-']) 
    stringindexreplacement('d:Ge/BeamPosition/RotY', filecontent , change_dictionary['-BEAMGRPROTY-']) 
    stringindexreplacement('d:Ge/BeamPosition/RotZ', filecontent , change_dictionary['-BEAMGRPROTZ-']) 
    stringindexreplacement('s:So/beam/BeamEnergySpectrumType', filecontent , '\"'+change_dictionary['-BEAMSPECTY-']+'\"') 
    stringindexreplacement('s:So/beam/Type', filecontent , '\"'+change_dictionary['-BEAMTY-']+'\"') 
    stringindexreplacement('s:So/beam/Component', filecontent , '\"'+change_dictionary['-BEAMCOMPO-']+'\"') 
    stringindexreplacement('s:So/beam/BeamParticle', filecontent , '\"'+change_dictionary['-BEAMPAR-']+'\"') 
    stringindexreplacement('s:So/beam/BeamPositionDistribution', filecontent , '\"'+change_dictionary['-BEAMPOSDISTRO-']+'\"') 
    stringindexreplacement('s:So/beam/BeamPositionCutoffShape', filecontent , '\"'+change_dictionary['-BEAMPOSHAPE-']+'\"') 
    stringindexreplacement('d:So/beam/BeamPositionCutoffX', filecontent , change_dictionary['-BEAMPOSCUTOFFX-']) 
    stringindexreplacement('d:So/beam/BeamPositionCutoffY', filecontent , change_dictionary['-BEAMPOSCUTTOFFY-']) 
    stringindexreplacement('d:So/beam/BeamPositionSpreadX', filecontent , change_dictionary['-BEAMPOSSPRDX-']) 
    stringindexreplacement('d:So/beam/BeamPositionSpreadY', filecontent , change_dictionary['-BEAMPOSSPRDY-']) 
    stringindexreplacement('s:So/beam/BeamAngularDistribution', filecontent , '\"'+change_dictionary['-BEAMSPOSANGDISTRO-']+'\"') 
    stringindexreplacement('d:So/beam/BeamAngularCutoffX', filecontent , change_dictionary['-BEAMPOSANGCUTOFFX-']) 
    stringindexreplacement('d:So/beam/BeamAngularCutoffY', filecontent , change_dictionary['-BEAMPOSANGCUTOFFY-']) 
    stringindexreplacement('d:So/beam/BeamAngularSpreadX', filecontent , change_dictionary['-BEAMPOSANGSPREADX-']) 
    stringindexreplacement('d:So/beam/BeamAngularSpreadY', filecontent , change_dictionary['-BEAMPOSANGSPREADY-']) 
    stringindexreplacement('i:So/beam/NumberOfHistoriesInRun', filecontent , change_dictionary['-HIST-']) 


    stringindexreplacement('i:Tf/NumberOfSequentialTimes', filecontent , change_dictionary['-TIMESEQ-']) 
    stringindexreplacement('i:Tf/Verbosity', filecontent , change_dictionary['-TIMEVERBO-']) 
    stringindexreplacement('d:Tf/TimelineEnd', filecontent , change_dictionary['-TIMELINEEND-']) 
    stringindexreplacement('s:Tf/Rotate/Function', filecontent , '\"'+change_dictionary['-TIMEROTFUNC-']+'\"') 
    stringindexreplacement('d:Tf/Rotate/Rate', filecontent , change_dictionary['-TIMEROTRATE-']) 
    stringindexreplacement('d:Tf/Rotate/StartValue', filecontent , change_dictionary['-TIMEROTSTART-']) 
    stringindexreplacement('i:Ts/ShowHistoryCountAtInterval', filecontent , change_dictionary['-TIMEHISTINT-']) 

    if change_dictionary['-GRAPHICS-'] ==False: 
        stringindexreplacement('Ts/UseQt', filecontent , ) 
        stringindexreplacement('s:Gr/ViewA/Type', filecontent , ) 
        stringindexreplacement('b:Gr/Enable', filecontent , ' "F" ') 
    elif change_dictionary['-GRAPHICS-'] ==True:
        stringindexreplacement('Ts/UseQt', filecontent , ' "True" ') 
        stringindexreplacement('s:Gr/ViewA/Type', filecontent , ' "OpenGL" ') 
        stringindexreplacement('b:Gr/Enable', filecontent , ' "T" ') 
        
        
    if change_dictionary['-FAN-'] == 'Full fan':
        ### First remove the other header, then edit the correct ones and add in shift of bowtie filter
        stringindexreplacement('#halffanrotationrate', filecontent , ) 
        # ADD EDITS TO THE BOWTIE GEOMETRY 
    elif change_dictionary['-FAN-'] == 'Half fan':
        ### First remove the unwanted other option, then edit the correct ones
        stringindexreplacement('#fullfanrotationrate', filecontent , )

    if filetype == 'DICOM':
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

    if filetype == 'CTDI':
        # CTDI specific 
        stringindexreplacement( 'couch_HLX', filecontent, '\''+ change_dictionary['-COUCHHLX-'] +'\'' )
        stringindexreplacement( 'couch_HLY', filecontent, '\''+ change_dictionary['-COUCHHLY-'] +'\'' )
        stringindexreplacement( 'couch_HLZ', filecontent, '\''+ change_dictionary['-COUCHHLZ-'] +'\'' )
        stringindexreplacement( 'couch_TransX', filecontent, '\''+ change_dictionary['-COUCHTRANSX-'] +'\'' )
        stringindexreplacement( 'couch_TransY', filecontent, '\''+ change_dictionary['-COUCHTRANSY-'] +'\'' )
        stringindexreplacement( 'couch_TransZ', filecontent, '\''+ change_dictionary['-COUCHTRANSZ-'] +'\'' )



    with open(TargetFile, 'w') as Write_file:
        Write_file.writelines( filecontent )

    pass 

if __name__== '__main__':
    editor()