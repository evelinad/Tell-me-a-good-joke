#!/usr/bin/python

import urllib2
from bs4 import BeautifulSoup

def main():
    response = urllib2.urlopen('http://en.wikipedia.org/wiki/List_of_emoticons')
    html = response.read()
    soup = BeautifulSoup(html)
    table = soup.find("table", {"class": "wikitable"}) 
    table = table.findAll("tr")
    emoticons = {}

    for row in table:
      cols = row.findAll("td")
      if cols != None and len(cols) >= 2:
        col1 = cols[0]
        col2 = cols[1]
        emoticonsline = col1.findAll("code")[0]
        #print col2.findAll("code") + col2.findAll("a") + col2.findAll("sup")
        strkey = "Emoticon"
        for key in col2.contents:
        #  keystr = ""
          try:
            if "<sup" not in str(key) and "<code>" not in str(key):
	      if "href" in str(key):
                strkey += str(key)[str(key).find(">") + 1 : str(key).find("</")]
              else:
                strkey += str(key) 
          except Exception as exc:
            print str(exc)
        #  if key.findAll('a') is None:
        #    print key
          #continue 
          #if key.find('sup') == None and key.find('code') == None:
          #  print key

        print strkey + " ",

        for emoticons in emoticonsline:                    
          emoticonslist = unicode(emoticons).split(" ")
          for elem in emoticonslist:
            for emoticon in elem.encode("utf8").split("\xa0"):
              emoticon = emoticon.replace("\xc2", "")
              print emoticon,
        print
 
if __name__ == "__main__":
    main()

