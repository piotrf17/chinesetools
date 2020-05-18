"""
build_learning_summary generates an HTML report page showing status of character
and world learning.
"""

from absl import app
from absl import flags
import logging
import os

from common import anki
from common import cdict
from common import config
from common import util

FLAGS = flags.FLAGS

flags.DEFINE_string('output_file', 'learning_summary.html',
                    'Path to output HTML file.')

class ReportGenerator:
  def __init__(self, output_file):
    self.outfile = open(output_file, 'w')

    self.d = cdict.Dict(config.get_data_dir())

    self.anki_reader = anki.AnkiReader(config.get_anki_collection())
    self.known_chars = set(self.anki_reader.get_known_characters())
    self.known_legacy_words = set(self.anki_reader.get_known_legacy_words())
    self.known_words = set(self.anki_reader.get_known_words())

    logging.info('{} known characters.'.format(len(self.known_chars)))
    logging.info('{} known legacy words.'.format(len(self.known_legacy_words)))
    logging.info('{} known words.'.format(len(self.known_words)))

    # Hack for traditional characters in frequency list.
    known_trad_chars = [u'乾',u'於',u'後']
    self.known_chars |= set(known_trad_chars)

  def write_header(self):
    self.outfile.write("""
<html>
<head>
  <title>Character Learning Summary</title>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<head>
<body>
""")

  def write_coverage(self):
    self.outfile.write('<h3>Coverage</h3>')

    known_chars = 0
    coverage = 0.0
    for c in self.known_chars:
      if not c in self.d.entries:
        continue
      known_chars += 1
      coverage += self.d.entries[c].char_frequency

    word_coverage = 0.0
    for w, entry in self.d.entries.items():
      if (w in self.known_words or w in self.known_legacy_words or
          w in self.known_chars):
        word_coverage += entry.word_frequency

    self.outfile.write('<p>Total known characters = {}'.format(known_chars))
    self.outfile.write('<p>Total frequency coverage = %.2f%%' % (100 * coverage))
    self.outfile.write('<p>Total known words = {}'.format(
      len(self.known_words | self.known_legacy_words)))
    self.outfile.write('<p>Total word coverage = %.2f%%' % (100 * word_coverage))

    self.outfile.write('<p>HSK Word Coverage</p>')
    self.outfile.write('<table border="1">')
    for l in range(6):
      coverage = 0
      for w in self.d.hsk_words[l]:
        if w in self.known_words or w in self.known_legacy_words:
         coverage += 1
      self.outfile.write('<tr><td>HSK %d</td><td>%d / %d</td></tr>' % (
        l + 1, coverage, len(self.d.hsk_words[l])))
    self.outfile.write('</table>')
    self.outfile.write('<br>')


  def write_frequency_table(self):
    self.outfile.write('<h3>Characters by Frequency</h3>')
    i = 0
    for c in self.d.chars_by_frequency:
      card_creator_link = 'http://localhost:5000/char/' + c
      url_style = 'text-decoration: none; color: black;'

      if i > 0 and i % 50 == 0:
        self.outfile.write('<br>')
      if i > 0 and i % 1000 == 0:
        self.outfile.write('<br>')
      i += 1
      style = ''
      if not(c in self.known_chars):
        style = 'style="background-color:red;"'
      self.outfile.write(
        '<a target="_blank" href="{}" style="{}"><span {}>{}</span></a>'.format(
          card_creator_link, url_style, style, c))
      if i == 5000:
        return

  def write_hsk_char_table(self):
    self.outfile.write('<h3>HSK Characters</h3>')
    for l in range(6):
      i = 0
      self.outfile.write('<p>HSK %d' % (l + 1))
      for c in self.d.hsk_chars[l]:
        card_creator_link = 'http://localhost:5000/char/' + c
        url_style = 'text-decoration: none; color: black;'
        
        if i % 50 == 0:
          self.outfile.write('<br>')
        i += 1
        style = ''
        if not(c in self.known_chars):
          style = 'style="background-color:red;"'
        self.outfile.write(
          '<a target="_blank" href="{}" style="{}"><span {}>{}</span></a>'.format(
            card_creator_link, url_style, style, c))
      self.outfile.write('<br>')

  def write_hsk_word_table(self):
    self.outfile.write('<h3>HSK Words</h3>')
    for l in range(6):
      i = 0
      self.outfile.write('<p>HSK %d' % (l + 1))
      for w in self.d.hsk_words[l]:
        card_creator_link = 'http://localhost:5000/word/' + w
        url_style = 'text-decoration: none; color: black;'
      
        if i % 10 == 0:
          self.outfile.write('<br>')
        i += 1
        style = ''
        if w in self.known_words:
          style = 'style="background-color:#BCED91;"'
        elif not w in self.known_legacy_words:
          style = 'style="background-color:red;"'
        w += u'\u3000' * (5 - len(w))
        self.outfile.write(
          '<a target="_blank" href="{}" style="{}"><span {}>{}</span></a>'.format(
            card_creator_link, url_style, style, w))
    self.outfile.write('<br>')

  def write_chars_with_no_words(self):
    self.outfile.write('<br><br><h3>Chars with no words</h3>')
    chars_in_words = []
    for w in (self.known_words | self.known_legacy_words):
      for c in w:
        if util.is_chinese(c):
          chars_in_words.append(c)
    chars_in_words = set(chars_in_words)
    i = 0
    for c in self.known_chars:
      if c not in chars_in_words and util.is_chinese(c) and c in self.d.entries:
        if i > 0 and i % 50 == 0:
          self.outfile.write('<br>')
        self.outfile.write(c)
        i += 1

  def write_not_learned_chars_in_words(self):
    self.outfile.write('<h3>Not yet learned chars in known words</h3>')
    chars_in_words = []
    for w in (self.known_words | self.known_legacy_words):
      for c in w:
        if util.is_chinese(c):
          chars_in_words.append(c)
    chars_in_words = set(chars_in_words)
    i = 0
    for c in chars_in_words:
      if not c in self.known_chars:
        card_creator_link = 'http://localhost:5000/char/' + c
        url_style = 'text-decoration: none; color: black;'

        if i > 0 and i % 50 == 0:
          self.outfile.write('<br>')
        self.outfile.write(
          '<a target="_blank" href="{}" style="{}">{}</a>'.format(
            card_creator_link, url_style, c))
        i += 1

  def write_footer(self):
    self.outfile.write("""
</body>
""")
    
  def write_report(self):
    self.write_header()
    self.write_coverage()
    self.write_frequency_table()
    self.write_hsk_char_table()
    self.write_hsk_word_table()
    self.write_chars_with_no_words()
    self.write_not_learned_chars_in_words()
    self.write_footer()

def main(argv):
  report_generator = ReportGenerator(FLAGS.output_file)
  report_generator.write_report()
  full_output = 'file://' + os.path.join(
    os.path.dirname(os.path.abspath(argv[0])), FLAGS.output_file)
  print('Report written to {}'.format(full_output))

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  app.run(main)
