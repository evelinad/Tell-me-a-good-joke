#!/usr/bin/python

import json
import os
import urllib2

#replace the token if you get an OAuth exception
TOKEN = "CAACEdEose0cBAGO4vq6FVkCcj3ZBvgzH8lmAWYw1Yf0xfnqWsHDCWruDBjG6ZAdFGhK5dTq1MmEkcXtWG5cIisNIvXpj3QB8Br68ecWZANU35GUXRvZAGASn4tavFcZASJnHGO2ZCfdaggmYEFTPXj5orlci2cwoIrH7f82bSzxyWJshhK9qGwPrYQ1iZBDFEKYSHGJ2XtcdRPzxoDZBqx0m9PbTDMpqYH8ZD"
VERSION = "v2.2/"
GRAPH_URL = "https://graph.facebook.com/"

#POSITIVE_FBPAGES = ["jokeoftheday999", "9gag"]
POSITIVE_FBPAGES = ["jokeoftheday999"]
NEGATIVE_FBPAGES = ["363725540304160"]
#NEGATIVE_FBPAGES = []
NEUTRAL_FBPAGES = ["english.jokes", "funnyordie"]
FBPAGES = POSITIVE_FBPAGES + NEGATIVE_FBPAGES + NEUTRAL_FBPAGES
FBPAGES = ["funnyordie"]
MAX_POSTS_PER_PAGE = 200
MAX_COMMENTS_PER_POST = 200

ROOT_PATH = os.getcwd() + "/corpus"

def create_directory (directory):
  if not os.path.exists(directory):
    os.makedirs(directory)

def download_json(page_request):
  try:
    data = urllib2.urlopen(page_request).read()
    json_data = json.loads(data.encode('utf-8'))
  except Exception, exc:
    json_data = None
    print "Failed to download JSON: ", str(exc)
    f = open(ROOT_PATH + "/error.log", 'w+')
    f.write(str(exc))
    f.close()
  return json_data

def count_likes(likes):
  like_no = 0
  if likes == None:
    return "0"
  like_no += len(likes["data"])

  if likes.has_key("paging") == False:
    return str(likes_no)

  while(likes.has_key("paging") and likes["paging"].has_key("next")):
    likes = download_json(likes["paging"]["next"].decode('unicode-escape').encode('ascii'))
    if likes == None:
      print "\nDownloading this page encountered an error (the token expired, the page does not exist or you have no internet connection)\n"
      break
    like_no += len(likes["data"])

  return str(like_no)

def write_comment(post_path, comment, comment_no):
  #remove comments that have only tags for persons
  temp = "".join(comment["message"].split())

  if comment.has_key("message_tags"):
    for tag in comment["message_tags"]:
      temp = temp.replace("".join(tag["name"].split()), "")
    if not temp:
      return False

  f = open(post_path + '/comments/' + str(comment_no), 'w+')
  f.write(str(comment).encode("utf8"))
  f.close()
  return True

def store_comments(post_path, comments):
  create_directory(post_path + "/comments")

  comment_no = 1
  for comment in comments["data"]:
    result = write_comment(post_path, comment, comment_no)
    if result:
      comment_no += 1

  if (comments.has_key('paging')) == False:
    return

  while (comments.has_key('paging') and comments['paging'].has_key('next')) and comment_no < MAX_COMMENTS_PER_POST:
    comments = download_json(comments["paging"]["next"].decode('unicode-escape').encode('ascii'))
    if comments == None:
      print "\nDownloading this page encountered an error (the token expired, the page does not exist or you have no internet connection)\n"
      break
    for comment in comments["data"]:
      result = write_comment(post_path, comment, comment_no)
      if result:
        comment_no += 1

def store_post(page_path, post, post_no):
   post_path = page_path + "/" + str(post_no)
   if os.path.exists(post_path):
     return
   create_directory(post_path)
   f = open(post_path + '/' + 'info', 'w+')
   if (post.has_key("id")):
     f.write("id: " + post["id"].encode("utf8") + "\n")
   if (post.has_key("created_time")):
     f.write("created_time: " + post["created_time"].encode("utf8") + "\n")
   if (post.has_key("likes")):
     f.write("likes: " + count_likes(post["likes"]) + "\n")
   if (post.has_key("shares")):
     f.write("shares: " + str(post["shares"]["count"]) + "\n")
   if (post.has_key("actions")):
     f.write("actions: " + str(post["actions"]).encode("utf8") + "\n")
   if (post.has_key("message")):
     f.write("message: " + post["message"].encode("utf8") + "\n")
   if (post.has_key("description")):
     f.write("description: " + post["description"].encode("utf8") + "\n")
   if (post.has_key("picture")):
     f.write("picture: " + post["picture"].encode("utf8") + "\n")
   if (post.has_key("comments")):
     store_comments(post_path, post["comments"])
   f.close()

def store_fbpage(page_request, page_path):
  posts = download_json(page_request)
  print page_request
  if posts == None:
    print "\nDownloading this page encountered an error (the token expired, the page does not exist or you have no internet connection)\n"
    return

  print page_path
  post_no = 1

  for post in posts["data"]:
    store_post(page_path, post, post_no)
    print post_no
    post_no += 1

  if posts.has_key('paging'):
    return

  while (posts.has_key('paging') and posts['paging'].has_key('next')) and post_no < MAX_POSTS_PER_PAGE:
    posts = download_json(posts["paging"]["next"].decode('unicode-escape').encode('ascii'))
    for post in posts["data"]:
      store_post(page_path, post, post_no)
      print post_no
      post_no += 1

def main():
  for fbpage in FBPAGES:
    fbpage_path = ROOT_PATH + "/" + fbpage

    create_directory(fbpage_path)

    page_request = GRAPH_URL + VERSION + fbpage + "/posts?access_token=" + TOKEN
    print page_request

    store_fbpage(page_request, fbpage_path)

if __name__ == "__main__":
    main()
