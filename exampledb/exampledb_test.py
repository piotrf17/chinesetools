"""Integration test for exampledb.

To make Python imports happy, run this as:
python3 -m exampledb.exampledb_test from the top level.

Not really a test, just a useful tool for double checking the db code does
something.
TODO(piotrf): make this actually a test
"""

import os

from common import  config
from exampledb import exampledb

if __name__ == "__main__":
  db = exampledb.ExampleDb(os.path.join(config.get_data_dir(), 'examples.db'))
  examples = db.get_examples(u'加剧')
  for example in examples:
    print('Chinese: {}'.format(example.chinese))
    print('English: {}'.format(example.english))
