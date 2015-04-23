#!/usr/bin/python

f = open("unicodes", "r")
lines = f.readlines()

for line in lines:
  unichar = line.split(" ;")[0]
  if " " not in unichar:
    print "\"" + unichar + "\""
