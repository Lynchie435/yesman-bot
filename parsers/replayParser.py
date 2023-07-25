def parse_first_json(file: bytes) -> dict[str, str]:
    rply_idx = file.find(b"rply")
    json_start_idx = rply_idx + 4 + 8 + 4

    first_bracket = 0
    bracket_indentation = 0
    for idx, c in enumerate(file[json_start_idx:]):
        if c == ord("{"):
            if bracket_indentation == 0:
                first_bracket = idx + json_start_idx
            bracket_indentation += 1
        elif c == ord("}"):
            bracket_indentation -= 1
            if bracket_indentation == 0:
                return eval(file[first_bracket: idx + json_start_idx + 1])
    raise Exception("Can't find game json")


def parse_last_json(file: bytes) -> dict[str, str]:
    rev_file = file[::-1]
    last_bracket = 0
    bracket_indentation = 0

    for idx, c in enumerate(rev_file):
        if c == ord("}"):
            if bracket_indentation == 0:
                last_bracket = idx
            bracket_indentation += 1
        elif c == ord("{"):
            bracket_indentation -= 1
            if bracket_indentation == 0:
                return eval(rev_file[last_bracket: idx + 1][::-1])

    raise Exception("Can't find result json")


def parse_file(file: bytes) -> tuple[dict[str, str], dict[str, str]]:
    first_json = parse_first_json(file)
    second_json = parse_last_json(file)

    return first_json, second_json