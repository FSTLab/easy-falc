# -*- coding: utf-8 -*-
"""Util methods for FALC."""
import re
import codecs
from summarize import summarize as pysummarize
import os
from polyglot.text import Text
from importlib import import_module

###############################################################################
#                                 Classes                                     #
###############################################################################
class Category:
    # Polarities
    BAD = 0
    ADVICE = 1
    GOOD = 2

    def __init__(self, polarity, title):
        self.polarity = polarity
        self.title = title

    def serialize(self):
        return {
            'polarity': self.polarity,
            'title': self.title
        }


class Tip:
    def __init__(self, category_id, start, end, snippet):
        self.category_id = category_id
        self.start = start
        self.end = end
        self.snippet = snippet


    def serialize(self):
        return {
            'category_id': self.category_id,
            'start': self.start,
            'end': self.end,
            'snippet': self.snippet
        }




class Falc:
    DIR_MODULES = 'falc-modules'

    MSG_INIT = "# init module: {}: {}"
    MSG_ADD = "# add module: {}"

    def __init__(self):
        print("\n# init falc core")
        self.modules = self.init_modules()
        print("\n")


    def init_modules(self):
        modules = []
        here = os.path.dirname(os.path.abspath(__file__))
        directory_modules = os.path.join(here, Falc.DIR_MODULES)

        for f in os.listdir(directory_modules):
            if f.startswith('m_') and f.endswith('.py'):
                path = "%s.%s" % (Falc.DIR_MODULES, os.path.splitext(f)[0])
                module = import_module(path)
                m_name = module.__name__
                if 'process' in dir(module):
                    try:
                        module.init()
                        print(Falc.MSG_INIT.format(m_name, "OK"))
                    except AttributeError:
                        print(Falc.MSG_INIT.format(m_name, "Not Found"))
                    modules.append(module)
                    print(Falc.MSG_ADD.format(m_name))
        return modules

    def process(self, text):
        tips = []
        for module in self.modules:
            tips += module.process(text)
        return tips


###############################################################################
#                                 Statics                                     #
###############################################################################
# Regex of what made a word
# Regex for the text format
R_SPAN = u'(<\/*span[^>]*>|<\/*p>)'

WARNING_SENTENCE_TOO_LONG = "Faites des phrases courtes."

PATH = os.path.dirname(os.path.abspath(__file__))
PATH_LEX = PATH +'/dict/lexique-dicollecte-fr-v6.0.2/lexique-dicollecte-fr-v6.0.2.txt'
PATH_DICT = PATH + '/dict/particles.txt'

# Categories
C_FREQUENT_WORD = 1000
C_SHORT_WORD = 1001

C_REMOVE_NOT_ESSENTIAL = 3000

C_SENTENCE_TOO_LONG = 4000
C_NEGATION = 4001
C_COMPLEX_PUNCTUATION = 4002
C_ACRONYMS = 4003
C_LONG_WORD = 4004
C_COMPLEX_WORD = 4005

CATEGORIES = {
    C_FREQUENT_WORD : Category(Category.GOOD, "Mot courant"),
    C_SHORT_WORD : Category(Category.GOOD, "Mot court"),

    C_REMOVE_NOT_ESSENTIAL : Category(Category.ADVICE, "Supprimer les phrases qui ne sont pas indispensables à la compréhension"),

    C_SENTENCE_TOO_LONG : Category(Category.BAD, "Phrase trop longue"),
    C_NEGATION : Category(Category.BAD, "Utilise des négations"),
    C_COMPLEX_PUNCTUATION : Category(Category.BAD, "Caractère à éviter, utiliser une ponctuation simple"),
    C_ACRONYMS : Category(Category.BAD, "Utilise des sigles et acronymes"),
    C_LONG_WORD : Category(Category.BAD, "Mot trop long")
}


def clean(text):
    """Clean text from html formatting."""
    return re.sub(R_SPAN, '', text)


def get_categories():
    return CATEGORIES


def summarize(text):
    return pysummarize(text, language='french', sentence_count=2)


word_freq = {}
lemma = {}
synonyms = {}
replacement = {}


def init_thesaurus():

    th_file = open(PATH_LEX, encoding='utf8')

    for i in range(0, 16):
        th_file.readline()
    for ln in th_file:
        lns = ln.strip().split()
        word_freq[lns[1]] = float(lns[-5])
        lemma[lns[1]] = lns[2]
    th_file.close()

    with open(PATH + '/dict/thesaurus-v2.3/thes_fr.dat') as sv_file:
        sv_file.readline()
        prev_word = ''
        for ln in sv_file:
            if ln.startswith('(') and prev_word != '':
                synonyms[prev_word] = ln.strip().split('|')
            else:
                prev_word = ln.strip().split('|')[0]

    for word in word_freq:
        if word in synonyms and len(synonyms[word]) > 0:
            wf_pair = [(w, word_freq[w]) for w in synonyms[word]
                       if w in word_freq and
                       word_freq[w] > word_freq[word] and
                       len(w) < len(word)]

            if len(wf_pair) == 1:
                newword_pair = wf_pair[0]
                replacement[word] = newword_pair[0]
            elif len(wf_pair) > 0:
                newword_pair = sorted(wf_pair,
                                      reverse=True,
                                      key=lambda x: x[1])[0]
                replacement[word] = newword_pair[0]


def replace_propn(word):
    if word.startswith("l'") or word.startswith("d'"):
        word = word.split("'")[1]
    if word in replacement:
        return replacement[word]
    return None


def replace_verb(verb):
    if verb.startswith("l'") or verb.startswith("d'"):
        verb = verb.split("'")[1]
    if verb in lemma:
        verb_lem = lemma[verb]
    else:
        print("No lemma for %s" % verb)
        return None
    if verb_lem not in replacement:
        print("No replacement for %s" % verb)
        return None
    rep_verb = replacement[verb_lem]
    return rep_verb


def simplify(text, tips):
    if len(text.strip()) == 0 or text is None:
        return
    pgText = Text(text)
    pgText.hint_language_code = 'fr'
    pgText.pos_tags

    for word, pos in pgText.pos_tags:
        startpos = text.index(word)
        if pos == u'PRON':
            new_word = replace_propn(word)
            if new_word:
                print(word)
                index = len(warnings)
                warnings.append(Warning(index, startpos, startpos+len(word),
                                        "Utiliser mot simple", new_word))
                # tips.append(Tip(C_COMPLEX_WORD, startpos, startpos + len(word), word))
        elif pos == u'VERB':
            if word.startswith("l'") or word.startswith("d'"):
                verb = word.split("'")[1]
            else:
                verb = word
            new_word = replace_verb(verb)
            if new_word:
                index = len(warnings)
                warnings.append(
                    Warning(
                        index,
                        startpos,
                        startpos + len(word),
                        "Utiliser:",
                        lemma[verb] + ' -> ' + new_word
                        )
                    )
    for sentence in Text(text).sentences:
        sentstr = str(sentence)
        if sentstr.count(',') >= 1:
            idofcomma = sentstr.index(',')
            startidx = sentence.start-1+idofcomma
            index = len(warnings)
#           TODO: change message to French
            warnings.append(
                Warning(
                    index,
                    startidx,
                    startidx + 5,
                    "Avoid clauses",
                    "Delete or use seperate sentences"
                    )
                )
