def _match_letter_to_number(s: str):
    return match_dict(s, matcher = {
        'O': '0',
        'I': '1',
        'Z': '2',
        'S': '5',
        'G': '6',
        'B': '8'
    })

def _match_number_to_letter(s: str):
    return match_dict(s, {
        '0': 'O',
        '1': 'I',
        '2': 'Z',
        '5': 'S',
        '6': 'G',
        '8': 'B'
    })

def match_dict(s: str, matcher: dict[str, str]):
    out = ""
    for c in s:
        if (matcher.get(c) != None): out += matcher[c]
        else: out += c
    return out

def try_format_booth_number(s: str, formatter: str):
    """
    Parameters:
    s (str): The base string.
    formatter (str): The string used to format the input s. # for numbers, $ for letters. Any other characters are treated as is.
    Returns:
    str: The formatted booth number. If len(s) and len(formatter) are not the same, returns s.
    """

    if (len(s) != len(formatter)):
        print(f"The length of inputted booth number and formatter are not the same. ({len(s)} and {len(formatter)})")
        return s
    
    out = ""
    for i, c in enumerate(formatter):
        match c:
            case '#': out += _match_letter_to_number(s[i])
            case '$': out += _match_number_to_letter(s[i])
            case _: out += c
    return out

def validate_booth_number(s: str, format: str):
    """
    Parameters:
    s (str): The booth number.
    format (str): The validator. # for numbers, $ for letters. Any other characters are treated as is.
    Returns:
    bool: Whether or not s matches format. If the length are not the same, always return False.
    """

    if len(s) != len(format): return False

    for i, c in enumerate(format):
        match c:
            case '#':
                if not s[i].isdigit(): return False
            case '$':
                if not s[i].isalpha(): return False
            case _:
                if s[i] != c: return False
    
    return True