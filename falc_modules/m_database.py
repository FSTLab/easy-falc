"""
Database module

This class is a FALC module. FALC modules MUST implement process method to be
used.

It can
"""
import sqlite3
import os
import falcore
from falc_modules.m_regex import get_words, create_tip, is_short

##############################
#          Globals           #
##############################

# Files
DIR_SCRIPT = os.path.dirname(__file__)
PATH_REL_DB = 'res/dictionaries.db'
PATH_ABS_DB = os.path.join(DIR_SCRIPT, PATH_REL_DB)

# Database
db = sqlite3.connect(PATH_ABS_DB)
cursor = db.cursor()

# Modifiers
FREQUENT_WORDS_COUNT = 1000

# Utils
RULES = {}
ponderation_min = 0.0

##############################
#       Module Methods       #
##############################

def init():
    global ponderation_min
    cursor.execute("SELECT ponderation FROM Mots WHERE fk_dictionnaires=1 ORDER BY ponderation DESC LIMIT 1 OFFSET {}".format(FREQUENT_WORDS_COUNT))
    ponderation_min = float(cursor.fetchone()[0])
    print("### ponderation_min={}".format(ponderation_min))

    global RULES
    RULES['word'] = [
        rule_word_complexity
    ]

def process(text):
    tips = []
    for word in get_words(text):
        for rule in RULES['word']:
            tips += rule(word)
    return tips

##############################
#           Rules            #
##############################
def rule_word_complexity(word):
    """
    In order to be considered easy, a word has to be frequent and short.
    """
    for row in cursor.execute("SELECT ponderation FROM Mots WHERE mot=\"{}\"".format(word.group())):
        ponderation = float(row[0])
        print("# process {} [p={}]".format(word.group(), ponderation))
        if ponderation < ponderation_min:
            return [create_tip(falcore.C_COMPLEX_WORD, word)]
        elif is_short(word.group()):
            return [create_tip(falcore.C_EASY_WORD, word)]
    return []
