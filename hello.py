"""Test flask."""
import sqlite3
from flask import g
from flask import Flask
from flask import request
from flask import render_template
import util
from lxml import html
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
    """Index page."""
    # for dictionnary in query_db('select * from Dictionnaires'):
    #     print dictionnary['code'], ' is ', dictionnary['libelle']
    text = ""
    try:
        t = request.form['text']
        text = html.fromstring(t).text_content()
        # text = util.clean(request.form['text'])
    except KeyError:
        print "No text received"

    words, warnings = util.process(text)

    # TODO: Find low ponderation words. Then offer synonyms, if possible.
    # if text is not "":
    #     im = ','.join(['?'] * len(words))
    #     print(im)
    #     query = 'select * from Mots where mot in ({})'.format(im)
    #     mots = query_db(query, [word[0].lower() for word in words])
    #     for word, mot in zip(words, mots):
    #         if int(mot['ponderation']) < 10.0:
    #             index = len(warnings)
    #             start = word[1]
    #             snippet = word[0]
    #             end = start + len(snippet) - 1
    #             comment = "Utilisez des mots plus courants."
    #             warnings.append(Warning(index, start, end, comment, snippet))

    return render_template('index.html.j2',
                           text=text,
                           warnings=warnings,
                           css='index',
                           js='index')
