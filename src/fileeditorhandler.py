# from topas_gui import stringindexreplacement
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

def editor(change_dictionary: dict, toggle_dictionary: dict, targetfile: str, filetype:str):
    '''
    Main function that handles the editting and changing of parameter files. 
    Uses the values and selectcomponent dictionary to reference for keys and value to replace. 

    :filetype str: either .bat file or a generate_allproc.py file 
    '''
    if filetype == 'foo.bat':
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

    

    pass 

if __name__== '__main__':
    editor()