# This script is used to handle all the edits that must be made to the .batch and python files.

def stringindexreplacement_Dictionary(SearchString :str , TargetList: str , ReplacementString :str):
    '''
    Targeted string replacement for dictionary. Only difference is that it uses : instead of =  
    Function looks for the line that startes with SearchString at the file directory of TargetFile and replaces it with Replacement String. 
    Function will replace the entire line and any information trailing the SearchString will be lost in this process. 
    '''
    for lineIndex in range(len(TargetList)):
        if TargetList[lineIndex].startswith(SearchString):
            TargetList[lineIndex] = SearchString + ":" + ReplacementString + '\n' 
            break #exits after the first instance of match. Saves compute. 

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

    if filetype == 'DICOM':
        stringindexreplacement('i:Ts/Seed', filecontent , change_dictionary['-SEED-']) 
        stringindexreplacement('i:Ts/NumberOfThreads', filecontent , change_dictionary['-THREAD-']) 
        stringindexreplacement('s:Ts/G4DataDirectory', filecontent , '\"'+change_dictionary['-G4FOLDERNAME-']+'\"') 

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
        
        if change_dictionary['-FAN-'] == 'Full fan':
            ### First remove the other header, then edit the correct ones and add in shift of bowtie filter
            stringindexreplacement('#halffanrotationrate', filecontent , ) 
            # ADD EDITS TO THE BOWTIE GEOMETRY 
        elif change_dictionary['-FAN-'] == 'Half fan':
            ### First remove the unwanted other option, then edit the correct ones
            stringindexreplacement('#fullfanrotationrate', filecontent , )
            # ADD EDITS TO THE BOWTIE GEOMETRY 
        ## Edits
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
        

    if filetype == 'CTDI':
        # CTDI specific 
        if change_dictionary['-CPCTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugCentre' +'\'', filecontent , '0,')
            pass
        if change_dictionary['-CPTTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugTop'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-CPBTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugBottom'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-CPLTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugLeft'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-CPRTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugRight'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-DTMTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugDose_dtm'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-TLETOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugDose_tle'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-DTWTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'ChamberPlugDose_dtw'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-COLLVERTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'CollimatorsVertical'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-COLLHORTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'CollimatorsHorizontal'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-TITFILTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'TitaniumFilter'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-BTFILTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'BowtieFilter'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-COLL1TOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'Coll1'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-COLL2TOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'Coll2'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-COLL3TOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'Coll3'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-COLL4TOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'Coll4'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-DEMOFLATTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'DemoFlat'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-DEMORTRAPTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'DemoRTrap'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-DEMOLTRAPTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'DemoLTrap'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-TSBTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'topsidebox'+'\'', filecontent , '0,')
            pass
        if change_dictionary['-BSBTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'bottomsidebox'+'\'', filecontent , '0,') 
            pass
        if change_dictionary['-COHTOG-'] == False: 
            stringindexreplacement_Dictionary( '\''+'couch'+'\'', filecontent , '0,') 
            pass

        stringindexreplacement( 'Seed', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'NumberOfThreads', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'G4DataDirectory', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'World_HLX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'World_HLY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'World_HLZ', filecontent, '\''+ change_dictionary['--'] +'\'' )



        stringindexreplacement( 'CTDI_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_RMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_RMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_HL', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_SPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_DPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CTDI_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_RMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_RMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_HL', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_SPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_DPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_isParallel', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugCentre_color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_RMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_RMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_HL', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_SPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_DPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_isParallel', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugTop_color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_RMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_RMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_HL', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_SPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_DPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_isParallel', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugBottom_color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_RMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_RMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_HL', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_SPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_DPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_isParallel', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugLeft_color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_RMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_RMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_HL', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_SPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_DPhi', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_isParallel', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugRight_color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_tle_Quantity', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_tle_InputFile', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_tle_Component', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_tle_IfOutputFileAlreadyExists', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_tle_ZBins', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtm_Quantity', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtm_Component', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtm_IfOutputFileAlreadyExists', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtm_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtm_ZBins', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtw_Quantity', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtw_Component', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtw_IfOutputFileAlreadyExists', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtw_ZBins', filecontent, '\''+ change_dictionary['--'] +'\'' )

        stringindexreplacement( 'ChamberPlugDose_tle_OutputFile', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtm_OutputFile', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ChamberPlugDose_dtw_OutputFile', filecontent, '\''+ change_dictionary['--'] +'\'' )

        stringindexreplacement( 'Ph_ListName', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Ph_ListProcesses', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Ph_Default_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Ph_Default_Modules', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Ph_Default_EMRangeMin', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Ph_Default_EMRangeMax', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotation_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsVertical_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsVertical_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsVertical_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsVertical_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsVertical_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsVertical_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsHorizontal_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsHorizontal_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsHorizontal_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsHorizontal_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsHorizontal_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'CollimatorsHorizontal_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BowtieFilter_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll1steel_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll2steel_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll3steel_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Coll4steel_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilterGroup_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilterGroup_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilterGroup_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilterGroup_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilterGroup_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilterGroup_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_HLX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_HLY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_HLZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TitaniumFilter_DrawingStyle', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_HLX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_HLY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_HLZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoFlat_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoRTrap_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_LZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_LY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_LX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_LTX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'DemoLTrap_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_HLX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_HLY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_HLZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'topsidebox_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_HLX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_HLY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_HLZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'bottomsidebox_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_Material', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_HLX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_HLY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_HLZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'couch_Color', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_Parent', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_TransX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_TransY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_TransZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_RotX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_RotY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamPosition_RotZ', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'BeamEnergySpectrumType', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_Type', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_Component', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamParticle', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamPositionDistribution', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamPositionCutoffShape', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamPositionCutoffX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamPositionCutoffY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamPositionSpreadX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamPositionSpreadY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamAngularDistribution', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamAngularCutoffX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamAngularCutoffY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamAngularSpreadX', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_BeamAngularSpreadY', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'beam_NumberOfHistoriesInRun', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'NumberOfSequentialTimes', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Verbosity', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'TimelineEnd', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotate_Function', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotate_Rate', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'Rotate_StartValue', filecontent, '\''+ change_dictionary['--'] +'\'' )
        stringindexreplacement( 'ShowHistoryCountAtInterval', filecontent, '\''+ change_dictionary['--'] +'\'' )



    with open(TargetFile, 'w') as Write_file:
        Write_file.writelines( filecontent )

    pass 

if __name__== '__main__':
    editor()