"""Test flask."""
import sqlite3
from flask import g
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from lxml import html

import falcore

app = Flask(__name__)
DATABASE = 'falc_modules/res/dictionaries.db'

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



falcore.init_thesaurus()
#
# class Mot(db.Model):
#     numero = db.Column(db.Integer, primary_key=True)
#     fk_dictionnaires = db.Column(db.Integer, db.ForeignKey('Dictionnaires.numero'))
#     dictionnaire = db.relationship('Dictionnaire',
#         backref=db.backref('mots', lazy=True))
#     mot = db.Column(db.String(50), nullable=False)
#     ponderation = db.Column(db.Float, nullable=False)
#
#     def __repr__(self):
#         return '<Mot %r>' % self.mot
#
# class Dictionnaire(db.Model):
#     numero = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(20), nullable=False)
#     ilbelle = db.Column(db.String(50))

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

falc = falcore.Falc()

##############################################
#                Flask views                 #
##############################################
@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Index page.
    """

    categories = falcore.get_categories()
    categories = {key: value.serialize() for key, value in categories.items()}
    return render_template('index.html.j2', categories=categories, css='index', js='index')


@app.route('/translate', methods=['POST'])
def translate():
    """
    This translates.
    """

    text = request.form['text']
    tips = falc.process(text, get_db())
    return jsonify(text=text, tips=[t.serialize() for t in tips])

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize text.
    """
    text = request.form['text']
    summary = falcore.summarize(text)
    tips = falc.process(summary)
    return jsonify(summary=summary, tips=[t.serialize() for t in tips])
