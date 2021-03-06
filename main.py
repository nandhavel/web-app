from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google.appengine.ext import ndb
import uuid, os, time, logging

app = Flask(__name__)
app.secret_key = '\x00(\x86N\x86D\xb4S|\xe3\xc0"\x15\xc9v\xd2c\xda7\xa8\xea\xaaD\x04'


class Registration(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)


class MessagePost(ndb.Model):
    title = ndb.StringProperty(required=True)
    my_post = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    email_id = ndb.StringProperty(required=True)


class SessionDb(ndb.Model):
    user_session_id = ndb.StringProperty(required=True)
    user_email = ndb.StringProperty(required=True)
    login_time = ndb.DateTimeProperty(auto_now=True)
    ip_address = ndb.StringProperty(required=True)
    browser = ndb.StringProperty(required=True)


def user_session_authenticate():
    if "user" not in session:
        return False
    user_session_id = session.get("user")
    session_exist = SessionDb.query().filter(SessionDb.user_session_id == user_session_id).get()
    if session_exist:
        return True
    return False


@app.route("/Posting_message/<email>", methods=["POST"])
def posting_messsage(email):
    if request.method == "POST":
        title = request.form.get("your_title")
        mypost = request.form.get("title")
        is_valid_session = user_session_authenticate()
        if not is_valid_session:
            return redirect(url_for('logout'))
        MessagePost(title=title, my_post=mypost, email_id=email).put()
        time.sleep(1)
        retrieved_post = MessagePost.query(MessagePost.email_id == email).order(-MessagePost.timestamp)
        return render_template("simple_post.html", retrieved_post=retrieved_post,email = email)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("user_name")
        email = request.form.get("user_email")
        password = request.form.get("user_password")
        user_key = Registration(name=name, email=email, password=password).put()
        return render_template("login_page.html")
    return render_template("Registration_form.html")


@app.route("/users/active_session")
def session_track():
    try:
        if "user" in session:
            my_id = session.get('user')
            my_email = SessionDb.query().filter(SessionDb.user_session_id == my_id).get().user_email
            logging.info(SessionDb)
            logging.info(my_email)
            session_list = SessionDb.query(SessionDb.user_email == my_email)
            session_detail = []
            for session_id in session_list:
                if session_id.user_session_id == my_id:

                    session_detail.append({"ip_address": session_id.ip_address,
                                           "browser": session_id.browser,
                                           "sign_in_time": session_id.login_time,
                                           "id": session_id.user_session_id,
                                           "current_session": True})
                else:
                    session_detail.append({"ip_address": session_id.ip_address,
                                           "browser": session_id.browser,
                                           "sign_in_time": session_id.login_time,
                                           "id": session_id.user_session_id,
                                           "current_session": False})
            return jsonify(session_detail)
        else:
            dict1 = {
                "success": False,
                "url": url_for('logout')
            }

            return jsonify(dict1)
    except AttributeError:
        dict1 = {
            "success": False,
            "url": url_for('logout')
        }

        return jsonify(dict1)


@app.route("/users/revoke", methods=["POST"])
def revoke_other_session():
    is_valid_session = user_session_authenticate()
    logging.info(is_valid_session)
    if not is_valid_session:
        dict = {
            'success': False,
            'url': url_for('logout')
        }
        return jsonify(dict)
    else:
        other_session_id = request.json.get("id_param")
        delete_session = SessionDb.query().filter(SessionDb.user_session_id == other_session_id).get()
        delete_session.key.delete()

        dict = {
            'success': True,
            'message': "other session deleted"
        }
        return jsonify(dict)


# @app.route('/v1/session/<id_>', methods=['DELETE'])
# def delete_session(id_):
#     session_db = SessionDb.get_by_id(id_)
#     if not session_db:
#         return jsonify({
#             'success': False,
#             'error': 'invalid session id'
#         })
#     session_db.key.delete()
#     return jsonify({
#         'success': True
#     })



@app.route("/user/validation", methods=["GET", "POST"])
def validate_user():
    error = ''
    if request.method == "POST":
        user_email = request.form.get("user_email")
        user_password = request.form.get("user_password")
        user_detail = Registration.query(Registration.email == user_email).get()

        if user_detail and user_detail.password == user_password:
            session_id = str(uuid.uuid4())
            session["user"] = session_id
            SessionDb(user_session_id=session_id,
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
    try:
        if "user" in session:
            id = session.get("user")
            user_email = SessionDb.query().filter(SessionDb.user_session_id == id).get().user_email
            return redirect(url_for("homepage", user_email = user_email))
        return render_template("login_page.html")
    except AttributeError:
        return redirect(url_for('logout'))


@app.route("/home/<user_email>/")
def homepage(user_email):
    try:
        if "user" in session:
            id = session.get("user")
            time.sleep(1)
            user_session = SessionDb.query().filter(SessionDb.user_session_id == id).get().user_session_id
            logging.info(user_session)
            if user_session:
                time.sleep(1)
                retrieved_post = MessagePost.query(MessagePost.email_id == user_email).order(-MessagePost.timestamp)
                return render_template("simple_post.html", email=user_email, retrieved_post=retrieved_post)
            else:
                return redirect(url_for("logout"))
        else:
            return redirect(url_for('logout'))
    except AttributeError:
        return redirect(url_for('logout'))


# logging out and dropping session
@app.route("/user/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":

        if "user" in session:
            user_session_id = session.get("user")
            delete_user_session = SessionDb.query().filter(SessionDb.user_session_id == user_session_id).get()
            if delete_user_session:
                delete_user_session.key.delete()
                session.pop("user", None)
                return render_template("login_page.html")
            else:
                return render_template("login_page.html")
        return render_template("login_page.html")
    return render_template("login_page.html")


# removing multiple session
def remove_multiple_session():
    if "user" in session:
        my_session_id = session.get("user")
        all_session_list = SessionDb.query(SessionDb.user_session_id)
        for check in all_session_list:
            if check.user_session_id != my_session_id:
                check.user_session_id.key.delete()
            continue

        return True


if __name__ == "__main__":
    app.run(debug=True)
