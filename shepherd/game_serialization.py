import json

def serialize(saving):
    """
    Serialize the dictionary of variables "saving"

    Input:
    saving - dictionary with keys as variable names

    Return:
    True - successful load signal
    False - unseccessful load signal
    """
    assert type(saving) == dict, "Input must be a dictionary"
    create_json(saving)

def load_game():
    """
    Load the game since last game
    """
    return load_json()

def load_json(path = "", fileName = "game_data.json"):
    with open(path + fileName) as json_file:
        data = json.load(json_file)
        return data
    return None

def create_json(data, path = "", fileName = "game_data.json"):
    with open(path + fileName, 'w') as outfile:
        json.dump(data, outfile)
        return True
    return False
