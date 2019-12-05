import json
from Shepherd import lcm_send, LCM_TARGETS, UI_HEADER

def serialize(saving):
    """
    Serialize the dictionary of variables "saving"

    Input:
    saving - dictionary with keys as variable names

    Return:
    True - successful load signal
    False - unseccessful load signal
    """
    assert isinstance(saving, dict), "Input must be a dictionary"
    create_json(saving)

def load_json(path = "", fileName = "game_data.json"):
    with open(path + fileName) as json_file:
        data = json.load(json_file)
        lcm_send(LCM_TARGETS.UI, UI_HEADER.LOAD_DATA, data)
        return
    print("JSON not loaded")

def create_json(data, path = "", fileName = "game_data.json"):
    with open(path + fileName, 'w') as outfile:
        json.dump(data, outfile)
        return True
    return False
