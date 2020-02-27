import random
import math
import numpy as np
from Utils import *

codes = []
solutions = []
code_solution = {}

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


def decode(code, level):
    '''
    Call all functions.
    Staff solution should be double checked and written.
    Level tells us the difficulty of the code challenge,
    which should be level 1 or 2.
    '''
    return

def assign_code_solution():
    '''
    Generate 16 codes and create a code_solution dictionary
    What is codes?
    solutions is their solutions?
    code_solution is our solution?
    Write.
    First, game initiates the coding challenge, and the challenge comes as lcm header,
    doesn't matter where, what we'll need to do is at the begnning of the game is have generate_code
    a list of seeds and we're gonna get the next seed and take this seed, and send it to  master robot.
    This call will go to runtime. Then we have to start a timer, which sends a lcm timer back to sheperd.
    Once this tmer has finished, we will pick this lcm message and ask runtime for it,
    then we'll display answer on the tablet and check if it was right. Anf it it's correct,
    we'll perform some ex. actions.

    When we send seed, we have to interanlly wait on a timer. Then, we go back to robot, and ask for answer.
    '''
    codes.clear()
    solutions.clear()
    code_solution.clear()
    for i in range(16):
        # pylint: disable=assignment-from-no-return
        new_code = generate_code(codes)
        codes.append(new_code)
    for code in codes:
        solutions.append(decode(code, """LEVEL"""))
    for i in range(16):
        code_solution[codes[i]] = solutions[i]
    return code_solution
