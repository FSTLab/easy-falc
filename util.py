# -*- coding: utf-8 -*-
"""Util methods for FALC."""
import re
import codecs
from summarize import summarize as pysummarize
import os
from polyglot.text import Text


###############################################################################
#                                 Classes                                     #
###############################################################################
class Word:
    """The word and the position of its first character in the whole text."""

    def __init__(self, text, position):
        """Word constructor."""
        self.text = text
        self.position = position


class Particle:
    """
    Describes a particle you should avoid and its mitigation.

    A particle is something that should be avoided in a FALC text. It can be
    specific punctuation, words or verb endings. The type WORD can also be used
    with regexes, in order to match some specific pattern, length in a word.
    """

    TYPE_PUNC = 'punc'     # character of punctuation
    TYPE_WORD = 'word'     # word/chars in text
    TYPE_ENDI = 'endi'     # terminaison (verb)

    def __init__(self, regex, comment, type):
        """Particle constructor."""
        self.regex = regex
        self.comment = comment
        self.type = type


class Warning:
    """
    A warning is used to inform the user about what he did wrong.

    :param index: Unique id
    :param start: Start position in the text
    :param end: End position in the text
    :param comment: Litteraly what the error is, will be displayed to user
    :param snippet: What caused the error, which part of the text
    """

    def __init__(self, index, start, end, comment, snippet):
        """Warning constructor."""
        self.index = index
        self.start = start
        self.end = end
        self.comment = comment
        self.snippet = snippet

    def serialize(self):
        return {
            'index': self.index,
            'start': self.start,
            'end': self.end,
            'comment': self.comment,
            'snippet': self.snippet,
        }

class Category:
    # Polarities
    BAD = 0
    ADVICE = 1
    GOOD = 2

    def __init__(self, title, polarity):
        self.title = title
        self.polarity = polarity


class Tip:
    def __init__(self, category_id, start, end, snippet):
        self.category_id = category_id
        self.start = start
        self.end = end
        self.snippet = snippet


###############################################################################
#                                 Statics                                     #
###############################################################################
# Regex of what made a word
R_WORDS = u'[a-zàâçéèêëîïôûùüÿñæœ\-]+\'*(?i)'
# Regex for the text format
R_SPAN = u'(<\/*span[^>]*>|<\/*p>)'
# Regex of a sentence
R_SENTENCE = u'[^.?!]+'

WARNING_SENTENCE_TOO_LONG = "Faites des phrases courtes."

PATH = os.path.dirname(os.path.abspath(__file__))
PATH_LEX = PATH +'/dict/lexique-dicollecte-fr-v6.0.2/lexique-dicollecte-fr-v6.0.2.txt'
PATH_DICT = PATH + '/dict/particles.txt'

# Read particles from external file. File is written as follow:
#
# - 3 lines per particle
# - first line is the regex
# - second line is the warning text
# - third line is the type (punc, word, endi)
particles = []
with codecs.open(PATH_DICT, encoding='utf8') as f:
    lines = f.read().splitlines()
    for i in range(0, len(lines), 3):
        regex = lines[i]
        comment = lines[i + 1]
        type = lines[i + 2]
        particle = Particle(regex, comment, type)
        particles.append(particle)


def clean(text):
    """Clean text from html formatting."""
    return re.sub(R_SPAN, '', text)


def get_categories():
    return ['test', 'lol']


def add_warning(warnings, m, comment, offset=0):
    """
    Create a Warning object, given the following parameters.

    :param warnings:    The list of warning where you want the new to be added.
    :param m:           The regex iterator of MatchObject
    :param particle:    The particle
    :param offset:      Offset, if you are not looping through the whole text.
    """
    index = len(warnings)
    start = m.start() + offset
    snippet = m.group()
    end = start + len(snippet) - 1
    warnings.append(Warning(index, start, end, comment, snippet))


def summarize(text):
    return pysummarize(text, language='french', sentence_count=2)

def process(text):
    """
    Process the text in order to get the differents warnings.

    :return warnings:   list of found warnings
    """
    words = []
    warnings = []
    tips = []

    # Check sentence length
    for m in re.compile(R_SENTENCE).finditer(text):
        if len(m.group().split(' ')) > 12:
            add_warning(warnings, m, WARNING_SENTENCE_TOO_LONG)
            tip = Tip()
            tips.append()

    # Check punctutation particles
    for particle in particles:
        if particle.type == Particle.TYPE_PUNC:
            for m in re.compile(particle.regex).finditer(text):
                add_warning(warnings, m, particle.comment)

    # Split text to words
    for m in re.compile(R_WORDS).finditer(text):
        words.append(Word(m.group(), m.start()))

    # Check word particles
    for word in words:
        for particle in particles:
            if particle.type == Particle.TYPE_WORD:
                # from the start to the end of the word
                r = '^{}$' .format(particle.regex)
                for m in re.compile(r).finditer(word.text):
                    add_warning(warnings, m, particle.comment, word.position)

    simplify(text, warnings)
    return warnings


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


def simplify(text, warnings):
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
