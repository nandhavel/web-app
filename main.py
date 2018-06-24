from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google.appengine.ext import ndb
import uuid, os, time, logging

app = Flask(__name__)
app.secret_key = '\x00(\x86N\x86D\xb4S|\xe3\xc0"\x15\xc9v\xd2c\xda7\xa8\xea\xaaD\x04'


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
    session_ID = ndb.StringProperty(required=True)
    user_email = ndb.StringProperty(required=True)
    Login_time = ndb.DateTimeProperty(auto_now=True)
    ip_address = ndb.StringProperty(required=True)
    browser = ndb.StringProperty(required=True)


def user_session_authenticate():
    if "user" not in session:
        return False
    user_session_id = session["user"]
    session_exist = SessionDb.query().filter(SessionDb.session_ID == user_session_id).get()
    if session_exist:
        return True
    return False


@app.route("/Posting_message/<email>", methods=["POST"])
def posting_messsage(email):
    if request.method == "POST":
        title = request.form["your_title"]
        mypost = request.form["title"]
        is_valid_session = user_session_authenticate()
        if not is_valid_session:
            return redirect(url_for('logout'))

        MessagePost(Title=title, MyPost=mypost, EmailID=email).put()
    return redirect(url_for("getting_message", email=email))


@app.route("/Getting_message/<email>")
def getting_message(email):
    time.sleep(1)
    retrieved_post = MessagePost.query(MessagePost.EmailID == email).order(-MessagePost.Timestamp)
    return render_template("simple_post.html", retrieved_post=retrieved_post)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        password = request.form["user_password"]
        user_key = Registration(Name=name, Email=email, Password=password).put()
        return render_template("login_page.html")
    return render_template("Registration_form.html")


@app.route("/active_session")
def session_track():
    my_id = session.get('user')
    my_email = SessionDb.query().filter(SessionDb.session_ID == my_id).get().user_email
    session_list = SessionDb.query(SessionDb.user_email == my_email)
    session_detail = []
    for session_id in session_list:
        session_detail.append({"ip_address": session_id.ip_address,
                               "browser": session_id.browser,
                               "sign_in_time": session_id.Login_time,
                               "id": session_id.session_ID})
    return jsonify(session_detail)


@app.route("/revoke", methods=["GET", "POST"])
def revoke_other_session():
    if request.method == "POST":
        if "user" in session:
            other_session_id = request.json["id_param"]

            delete_session = SessionDb.query().filter(SessionDb.session_ID == other_session_id).get()
            delete_session.key.delete()
        return "other session deleted"
    return "send a post request"


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
            SessionDb(session_ID=session_id,
                      user_email=user_email,
                      ip_address=request.remote_addr,
                      browser=request.headers.get('User-Agent')).put()

            return redirect(url_for('homepage', user_email=user_email))

        else:
            error = "invalid credentials!"
    return render_template("login_page.html", error=error)


#  user_login
@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        id = session.get("user")

        return render_template("simple_post.html")
    return render_template("login_page.html")


@app.route("/home/<user_email>/")
def homepage(user_email):
    if "user" in session:
        time.sleep(1)
        # a = session_track(user_email)
        retrieved_post = MessagePost.query(MessagePost.EmailID == user_email).order(-MessagePost.Timestamp)
        return render_template("simple_post.html", email=user_email, retrieved_post=retrieved_post)
    else:
        return redirect(url_for('logout'))


@app.route("/post")
def post_page():
    return render_template("simple_post.html")


# logging out and dropping session
@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        user_session_id = session.get("user")
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
        my_session_id = session.get("user")
        all_session_list = SessionDb.query(SessionDb.session_ID)
        for check in all_session_list:
            if check.session_ID != my_session_id:
                check.session_ID.key.delete()
            continue

        return True


if __name__ == "__main__":
    app.run(debug=True)
