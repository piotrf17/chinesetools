# -*- coding: utf-8 -*-

import re

IS_CHINESE = re.compile(u'^[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-\u9FC3豈-鶴侮-頻並-龎]+$', re.UNICODE)

def is_chinese(word):
  return IS_CHINESE.match(word) != None
