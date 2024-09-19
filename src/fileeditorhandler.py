# from topas_gui import stringindexreplacement
def stringindexreplacement_Legacy(SearchString :str , TargetFile: str , ReplacementString: str):
    '''
    Targeted string replacement. 
    Function looks for the line that startes with SearchString at the file directory of TargetFile and replaces it with Replacement String. 
    Function will replace the entire line and any information trailing the SearchString will be lost in this process. 
    Probably a huge memory hog as it repeatedly reads, write then close the file. 
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
                TargetList[lineIndex] = SearchString + "=" + ReplacementString + '\n' 
                break #exits after the first instance of match. Saves compute. 



def editor(change_dictionary: dict, toggle_dictionary: dict, TargetFile: str, filetype:str):
    '''
    Main function that handles the editting and changing of parameter files. 
    Uses the values and selectcomponent dictionary to reference for keys and value to replace. 

    :filetype str: either .bat file or a generate_allproc.py file 
    '''
    with open(TargetFile, 'r') as Rread_file:
        filecontent = Rread_file.readlines()

    if filetype == '.bat':
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

        stringindexreplacement('i:Sc/DoseOnRTGrid_tle/ZBins', filecontent , change_dictionary['-TLEZB-']) 
        #missing 2 other zbins
        stringindexreplacement('s:Ph/ListName', filecontent , '\"'+change_dictionary['-PHYLST-']+'\"') 
        stringindexreplacement('b:Ph/ListProcesses', filecontent , '\"'+change_dictionary['-PHYPRO-']+'\"') 
        stringindexreplacement('s:Ph/Default/Type', filecontent , '\"'+change_dictionary['-PHYDEFTY-']+'\"') 
        stringindexreplacement('sv:Ph/Default/Modules', filecontent , change_dictionary['-PHYDEFMO-']) 

        stringindexreplacement('d:Ph/Default/EMRangeMin', filecontent , change_dictionary['-PHYEMIN-']) 
        stringindexreplacement('d:Ph/Default/EMRangeMax', filecontent , change_dictionary['-PHYEMAX-']) 


        stringindexreplacement('s:Ge/Rotation/Type', filecontent , '\"'+change_dictionary['-ROTTY-']+'\"') 
        stringindexreplacement('d:Ge/Rotation/RotX', filecontent , change_dictionary['-ROTROTX-']) 
        stringindexreplacement('d:Ge/Rotation/RotY', filecontent , change_dictionary['-ROTROTY-']) 
        stringindexreplacement('d:Ge/Rotation/RotZ', filecontent , change_dictionary['-ROTROTZ-']) 
        stringindexreplacement('d:Ge/Rotation/TransX', filecontent , change_dictionary['-ROTTRANSX-']) 
        stringindexreplacement('d:Ge/Rotation/TransY', filecontent , change_dictionary['-ROTTRANSY-']) 
        stringindexreplacement('d:Ge/Rotation/TransZ', filecontent , change_dictionary['-ROTTRANSZ-']) 

        stringindexreplacement('s:Ge/CollimatorsVertical/Type', filecontent , '\"'+change_dictionary['-COLLVERTY-']+'\"') 
        stringindexreplacement('d:Ge/CollimatorsVertical/RotX', filecontent , change_dictionary['-COLLVERROTX-']) 
        stringindexreplacement('d:Ge/CollimatorsVertical/RotY', filecontent , change_dictionary['-COLLVERROTY-']) 
        stringindexreplacement('d:Ge/CollimatorsVertical/RotZ', filecontent , change_dictionary['-COLLVERROTZ-']) 
        stringindexreplacement('d:Ge/CollimatorsVertical/TransZ', filecontent , change_dictionary['-COLLVERTRANSZ-'] + ' + Ge/BeamPosition/TransZ') 

        stringindexreplacement('s:Ge/CollimatorsHorizontal/Type', filecontent , '\"'+change_dictionary['-COLLHORTY-']+'\"') 
        stringindexreplacement('d:Ge/CollimatorsHorizontal/RotX', filecontent , change_dictionary['-COLLHORROTX-']) 
        stringindexreplacement('d:Ge/CollimatorsHorizontal/RotY', filecontent , change_dictionary['-COLLHORROTY-']) 
        stringindexreplacement('d:Ge/CollimatorsHorizontal/RotZ', filecontent , change_dictionary['-COLLHORROTZ-']) 
        stringindexreplacement('d:Ge/CollimatorsHorizontal/TransZ', filecontent , change_dictionary['-COLLHORTRANSZ-'] + ' + Ge/Coll1/LY') 

        stringindexreplacement('s:Ge/BowtieFilter/Type', filecontent , '\"'+change_dictionary['-BFTY-']+'\"') 
        stringindexreplacement('dc:Ge/BowtieFilter/RotX', filecontent , change_dictionary['-BFROTX-']) 
        stringindexreplacement('d:Ge/BowtieFilter/RotY', filecontent , change_dictionary['-BFROTY-']) 
        stringindexreplacement('d:Ge/BowtieFilter/RotZ', filecontent , change_dictionary['-BFROTZ-']) 
        stringindexreplacement('d:Ge/BowtieFilter/TransX', filecontent , change_dictionary['-BFTRANSX-']) 
        stringindexreplacement('d:Ge/BowtieFilter/TransY', filecontent , change_dictionary['-BFTRANSY-']) 
        stringindexreplacement('d:Ge/BowtieFilter/TransZ', filecontent , change_dictionary['-BFTRANSZ-']) 

        stringindexreplacement('s:Ge/Coll1/Type', filecontent , '\"'+change_dictionary['-Coll1TY-']+'\"') 
        stringindexreplacement('s:Ge/Coll1/Material', filecontent , '\"'+change_dictionary['-Coll1MAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll1/TransX', filecontent , change_dictionary['-Coll1TRANSX-']) 
        stringindexreplacement('dc:Ge/Coll1/TransY', filecontent , change_dictionary['-Coll1TRANSY-']) 
        stringindexreplacement('dc:Ge/Coll1/TransZ', filecontent , change_dictionary['-Coll1TRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll1/RotX', filecontent , change_dictionary['-Coll1ROTX-']) 
        stringindexreplacement('dc:Ge/Coll1/RotY', filecontent , change_dictionary['-Coll1ROTY-']) 
        stringindexreplacement('dc:Ge/Coll1/RotZ', filecontent , change_dictionary['-Coll1ROTZ-']) 
        stringindexreplacement('dc:Ge/Coll1/LZ', filecontent , change_dictionary['-Coll1LZ-']) 
        stringindexreplacement('dc:Ge/Coll1/LY', filecontent , change_dictionary['-Coll1LY-']) 
        stringindexreplacement('dc:Ge/Coll1/LX', filecontent , change_dictionary['-Coll1LX-']) 
        stringindexreplacement('dc:Ge/Coll1/LTX', filecontent , change_dictionary['-Coll1LTX-']) 

        stringindexreplacement('s:Ge/Coll2/Type', filecontent , '\"'+change_dictionary['-Coll2TY-']+'\"') 
        stringindexreplacement('s:Ge/Coll2/Material', filecontent , '\"'+change_dictionary['-Coll2MAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll2/TransX', filecontent , change_dictionary['-Coll2TRANSX-']) 
        stringindexreplacement('dc:Ge/Coll2/TransY', filecontent , change_dictionary['-Coll2TRANSY-']) 
        stringindexreplacement('dc:Ge/Coll2/TransZ', filecontent , change_dictionary['-Coll2TRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll2/RotX', filecontent , change_dictionary['-Coll2ROTX-']) 
        stringindexreplacement('dc:Ge/Coll2/RotY', filecontent , change_dictionary['-Coll2ROTY-']) 
        stringindexreplacement('dc:Ge/Coll2/RotZ', filecontent , change_dictionary['-Coll2ROTZ-']) 
        stringindexreplacement('dc:Ge/Coll2/LZ', filecontent , change_dictionary['-Coll2LZ-']) 
        stringindexreplacement('dc:Ge/Coll2/LY', filecontent , change_dictionary['-Coll2LY-']) 
        stringindexreplacement('dc:Ge/Coll2/LX', filecontent , change_dictionary['-Coll2LX-']) 
        stringindexreplacement('dc:Ge/Coll2/LTX', filecontent , change_dictionary['-Coll2LTX-'])

        stringindexreplacement('s:Ge/Coll3/Type', filecontent , '\"'+change_dictionary['-Coll3TY-']+'\"') 
        stringindexreplacement('s:Ge/Coll3/Material', filecontent , '\"'+change_dictionary['-Coll3MAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll3/TransX', filecontent , change_dictionary['-Coll3TRANSX-']) 
        stringindexreplacement('dc:Ge/Coll3/TransY', filecontent , change_dictionary['-Coll3TRANSY-']) 
        stringindexreplacement('dc:Ge/Coll3/TransZ', filecontent , change_dictionary['-Coll3TRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll3/RotX', filecontent , change_dictionary['-Coll3ROTX-']) 
        stringindexreplacement('dc:Ge/Coll3/RotY', filecontent , change_dictionary['-Coll3ROTY-']) 
        stringindexreplacement('dc:Ge/Coll3/RotZ', filecontent , change_dictionary['-Coll3ROTZ-']) 
        stringindexreplacement('dc:Ge/Coll3/LZ', filecontent , change_dictionary['-Coll3LZ-']) 
        stringindexreplacement('dc:Ge/Coll3/LY', filecontent , change_dictionary['-Coll3LY-']) 
        stringindexreplacement('dc:Ge/Coll3/LX', filecontent , change_dictionary['-Coll3LX-']) 
        stringindexreplacement('dc:Ge/Coll3/LTX', filecontent , change_dictionary['-Coll3LTX-'])

        stringindexreplacement('s:Ge/Coll4/Type', filecontent , '\"'+change_dictionary['-Coll4TY-']+'\"') 
        stringindexreplacement('s:Ge/Coll4/Material', filecontent , '\"'+change_dictionary['-Coll4MAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll4/TransX', filecontent , change_dictionary['-Coll4TRANSX-']) 
        stringindexreplacement('dc:Ge/Coll4/TransY', filecontent , change_dictionary['-Coll4TRANSY-']) 
        stringindexreplacement('dc:Ge/Coll4/TransZ', filecontent , change_dictionary['-Coll4TRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll4/RotX', filecontent , change_dictionary['-Coll4ROTX-']) 
        stringindexreplacement('dc:Ge/Coll4/RotY', filecontent , change_dictionary['-Coll4ROTY-']) 
        stringindexreplacement('dc:Ge/Coll4/RotZ', filecontent , change_dictionary['-Coll4ROTZ-']) 
        stringindexreplacement('dc:Ge/Coll4/LZ', filecontent , change_dictionary['-Coll4LZ-']) 
        stringindexreplacement('dc:Ge/Coll4/LY', filecontent , change_dictionary['-Coll4LY-']) 
        stringindexreplacement('dc:Ge/Coll4/LX', filecontent , change_dictionary['-Coll4LX-']) 
        stringindexreplacement('dc:Ge/Coll4/LTX', filecontent , change_dictionary['-Coll4LTX-'])  

        stringindexreplacement('s:Ge/Coll1steel/Type', filecontent , '\"'+change_dictionary['-Coll1steelTY-']+'\"') 
        stringindexreplacement('s:Ge/Coll1steel/Material', filecontent , '\"'+change_dictionary['-Coll1steelMAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll1steel/TransX', filecontent , change_dictionary['-Coll1steelTRANSX-']) 
        stringindexreplacement('dc:Ge/Coll1steel/TransY', filecontent , 'Ge/Coll1/TransY - ' + change_dictionary['-Coll1steelTRANSY-']) 
        stringindexreplacement('dc:Ge/Coll1steel/TransZ', filecontent , change_dictionary['-Coll1steelTRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll1steel/RotX', filecontent , change_dictionary['-Coll1steelROTX-']) 
        stringindexreplacement('dc:Ge/Coll1steel/RotY', filecontent , change_dictionary['-Coll1steelROTY-']) 
        stringindexreplacement('dc:Ge/Coll1steel/RotZ', filecontent , change_dictionary['-Coll1steelROTZ-']) 
        stringindexreplacement('dc:Ge/Coll1steel/LZ', filecontent , change_dictionary['-Coll1steelLZ-']) 
        stringindexreplacement('dc:Ge/Coll1steel/LY', filecontent , change_dictionary['-Coll1steelLY-']) 
        stringindexreplacement('dc:Ge/Coll1steel/LX', filecontent , change_dictionary['-Coll1steelLX-']) 
        stringindexreplacement('dc:Ge/Coll1steel/LTX', filecontent , change_dictionary['-Coll1steelLTX-']) 

        stringindexreplacement('s:Ge/Coll2steel/Type', filecontent , '\"'+change_dictionary['-Coll2steelTY-']+'\"') 
        stringindexreplacement('s:Ge/Coll2steel/Material', filecontent , '\"'+change_dictionary['-Coll2steelMAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll2steel/TransX', filecontent , change_dictionary['-Coll2steelTRANSX-']) 
        stringindexreplacement('dc:Ge/Coll2steel/TransY', filecontent , 'Ge/Coll2/TransY + ' + change_dictionary['-Coll2steelTRANSY-']) 
        stringindexreplacement('dc:Ge/Coll2steel/TransZ', filecontent , change_dictionary['-Coll2steelTRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll2steel/RotX', filecontent , change_dictionary['-Coll2steelROTX-']) 
        stringindexreplacement('dc:Ge/Coll2steel/RotY', filecontent , change_dictionary['-Coll2steelROTY-']) 
        stringindexreplacement('dc:Ge/Coll2steel/RotZ', filecontent , change_dictionary['-Coll2steelROTZ-']) 
        stringindexreplacement('dc:Ge/Coll2steel/LZ', filecontent , change_dictionary['-Coll2steelLZ-']) 
        stringindexreplacement('dc:Ge/Coll2steel/LY', filecontent , change_dictionary['-Coll2steelLY-']) 
        stringindexreplacement('dc:Ge/Coll2steel/LX', filecontent , change_dictionary['-Coll2steelLX-']) 
        stringindexreplacement('dc:Ge/Coll2steel/LTX', filecontent , change_dictionary['-Coll2steelLTX-']) 

        stringindexreplacement('s:Ge/Coll3steel/Type', filecontent , '\"'+change_dictionary['-Coll3steelTY-']+'\"') 
        stringindexreplacement('s:Ge/Coll3steel/Material', filecontent , '\"'+change_dictionary['-Coll3steelMAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll3steel/TransX', filecontent , 'Ge/Coll3/TransX - '+ change_dictionary['-Coll3steelTRANSX-']) 
        stringindexreplacement('dc:Ge/Coll3steel/TransY', filecontent , change_dictionary['-Coll3steelTRANSY-']) 
        stringindexreplacement('dc:Ge/Coll3steel/TransZ', filecontent , change_dictionary['-Coll3steelTRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll3steel/RotX', filecontent , change_dictionary['-Coll3steelROTX-']) 
        stringindexreplacement('dc:Ge/Coll3steel/RotY', filecontent , change_dictionary['-Coll3steelROTY-']) 
        stringindexreplacement('dc:Ge/Coll3steel/RotZ', filecontent , change_dictionary['-Coll3steelROTZ-']) 
        stringindexreplacement('dc:Ge/Coll3steel/LZ', filecontent , change_dictionary['-Coll3steelLZ-']) 
        stringindexreplacement('dc:Ge/Coll3steel/LY', filecontent , change_dictionary['-Coll3steelLY-']) 
        stringindexreplacement('dc:Ge/Coll3steel/LX', filecontent , change_dictionary['-Coll3steelLX-']) 
        stringindexreplacement('dc:Ge/Coll3steel/LTX', filecontent , change_dictionary['-Coll3steelLTX-']) 

        stringindexreplacement('s:Ge/Coll4steel/Type', filecontent , '\"'+change_dictionary['-Coll4steelTY-']+'\"') 
        stringindexreplacement('s:Ge/Coll4steel/Material', filecontent , '\"'+change_dictionary['-Coll4steelMAT-']+'\"') 
        stringindexreplacement('dc:Ge/Coll4steel/TransX', filecontent , 'Ge/Coll4/TransX + ' + change_dictionary['-Coll4steelTRANSX-']) 
        stringindexreplacement('dc:Ge/Coll4steel/TransY', filecontent , change_dictionary['-Coll4steelTRANSY-']) 
        stringindexreplacement('dc:Ge/Coll4steel/TransZ', filecontent , change_dictionary['-Coll4steelTRANSZ-']) 
        stringindexreplacement('dc:Ge/Coll4steel/RotX', filecontent , change_dictionary['-Coll4steelROTX-']) 
        stringindexreplacement('dc:Ge/Coll4steel/RotY', filecontent , change_dictionary['-Coll4steelROTY-']) 
        stringindexreplacement('dc:Ge/Coll4steel/RotZ', filecontent , change_dictionary['-Coll4steelROTZ-']) 
        stringindexreplacement('dc:Ge/Coll4steel/LZ', filecontent , change_dictionary['-Coll4steelLZ-']) 
        stringindexreplacement('dc:Ge/Coll4steel/LY', filecontent , change_dictionary['-Coll4steelLY-']) 
        stringindexreplacement('dc:Ge/Coll4steel/LX', filecontent , change_dictionary['-Coll4steelLX-']) 
        stringindexreplacement('dc:Ge/Coll4steel/LTX', filecontent , change_dictionary['-Coll4steelLTX-']) 


        stringindexreplacement('s:Ge/DemoFlat/Type', filecontent , '\"'+change_dictionary['-DEMOFLATTY-']+'\"') 
        stringindexreplacement('s:Ge/DemoFlat/Material', filecontent , '\"'+change_dictionary['-DEMOFLATMAT-']+'\"') 
        stringindexreplacement('d:Ge/DemoFlat/HLX', filecontent , change_dictionary['-DEMOFLATHLX-']) 
        stringindexreplacement('d:Ge/DemoFlat/HLY', filecontent , change_dictionary['-DEMOFLATHLY-']) 
        stringindexreplacement('d:Ge/DemoFlat/HLZ', filecontent , change_dictionary['-DEMOFLATHLZ-']) 
        stringindexreplacement('d:Ge/DemoFlat/TransX', filecontent , change_dictionary['-DEMOFLATTRANSX-']) 
        stringindexreplacement('d:Ge/DemoFlat/TransY', filecontent , change_dictionary['-DEMOFLATTRANSY-']) 
        stringindexreplacement('d:Ge/DemoFlat/TransZ', filecontent , change_dictionary['-DEMOFLATTRANSZ-']) 
        stringindexreplacement('d:Ge/DemoFlat/RotX', filecontent , change_dictionary['-DEMOFLATROTX-']) 
        stringindexreplacement('d:Ge/DemoFlat/RotY', filecontent , change_dictionary['-DEMOFLATROTY-']) 
        stringindexreplacement('d:Ge/DemoFlat/RotZ', filecontent , change_dictionary['-DEMOFLATROTZ-']) 

        stringindexreplacement('s:Ge/DemoRTrap/Type', filecontent , '\"'+change_dictionary['-DEMORTRAPTY-']+'\"') 
        stringindexreplacement('s:Ge/DemoRTrap/Material', filecontent , '\"'+change_dictionary['-DEMORTRAPMAT-']+'\"') 
        stringindexreplacement('d:Ge/DemoRTrap/TransX', filecontent , change_dictionary['-DEMORTRAPTRANSX-']) 
        stringindexreplacement('d:Ge/DemoRTrap/TransY', filecontent , change_dictionary['-DEMORTRAPTRANSY-'] + ' - Ge/DemoFlat/HLY') 
        stringindexreplacement('d:Ge/DemoRTrap/TransZ', filecontent , change_dictionary['-DEMORTRAPTRANSZ-']) 
        stringindexreplacement('d:Ge/DemoRTrap/RotX', filecontent , change_dictionary['-DEMORTRAPROTX-']) 
        stringindexreplacement('d:Ge/DemoRTrap/RotY', filecontent , change_dictionary['-DEMORTRAPROTY-']) 
        stringindexreplacement('d:Ge/DemoRTrap/RotZ', filecontent , change_dictionary['-DEMORTRAPROTZ-']) 
        stringindexreplacement('dc:Ge/DemoRTrap/LZ', filecontent , change_dictionary['-DEMORTRAPLZ-']) 
        stringindexreplacement('dc:Ge/DemoRTrap/LY', filecontent , change_dictionary['-DEMORTRAPLY-']) 
        stringindexreplacement('dc:Ge/DemoRTrap/LX', filecontent , change_dictionary['-DEMORTRAPLX-']) 
        stringindexreplacement('dc:Ge/DemoRTrap/LTX', filecontent , change_dictionary['-DEMORTRAPLTX-']) 

        stringindexreplacement('s:Ge/DemoLTrap/Type', filecontent , '\"'+change_dictionary['-DEMOLTRAPTY-']+'\"') 
        stringindexreplacement('s:Ge/DemoLTrap/Material', filecontent , '\"'+change_dictionary['-DEMOLTRAPMAT-']+'\"') 
        stringindexreplacement('d:Ge/DemoLTrap/TransX', filecontent , change_dictionary['-DEMOLTRAPTRANSX-']) 
        stringindexreplacement('d:Ge/DemoLTrap/TransY', filecontent , change_dictionary['-DEMOLTRAPTRANSY-'] + ' + Ge/DemoFlat/HLY') 
        stringindexreplacement('d:Ge/DemoLTrap/TransZ', filecontent , change_dictionary['-DEMOLTRAPTRANSZ-']) 
        stringindexreplacement('d:Ge/DemoLTrap/RotX', filecontent , change_dictionary['-DEMOLTRAPROTX-']) 
        stringindexreplacement('d:Ge/DemoLTrap/RotY', filecontent , change_dictionary['-DEMOLTRAPROTY-']) 
        stringindexreplacement('d:Ge/DemoLTrap/RotZ', filecontent , change_dictionary['-DEMOLTRAPROTZ-']) 
        stringindexreplacement('d:Ge/DemoLTrap/LZ', filecontent , change_dictionary['-DEMOLTRAPLZ-']) 
        stringindexreplacement('dc:Ge/DemoLTrap/LY', filecontent , change_dictionary['-DEMOLTRAPLY-']) 
        stringindexreplacement('dc:Ge/DemoLTrap/LX', filecontent , change_dictionary['-DEMOLTRAPLX-']) 
        stringindexreplacement('d:Ge/DemoLTrap/LTX', filecontent , change_dictionary['-DEMOLTRAPLTX-']) 

        stringindexreplacement('s:Ge/topsidebox/Type', filecontent , '\"'+change_dictionary['-TSBTY-']+'\"') 
        stringindexreplacement('s:Ge/topsidebox/Material', filecontent , '\"'+change_dictionary['-TSBMAT-']+'\"') 
        stringindexreplacement('d:Ge/topsidebox/HLX', filecontent , change_dictionary['-TSBHLX-']) 
        stringindexreplacement('d:Ge/topsidebox/HLY', filecontent , change_dictionary['-TSBHLY-']) 
        stringindexreplacement('d:Ge/topsidebox/HLZ', filecontent , change_dictionary['-TSBHLZ-']) 
        stringindexreplacement('d:Ge/topsidebox/TransX', filecontent , change_dictionary['-TSBTRANSX-']) 
        stringindexreplacement('d:Ge/topsidebox/TransY', filecontent , change_dictionary['-TSBTRANSY-'] + ' + Ge/DemoLTrap/TransY') 
        stringindexreplacement('dc:Ge/topsidebox/TransZ', filecontent , change_dictionary['-TSBTRANSZ-']) 
        stringindexreplacement('d:Ge/topsidebox/RotX', filecontent , change_dictionary['-TSBROTX-']) 
        stringindexreplacement('d:Ge/topsidebox/RotY', filecontent , change_dictionary['-TSBROTY-']) 
        stringindexreplacement('d:Ge/topsidebox/RotZ', filecontent , change_dictionary['-TSBROTZ-']) 

        stringindexreplacement('s:Ge/bottomsidebox/Type', filecontent , '\"'+change_dictionary['-BSBTY-']+'\"') 
        stringindexreplacement('s:Ge/bottomsidebox/Material', filecontent , '\"'+change_dictionary['-BSBMAT-']+'\"') 
        stringindexreplacement('d:Ge/bottomsidebox/HLX', filecontent , change_dictionary['-BSBHLX-']) 
        stringindexreplacement('d:Ge/bottomsidebox/HLY', filecontent , change_dictionary['-BSBHLY-']) 
        stringindexreplacement('d:Ge/bottomsidebox/HLZ', filecontent , change_dictionary['-BSBHLZ-']) 
        stringindexreplacement('d:Ge/bottomsidebox/TransX', filecontent , change_dictionary['-BSBTRANSX-']) 
        stringindexreplacement('d:Ge/bottomsidebox/TransY', filecontent , change_dictionary['-BSBTRANSY-'] + ' + Ge/DemoRTrap/TransY') 
        stringindexreplacement('dc:Ge/bottomsidebox/TransZ', filecontent , change_dictionary['-BSBTRANSZ-']) 
        stringindexreplacement('dc:Ge/bottomsidebox/RotX', filecontent , change_dictionary['-BSBROTX-']) 
        stringindexreplacement('d:Ge/bottomsidebox/RotY', filecontent , change_dictionary['-BSBROTY-']) 
        stringindexreplacement('d:Ge/bottomsidebox/RotZ', filecontent , change_dictionary['-BSBROTZ-']) 

        stringindexreplacement('# s:Ge/couch/Type', filecontent , '\"'+change_dictionary['-COUCHTY-']+'\"') 
        stringindexreplacement('# s:Ge/couch/Material', filecontent , '\"'+change_dictionary['-COUCHMAT-']+'\"') 
        stringindexreplacement('# d:Ge/couch/HLX', filecontent , change_dictionary['-COUCHHLX-']) 
        stringindexreplacement('# d:Ge/couch/HLY', filecontent , change_dictionary['-COUCHHLY-']) 
        stringindexreplacement('# d:Ge/couch/HLZ', filecontent , change_dictionary['-COUCHHLZ-']) 
        stringindexreplacement('# d:Ge/couch/TransX', filecontent , change_dictionary['-COUCHTRANSX-']) 
        stringindexreplacement('# d:Ge/couch/TransY', filecontent , change_dictionary['-COUCHTRANSY-']) 
        stringindexreplacement('# d:Ge/couch/TransZ', filecontent , change_dictionary['-COUCHTRANSZ-']) 


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
            ## Edits
            stringindexreplacement('i:Tf/NumberOfSequentialTimes', filecontent , change_dictionary['-TIMESEQ-']) 
            stringindexreplacement('i:Tf/Verbosity', filecontent , change_dictionary['-TIMEVERBO-']) 
            stringindexreplacement('d:Tf/TimelineEnd', filecontent , change_dictionary['-TIMELINEEND-']) 
            stringindexreplacement('s:Tf/Rotate/Function', filecontent , '\"' + change_dictionary['-TIMEROTFUNC-'] +'\"') 
            stringindexreplacement('d:Tf/Rotate/Rate', filecontent , change_dictionary['-TIMEROTRATE-']) 
            stringindexreplacement('d:Tf/Rotate/StartValue', filecontent , change_dictionary['-TIMEROTSTART-']) 
            stringindexreplacement('i:Ts/ShowHistoryCountAtInterval', filecontent , change_dictionary['-TIMEHISTINT-']) 

        if change_dictionary['-FAN-'] == 'Half fan':
            ### First remove the unwanted other option, then edit the correct ones
            stringindexreplacement('#fullfanrotationrate', filecontent , )
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
        
        pass


    if filetype == 'foo.py':
        if toggle_dictionary['ChamberPlugCentre'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass

        if toggle_dictionary['ChamberPlugTop'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass

        if toggle_dictionary['ChamberPlugBottom'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['ChamberPlugLeft'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['ChamberPlugRight'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['ChamberPlugDose_tle'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['ChamberPlugDose_dtm'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['ChamberPlugDose_dtw'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['CollimatorsVertical'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['CollimatorsHorizontal'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['TitaniumFilter'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['BowtieFilter'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['Coll1'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['Coll2'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['Coll3'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['Coll4'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['DemoFlat'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['DemoRTrap'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['DemoLTrap'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['topsidebox'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['bottomsidebox'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['couch'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass
        if toggle_dictionary['Graphics'] == 1: 
            #make edits 
            pass
        else:
            #comment 
            pass

    with open(TargetFile, 'w') as Write_file:
        Write_file.writelines( filecontent )

    pass 

if __name__== '__main__':
    editor()