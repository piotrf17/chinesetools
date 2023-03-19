import logging
from exampledb.linedict import LineDictScraper

def main():
  scraper = LineDictScraper()
  sentences = scraper.get_sentences(u'加剧')
  for sentence in sentences:
    print(sentence[0])
    print(sentence[1])
  

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  main()  
