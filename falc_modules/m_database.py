"""
Database module

This class is a FALC module. FALC modules MUST implement process method to be
used.

It can
"""
import sqlite3
import os
import falcore
import falc_modules.m_regex as m_regex
from falc_modules.m_regex import create_tip

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
PONDERATION_MIN = 0.0
print(db);

##############################
#       Module Methods       #
##############################

def init():
    global PONDERATION_MIN
    cursor.execute("SELECT ponderation FROM Mots WHERE fk_dictionnaires=1 ORDER BY ponderation DESC LIMIT 1 OFFSET {}".format(FREQUENT_WORDS_COUNT))
    PONDERATION_MIN = float(cursor.fetchone()[0])
    print("### PONDERATION_MIN={}".format(PONDERATION_MIN))

    global RULES
    RULES['word'] = [
        rule_word_complexity
    ]

def process(text):
    tips = []
    for word in m_regex.get_words(text):
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
    tips = []

    word_text = word.group().lower()
    print("- word: {}".format(word_text))

    sql = "SELECT * FROM Mots WHERE fk_dictionnaires=1 AND mot=\"{}\"".format(word_text)
    cursor.execute(sql)
    word_db = cursor.fetchone()
    if word_db:
        print("  - db: {}".format(word_db))
        ponderation = float(word_db[3])

        is_frequent = ponderation > PONDERATION_MIN
        is_short = True if m_regex.is_short(word_text) else False
        is_long = True if m_regex.is_long(word_text) else False

        print("  - is_frequent: {}".format(is_frequent))
        print("  - is_short: {}".format(is_short))
        print("  - is_long: {}".format(is_long))

        if is_frequent and is_short:
            tips += [create_tip(falcore.C_EASY_WORD, word)]
            print("  - add_tip: EASY_WORD")
        elif is_frequent and is_long:
            tips += [create_tip(falcore.C_LONG_WORD, word)]
            print("  - add_tip: LONG_WORD")
        elif not is_frequent and is_long:
            tips += [create_tip(falcore.C_COMPLEX_WORD, word)]
            print("  - add_tip: COMPLEX_WORD")

        if is_multisemic(word_db):
            tips += [create_tip(falcore.C_MULTISEMIC_WORD, word)]
    else:
        # avoid abréviations
        if '\'' not in word_text:
            tips += [create_tip(falcore.C_NOT_IN_DICTIONARY, word)]
            print("  - add_tip: NOT_IN_DICTIONARY")


    return tips

##############################
#           Utils            #
##############################
def is_multisemic(word_db):

    # word has no defintion
    if word_db[6] is None:
        return False

    # get definition
    tmp_cursor = db.cursor()
    tmp_cursor.execute("SELECT definition FROM Definitions WHERE numero = {}".format(word_db[6]))
    one = tmp_cursor.fetchone()

    # TODO check if definition is multiple or not
    return False
