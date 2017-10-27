import sqlite3
from falc_modules.m_regex import get_words

DATABASE = 'dictionaries.db'
db = sqlite3.connect(DATABASE)


def process(text):
    words = get_words(text)
    
    return []
