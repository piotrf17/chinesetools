# -*- coding: utf-8 -*-
"""Scraper for dictionary at yellowbridge.com

NOTE: the english translations this scraper provides are a little broken.
"""

import logging
import unicodedata
import urllib
from bs4 import BeautifulSoup

from exampledb import scraper

SENTENCE_URL_BASE = 'http://www.yellowbridge.com/chinese/sentsearch.php?word='

class YellowBridgeScraper(scraper.BaseScraper):
  
  def get_sentences(self, word):
    sentences = []
    sentence_url = SENTENCE_URL_BASE + urllib.parse.quote(word.encode('utf-8'))
    html = self._get(sentence_url)
    soup = BeautifulSoup(html, features="lxml")
        
    for span in soup.find_all('span', attrs={'class': 'zh'}):
      chinese_sentence = []
      for c in span.text:
        # Remove some special characters that yellowbridge uses for tooltips.
        if (unicodedata.name(c).startswith('CIRCLED DIGIT') or
            unicodedata.name(c).startswith('PARENTHESIZED DIGIT') or
            unicodedata.name(c).startswith('CIRCLED NUMBER')):
          continue
        if c == u'{' or c == u'}':
          continue
        chinese_sentence.append(c)
      chinese_sentence = ''.join(chinese_sentence)
      english_sentence = str(span.next_sibling.next_sibling)
      sentences.append((chinese_sentence, english_sentence))
    return sentences

  
def main():
  scraper = YellowBridgeScraper()
  sentences = scraper.get_sentences(u'加剧')
  for sentence in sentences:
    print(sentence[0])
    print(sentence[1])


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  main()
