import random
from Utils import *

MASTER_RECIPES = [RECIPE_PROBABILITIES.EASY_RECIPE, RECIPE_PROBABILITIES.MEDIUM_RECIPE, \
    RECIPE_PROBABILITIES.HARD_RECIPE, RECIPE_PROBABILITIES.VERY_HARD_RECIPE]
master_recipes_names = []
master_recipes = []
gold_recipes = []
blue_recipes = []
gold_recipes_completed = 0
blue_recipes_completed = 0

###### "Autograders" #####
def generate_recipes_Autograder():
    generate_recipes()
    print(master_recipes_names)
    print(master_recipes)

def printAll():
    print(master_recipes_names)
    print(master_recipes)
    print("Blue:", blue_recipes)
    print("Gold:", gold_recipes)
##########################

def generate_recipes():
    '''
    reset recipe list with 4 newly selected recipes
    both teams should have the same recipes
    '''
    gold_recipes.clear()
    blue_recipes.clear()
    master_recipes.clear()
    master_recipes_names.clear()
    recipe_probabilities = RECIPE_PROBABILITIES.RECIPE_PROBABILITIES
    prob_keys = list(recipe_probabilities.keys())
    for probKeys in prob_keys:
        bounds = rngBoundaries(recipe_probabilities[probKeys])
        randomSpoken = random.randint(1, 100)
        for idx in range(len(bounds) - 1):
            curr_i = len(bounds) - 1 - idx
            if bounds[curr_i - 1] != bounds[curr_i] \
                and bounds[curr_i - 1] < randomSpoken and randomSpoken <= bounds[curr_i]:
                recipe_name, recipe_ingred = getRandomRecipes(MASTER_RECIPES[curr_i - 1])
                master_recipes_names.append(recipe_name)
                master_recipes.append(recipe_ingred)
                break

def rngBoundaries(probs):
    overall = sum(probs)
    bounds = [0]
    for aProb in probs:
        bounds.append(bounds[-1] + 100*aProb/overall)
    return bounds

def getRandomRecipes(recipe_level):
    recipe_keys = list(recipe_level.keys())
    rng_recipes = random.choice(recipe_keys)
    return rng_recipes, list(recipe_level[rng_recipes])

def allocateMinVals(lst):
    probs = list(lst)
    counter = probs[0]
    for i in range(1, len(probs)):
        probs[i] = counter + probs[i]
    return probs

def finished_recipe(team):
    '''
    pop the recipe from the front of the list
    The recipe being popped is done
    '''
    global gold_recipes_completed
    global blue_recipes_completed

    if team == ALLIANCE_COLOR.BLUE:
        if blue_recipes:
            blue_recipes.pop(0)
            blue_recipes_completed += 1
    else:
        if gold_recipes:
            gold_recipes.pop(0)
            gold_recipes_completed += 1

def distribute_recipe():
    '''
    pop first recipe off master list and add it to both team's recipe list
    '''
    if not master_recipes:
        return
    gold_recipes.append(master_recipes[0])
    blue_recipes.append(master_recipes[0])
    master_recipes.pop(0)
    master_recipes_names.pop(0)

def get_recipe(team):
    '''
    return first element of recipes
    '''
    if team == ALLIANCE_COLOR.BLUE:
        if not blue_recipes:
            return None
        return blue_recipes[0]
    else:
        if not gold_recipes:
            return None
        return gold_recipes[0]

def check_recipe(team, ingredients, num_cooked=0):
    '''
    checks correctness of recipe
    '''
    recipes = []
    if team == ALLIANCE_COLOR.BLUE:
        recipes = blue_recipes
    else:
        recipes = gold_recipes
    if len(recipes) != len(ingredients):
        return False
    else:
        for item in ingredients:
            if item not in recipes:
                return False
    return True

def set_recipes(gold_recipes_in, blue_recipes_in):
    '''
    overwrite recipes
    '''
    if gold_recipes_in is not None:
        global gold_recipes
        gold_recipes = list(gold_recipes_in)

    if blue_recipes_in is not None:
        global blue_recipes
        blue_recipes = list(blue_recipes_in)
