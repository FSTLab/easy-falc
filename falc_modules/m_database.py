"""
Database module

This class is a FALC module. FALC modules MUST implement process method to be
used.

It can
"""
import sqlite3
import os
from falc_modules.m_regex import get_words

##############################
#          Globals           #
##############################

DIR_SCRIPT = os.path.dirname(__file__)
PATH_REL_DB = 'res/dictionaries.db'
PATH_ABS_DB = os.path.join(DIR_SCRIPT, PATH_REL_DB)

db = sqlite3.connect(PATH_ABS_DB)
cursor = db.cursor()

ponderation_min = 0.0

##############################
#       Module Methods       #
##############################

def init():
    global ponderation_min
    cursor.execute("SELECT ponderation FROM Mots LIMIT 1 OFFSET 1000")
    ponderation_min = cursor.fetchone()
    print(ponderation_min)

def process(text):
    cursor = conn.cursor("SELECT mot, ponderation WHERE")


    words = get_words(text)
    for word in words:
        pass
    return []
