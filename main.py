from flask import Flask, render_template, request, redirect, url_for, session
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


@app.route("/Posting_message/<email>", methods=["POST"])
def posting_messsage(email):
    if request.method == "POST":
        title = request.form["your_title"]
        mypost = request.form["title"]
        is_valid_session = user_session_authenticate()
        if  not is_valid_session:
            return redirect(url_for('logout'))

        MessagePost(Title=title, MyPost=mypost, EmailID = email).put()
    return redirect(url_for("getting_message", email=email))


@app.route("/Getting_message/<email>")
def getting_message(email):
    time.sleep(1)
    retrieved_post = MessagePost.query(MessagePost.EmailID==email).order(-MessagePost.Timestamp)
    return render_template("simple_post.html", retrieved_post = retrieved_post)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        password = request.form["user_password"]
        user_key = Registration(Name=name, Email=email, Password=password).put()
        return render_template("login_page.html")
    return render_template("Registration_form.html")


def session_track(user_email):
    session_list= SessionDb.query(SessionDb.User_Email==user_email, projection=[SessionDb.session_ID])
    count = 0
    for session in session_list:
        count+= 1
    return count


@app.route("/revoke")
def revoke_other_session():
    if "user" in session:
        my_record = SessionDb.query().filter(SessionDb.session_ID == session["user"]).get()
        my_session_list = SessionDb.query(SessionDb.User_Email == my_record.User_Email, SessionDb.session_ID != my_record.session_ID)
        for mysession in my_session_list:
            mysession.key.delete()
        return "session deleted in database"
    return "no session available"


@app.route("/validation", methods=["GET", "POST"])
def validate_user():
    error = ''
    if request.method == "POST":
        user_email = request.form["user_email"]
        user_password = request.form["user_password"]
        user_detail = Registration.query(Registration.Email == user_email).get()

        if user_detail and user_detail.Password == user_password:
            session_id = str(uuid.uuid4())
            session["user"] = session_id
            SessionDb(session_ID=session_id,User_Email=user_email).put()

            return redirect(url_for('homepage', user_email=user_email))

        else:
            error = "invalid credentials!"
    return render_template("login_page.html", error=error)


#  user_login
@app.route("/", methods=["GET" ,"POST"])
def login():
    if "user" in session:
        id = session["user"]

        return render_template("simple_post.html", session_list=0)
    return render_template("login_page.html")


@app.route("/home/<user_email>/")
def homepage(user_email):
    if "user" in session:
        time.sleep(1)
        a = session_track(user_email)
        retrieved_post = MessagePost.query(MessagePost.EmailID == user_email).order(-MessagePost.Timestamp)
        return render_template("simple_post.html", email=user_email, session_list=a, retrieved_post=retrieved_post)
    else:
        return redirect(url_for('logout'))


@app.route("/post")
def post_page():
    return render_template("simple_post.html")


# logging out and dropping session
@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        user_session_id = session["user"]
        delete_user_session = SessionDb.query().filter(SessionDb.session_ID == user_session_id).get()
        if delete_user_session:
            delete_user_session.key.delete()
            session.pop("user", None)
            return render_template("login_page.html")
        else:
             return render_template("login_page.html")

    return render_template("login_page.html")

# removing multiple session
def remove_multiple_session():
    if "user" in session:
        my_session_id = session["user"]
        all_session_list=SessionDb.query(SessionDb.session_ID)
        for check in all_session_list:
            if check.session_ID!= my_session_id:
                check.session_ID.key.delete()
            continue

        return True


if __name__ == "__main__":

    app.run(debug=True)
