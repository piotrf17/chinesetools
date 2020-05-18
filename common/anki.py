# -*- coding: utf-8 -*-
# Utility for reading anki collection.

import json
import os.path
import re
import shutil
import sqlite3

class AnkiReader:
  def __init__(self, collection_path):
    db_uri = 'file:{}?mode=ro'.format(collection_path)
    self.conn = sqlite3.connect(db_uri, uri=True)
    self.c = self.conn.cursor()

    # Read the decks in the table.
    self.decks = {}
    self.c.execute('SELECT decks FROM col')
    deck_infos = json.loads(self.c.fetchone()[0])
    for creation_time, deck_info in deck_infos.items():
      self.decks[deck_info['name']] = int(deck_info['id'])

  def get_notes(self, deck_name):
    deck_id = self.decks[deck_name]
    notes = []
    for row in self.c.execute(
        'SELECT flds FROM notes WHERE id IN '
        '(SELECT nid FROM cards WHERE did=?)', (deck_id,)):
      notes.append(row[0].split(u'\u001f'))
    return notes

  def get_known_characters(self):
    char_notes = self.get_notes('Chinese::Characters')
    chars = []
    for note in char_notes:
      chars.append(note[0])
    return chars

  def get_character_cards(self, char):
    notes = []
    for row in self.c.execute(
      'SELECT flds FROM notes WHERE flds LIKE ? AND id IN'
      '(SELECT nid FROM cards WHERE did=?)', (
        "%" + char + "%", self.decks['Chinese::Characters'])):
      note = row[0].split(u'\u001f')
      if note[0] == char:
        notes.append(note)
    return notes


  def get_known_legacy_words(self):
    word_notes = self.get_notes('Chinese::Words')
    words = []
    for note in word_notes:
      words.append(note[0])
    return words

  def get_legacy_word_cards(self, word):
    notes = []
    for row in self.c.execute(
      'SELECT flds FROM notes WHERE flds LIKE ? AND id IN'
      '(SELECT nid FROM cards WHERE did=?)', (
        "%" + word + "%", self.decks['Chinese::Words'])):
      note = row[0].split(u'\u001f')
      if note[0] == word:
        notes.append(note)
    return notes

  def get_known_words(self):
    word_notes = self.get_notes('Chinese::General')
    words = []
    for note in word_notes:
      # Skip legacy front/back cards.
      if len(note) == 2:
        continue
      word = note[3]
      # A lot of notes lack a character in the 'back' slot, skip those.
      if word:
        words.append(word)
    words = list(set(words))
    return words

  def get_word_cards(self, word):
    notes = []
    for row in self.c.execute(
        'SELECT flds FROM notes WHERE flds LIKE ? AND id IN '
        '(SELECT nid FROM cards WHERE did=?)', (
          "%" + word + "%", self.decks['Chinese::General'])):
      note = row[0].split(u'\u001f')
      if len(note) == 2:
        continue
      if note[3] == word:
        notes.append(note)
    return notes
