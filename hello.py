"""Test flask."""
import sqlite3
from flask import g
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
import util
from lxml import html
app = Flask(__name__)
util.init_thesaurus()

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

DATABASE = 'dictionaries.db'


##############################################
#                  Database                  #
##############################################
def get_db():
    """Get db connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

    return db


def query_db(query, args=(), one=False):
    """Query db."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    print(rv)
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    """Close db connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


##############################################
#                Flask views                 #
##############################################
@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Index page.
    """

    return render_template('index.html.j2',
                           text='',
                           warnings=[],
                           css='index',
                           js='index')


@app.route('/translate', methods=['POST'])
def translate():
    """
    This translates.
    """
    text = request.form['text']
    # text = html.fromstring(t).text_content()
    print(text)
    warnings = util.process(text)
    return jsonify(text=text, warnings=[w.serialize() for w in warnings])

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize text.
    """
    text = request.form['text']
    summary = util.summarize(text)
    warnings = util.process(summary)
    return jsonify(summary=summary, warnings=[w.serialize() for w in warnings])
