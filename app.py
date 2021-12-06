from flask import Flask, url_for, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
@app.route('/hello/')
def hello():
    return "Hello!"


@app.route('/hello/<name>')
def hello_world(name=None):
    user = {'name': name}
    return render_template('index.html', user=user)


@app.route('/time')
def hello_time():
    now = datetime.now().time()
    return ("The time is: " + str(now))

# Authentication
# Feed
# NewPost
# Interaction
# Register
# Profile
# Messages
# Messages/<recipient_id>



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)