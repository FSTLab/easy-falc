# -*- coding: utf-8 -*-
"""Util methods for FALC."""
import re


###############################################################################
#                                 Classes                                     #
###############################################################################
class Lexem:
    """Lexem contains."""

    TYPE_WORD = 'word'  # word
    TYPE_PUNC = 'punc'  # punctuation
    TYPE_SPAC = 'spac'  # space

    def __init__(self, content, type):
        """Lexem init."""
        self.content = content
        self.type = type


class Particle:
    """A Particle and its warning."""

    TYPE_CHAR = 'char'  # character
    TYPE_TERM = 'term'  # terminaison

    def __init__(self, regex, comment, type):
        """Particle init."""
        self.regex = regex
        self.comment = comment
        self.type = type


class Warning:
    """A warning."""

    def __init__(self, id, start, end, comment):
        """Warning init."""
        self.id = id
        self.start = start
        self.end = end
        self.comment = comment


REGEX_WORD = u'[a-zàâçéèêëîïôûùüÿñæœ\-]+(?i)'
REGEX_PUNC = u'[.,\/#!$%\^&\*;:{}=\-_`~()?\']'
REGEX_SPAN = u'<\/*span[^>]*>'

particles = [
    Particle(
        u'n[\'e]',
        u"utilise une formulation négative, privilégier plutôt la forme\
            affirmative",
        Particle.TYPE_CHAR
    ),
    Particle(
        u':',
        u"caractère à éviter, utiliser une ponctuation simple",
        Particle.TYPE_CHAR)
]


def clean(text):
    """Clean text from format html."""
    return re.sub(REGEX_SPAN, '', text)


def lexems(text):
    """Do the things."""
    lexems = []
    pos = []

    warnings = []   # each item (start, end, comment)
    for particle in particles:
        for m in re.compile(particle.regex).finditer(text):
            s = m.start()
            g = m.group()
            w = Warning(len(warnings), s, s + len(g), particle.comment)
            warnings.append(w)

    for m in re.compile(REGEX_WORD).finditer(text):
        s = m.start()
        g = m.group()
        pos.append((s, s + len(g), g))

    for i in range(len(text)):
        is_word = False
        for p in pos:
            if p[0] <= i < p[1]:
                is_word = True
                if p[0] == i:
                    lexems.append(Lexem(p[2], Lexem.TYPE_WORD))
        if not is_word:
            if re.match(REGEX_PUNC, text[i]):
                lexems.append(Lexem(text[i], Lexem.TYPE_PUNC))
            else:
                lexems.append(Lexem(text[i], Lexem.TYPE_SPAC))

    return lexems, warnings
