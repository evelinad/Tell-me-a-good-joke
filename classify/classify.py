#!/usr/bin/python
import sys
import os
from shutil import copyfile, rmtree
import json
import ast

ROOT_PATH = os.getcwd()
POS_CMD = "pos"
NEG_CMD = "neg"
SPAM_CMD = "spam"

def main():
  if len(sys.argv) != 2:
    print "Give the folder with posts as argument"
    sys.exit(-1)

  print "Folder to classify in positive/negative/spam comments: " + sys.argv[1]

  SOURCE_PATH = ROOT_PATH + "/" + sys.argv[1]
  DEST_PATH = ROOT_PATH + "/classified_" + sys.argv[1]

  if os.path.exists(DEST_PATH) == True:
    rmtree(DEST_PATH)

  os.mkdir(DEST_PATH, 0755)
 
  while True:
    childdirs = [int(childdir) for childdir in os.listdir(SOURCE_PATH)]
    childdirs = sorted(childdirs)
    for childdir in childdirs:
      print "Post " + str(childdir) + ":"

      COMMENTS_SOURCE_DIR = SOURCE_PATH + "/" + str(childdir) + "/comments"
      COMMENTS_DEST_DIR = DEST_PATH + "/" + str(childdir)

      if os.path.exists(COMMENTS_DEST_DIR) == True:
        rmtree(COMMENTS_DEST_DIR)

      os.mkdir(COMMENTS_DEST_DIR, 0755)

      if os.path.exists(COMMENTS_SOURCE_DIR):
        childfiles = [int(childfile) for childfile in os.listdir(COMMENTS_SOURCE_DIR)]
        childfiles = sorted(childfiles)

        POS_DIR = COMMENTS_DEST_DIR + "/positive"
        NEG_DIR = COMMENTS_DEST_DIR + "/negative"
        SPAM_DIR = COMMENTS_DEST_DIR + "/spam"   

        if os.path.exists(POS_DIR) == True:
          rmtree(POS_DIR)

        os.mkdir(POS_DIR, 0755)

        if os.path.exists(NEG_DIR) == True:
           rmtree(NEG_DIR)

        os.mkdir(NEG_DIR, 0755)

        if os.path.exists(SPAM_DIR) == True:
           rmtree(SPAM_DIR)

        os.mkdir(SPAM_DIR, 0755)

        for childfile in childfiles:
          COMMENT_SOURCE_FILE = COMMENTS_SOURCE_DIR + "/" + str(childfile)

          json_data = None
          json_file = open(COMMENT_SOURCE_FILE, "r")
          json_data = ast.literal_eval(json.loads(json.dumps(json_file.read())))

          print "Comment " + str(childfile)
          print "Content for comment " + str(childfile)
          print "\tMessage: [" + json_data["message"] + "]"

          if json_data.has_key("message_tags"):
            print "\tMessage tags: [" + str(json_data["message_tags"]) + "]"
 
          print "Type pos/neg/spam to move to positive/negative/spam directory."
          valid_answer = False
          while valid_answer == False:
             answer = raw_input()
             COMMENT_DEST_FILE = ""

             if answer == POS_CMD:
               COMMENT_DEST_FILE = POS_DIR + "/" + str(childfile)
               valid_answer = True
             if answer == NEG_CMD:
               COMMENT_DEST_FILE = NEG_DIR + "/" + str(childfile)
               valid_answer = True
             if answer == SPAM_CMD:
               COMMENT_DEST_FILE = SPAM_DIR + "/" + str(childfile)
               valid_answer = True

             if valid_answer == False:
               print "Type a valid command. Type pos/neg/spam to move to positive/negative/spam directory."

          copyfile(COMMENT_SOURCE_FILE, COMMENT_DEST_FILE)            

          json_file.close()


if __name__ == "__main__":
    main()
