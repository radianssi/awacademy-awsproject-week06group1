from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from datetime import datetime
import boto3
import logging
from botocore.exceptions import ClientError
import json
import psycopg2
import os

logger = logging.getLogger(__name__)

def get_secret_value(name):   
        client = boto3.client("secretsmanager", region_name="ap-southeast-2")

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
    data = get_secret_value("w6pg1_rds-secret")
    conn = psycopg2.connect("host=%s dbname=%s port=%s user=%s password=%s" % (data['host'], data['dbname'], data['port'], data['username'], data['password']))
    return conn


def get_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    SQL = 'SELECT * FROM posts WHERE id = %s'
    cursor.execute(SQL,(post_id,))
    post = cursor.fetchone()
    conn.close()
    dict_post = {"id" : post[0], "created": format_date(post[1]), "title":post[2], "content":post[3]}
    if post is None:
        abort(404)
    return dict_post


app = Flask(__name__)
app.config['SECRET_KEY'] = 'do_not_touch_or_you_will_be_fired'


# this function is used to format date to a finnish time format from database format
# e.g. 2021-07-20 10:36:36 is formateed to 20.07.2021 klo 10:36
def format_date(post_date):
    post_date = post_date.replace(microsecond=0)
    post_date = str(post_date)
    isodate = post_date.replace(' ', 'T')
    newdate = datetime.fromisoformat(isodate)
    return newdate.strftime('%d.%m.%Y') + ' klo ' + newdate.strftime('%H:%M')


# this index() gets executed on the front page where all the posts are
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    # we need to iterate over all posts and format their date accordingly
    #dictrows = [dict(row) for row in posts]
    postcreated_list = []
    for post in posts:
        # using our custom format_date(...)
        postcreated_list.append({"id": post[0], "created": format_date(post[1]), "title":post[2], "content":post[3]})
        #postcreated_list.append(format_date(post[1]))
    return render_template('index.html', posts=postcreated_list)


# here we get a single post and return it to the browser
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    #post['created'] = format_date(post['created'])
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
            cursor = conn.cursor()
            cursor.execute('INSERT INTO posts (title, content) VALUES (%s, %s)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)
    print(post)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE posts SET title = %s, content = %s'
                         ' WHERE id = %s',
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
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)