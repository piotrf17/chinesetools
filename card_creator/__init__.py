import os
from flask import Flask

from common import config

def create_app(test_config=None):
  # Create and configure the app.
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY='dev',
    EXAMPLE_DB=config.get_example_db_path(),
    PENDING_ANKI_CSV=config.get_pending_anki_csv(),
    ANKI_COLLECTION=config.get_anki_collection(),
    DATA_DIR=config.get_data_dir(),
  )

  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)

  from . import cards
  app.register_blueprint(cards.bp)
  app.add_url_rule('/', endpoint='index')
  
  return app
