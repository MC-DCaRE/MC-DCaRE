#unreferenced function added in case it is required in the future to calculate more blade openings values
def fieldtobladeopening(field_size_list):
    '''
    Input is to be given as a list of 4 strings of field size 
    [Field_x1, Field_x2, Field_y1, Field_y2]
    Build in string strip to separate float value for calculation before merging the unit and float back together
    blade 2s have to be multipled by -1 to get a mirrored (negative) coor position
    '''
    # yfieldopening = lambda blade : 17.3699885452463 * blade - 90.2972966781214
    # xfieldopening = lambda blade : 13.9904761904762 * blade - 72.3986904761904
    # Inverse it 
    ybladeopening = lambda field : (field + 90.2972966781214)/17.3699885452463
    xbladeopening = lambda field : (field + 72.3986904761904)/13.9904761904762 

    blade_position_list = []
    count= 0
    for field in field_size_list:
        numbers = []
        units = []
        for character in field.split():
            try:
                numbers = float(character)
            except ValueError:
                units = character
        if count == 0: 
            blade_position_float = xbladeopening(numbers)
        elif count == 1:
            blade_position_float = xbladeopening(numbers) *-1
        elif count == 2:
            blade_position_float = ybladeopening(numbers)
        elif count == 3:
            blade_position_float = ybladeopening(numbers) *-1
        blade_position_string = str(blade_position_float) + " " +units
        blade_position_list.append(blade_position_string)
        count+=1
        
    return blade_position_list

if __name__ == '__main__':
    print(fieldtobladeopening(['2 cm', '2 cm' ,'16 cm', '16 cm']) )
    print(fieldtobladeopening(['10 cm', '10 cm' ,'10 cm', '10 cm']) )
