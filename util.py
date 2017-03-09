# -*- coding: utf-8 -*-
"""Util methods for FALC."""
import re
import codecs


###############################################################################
#                                 Classes                                     #
###############################################################################
class Word:
    """Defines a word."""

    def __init__(self, text, position):
        """Word inits."""
        self.text = text
        self.position = position


class Particle:
    """
    Describes particle you should avoir and its mitigation.

    A particle is a something that should be avoided in a FALC text. It can be
    a
    """

    TYPE_PUNC = 'punc'     # character of punctuation
    TYPE_WORD = 'word'     # word/chars in text
    TYPE_ENDI = 'endi'     # terminaison (verb)

    def __init__(self, regex, comment, type):
        """Particle init."""
        self.regex = regex
        self.comment = comment
        self.type = type


class Warning:
    """A warning."""

    def __init__(self, index, start, end, comment, snippet):
        """Warning init."""
        self.index = index
        self.start = start
        self.end = end
        self.comment = comment
        self.snippet = snippet


R_WORDS = u'[a-zàâçéèêëîïôûùüÿñæœ\-]+\'*(?i)'
# REGEX_PUNC = u'[.,\/#!$%\^&\*;:{}=\-_`~()?\']'
# R_WORDS = ur'[^\\p{Z}]*\\p{L}[^\\p{Z}]*'
R_SPAN = u'(<\/*span[^>]*>|<\/*p>)'
R_SENTENCE = u'[^.?!]+'

particles = []
with codecs.open('dict/particles.txt', encoding='utf8') as f:
    lines = f.read().splitlines()
    for i in range(0, len(lines), 3):
        regex = lines[i]
        comment = lines[i + 1]
        type = lines[i + 2]
        particle = Particle(regex, comment, type)
        particles.append(particle)


def clean(text):
    """Clean text from format html."""
    return re.sub(R_SPAN, '', text)


def add_warning(warnings, m, particle, offset=0):
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
    comment = particle.comment
    warnings.append(Warning(index, start, end, comment, snippet))


def process(text):
    """Do the things."""
    words = []
    warnings = []

    # Check sentence length
    # for m in re.compile(R_SENTENCE).finditer(text):
    #     if len(m.group().split(' ')) > 12:
    #         s = m.start()
    #         end = s + len(m.group())
    #         warnings.append((len(warnings), s, end, "too many wordz", m.group()))

    # Check punctutation that should be avoided
    for particle in particles:
        if particle.type == Particle.TYPE_PUNC:
            for m in re.compile(particle.regex).finditer(text):
                add_warning(warnings, m, particle)

    # Split text to words, keeping offset in 2nd item of tuple
    for m in re.compile(R_WORDS).finditer(text):
        words.append((m.group(), m.start()))

    # Check word particles
    for word in words:
        for particle in particles:
            if particle.type == Particle.TYPE_WORD:
                r = '^' + particle.regex + '$'
                for m in re.compile(r).finditer(word[0]):
                    add_warning(warnings, m, particle, word[1])

    return words, warnings
