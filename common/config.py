"""Library for configuration data.

This library expects the top level project to have a file called config.json.
"""

import json
import os

# TODO(piotrf): cache this.
def get_config():
  config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'config.json')
  return json.load(open(config_path, 'r'))

def get_data_dir():
  return get_config()['data_dir']

def get_anki_collection():
  return get_config()['anki_collection']

def get_example_db_path():
  return os.path.join(get_data_dir(), 'examples.db')

def get_pending_anki_csv():
  return get_config()['pending_anki_csv']
