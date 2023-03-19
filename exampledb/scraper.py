"""Base class for all scrapers.
"""

import logging
import urllib.request

HEADERS = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
  }

# If set to true, then the fetched data will be saved to disk, and loaded
# from there on the next run. Useful for debugging and fixing scraping code.
DEBUG=False

class BaseScraper:
  def _get(self, url):
    request = urllib.request.Request(url, headers=HEADERS)
    if DEBUG:
      logging.info('Scraper debug mode is enabled')
      try:
        return open('/tmp/scraped_data.txt').read()
      except FileNotFoundError:
        logging.info('Saved scrape not found, fetching live.')
    data = urllib.request.urlopen(request).read()
    if DEBUG:
      open('/tmp/scraped_data.txt', 'w').write(data.decode('utf-8'))
    return data
