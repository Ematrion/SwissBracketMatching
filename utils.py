def flat_match(elems: list[int]) -> list:
    # [1,2,3,4,5,6,7,8] -> [1,8,2,7,3,6,4,5]
    l = len(elems)
    return [x for i in range(0, l//2) for x in (elems[i], elems[l-(i+1)])]

def cross_match(elems: list[int]) -> list:
    # [1,2,3,4,5,6,7,8] -> [1,7,2,8,3,5,4,6]
    l = len(elems)
    return [x for i in range(0, l//2) for x in (elems[i], elems[l-i] if i%2==1 else elems[l-(i+2)])]

def speed_up(elems: list[int]) -> list:
    # [1,2,3,4,5,6,7,8] -> [1,5,2,6,3,7,4,8]
    l = len(elems)
    return [x for i in range(0, l//2) for x in (elems[i], elems[l//2 + i])]

def swiss_bracket_n6(players: list[int]) -> list[list]:
    '''
    https://github.com/ValveSoftware/counter-strike_rules_and_regs/blob/main/major-supplemental-rulebook.md
    Look for the 'Priority' table in section 'Swiss Bracket'
    '''
    matchings = [
        [players[0], players[5], players[1], players[4], players[2], players[3]],
        [players[0], players[5], players[1], players[3], players[2], players[4]],
        [players[0], players[4], players[1], players[5], players[2], players[3]],
        [players[0], players[4], players[1], players[3], players[2], players[5]],
        [players[0], players[3], players[1], players[5], players[2], players[4]],

        [players[0], players[3], players[1], players[4], players[2], players[5]],
        [players[0], players[5], players[1], players[2], players[3], players[4]],
        [players[0], players[4], players[1], players[2], players[3], players[5]],
        [players[0], players[2], players[1], players[5], players[3], players[4]],
        [players[0], players[2], players[1], players[4], players[3], players[5]],

        [players[0], players[3], players[1], players[2], players[4], players[5]],
        [players[0], players[2], players[1], players[3], players[4], players[5]],
        [players[0], players[1], players[2], players[5], players[3], players[4]],
        [players[0], players[1], players[2], players[4], players[3], players[5]],
        [players[0], players[1], players[2], players[3], players[4], players[5]],
    ]
    return matchings

