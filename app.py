import hashlib
import os
import string
import random

from flask import Flask, url_for, render_template, request, session, redirect, abort, make_response
from datetime import timedelta, datetime
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plsgivemeagoodmark'
#app.config['FLASK_RUN_CERT'] = #/etc/letsencrypt/live/webtech-13.napier.ac.uk/fullchain.pem'
#app.config['FLASK_RUN_KEY'] = '/etc/letsencrypt/live/webtech-13.napier.ac.uk/privkey.pem'

# connect to sql database
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='beanbefore')

def is_valid_login(request):
    token = request.cookies.get('auth_token')
    if token is None:
        return False
    else:
        if check_token_expiration(token):
            return True
        else:
            return False

def get_posts_for_user(userid):

    db.connect()
    cursor = db.cursor()

    if userid == -1:
        cursor.execute("SELECT * FROM posts ORDER BY postid DESC")
    else:
        cursor.execute("SELECT * FROM posts WHERE authorid != %s", userid)

    #check if  any posts
    if cursor.rowcount == 0:
        return None
    else:
        posts = cursor.fetchall()

        post_list = []
        for post in posts:
            post_dict = {}
            post_dict['postid'] = post[0]
            post_dict['authorid'] = post[1]
            post_dict['time'] = post[2]
            post_dict['heading'] = post[3]
            post_dict['caption'] = post[4]
            post_dict['media'] = post[5]

            post_list.append(post_dict)
        return post_list

def get_own_posts(userid):
    db.connect()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE authorid = %s", userid)
    if cursor.rowcount == 0:
        return None
    else:
        posts = cursor.fetchall()

        post_list = []
        for post in posts:
            post_dict = {}
            post_dict['postid'] = post[0]
            post_dict['authorid'] = post[1]
            post_dict['time'] = post[2]
            post_dict['heading'] = post[3]
            post_dict['caption'] = post[4]
            post_dict['media'] = post[5]

            post_list.append(post_dict)
        return post_list


def get_user_data(token):
    # connect to db join auth_token and userid on userid and select userid, username, email, password
    db.connect()
    cursor = db.cursor()
    sql = "SELECT users.userid, email, username, token FROM users JOIN auth_tokens ON users.userid = auth_tokens.userid WHERE token = %s"
    cursor.execute(sql, (token))
    data = cursor.fetchone()
    db.close()
    # convert data to set
    data = {'userid': data[0], 'email':data[1] ,'username': data[2], 'token': data[3]}

    return data


# def is_valid_login(request):
#     token = request.cookies.get('auth_token')
#     if token is None:
#         return False
#     else:
#         if check_token_expiration(token):
#             return True
#         else:
#             return False


def create_auth_token(userid):
    # generate random token
    token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    # generate expiration date
    expiration = datetime.now() + timedelta(days=1)  # 1 day expiration
    # insert token into database
    db.connect()
    cursor = db.cursor()
    sql = "INSERT INTO auth_tokens (userid, token, expiration) VALUES (%s, %s, %s)"
    cursor.execute(sql, (userid, token, expiration))
    db.commit()
    db.close()
    return token


def force_expire_token(token):
    print("clearing users tokens")
    userid = get_userid_from_token(token)
    db.connect()
    cursor = db.cursor()
    # delete all tokens where userid = userid
    sql = "DELETE FROM auth_tokens WHERE userid = " + str(userid)
    cursor.execute(sql)
    db.commit()
    db.close()
    return True


# true means token is valid
def check_token_expiration(token):
    db.connect()
    cursor = db.cursor()
    sql = "SELECT expiration FROM auth_tokens WHERE token = %s"
    cursor.execute(sql, token)
    expiration = cursor.fetchone()

    if expiration is not None:
        expiration = datetime.strptime(expiration[0], '%Y-%m-%d %H:%M:%S.%f')
        if expiration < datetime.now():
            return False
        else:
            return True
    else:
        return False


# Register User
def register_user(username, hash, email):

    salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))

    if check_if_username_or_email_exists(username, email):
        return 2  # Throw error

    db.connect()
    cursor = db.cursor()

    # find largest userid - add 1 to it
    sql = "SELECT MAX(userid) FROM users"
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count is None:
        count = 0
    else:
        count += 1

    # salt and hash password
    hash = hashlib.sha512(salt.encode('utf-8') + hash.encode('utf-8')).hexdigest()


    sql = "INSERT INTO users (userid, username, salt, hash, email) VALUES (%s, %s, %s, %s, %s)"
    val = (count, username, salt, hash, email)
    cursor.execute(sql, val)
    db.commit()
    db.close()

    # Create user data dir
    create_user_directory(count)
    print(count)

    return 1


def check_if_username_or_email_exists(username, email):
    db.connect()
    cursor = db.cursor()

    sql = "SELECT COUNT(*) FROM users WHERE username = %s OR email = %s"
    val = (username, email)
    cursor.execute(sql, val)
    result = cursor.fetchone()[0]
    db.close()

    # if result is greater than 0, then username or email already exists
    if result > 0:
        return 1
    else:
        return 0


# Get cookies
def get_userid_cookie(request):
    userid = request.cookies.get('userid')
    return userid


def handle_login(email, password):

    db.connect()
    cursor = db.cursor()

    # get salt and hash from database
    sql = "SELECT salt, hash FROM users WHERE email = %s"
    cursor.execute(sql, email)
    data = cursor.fetchone()
    db.close()

    # if data is None, then email is not in database
    if data is None:
        return 0

    # salt and hash password
    salthash = data[0] + password
    hash = hashlib.sha512(salthash.encode('utf-8')).hexdigest()

    # if hash is not equal to hash in database, then password is incorrect
    if hash == data[1]:
        return 1
    else:
        return 0


def get_userid_from_token(token):
    db.connect()
    cursor = db.cursor()

    sql = "SELECT userid FROM auth_tokens WHERE token = %s"
    cursor.execute(sql, token)
    result = cursor.fetchone()
    db.close()

    if result is not None:
        return result[0]
    else:
        return 0


def get_username(userid):
    db.connect()
    cursor = db.cursor()

    sql = "SELECT username FROM users WHERE userid = %s"
    val = (userid)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    db.close()

    return result[0]


def get_username_from_email(email):
    db.connect()
    cursor = db.cursor()

    sql = "SELECT username FROM users WHERE email = %s"
    val = (email)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    db.close()

    return str.encode(result[0])


def get_hash(userid):
    db.connect()
    cursor = db.cursor()

    sql = "SELECT hash FROM users WHERE userid = %s"
    val = (userid)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    db.close()

    return result[0]


def get_userid(email):
    db.connect()
    cursor = db.cursor()

    sql = "SELECT userid FROM users WHERE email = %s"
    val = (email)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    db.close()

    return str.encode(str(result[0]))

# create user directory in static/data/users/<userid>
def create_user_directory(userid):
    # current working directory
    cwd = os.getcwd()

    path = cwd + "/static/data/users/" + str(userid)
    if not os.path.exists(path):
        os.makedirs(path)

def get_next_postid():
    db.connect()
    cursor = db.cursor()

    sql = "SELECT MAX(postid) FROM posts"
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count is None:
        count = 0
    else:
        count += 1

    return count

def insert_new_post(postid, authorid, time, heading, caption, media):
    db.connect()
    cursor = db.cursor()

    sql = "INSERT INTO posts (postid, authorid, time, heading, caption, media) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (postid, authorid, time, heading, caption, media)
    cursor.execute(sql, val)
    db.commit()
    db.close()

# Saves post image to static/data/users/<userid>/<postid>.jpg or .png
def save_post_image(userid, postid, image):

    # current working directory
    cwd = os.getcwd()

    # check image type
    if image.content_type == "image/jpeg":
        ext = ".jpg"
    elif image.content_type == "image/png":
        ext = ".png"
    else:
        return 0

    path = "/static/data/users/" + str(userid) + "/" + str(postid) + ext
    image.save(cwd + path)

    return path

@app.route('/')
@app.route('/home')
@app.route('/index')
def hello_world():
    if is_valid_login(request):
        return redirect(url_for('feed'))
    else:
        posts = get_posts_for_user(-1)
        return render_template('index.html',posts=posts)

@app.route('/feed')
def feed():
    auth_token = request.cookies.get('auth_token')

    if auth_token is None:
        posts = get_posts_for_user(-1)
        return render_template('index.html',posts=posts)
    else:
        if check_token_expiration(auth_token):
            data = get_user_data(auth_token)
            posts = get_posts_for_user(data['userid'])
            return render_template('home-loggedin.html', data=data, posts=posts)
        else:
            posts = get_posts_for_user(-1)
            return render_template('index.html',posts=posts)




@app.route('/feed/newpost', methods=['POST', 'GET'])
@app.route('/profile/newpost', methods=['POST', 'GET'])
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    # validate login
    if is_valid_login(request):
        data = get_user_data(request.cookies.get('auth_token'))
        if request.method == 'POST':

            if request.form['heading'] == "" or request.form['caption'] == "":
                return "Please enter a heading and caption", 500

            # insert new post
            postid = get_next_postid()
            authorid = get_userid_from_token(request.cookies.get('auth_token'))
            print(str(authorid) + str(postid))

            # load image from 'media' in form request.form['media']
            if request.files['image'] is not None:
                print("not none")
                path = save_post_image(authorid, postid, request.files['image'])
            else:
                print("none")
                path = ""

            time = datetime.now()
            heading = request.form['heading']
            caption = request.form['caption']
            media = path
            insert_new_post(postid, authorid, time, heading, caption, media)
            return redirect(url_for('feed')), 301
        else:
            return render_template('newpost.html', data=data)
    else:
        return redirect(url_for('login'))





@app.route('/messages')
@app.route('/404')
@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


@app.route('/signout')
def signout():
    print("logging out")
    auth_token = request.cookies.get('auth_token')
    if auth_token is not None:
        force_expire_token(auth_token)
    resp = make_response(render_template('signed_out.html'))
    resp.set_cookie('auth_token', '', expires=0)
    return resp, 200


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        result = handle_login(request.form['email'], request.form['password'])
        if result == 1:
            resp = make_response(redirect('/profile'))
            resp.set_cookie('auth_token', create_auth_token(get_userid(request.form['email'])))
            return resp, 301
        else:
            string = "Login Failed - please check your password and try again. Email: " + request.form['email']
            return string, 500
    else:
        # check if already logged in
        if is_valid_login(request):
            return redirect(url_for('profile'))
        else:
            return render_template('login.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        result = register_user(request.form['username'], request.form['password'], request.form['email'])
        if result == 1:
            return redirect(url_for('login')), 301
        elif result == 0:
            return "Something went wrong...", 500
        elif result == 2:
            return "Username or email already exists", 500
    else:
        return render_template('register.html')


@app.route("/profile", methods=['POST', 'GET'])
def profile():
    logged_in = is_valid_login(request)

    if logged_in:
        data = get_user_data(request.cookies.get('auth_token'))
        posts = get_own_posts(get_userid_from_token(request.cookies.get('auth_token')))
        return render_template('profile.html', data=data, posts=posts), 200
    else:
        return redirect(url_for('login')), 301


@app.route('/time')
def hello_time():
    now = datetime.now().time()
    return ("The time is: " + str(now))


# Authentication
# Feed
# NewPost
# Register
# Profile


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)


