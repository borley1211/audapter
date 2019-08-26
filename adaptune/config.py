import alsaaudio as alsa
import os
import json

with open(
    os.path.join(os.path.dirname(__file__), "params.json"), 'r', encoding='UTF-8'
) as file:
    default = json.load(file)
    params = default["params"]
    params["format"] = eval(params["format"])

    # print(params)
