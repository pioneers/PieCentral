from Utils import *


class RecipeManager():

    master_recipes = [RECIPE_PROBABILITIES.EASY_RECIPE, RECIPE_PROBABILITIES.MEDIUM_RECIPE, \
                      RECIPE_PROBABILITIES.HARD_RECIPE, RECIPE_PROBABILITIES.VERY_HARD_RECIPE]
    gold_recipes = []
    blue_recipes = []
    gold_recipes_completed = 0
    blue_recipes_completed = 0

    def generate_recipes():
        '''
        reset recipe list with 4 newly selected recipes
        both teams should have the same recipes
        '''
        gold_recipes.clear()
        blue_recipes.clear()
        for recipe in master_recipes:
            gold_recipes += list(recipe.values)
            blue_recipes += list(recipe.values)

    def finished_recipe(team):
        '''
        pop the recipe from the front of the list

        The recipe being popped is done
        '''
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
        gold_recipes += master_recipes[0]
        blue_recipes += master_recipes[0]
        master_recipes.pop(0)
    

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

    def set_recipes(gold_recipes, blue_recipes):
        '''
        overwrite recipes
        '''
        if gold_recipes is not None:
            gold_recipes = list(gold_recipes)

        if blue_recipes is not None:
            blue_recipes = list(blue_recipes)
