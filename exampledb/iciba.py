# -*- coding: utf-8 -*-
"""Scraper for dictionary at iciba.com.

NOTE: this scraper does not work!
Iciba has changed to a jquery lookup, which seems to compute some kind of
signature per word that I didn't want to figure out.
"""

import unicodedata
import urllib
from bs4 import BeautifulSoup

from exampledb import scraper

SENTENCE_URL_BASE = 'http://www.iciba.com/'

class IcibaScraper(scraper.BaseScraper):
  
  def get_sentences(self, word):
    sentences = []
    sentence_url = SENTENCE_URL_BASE + urllib.parse.quote(word.encode('utf-8'))
    html = self._get(sentence_url)
    soup = BeautifulSoup(html, features="lxml")
    for li in soup.findAll('li', 'dj_li'):
      zh = li.findAll('p', 'stc_cn')
      assert len(zh) == 1
      en = li.findAll('p', 'stc_en')
      assert len(en) == 1
      sentences.append((zh[0].span.text, en[0].span.text))
    return sentences

  
def main():
  scraper = IcibaScraper()
  sentences = scraper.get_sentences(u'加剧')
  for sentence in sentences:
    print(sentence[0])
    print(sentence[1])


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  main()
