from flask import Flask, render_template, request, redirect, url_for, make_response, session, flash, app
from datetime import timedelta
from google.appengine.ext import ndb
import uuid,os,time



app = Flask(__name__)
app.secret_key = os.urandom(24)


class Registration(ndb.Model):
    Name = ndb.StringProperty(required=True)
    Email = ndb.StringProperty(required=True)
    Password = ndb.StringProperty(required=True)


class MessagePost(ndb.Model):
    Title = ndb.StringProperty(required=True)
    MyPost = ndb.StringProperty(required=True)
    Timestamp = ndb.DateTimeProperty(auto_now_add=True)
    EmailID = ndb.StringProperty(required=True)


class SessionDb(ndb.Model):
    session_ID =ndb.StringProperty(required = True)
    User_Email = ndb.StringProperty(required = True)
    Login_time = ndb.DateTimeProperty(auto_now =True)





def user_session_authenticate():
    if "user" not in session:
        return False
    user_session_id  = session["user"]
    session_exist = SessionDb.query().filter(SessionDb.session_ID==user_session_id).get()
    if session_exist:
        return  True
    return False



#
@app.route("/Posting_message/<email>", methods=["POST"])
def posting_messsage(email):
    if request.method == "POST":
        title = request.form["your_title"]
        mypost = request.form["title"]
        is_valid_session = user_session_authenticate()
        if  not is_valid_session:
            return render_template("login_page.html")

        MessagePost(Title=title, MyPost=mypost, EmailID = email).put()
    return redirect(url_for("getting_message", email=email))


@app.route("/Getting_message/<email>")
def getting_message(email):
    time.sleep(1)
    retrieved_post = MessagePost.query(MessagePost.EmailID==email).order(-MessagePost.Timestamp)
    # print(type(retrieved_post.Title))
    return render_template("simple_post.html", retrieved_post = retrieved_post)
    # return render_template("simple_post.html", retrieved_post=retrieved_post)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        password = request.form["user_password"]
        user_key = Registration(Name=name, Email=email, Password=password).put()
        return render_template("login_page.html")
    return render_template("Registration_form.html")


# def setting_cookies():
#      user_id = str(uuid.uuid4())
#      getting_message= url_for("getting_message",
#      response_object = make_response(render_template("simple_post.html", posts=posts))
#      response_object.set_cookie("user_id", value=user_id)
#      return response_object





@app.route("/validation", methods=["GET", "POST"])
def validate_user():
    if request.method == "POST":

        user_email = request.form["user_email"]
        user_password = request.form["user_password"]
        user_detail = Registration.query(Registration.Email == user_email).get()
        if user_detail and user_detail.Password == user_password:
            session_id = str(uuid.uuid4())
            session["user"] = session_id
            # make_session_permanent()
            SessionDb(session_ID=session_id,User_Email =user_email).put()
            return render_template("simple_post.html", email=user_email)

    return ("invalid credentials!")


a = {}
a.update({"a": 1,"b": 2 })

@app.route("/", methods=["GET" ,"POST"])
def login():
    if "user" in session:
        id = session["user"]

        return render_template("simple_post.html")
    return render_template("login_page.html")


@app.route("/post")
def post_page():
    return render_template("simple_post.html")


# logging out and dropping session
@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        user_session_id = session["user"]
        delete_user_session = SessionDb.query().filter(SessionDb.session_ID == user_session_id).get()
        delete_user_session.key.delete()
        session.pop("user", None)
    return render_template("login_page.html")

# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=1)


if __name__ == "__main__":

    app.run(debug=True)
  