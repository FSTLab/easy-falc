# -*- coding: utf-8 -*-
"""Util methods for FALC."""
import re
import codecs


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

# Read particles from external file. File is written as follow:
#
# - 3 lines per particle
# - first line is the regex
# - second line is the warning text
# - third line is the type (punc, word, endi)
particles = []
with codecs.open('./dict/particles.txt', encoding='utf8') as f:
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


def process(text):
    """
    Process the text in order to get the differents warnings.

    :return warnings:   list of found warnings
    """
    words = []
    warnings = []

    # Check sentence length
    for m in re.compile(R_SENTENCE).finditer(text):
        if len(m.group().split(' ')) > 12:
            add_warning(warnings, m, WARNING_SENTENCE_TOO_LONG)

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
                r = '^' + particle.regex + '$'
                for m in re.compile(r).finditer(word.text):
                    add_warning(warnings, m, particle.comment, word.position)

    return warnings
