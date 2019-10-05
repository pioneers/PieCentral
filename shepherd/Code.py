import random
import math
import numpy as np
from Utils import *

codes = []
solutions = []
code_solution = {}
code_effect = {}

def generate_code(code_list):
    '''
    Take a list of codes that return a new random code
    '''
    temp = np.random.permutation(10)
    num = 0
    for a in temp:
        num = num * 10 + a
    while num in code_list:
        temp = np.random.permutation(10)
        num = 0
        for a in temp:
            temp = temp * 10 + a
    return num


def decode(code):
    '''
    Call all functions
    '''
    return

def assign_code_solution():
    '''
    Generate 16 codes and create a code_solution dictionary
    '''
    codes.clear()
    solutions.clear()
    code_solution.clear()
    code_effect.clear()
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
        code_effect[codes[i]] = (EFFECTS.TWIST if random.random() <
                                 CONSTANTS.TWIST_CHANCE else
                                 EFFECTS.SPOILED_CANDY)
    return code_effect