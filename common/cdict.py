# -*- coding: utf-8 -*-
"""Dictionary for both characters and words.

Data comes from CC-CEDICT as well as a character frequency table.
"""

from dataclasses import dataclass, field
import logging
import re
import os
from typing import List

CEDICT_FILE = 'cedict_ts.u8'
CHAR_FREQUENCY_FILE = 'characters_by_frequency.txt'
WORD_FREQUENCY_FILE = 'words_by_frequency.csv'
HSK_CHARS_FILE = 'hsk_chars.txt'
HSK_WORDS_FILE = 'hsk_words.txt'


def _tone_diacritic(tone):
  """Returns the unicode diacritic for the given tone string."""
  if tone == '1':
    return u'\u0304'
  elif tone == '2':
    return u'\u0301'
  elif tone == '3':
    return u'\u030c'
  elif tone == '4':
    return u'\u0300'
  else:
    return ''

  
def _find_first(string, characters):
  """Find the first ocurrance of a character in a string.

  Goes through characters in order. If a character occurs in string,
  then it returns the index. If none exist, returns -1.
  """
  for c in characters:
    i = string.find(c)
    if i != -1:
      return i
  return -1


def pinyin_diacritic(pinyin):
  """Returns pinyin with diacritics."""
  result = []
  for w in pinyin.split():
    # Don't do anything for words without valid pronunciations.
    if w in ['xx5', 'm2', 'm4']:
      result.append(w)
      continue
    # Handle retroflex r appended on previous symbol.
    if w == 'r5':
      if len(result):
        result[-1] = result[-1] + 'r'
      else:
        result.append('r')
      continue
    # Convert 'u:' to umlaut.
    if 'u:' in w:
      parts = w.split('u:')
      w = parts[0] + u'\u00fc' + parts[1]
    # Convert tone number to diacritic.
    if w[-1].isdigit():
      tone = _tone_diacritic(w[-1])
      if 'iu' in w:
        i = w.index('iu') + 1
      else:
        i = _find_first(w, ['a', 'A', 'o', 'O', 'e', 'E', 'i', 'I', 'u', 'U',
                           u'\u00fc', u'\u00dc'])
      # We expect that a vowel exists for a valid chinese word.
      if i == -1:
        print(pinyin)
        print(w)
      assert i != -1
      w = w[0:i+1] + tone + w[i+1:-1]
    result.append(w)
  return ' '.join(result)


def _meaning_importance(entry):
  if entry.meaning.startswith(u'variant'):
    return 1
  elif entry.meaning.startswith(u'old variant'):
    return 2
  elif entry.meaning.startswith(u'archaic variant'):
    return 3
  else:
    return -1


@dataclass
class MeaningEntry(object):
  # The pinyin for this word/character, with the tones indicated by numbers.
  pinyin: str

  # The dictionary meaning for this word/character, in English.
  meaning: str

  # Same as `pinyin`, but with the tone indicated by a diacritic over the
  # letters.
  @property
  def pinyin_diacritic(self) -> str:
    return pinyin_diacritic(self.pinyin)

    
@dataclass
class DictEntry:
  # The word/character this entry represents.
  word: str

  # The same word/character in traditional.
  traditional: str

  # A list of different meanings from CC-CEDICT.
  meanings: List[MeaningEntry] = field(default_factory=list)

  # If >0, the relative frequency of this character from a corpus of
  # written Chinese.
  char_frequency: float = 0.0

  # If >0, the relative frequency of this word from a corpus of
  # written Chinese. Note that the frequency of a character as word is
  # distinct from the frequency of it appearing as a character.
  word_frequency: float = 0.0

  # HSK level for this entry as a character. 1 through 6.
  # If 0, then this is not any HSK list.
  char_hsk_level: int = 0

  # HSK level for this entry as a word. 1 through 6.
  # If 0, then this is not any HSK list.
  word_hsk_level: int = 0

  
class Dict:
  """A dictionary for Chinese words and characters.

  Attributes:
    entries: A map from character/word to a DictEntry.
    traditional_to_entry: Like entries, except from traditional to DictEntry.
    chars_by_frequency: A list of chinese characters, in order from most
      to least frequent.
    hsk_chars: A list of lists, e.g. hsk_chars[0] is all Level 1 HSK chars.
    hsk_words: Similar to `hsk_chars`, but for words. Note that the HSK word
      lists do also include single character words, though not every character
      in `hsk_chars` also appears in `hsk_words`.
  """

  def __init__(self, data_dir):
    self.entries = {}
    self.traditional_to_entry = {}
    self.chars_by_frequency = []
    self.hsk_chars = []
    self.hsk_words = []
    
    logging.info('Loading cedict data...')
    self.load_cedict(os.path.join(data_dir, CEDICT_FILE))
    logging.info('Done')
    
    self.load_char_frequencies(os.path.join(data_dir, CHAR_FREQUENCY_FILE))
    self.load_word_frequencies(os.path.join(data_dir, WORD_FREQUENCY_FILE))
    self.load_hsk_chars(os.path.join(data_dir, HSK_CHARS_FILE))
    self.load_hsk_words(os.path.join(data_dir, HSK_WORDS_FILE))

  def load_cedict(self, cedict_file):
    # Read all data from the data file.
    for line in open(cedict_file, 'r').readlines():
      if line[0] == '#':
        continue
      m = re.match(r"(\S*)\s(\S*)\s\[(.*)\] /(.*)/", line)
      assert m
      trad = m.group(1)
      word = m.group(2)
      pinyin = m.group(3)
      meaning = m.group(4)
      if not word in self.entries:
        self.entries[word] = DictEntry(word, trad)
        self.traditional_to_entry[trad] = self.entries[word]
      self.entries[word].meanings.append(MeaningEntry(pinyin, meaning))
 
    # Re-sort meaning entries so the "main" meaning comes first. We prioritize
    # definitions that are not a "variant".
    for _, entry in self.entries.items():
      entry.meanings.sort(key=_meaning_importance)

  def load_char_frequencies(self, frequency_file):
    last_cdf = 0.0
    num_not_found = 0
    num_traditional = 0
    probability_mass_not_found = 0.0
    for line in open(frequency_file).readlines():
      c = line.split()[1]
      cdf = float(line.split()[3]) / 100.0
      frequency = cdf - last_cdf
      last_cdf = cdf

      if not c in self.entries:
        if c in self.traditional_to_entry:
          num_traditional += 1
        else:
          num_not_found += 1
          probability_mass_not_found += frequency
      else:
        self.chars_by_frequency.append(c)
        self.entries[c].char_frequency = frequency

    if num_not_found:
      logging.info('{} characters in frequency table, but not found in CC-CEDICT.'.format(num_not_found))
      logging.info('Total mass not found: {}'.format(probability_mass_not_found))
      logging.info('Total traditional characters ignored for frequency: {}'.format(num_traditional))

  def load_word_frequencies(self, frequency_file):
    l = 0
    num_not_found = 0
    probability_mass_not_found = 0.0

    for line in open(frequency_file).readlines():
      if l == 0:
        word_count = int(line.split(':')[1].split('"')[0].replace(',',''))
      elif l > 2:
        line = line.split(',')
        word = line[0].strip()
        frequency = float(line[1]) / word_count
        
        if not word in self.entries:
          num_not_found += 1
          probability_mass_not_found += frequency
        else:
          self.entries[word].word_frequency = frequency
      l += 1

    if num_not_found:
      logging.info(
        '{} words in frequency table, but not found in CC-CEDICT'.format(
          num_not_found))
      logging.info('Total mass not found: {}'.format(probability_mass_not_found))

  def load_hsk_chars(self, hsk_chars_file):
    for line in open(hsk_chars_file).readlines():
      chars = [c for c in line.strip().split(u'，')]
      if len(chars):
        self.hsk_chars.append(chars)
        for c in chars:
          self.entries[c].char_hsk_level = len(self.hsk_chars)

  def load_hsk_words(self, hsk_words_file):
    level_words = []
    num_words_without_entries = 0

    for line in open(hsk_words_file).readlines():
      if line[0] == '#':
        if level_words:
          self.hsk_words.append(level_words)
        level_words = []
        continue
      word = line.strip()
      if word in self.entries:
        self.entries[word].word_hsk_level = len(self.hsk_words) + 1
      else:
        num_words_without_entries += 1
      level_words.append(word)
    if level_words:
      self.hsk_words.append(level_words)

    if num_words_without_entries:
      logging.info('{} HSK words have no dictionary entries.'.format(
        num_words_without_entries))


if __name__ == "__main__":
  import config
  logging.basicConfig(level=logging.INFO)
  d = Dict(config.get_data_dir())
  print(d.entries[u'差'])
