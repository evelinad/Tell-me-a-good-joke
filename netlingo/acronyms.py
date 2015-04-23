#!/usr/bin/python
import urllib2
from bs4 import BeautifulSoup

def main():
    response = urllib2.urlopen('http://www.netlingo.com/acronyms.php')
    html = response.read()
    soup = BeautifulSoup(html)
    div = soup.find("div", {"class": "list_box3"})
    div = div.findAll("li")
    abbrevlist = []

    for d in div:
        if len(d.find('a').contents) != 0:
          abbrevlist.append(d.find('a').contents[0])# = d.contents[1]

    for elem in abbrevlist:
        print elem.lower()

if __name__ == "__main__":
    main()
