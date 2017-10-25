from falcore import Tip
import json
import re
import os

##############################
#          STATICS           #
##############################
R_SENTENCE = u'[^.?!]+'
R_WORDS = u'[a-zàâçéèêëîïôûùüÿñæœ\-]+\'*(?i)'

DIR_SCRIPT = os.path.dirname(__file__)
PATH_REL = 'res/particles.json'
PATH_ABS = os.path.join(DIR_SCRIPT, PATH_REL)

with open(PATH_ABS) as datas:
    particles = json.load(datas)['particles']


def process(text):
    tips = []
    tips += process_all(text)
    tips += process_sent(text)
    tips += process_word(text)
    tips += process_char(text)
    return tips


def process_all(text):
    t = []
    for particle in particles_generator('all'):
        for m in re.compile(particle['regex']).finditer(text):
            t.append(create_tip(particle['category_id'], m))
    return t

def process_sent(text):
    t = []
    for sentence in re.compile(R_SENTENCE).finditer(text):
        offset = sentence.start()
        for particle in particles_generator('sent'):
            for m in re.compile(particle['regex']).finditer(sentence.group()):
                t.append(create_tip(particle['category_id'], m))
    return t

def process_word(text):
    t = []
    for word in re.compile(R_WORDS).finditer(text):
        for particle in particles_generator('word'):
            for m in re.compile(particle['regex']).finditer(word.group()):
                t.append(create_tip(int(particle['category_id']), m, word.start()))
    return t

def process_char(text):
    t = []
    for particle in particles_generator('char'):
        for m in re.compile(particle['regex']).finditer(text):
            t.append(create_tip(particle['category_id']))
    return t


##############################
#          UTILS             #
##############################
def create_tip(category_id, m, offset=0):
    start = m.start() + offset
    snippet = m.group()
    end = start + len(snippet) - 1
    return Tip(category_id, start, end, snippet)


def particles_generator(particle_type):
    return (particle for particle in particles if particle['type'] == particle_type)
