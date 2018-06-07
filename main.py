from flask import Flask, render_template, request, redirect, url_for
from google.appengine.ext import ndb
import time


app = Flask(__name__)


class MessagePost(ndb.Model):
    Title = ndb.StringProperty(required=True)
    MyPost = ndb.StringProperty(required=True)
    Timestamp = ndb.DateTimeProperty(auto_now_add=True)


@app.route("/Posting_message", methods=["POST"])
def posting_messsage():
    title = request.form["your_title"]
    mypost = request.form["title"]

    post_key = MessagePost(Title=title, MyPost=mypost).put()

    return  redirect(url_for("getting_message"))

@app.route("/Getting_message")
def getting_message():
    retrieved_post = MessagePost.query().order(-MessagePost.Timestamp)

    return render_template("simple_post.html", retrieved_post=retrieved_post)





@app.route("/")
def post_page():
    # return 'Hello World'
    return render_template("simple_post.html")


if __name__ == "__main__":
    app.run(debug=True)