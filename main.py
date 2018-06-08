from flask import Flask, render_template, request, redirect, url_for
from google.appengine.ext import ndb



app = Flask(__name__)

class Registration(ndb.Model):
    Name = ndb.StringProperty(required=True)
    Email = ndb.StringProperty(required=True)
    Password = ndb.StringProperty(required=True)


class MessagePost(ndb.Model):
    Title = ndb.StringProperty(required=True)
    MyPost = ndb.StringProperty(required=True)
    Timestamp = ndb.DateTimeProperty(auto_now_add=True)

@app.route("/Posting_message", methods=["POST"])
def posting_messsage():
    title = request.form["your_title"]
    mypost = request.form["title"]
    post_key = MessagePost(Title=title, MyPost=mypost).put()
    return redirect(url_for("getting_message"))


@app.route("/Getting_message")
def getting_message():
    retrieved_post = MessagePost.query().order(-MessagePost.Timestamp)

    return render_template("simple_post.html", retrieved_post=retrieved_post)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name =request.form["user_name"]
        email =request.form["user_email"]
        password =request.form["user_password"]
        user_key = Registration(Name=name,Email=email,Password=password).put()
        return render_template("login_page.html")
    return render_template("Registration_form.html")




@app.route("/validation", methods=["GET","POST"])
def validate_user():
    if request.method == 'POST':
        user_email = request.form["user_email"]
        user_password = request.form["user_password"]
        user_detail =Registration.query(Registration.Email == user_email).get()
        if user_detail and user_detail.Password == user_password:
                return  render_template("simple_post.html")
        else: return "invalid credentials!"
    return  render_template("login_page.html")


@app.route("/", methods=["POST"])
def login():
    return render_template("login_page.html")

@app.route("/post")
def post_page():

    return render_template("simple_post.html")


if __name__ == "__main__":
    app.run(debug=True)