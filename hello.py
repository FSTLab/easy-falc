"""Test flask."""
import sqlite3
from flask import g
from flask import Flask
from flask import request
from flask import render_template
import util
app = Flask(__name__)

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
    """Index page."""
    # for dictionnary in query_db('select * from Dictionnaires'):
    #     print dictionnary['code'], ' is ', dictionnary['libelle']
    text = ""
    try:
        text = util.clean(request.form['text'])
    except KeyError:
        print "No text received"

    lexems, warnings = util.lexems(text)

    # NOT a good way to do it. too slow.
    # words = []
    # for word in text.split(' '):
    #     w = query_db('select * from Mots where mot = ?',
    #                  [word.lower()], one=True)
    #     if w is not None:
    #         words.append((word, w['ponderation']))

    return render_template('index.html.j2', text=text, lexems=lexems,
                           warnings=warnings)
