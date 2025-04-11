import os
from datetime import datetime

def is_valid_date(year, month, day):
    try:
        datetime(year=int(year), month=int(month), day=int(day))
        return True
    except ValueError:
        return False

def calculate_check_digit(first_seventeen):
    coefficients = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_map = {'0':'1','1':'0','2':'X','3':'9','4':'8','5':'7','6':'6','7':'5','8':'4','9':'3','10':'2'}
    total = sum(int(c) * coeff for c, coeff in zip(first_seventeen, coefficients))
    return check_map[str(total % 11)]

def all_possible_sfz(first_fourteen, sex=0):
    # Validate input
    if len(first_fourteen) != 14 or not first_fourteen.isdigit():
        raise ValueError("Invalid first 14 digits")
    
    # Validate date (positions 7-14)
    yyyy = first_fourteen[6:10]
    mm = first_fourteen[10:12]
    dd = first_fourteen[12:14]
    if not is_valid_date(yyyy, mm, dd):
        raise ValueError("Invalid date in first 14 digits")

    # Generate possible sequence codes
    possible = []
    for seq_first_two in [f"{i:02d}" for i in range(100)]:
        for seq_third in range(10):
            if (sex == 1 and seq_third % 2 == 1) or (sex == 0 and seq_third % 2 == 0):
                sequence = f"{seq_first_two}{seq_third}"
                first_seventeen = first_fourteen + sequence
                check_digit = calculate_check_digit(first_seventeen)
                possible.append(f"{first_seventeen}{check_digit}")

    # Write to file
    filename = f"{first_fourteen}xxxx.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(possible))
    
    print(f"Generated {len(possible)} ID numbers in {filename}")
    return filename


all_possible_sfz('SFSSXXYYYYMMDD', sex=0)  # sex=0 女，sex=1 男