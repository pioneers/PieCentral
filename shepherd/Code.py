import random
from Utils import *

codes = []
solutions = []
code_solution = {}
code_effect = {}
effect_list = list(EFFECTS.ALL_EFFECTS)

def generate_code(code_list):
    ##: TODO
    pass

def decode(code):
    ##: TODO
    pass

def assign_code_solution():
    '''
    Generate 16 codes and create a code_solution dictionary
    '''
    codes.clear()
    solutions.clear()
    for i in range(16):
        # pylint: disable=assignment-from-no-return
        new_code = generate_code(codes)
        codes.append(new_code)
    for code in codes:
        solutions.append(decode(code))
    for i in range(16):
        code_solution[codes[i]] = solutions[i]
    return code_solution

def assign_code_effect():
    '''
    Assign each code to a random effect
    '''
    for i in range(16):
        code_effect[codes[i]] = random.choice(effect_list)
    return code_effect
