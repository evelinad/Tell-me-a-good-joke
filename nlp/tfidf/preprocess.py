#!/usr/bin/python
import sys
import os
import json
import ast
import re
import enchant
import string
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet, stopwords
from nltk.metrics import edit_distance
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction import stop_words

class AbreviationReplacer(object):
  replacement_patterns = [
    (r'won\'t', 'will not'),
    (r'can\'t', 'cannot'),
    (r'i\'m', 'i am'),
    (r'ain\'t', 'is not'),
    (r'(\w+)\'ll', '\g<1> will'),
    (r'(\w+)n\'t', '\g<1> not'),
    (r'(\w+)\'ve', '\g<1> have'),
    (r'(\w+)\'s', '\g<1> is'),
    (r'(\w+)\'re', '\g<1> are'),
    (r'(\w+)\'d', '\g<1> would')
  ]

  def __init__(self, patterns=replacement_patterns):
    self.patterns = [(re.compile(regex), repl) for (regex, repl) in patterns]
  
  def replace(self, text):
    s = text
    for (pattern, repl) in self.patterns:
      (s, count) = re.subn(pattern, repl, s)
    return s


class SqueezeLetters(object):
  def __init__(self):
    self.repeat_regexp = re.compile(r'(\w*)(\w)\2\2(\w*)')
    self.repl = r'\1\2\2\3'

  def squeeze(self, word):
    if wordnet.synsets(word):
      return word
    repl_word = self.repeat_regexp.sub(self.repl, word)
    if repl_word != word:
      return self.squeeze(repl_word)
    else:
      return repl_word


ROOT_PATH = os.getcwd() + "/"

#check wikipedia
ASCII_EMOTICONS=[":-P", ":-\\", ":-D", ":\'D", ":\'P", ":-)", ":\'-(", ":-(", ":-((", ":0(", ":''(", ":-O", ":@", ":\"(", ":,(", ":)", ":D", ":(", ":'(", ":P", "O:)", "3:)", "o.O", ";)", ":O", "-_-", ">:O", ":*", "<3", "^_^", "8-)", "8|", "(^^^)", ":|]", ">:(", ":v", ":/", ":3", "(y)", ":poop:", ":putnam:", "<(\")"]

EMOTICONS = []
with open(ROOT_PATH + "emoticons/emoticons") as f:
  EMOTICONS = [line.split() for line in f.read().splitlines()]

UNICODE=[]
with open(ROOT_PATH + "unicode/unicodechars") as f:
  UNICODE = f.read().splitlines()

CORPUSDIR="classified_corpus/"
PROCESSEDCORPUSDIR="processed_corpus/"
FBPAGES=["jokeoftheday999", "363725540304160"]

DICT = enchant.DictWithPWL("en", ROOT_PATH + "netlingo/netlingowords")

ASCII = ''.join(chr(x) for x in range(128))

LMTZR = WordNetLemmatizer()

STOPWORDS = [stopword for stopword in stopwords.words('english') + list(stop_words.ENGLISH_STOP_WORDS) if stopword not in [u'no', u'nor', u'not', u'nobody', u'none', u'nothing', u'nowhere', u'against']]

positivesfile = open(ROOT_PATH + "/positives", "w")
negativesfile = open(ROOT_PATH + "/negatives", "w")

def remove_message_tags(message, message_tags):
  for tag in message_tags:
    message = message.replace(tag["name"].encode('ascii','ignore'), "")
  return message


def remove_emoticons(message):
  for emoticontype in EMOTICONS:
    for i in range(1, len(emoticontype)):
      message = message.replace(emoticontype[i].lower(), " " + emoticontype[0].lower() + " ")
  return message


def remove_unicode(message):
  return re.sub(r'[^\x00-\x7f]',r'', message)


def squeeze_letters(wordtoken):
  wordtoken = re.sub(r'(^(h+[aeiou]*)*(h+[aeiou]*){2}$)', "haha", wordtoken)
  #TODO
  #wordtoken = re.sub(r'((\w+)(h+[aeiou]*)*(h+[aeiou]*){2}$)', '\g<1>haha', wordtoken)
  #wordtoken = re.sub(r'(^((h+[aeiou]*)*(h+[aeiou]*){2})(\w+))', 'haha\g<2>', wordtoken)
  wordtoken = re.sub(r'((lolo)+l)', "lol", wordtoken)
  squeeze = SqueezeLetters()
  wordtoken = squeeze.squeeze(wordtoken)
  return wordtoken


def spellcheck(wordtoken):
  if wordtoken == "":
    return wordtoken

  if DICT.check(wordtoken) == False:
    suggestions = DICT.suggest(wordtoken)
    if suggestions:
      for suggestion in suggestions:
        if edit_distance(wordtoken, suggestion) <= 2:
          return suggestion

  return wordtoken


def tokenize(message):
  replacer = AbreviationReplacer()
  message = replacer.replace(message)
  sentences = sent_tokenize(message)
  words = []
  for sentence in sentences:
    words = word_tokenize(sentence)
    #lematization
  newwords = []
  for word in words:
    if word not in string.punctuation:
      for psign in string.punctuation:
        word = word.replace(psign, "")
        word = squeeze_letters(word)
      if re.match(r'(^(h[aeiou])+$)', word) != None and len(newwords) != 0:
        newwords[-1] += word
        newwords[-1] = squeeze_letters(newwords[-1])
        newwords[-1] = spellcheck(newwords[-1])
        try: 
          newword = LMTZR.lemmatize(newwords[-1])
          newwords[-1] = newword
        except Exception as exc:
          #print "Exception" +  str(exc)
          pass
      else:
        word = spellcheck(word)
        try:
          newword = LMTZR.lemmatize(word)
          newwords.append(newword)
        except Exception as exc:
          #print "Exception" +  str(exc)
          newwords.append(word)

  print newwords
  return newwords 


def handle_negation(tokens):
  pass


def process_comments(DIR, f):
  comments = [int(comment) for comment in os.listdir(DIR)]
  comments = sorted(comments)
  for comment in comments:
    print "Comment " + str(comment)
    COMMENT_SOURCE_FILE = DIR + str(comment)
    json_file = open(COMMENT_SOURCE_FILE, "r")
    json_data = ast.literal_eval(json.loads(json.dumps(json_file.read())))
    json_file.close()
    message = json_data["message"].encode('ascii','ignore')
    if json_data.has_key("message_tags"):
      message = remove_message_tags(message, json_data["message_tags"])
    message = remove_unicode(message)
    message = message.lower()
    message = remove_emoticons(message)
    wordtokens = tokenize(message)
    for token in wordtokens:
      if (token != "") and (not token in STOPWORDS):
        f.write(token + " ")
    if len(wordtokens) != 0:
      f.write(".\n") 


def process_fbpage(fbpage):
  print "Processing facebook page " + fbpage
  FBPAGE_PATH = ROOT_PATH + CORPUSDIR + fbpage + "/"
  print FBPAGE_PATH

  childfiles = [int(childfile) for childfile in os.listdir(FBPAGE_PATH)]
  childfiles = sorted(childfiles)
  for childfile in childfiles:
     print "Post " + str(childfile)
     POS_DIR = FBPAGE_PATH + str(childfile) + "/positive/"
     NEG_DIR = FBPAGE_PATH + str(childfile) + "/negative/"

     print "Processing positive comments "     
     if os.path.exists(POS_DIR) == True:
       process_comments(POS_DIR, positivesfile)

     print "Processing negative comments "
     if os.path.exists(NEG_DIR) == True:
       process_comments(NEG_DIR, negativesfile)


def main():
  for page in FBPAGES:
    process_fbpage(page)

  positivesfile.close()
  negativesfile.close()


if __name__ == "__main__":
  main()

