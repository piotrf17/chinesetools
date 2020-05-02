# Tool for printing some stats about the anki deck.
# Useful for testing the anki library.

import anki
import config

if __name__ == "__main__":
  reader = anki.AnkiReader(config.get_anki_collection())
  for deck in reader.decks:
    print('{} has {} notes'.format(deck, len(reader.get_notes(deck))))
