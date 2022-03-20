SAME_LEN_REQ_OUTPUT: str = "guess must be the same length as answer"

def char_is_green(guess: str, letter_i: int, answer: str) -> bool:
    """check that the guess letter matches answer's letter at that index"""
    return guess[letter_i] == answer[letter_i]

def char_is_yellow(guess: str, letter_i: int, answer: str) -> bool: 
    """check that the guess letter at that index was misplaced"""
    if len(guess) != len(answer):
        raise ValueError(SAME_LEN_REQ_OUTPUT)
    
    # check that the letter is actually in answer
    if not guess[letter_i] in answer:
        return False
    # letter in both guess and answer, but has duplicates in guess and potential duplicates in answer
    elif guess.count(guess[letter_i]) > 1:
        return is_viable_duplicate(guess, letter_i, answer)
    # letter at i is both in guess and answer, check that it's not green
    else:
        return not char_is_green(guess, letter_i, answer)

def is_viable_duplicate(guess: str, letter_i: int, answer: str) -> bool:
    """According to the colour, check to see if the duplicate letter is viable"""

    duplicate_letter: str = guess[letter_i]
    n_greens: int = n_greens_with_letter(guess, duplicate_letter, answer)
    n_possible_yellows: int = answer.count(duplicate_letter) - n_greens
    i: int = 0
    while n_possible_yellows > 0 and i <= letter_i:
        if guess[i] == duplicate_letter and duplicate_letter != answer[i]:
            n_possible_yellows -= 1
            if i == letter_i:
                return True
        i += 1
    return False

def char_is_grey(guess:str, letter_i: int, answer: str) -> bool:
    """Check that guess letter at that index is nonexistent in the answer.
       Should the guess letter exist, verify that it isn't a duplicate dud"""
    # letter not in answer
    if guess[letter_i] not in answer:
        return True
    # letter in answer but may be an irrelevant duplicate
    elif guess.count(guess[letter_i]) > 1:
        return not is_viable_duplicate(guess, letter_i, answer)
    else:
    # single letter is in answer
        return False

def n_greens_with_letter(guess: str, duplicate_letter: str, answer: str) -> int:
    """count the number of correctly positioned occurences for a particular letter"""
    if len(guess) != len(answer):
        raise ValueError(SAME_LEN_REQ_OUTPUT)
    
    count: int = 0
    for i in range(len(guess)):
        if guess[i] == duplicate_letter and answer[i] == duplicate_letter:
            count += 1
    return count


    