from flask import Blueprint, render_template, jsonify, g, request, current_app

from common.anki import AnkiReader
from common.cdict import Dict
from exampledb.exampledb import ExampleDb

bp = Blueprint('cards', __name__)

# I'm running this locally as an app, so for expediency we store
# global variables instead of dealing with application context or sessions.
cdict = None
def get_dict():
  global cdict
  if cdict is None:
    cdict = Dict(current_app.config['DATA_DIR'])
  return cdict


def get_example_db():
  if 'example_db' not in g:
    g.example_db = ExampleDb(current_app.config['EXAMPLE_DB'])
  return g.example_db


def get_anki_reader():
  if 'anki_reader' not in g:
    g.anki_reader = AnkiReader(current_app.config['ANKI_COLLECTION'])
  return g.anki_reader

@bp.route('/')
def index():
  return render_template('index.html')


@bp.route("/api/lookup/<word>")
def lookup(word):
  data = {}

  # Get definition.
  entry = get_dict().entries[word]
  data["definitions"] = []
  for meaning in entry.meanings:
    definition = {}
    definition["pinyin_diacritic"] = meaning.pinyin_diacritic
    definition["meaning"] = meaning.meaning
    data["definitions"].append(definition)

  # Get anki cards.
  reader = get_anki_reader()
  data["legacy_word_cards"] = reader.get_legacy_word_cards(word)
  data["word_cards"] = reader.get_word_cards(word)

  # Get example sentences.
  db_examples = get_example_db().get_examples(word)
  data["examples"] = []  
  for db_example in db_examples:
    example = {}
    example["chinese"] = db_example.chinese
    example["english"] = db_example.english
    data["examples"].append(example)

  return jsonify(data)


@bp.route("/api/add_cards", methods=['POST'])
def add_cards():
  with open(current_app.config['PENDING_ANKI_CSV'], 'a') as f:
    for card in request.get_json():
      csv_line = '%s;;%s;%s;%s;%s;%s\n' % (
        card['frontExample'], card['frontHints'], card['backWord'],
        card['sentence'], card['info'], card['twoCards'])
      f.write(csv_line)
  return jsonify({'success': True})


@bp.route("/words/<word>")
def info(word):
  return render_template('word.html', word=word)
