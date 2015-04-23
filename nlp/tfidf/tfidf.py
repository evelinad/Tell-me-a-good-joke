#!/usr/bin/python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
import os
import numpy as np
import json
import urllib

ROOT_PATH = os.getcwd() + "/"

UCLASSIFY_KEY = "7SPvAicl3Li8bpFnAA2bVcFOfVA"
UCLASSIFY_LINK = "http://uclassify.com/browse/uClassify/sentiment/ClassifyText?readKey=" + UCLASSIFY_KEY + "&text="
QUERY = "&output=json&version=1.01"

EMOTICONS = []
with open(ROOT_PATH + "emoticons/emoticons") as f:
  EMOTICONS = [line.split() for line in f.read().splitlines()]

corpus = []
for filename in ["/positives", "/negatives"]:
  corpus.append(open(ROOT_PATH + filename).read())

vectorizer = TfidfVectorizer(ngram_range=(1,3), max_features=3000, norm='l2', sublinear_tf=True)
tfidf = vectorizer.fit_transform(corpus)
feature_names = vectorizer.get_feature_names()
ch2 = SelectKBest(chi2, k=13)
feature = ch2.fit_transform(tfidf, [1,2])
feature_names = [feature_names[i] for i in ch2.get_support(indices=True)]
scores = np.array(feature.toarray()).T
#print scores
#print feature_names, len(feature_names)


for i in range(len(feature_names)):
  name = feature_names[i]
  for emoticonlist in EMOTICONS:
    name = name.replace(emoticonlist[0], "")
  name = name.replace(" ", "%20")
  url = UCLASSIFY_LINK + name + QUERY
  #print url
  data = urllib.urlopen(url).read()
  json_data = json.loads(data.encode("utf-8"))
  print feature_names[i], " ", scores[i][0], " ", scores[i][1], " ", json_data["cls1"]["positive"], " ", json_data["cls1"]["negative"]

#print scores
#print np.array(tfidf.toarray()).T
#print vectorizer.get_feature_names()
