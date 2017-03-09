# -*- coding: utf-8 -*-
"""Util methods for FALC."""
import re


###############################################################################
#                                 Classes                                     #
###############################################################################
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

particles = [
    Particle(
        u'n[\'e]',
        u"utilise une formulation négative, privilégier plutôt la forme\
            affirmative",
        Particle.TYPE_WORD
    ),
    Particle(
        u':',
        u"caractère à éviter, utiliser une ponctuation simple",
        Particle.TYPE_PUNC
    )
]


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
    start = m.start() + offset - 1
    snippet = m.group()
    end = start + len(snippet)
    comment = particle.comment
    warnings.append(Warning(index, start, end, comment, snippet))


def lexems(text):
    """Do the things."""
    words = []
    warnings = []

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
                    print(m.group())
                    add_warning(warnings, m, particle, word[1])

    return words, warnings
