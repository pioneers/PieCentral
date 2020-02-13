from Utils import *


class RecipeManager():

    master_recipes = [RECIPE_PROBABILITIES.EASY_RECIPE, RECIPE_PROBABILITIES.MEDIUM_RECIPE, \
                      RECIPE_PROBABILITIES.HARD_RECIPE, RECIPE_PROBABILITIES.VERY_HARD_RECIPE]
    gold_recipes = []
    blue_recipes = []
    gold_recipes_completed = 0
    blue_recipes_completed = 0        

    # FIXME: Fix this to actually have list of recipies, not the difficulties
    def generate_recipes(self):
        '''
        reset recipe list with 4 newly selected recipes
        both teams should have the same recipes
        '''
        self.gold_recipes = list(self.master_recipes)
        self.blue_recipes = list(self.master_recipes)

    def next_recipe(self, team):
        '''
        pop the recipe from the front of the list

        The recipe being popped is done
        '''
        if team == ALLIANCE_COLOR.BLUE:
            if len(self.blue_recipes) == 0:
                return None
            else:
                self.blue_recipes.pop(0)
                self.blue_recipes_completed += 1
        else:
            if len(self.gold_recipes) == 0:
                return None
            else:
                self.gold_recipes.pop(0)
                self.gold_recipes_completed += 1

    def get_recipe(self, team):
        '''
        return first element of recipes
        '''
        if team == ALLIANCE_COLOR.BLUE:
            if len(self.blue_recipes) == 0:
                return None
            return self.blue_recipes[0]
        else:
            if len(self.gold_recipes) == 0:
                return None
            return self.gold_recipes[0]

    def check_recipe(self, team, ingredients, num_cooked=0):
        '''
        checks correctness of recipe
        '''
        recipes = []
        if team == ALLIANCE_COLOR.BLUE:
            recipes = self.blue_recipes
        else:
            recipes = self.gold_recipes
        if len(recipes) != len(ingredients):
            return False
        else:
            for item in ingredients:
                if item not in recipes:
                    return False
        return True

    def set_recipes(self, gold_recipes, blue_recipes):
        '''
        overwrite recipes
        '''
        if gold_recipes != None:
            self.gold_recipes = list(gold_recipes)

        if blue_recipes != None:
            self.blue_recipes = list(blue_recipes)
