import os.path
import json

import jetcomcrawl


def get_settings():
    current_dir = os.path.dirname(os.path.abspath(jetcomcrawl.__file__))
    return json.load(open(os.path.join(current_dir, 'settings.json')))
