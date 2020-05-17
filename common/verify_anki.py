# Tool for printing some stats about the anki deck, and verifying some
# assumptions I make about how cards are structured.
# Also useful for testing the anki library.

import anki
import config


def check_legacy_word_deck(reader):
  words = reader.get_known_legacy_words()
  print('Verifying {} legacy words.'.format(len(words)))
  num_checked = 0
  for word in words:
    notes = reader.get_legacy_word_cards(word)
    if len(notes) == 0:
      print('  {} has no legacy word cards, but is in known_legacy_words'.format(word))
    elif len(notes) > 1:
      print('  {} has multiple legacy word cards'.format(word))    
    num_checked += 1
    if num_checked % 100 == 0:
      print('  verified {} so far'.format(num_checked))
  print()      


def check_word_deck(reader):
  notes = reader.get_notes('Chinese::General')
  print('Verifying {} general deck notes'.format(len(notes)))
  legacy_general_notes = 0
  notes_without_word = 0
  for note in notes:
    if len(note) == 2:
      legacy_general_notes += 1
      continue
    if not note[3]:
      print(note)
      notes_without_word += 1
  print('Found {} legacy general notes'.format(legacy_general_notes))
  print('Found {} notes without a word on the back'.format(
    notes_without_word))
  print()


if __name__ == "__main__":
  reader = anki.AnkiReader(config.get_anki_collection())
  for deck in reader.decks:
    print('{} has {} notes'.format(deck, len(reader.get_notes(deck))))
  print()

#  check_legacy_word_deck(reader)
  check_word_deck(reader)
