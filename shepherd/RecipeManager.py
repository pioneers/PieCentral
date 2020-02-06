from Utils import *


class RecipeManager():

    gold_recipes = []
    blue_recipes = []
    gold_recipes_completed = 0
    blue_recipes_completed = 0


    def generate_recipes():
    '''
    reset recipe list with 4 newly selected recipes 
    both teams should have the same recipes
    '''
        return 0

    def next_repice(team):
    '''
    pop the recipe from the front of the list
    '''
        if team = ALLIANCE_COLOR.BLUE:
            if len(blue_recipes) == 0:
                return None
            else:
                blue_recipes.pop(0)
        else:
            if len(gold_recipes) == 0:
                return None
            else:
                gold_recipes.pop(0)


    def get_recipe(team):
        '''
        return first element of recipes
        '''
        if team = ALLIANCE_COLOR.BLUE:
            if len(blue_recipes) == 0:
                return None          
            return blue_recipes[0]
        else:
            if len(gold_recipes) == 0:
                return None
            return gold_recipes[0]

    def check_recipe(ingredients):
    '''
    checks correctness of recipe 
    '''
        if len(Recipe) != len(ingredients):
            return False
        else:
            for item in ingredients:
                if item not in Recipe:
                    return False 
        return True              


    def set_recipes(gold_recipes, blue_recipes):
    '''
    overwrite recipes 
    '''
        return 0