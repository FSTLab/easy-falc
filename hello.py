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
falcore.init_thesaurus()

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

FALC = falcore.Falc()

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

    categories = falcore.get_categories()
    categories = {key: value.serialize() for key, value in categories.items()}
    return render_template('index.html.j2', categories=categories, css='index', js='index')


@app.route('/translate', methods=['POST'])
def translate():
    """
    This translates.
    """
    text = request.form['text']
    tips = FALC.process(text)
    return jsonify(text=text, tips=[t.serialize() for t in tips])

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize text.
    """
    text = request.form['text']
    summary = falcore.summarize(text)
    tips = FALC.process(summary)
    return jsonify(summary=summary, tips=[t.serialize() for t in tips])
