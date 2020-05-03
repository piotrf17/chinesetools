# -*- coding: utf-8 -*-
"""Database of example sentences.

Combines a sqlite database stored in the data directory with scrapers
to dynamically fetch more sentences.
"""

import sqlite3
import time

from exampledb import exampledb_pb2
from exampledb import iciba
from exampledb import linedict
from exampledb import yellowbridge

SCHEMA = """
DROP TABLE IF EXISTS examples;

CREATE TABLE examples (
  word TEXT NOT NULL,
  entry TEXT NOT NULL
);
"""

class ExampleDb:

  def __init__(self, db_path):
    self.conn = sqlite3.connect(db_path)
    self.scrapers = {
# ICIBA is disabled because the scraper is currently broken.
#      exampledb_pb2.Example.ICIBA: iciba.IcibaScraper(),
      exampledb_pb2.Example.LINEDICT: linedict.LineDictScraper(),
      exampledb_pb2.Example.YELLOWBRIDGE: yellowbridge.YellowBridgeScraper(),
    }

  def create(self):
    """Drops any existing table and creates a new one."""
    self.conn.executescript(SCHEMA)

  def close(self):
    self.conn.close()

  def insert_entry(self, entry : exampledb_pb2.WordEntry):
    assert entry.HasField('word')
    assert len(entry.examples) > 0

    raw_entry = entry.SerializeToString()
    self.conn.execute('INSERT INTO examples (word, entry) VALUES (?, ?)',
                      (entry.word, raw_entry))
    self.conn.commit()

  def get_examples(self, word):
    """Get example sentences for the given word.

    Returns a list of Example protos.
    """
    row = self.conn.execute('SELECT entry FROM examples WHERE word=?',
                            (word,)).fetchone()
    if row is not None:
      entry = exampledb_pb2.WordEntry.FromString(row[0])
      return list(entry.examples)
    else:
      # Try scraping for example sentences.
      entry = exampledb_pb2.WordEntry()
      entry.word = word

      for source, scraper in self.scrapers.items():
        sentences = scraper.get_sentences(word)
        for chinese, english in sentences:
          example = entry.examples.add()
          example.chinese = chinese
          example.english = english
          example.source = source
          example.created_ts = time.time()
 
      # Don't put an empty entry into the database.
      # Maybe all scrapers failed and we want to try again.
      if not entry.examples:
        return []

      # Save the entry in the DB.
      self.insert_entry(entry)
      return list(entry.examples)
