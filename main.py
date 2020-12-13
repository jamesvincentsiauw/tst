from flask import Flask, request, jsonify, url_for, session, redirect, render_template
from flaskext.mysql import MySQL
from flask_oauth import OAuth
import logging
import time
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'secretkey'
oauth = OAuth()
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'yubelajar'
app.config['MYSQL_DATABASE_HOST'] = 'tst_db_nama_1'
app.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(app)
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key='924675044568-a4hm7p8bi0d54d1rpulp8ekgoieeivso.apps.googleusercontent.com',
                          consumer_secret='YDlo2Uv89PQcrauCjuTWko5L')


@app.route('/login')
def login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route('/authorized')
@google.authorized_handler
def authorized(resp):
    print(resp)
    access_token = resp['access_token']
    print(access_token)
    session['access_token'] = access_token, ''
    # return access_token
    return redirect(url_for('index'))


@app.route('/')
def landing():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S') + ' landing akses')
    return render_template('index.html')
# route root


@app.route('/home')
def index():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S') + ' home akses')
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return 'HELLO'


# GET, POST, PUT, DELETE http request method
@app.route('/user', methods=['GET'])
def get_user():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM authors limit 10'

    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    result_baru = []

    for author in result:
        author_baru = {
            'id': author[0],
            'first-name': author[1],
            'last-name': author[2],
            'email': author[3]
        }
        result_baru.append(author_baru)

    return {'hasil': result_baru}


@app.route('/mahasiswa', methods=['GET'])
def mahasiswa():
    mahasiswa_nama = request.args.get('nama')
# localhost:5000/mahasiswa?nama=vincent


@app.route('/create', methods=['POST'])
def insert_author():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    firstname = request.form['first-name']
    lastname = request.form['last-name']
    email = request.form['email']
    birthdate = request.form['birthdate']

    query = 'INSERT INTO authors (first_name, last_name, email, birthdate) VALUES (%s, %s,%s,%s)'
    data = (firstname, lastname, email, birthdate)

    cursor.execute(query, data)
    conn.commit()
    conn.close()

    result = {
        'firstname': firstname,
        'lastname': lastname,
        'email': email,
        'birthdate': birthdate
    }
    return {'hasil': result}


if __name__ == "__main__":
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
