"""
Database module

This class is a FALC module. FALC modules MUST implement process method to be
used.

It can
"""
import sqlite3
import os
import falcore
from falcore import create_tip_m
import falc_modules.m_regex as m_regex

class ModuleDatabase(falcore.FalcModule):
    ##############################
    #          Statics           #
    ##############################
    FREQUENT_WORDS_COUNT = 1000


    ##############################
    #          Module            #
    ##############################
    def __init__(self):
        super().__init__()

        # files and paths
        self.abspath = os.path.dirname(os.path.abspath(__file__))
        self.relpathdb = 'res/dictionaries.db'
        self.pathdb = os.path.join(self.abspath, self.relpathdb)

        # db
        self.db = sqlite3.connect(self.pathdb)

        # vars
        self.ponderation_min = self.get_ponderation_min()
        self.rules = [
            self.rule_word_complexity,
            self.rule_multisemic
        ]

    def process(self, text, db):
        super().process()
        tips = []
        cursor = db.cursor()

        for word_m in m_regex.get_words_m(text):
            word = word_m.group().lower()
            print("- word: {}".format(word))

            sql = "SELECT * FROM Mots WHERE fk_dictionnaires=1 AND mot=\"{}\"".format(word)
            word_db = cursor.execute(sql).fetchone()
            print(word_db)

            if word_db:
                for rule in self.rules:
                    tips += rule(word, word_m, word_db)
            elif '\'' not in word:
                tips += create_tip_m(falcore.C_NOT_IN_DICTIONARY, word_m)
        return tips

    ##############################
    #          Rules             #
    ##############################
    def rule_word_complexity(self, word, word_m, word_db):
        """
        In order to be considered easy, a word has to be frequent and short.
        """
        tips = []

        ponderation = float(word_db['ponderation'])
        is_frequent = ponderation > self.ponderation_min
        is_short = True if m_regex.is_short(word) else False
        is_long = True if m_regex.is_long(word) else False

        c_id = None
        if is_frequent and is_short:
            c_id = falcore.C_EASY_WORD
        elif is_frequent and is_long:
            c_id = falcore.C_LONG_WORD
        elif not is_frequent and is_long:
            c_Id = falcore.C_COMPLEX_WORD

        if c_id:
            tips += create_tip_m(c_id, word_m)

        return tips

    def rule_multisemic(self, word, word_m, word_db):
        if self.is_multisemic(word_db):
            return create_tip_m(falcore.C_MULTISEMIC_WORD, word_m)
        else:
            return []


    ##############################
    #          Utils             #
    ##############################
    def is_multisemic(self, word_db):

        # word has no defintion
        if word_db['fk_definitions'] is None:
            return False

        # get definition
        # cursor = self.db.cursor()
        # cursor.execute("SELECT definition FROM Definitions WHERE numero = {}".format(word_db[6]))
        # one = cursor.fetchone()[0]

        # TODO check if definition is multiple or not
        return False

    ##############################
    #          Db utils          #
    ##############################
    def get_ponderation_min(self):
        cursor = self.db.cursor()
        sql = "SELECT ponderation FROM Mots WHERE fk_dictionnaires=1 \
               ORDER BY ponderation DESC LIMIT 1 OFFSET {}".format(self.FREQUENT_WORDS_COUNT)
        cursor.execute(sql)
        return float(cursor.fetchone()[0])




##############################
#           Utils            #
##############################
