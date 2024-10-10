#unreferenced function added in case it is required in the future to calculate more blade openings values
def fieldtobladeopening(change_dictionary):
    yfieldopening = lambda blade : 17.3699885452463 * blade - 90.2972966781214
    xfieldopening = lambda blade : 13.9904761904762 * blade - 72.3986904761904

    # Inverse it 
    ybladeopening = lambda field : (field + 90.2972966781214)/17.3699885452463
    xbladeopening = lambda field : (field + 72.3986904761904)/13.9904761904762 

    x1_field = change_dictionary['-FIELD_X1-']
    x2_field = change_dictionary['-FIELD_X2-']
    y1_field = change_dictionary['-FIELD_Y1-']
    y2_field = change_dictionary['-FIELD_Y2-']

    # Was to be implemented, cancelled as not required
    # stringing = 'take the value of the field opening with units, eg -0.5 cm and strips it to -0.5 and cm'
    # l = []
    # for t in stringing.split():
    #     try:
    #         l.append(float(t))
    #     except ValueError:
    #         pass

    # strip for values and keep units 
    # strip negative 
    # calculate 
    # add negtaive and unit 
    x1_blade = xbladeopening(x1_field)
    x2_blade = xbladeopening(x2_field)
    y1_blade = ybladeopening(y1_field)
    y2_blade = ybladeopening(y2_field)
    openings = [x1_blade,x2_blade, y1_blade, y2_blade]
    return openings

if __name__ == '__main__':
    testing_dictionary = {'-BLADE_X1-': 13.2, '-BLADE_X2-': 13.2, '-BLADE_Y1-': 9.9, '-BLADE_Y2-': 9.9}
    print(fieldtobladeopening(testing_dictionary) )
    # foo = '5 cm'
    # foo1 = '-5 cm'
    # foo3 = ''
    # l = []
    # unit = []
    # for t in foo1.split():
    #     try:
    #         l.append(float(t))
    #         print(l)
    #     except ValueError:
    #         unit.append(t)
    #         print(unit)
    # print(l)
    # print(unit)