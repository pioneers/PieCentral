import random
import math
import numpy as np
from Utils import *

codes = []
solutions = []
code_solution = {}
levelOneQuestions = [convert_time, eta, wacky_numbers, num_increases]
levelTwoQuestions = [wheresAramdillo, pie_cals_triangle, road_trip, convertToRoman]

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


def decode(code, seed):
    '''
    Call all functions.
    Staff solution should be double checked and written.
    Level tells us the difficulty of the code challenge,
    which should be level 1 or 2.
    Code is a list of functions that should be called.
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

def answers(seed, level):
    """
    Returns answers in a list based on a particular seed.
    """
    results = []



"""
The following functions below are coding challenge questions.
Used Spring 2020. These functions are hardcoded into this file.
Please change the following functions and corresponding elements in this file
if you're using new functions. Outside functions should never see the functions
being used in this file.
"""

#Easy Solutions
​
#solution Question 1
def convert_time(time):
    minutes, hours = time%100, time//100
    if hours > 12:
        hours -=12
    return [hours, minutes]
​
​
​
#solution Question 2
from math import *
def eta(pos):
    x, y = pos[0], pos[1]
    distance = sqrt((x - 5)** 2+ (y - 14)**2)
    return int(distance//3)
​
#solution Question 3
def wacky_numbers(x):
    total_steps = 0
    for i in range(0,20):
        if x % 2 == 0:
            x = x//2
        elif x % 2 == 1:
            x = x*5 + 5
        total_steps += 1
    return x
​
#solution Question 4
def num_increases(n):
    n, last, total = n//10, n%10, 0
    while n:
        if last > n%10:
            total += 1
        n, last = n//10, n%10
    return total
​
#HardProblem
​
​
#Question 1
​
def wheresArmadillo(animals, weights = animal_weights ):
    """
    :type animal: list containing the names of the animals presorted by weight
    :type weights: Dictionary containing the weights of each animal:
    :output: the sum of the number of passes through the list and the index of the armadillo
    """
    upperBound=len(animals)
    lowerBound=0
    passes=1
    while checkAnimal(animals[lowerBound+(upperBound-lowerBound)//2],weights)!= 0 :
        if checkAnimal(animals[lowerBound+(upperBound-lowerBound)//2],weights)==1:
            lowerBound= (upperBound+lowerBound)//2+1
            passes +=1
        elif checkAnimal(animals[lowerBound+(upperBound-lowerBound)//2],weights)==-1:
            upperBound=(upperBound+lowerBound)//2-1
            passes +=1
    return passes + (lowerBound+(upperBound-lowerBound))
​
#Question 2
def pie_cals_triangle(x):
    start = [1,x,1]
    temp = [1]
    s = x
    for x in range(0,4):
        for x in range(0, len(start) - 1):
            temp.append(start[x]*start[x+1])
        temp.append(1)
        s += (sum(temp) - 2)
        start = temp
        temp=[1]
    return s
​
​
#Question 3
def road_trip(d):
    if d <= 0:
        #print("we there")
        return 0
    elif d == 1:
        return 1
    elif d % 5 == 0:
        return 1 + road_trip(d+3)
    else:
        return 1 + road_trip(d-2)
​
​
#Question 4
def convertToRoman(self, num):
    conversionDict = [[1, 'I'],
                      [4, 'IV'],
                      [5, 'V'],
                      [9, 'IX'],
                      [10,'X'],
                      [40,'XL'],
                      [50,'L'],
                      [90,'XC'],
                      [100,'C'],
                      [400,'CD'],
                      [500,'D'],
                      [900,'CM'],
                      [1000, 'M']]
    roman = ""
    index = len(conversionDict) - 1
    while index >= 0:
    if num >= conversionDict[index][0]:
        roman += conversionDict[index][1]
        num -= conversionDict[index][0]
    else:
        index -= 1
    return roman
​
​
​
​
​
def convertStringToList(animals):
	"""
	DO NOT TOUCH THIS FUNCTION
	:type animals: String representing a list of animals
	:output list of the string animal converted to a list split by ";"
	"""
	return animals.split(";")
​
​
def checkAnimal(animal,weights):
    """
    DO NOT TOUCH THIS FUNCTION
    :type animal: String representing the name of the animal
    :type weights: Dictionary containing the weights of each animal
    :output: a 1 if the armadillo is heavier than the input animal,
             a -1 if the armadillo is lighter than the input animal,
             a 0 if the armadillo is the input animal.
    """
    animalWeight=weights.get(animal)
    armadilloWeight=weights.get("armadillo")
    if animalWeight>armadilloWeight:
        return -1
    elif animalWeight<armadilloWeight:
        return 1
    elif animalWeight==armadilloWeight:
        return 0


animal_weights={"mouse":0.01, "frog":0.1, "dove":1, "chicken":3, "cat":5, "koala":10, "dog":15, "turkey":20, "armadillo":27, "alligator":50, "leopard":100,
				"wolf":150, "pig":200, "deer":250, "lion":300,"cow":310, "buffalo":400, "elephant":500, "dinosaur":1000}
​
animals_list = ["mouse", "frog", "dove", "chicken", "cat", "koala", "dog", "turkey", "armadillo", "alligator", "leopard", "wolf", "pig", "deer", "lion", "cow", "buffalo", "elephant", "dinosaur"]
