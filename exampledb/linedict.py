# -*- coding: utf-8 -*-
"""Scraper for dictionary at nciku.com.
"""

import logging
import urllib
import json
from bs4 import BeautifulSoup

from exampledb import scraper

SENTENCE_URL_BASE = 'http://linedict.naver.com/cnen/example/search.dict?page=1&page_size=20&examType=normal&fieldType=&author=&country=&ql=default&format=json&platform=isPC&'

class LineDictScraper(scraper.BaseScraper):
  
  def get_sentences(self, word):
    sentences = []
    params = {'query': word.encode('utf-8')}
    sentence_url = SENTENCE_URL_BASE + urllib.parse.urlencode(params)
    data = json.loads(self._get(sentence_url))
    for example in data['exampleList']:
      sentences.append((example['example'], example['recentTrslation']))
    return sentences

  
def main():
  scraper = LineDictScraper()
  sentences = scraper.get_sentences(u'加剧')
  for sentence in sentences:
    print(sentence[0])
    print(sentence[1])
  

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  main()
