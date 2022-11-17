from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from datetime import datetime
from init_db import do_init
import boto3
import logging
from botocore.exceptions import ClientError
import json
import psycopg2

logger = logging.getLogger(__name__)

def get_secret_value(name):   
        client = boto3.client("secretsmanager")

        try:
            kwargs = {'SecretId': name}
            response = client.get_secret_value(**kwargs)
            logger.info("Got value for secret %s.", name)
        except ClientError:
            logger.exception("Couldn't get value for secret %s.", name)
            raise
        else:
            return json.loads(response['SecretString'])

def get_db_connection():
    data = get_secret_value("w6pg1_rds")
    conn = psycopg2.connect("host=%s database=%s port=%s user=%s password=%s" % (data['host'], data['dbname'], data['port'], data['username'], data['password']))
    return conn

#


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
do_init()
app.config['SECRET_KEY'] = 'do_not_touch_or_you_will_be_fired'


# this function is used to format date to a finnish time format from database format
# e.g. 2021-07-20 10:36:36 is formateed to 20.07.2021 klo 10:36
def format_date(post_date):
    isodate = post_date.replace(' ', 'T')
    newdate = datetime.fromisoformat(isodate)
    return newdate.strftime('%d.%m.%Y') + ' klo ' + newdate.strftime('%H:%M')


# this index() gets executed on the front page where all the posts are
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    # we need to iterate over all posts and format their date accordingly
    dictrows = [dict(row) for row in posts]
    for post in dictrows:
        # using our custom format_date(...)
        post['created'] = format_date(post['created'])
    return render_template('index.html', posts=dictrows)


# here we get a single post and return it to the browser
@app.route('/<int:post_id>')
def post(post_id):
    post = dict(get_post(post_id))
    return render_template('post.html', post=post)


# here we create a new post
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


# Here we delete a SINGLE post.
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts')
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))
