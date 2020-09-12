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
    for row in self.c.execute('SELECT * FROM decks'):
      name = row[1]
      deck_id = int(row[0])
      self.decks[name] = deck_id
    print(self.decks)

  def get_notes(self, deck_name):
    deck_id = self.decks[deck_name]
    notes = []
    for row in self.c.execute(
        'SELECT flds FROM notes WHERE id IN '
        '(SELECT nid FROM cards WHERE did=?)', (deck_id,)):
      notes.append(row[0].split(u'\u001f'))
    return notes

  def get_known_characters(self):
    char_notes = self.get_notes(u'Chinese\x1fCharacters')
    chars = []
    for note in char_notes:
      chars.append(note[0])
    return chars

  def get_character_cards(self, char):
    notes = []
    for row in self.c.execute(
      'SELECT flds FROM notes WHERE flds LIKE ? AND id IN'
      '(SELECT nid FROM cards WHERE did=?)', (
        "%" + char + "%", self.decks[u'Chinese\x1fCharacters'])):
      note = row[0].split(u'\u001f')
      if note[0] == char:
        notes.append(note)
    return notes


  def get_known_legacy_words(self):
    word_notes = self.get_notes(u'Chinese\x1fWords')
    words = []
    for note in word_notes:
      words.append(note[0])
    return words

  def get_legacy_word_cards(self, word):
    notes = []
    for row in self.c.execute(
      'SELECT flds FROM notes WHERE flds LIKE ? AND id IN'
      '(SELECT nid FROM cards WHERE did=?)', (
        "%" + word + "%", self.decks[u'Chinese\x1fWords'])):
      note = row[0].split(u'\u001f')
      if note[0] == word:
        notes.append(note)
    return notes

  def get_known_words(self):
    word_notes = self.get_notes(u'Chinese\x1fGeneral')
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
          "%" + word + "%", self.decks[u'Chinese\x1fGeneral'])):
      note = row[0].split(u'\u001f')
      if len(note) == 2:
        continue
      if note[3] == word:
        notes.append(note)
    return notes
