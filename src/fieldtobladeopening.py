from typing import List


def fieldtobladeopening(field_size_list: List[str]) -> List[str]:
    """
    Input is to be given as a list of 4 strings of field size
    [Field_x1, Field_x2, Field_y1, Field_y2]
    Build in string strip to separate float value for calculation before merging the unit and float back together
    blade 2s have to be multipled by -1 to get a mirrored (negative) coor position
    """

    # yfieldopening = lambda blade : 17.3699885452463 * blade - 90.2972966781214
    # xfieldopening = lambda blade : 13.9904761904762 * blade - 72.3986904761904
    # Inverse it
    def ybladeopening(field: float) -> float:
        return (field + 90.2972966781214) / 17.3699885452463

    def xbladeopening(field: float) -> float:
        return (field + 72.3986904761904) / 13.9904761904762

    blade_position_list: List[str] = []
    count = 0
    for field in field_size_list:
        numbers: float = 0.0
        units: str = ""
        found_number = False
        for character in field.split():
            try:
                numbers = float(character)
                found_number = True
            except ValueError:
                units = character
        if not found_number:
            raise TypeError(
                "Field size must contain a numeric value, e.g. '14 cm'. Got: "
                + repr(field)
            )
        if count == 0:
            blade_position_float = xbladeopening(numbers)
        elif count == 1:
            blade_position_float = xbladeopening(numbers) * -1
        elif count == 2:
            blade_position_float = ybladeopening(numbers)
        elif count == 3:
            blade_position_float = ybladeopening(numbers) * -1
        blade_position_string = str(blade_position_float) + " " + units
        blade_position_list.append(blade_position_string)
        count += 1

    return blade_position_list


if __name__ == "__main__":
    print(fieldtobladeopening(["2 cm", "2 cm", "16 cm", "16 cm"]))
    print(fieldtobladeopening(["10 cm", "10 cm", "10 cm", "10 cm"]))
