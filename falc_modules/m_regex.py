"""
Regex module

This class is a FALC module. FALC modules MUST implement process method to be
used.

It can
"""
import falcore
from falcore import Tip, create_tip_m
import json
import re
import os

##############################
#       Static public        #
##############################
def get_words_m(text):
    return [word for word in re.compile(ModuleRegex.R_WORDS).finditer(text)]

def is_short(word):
    return re.compile(ModuleRegex.R_WORD_SHORT).match(word)

def is_long(word):
    return re.compile(ModuleRegex.R_WORD_LONG).match(word)


class ModuleRegex(falcore.FalcModule):
    ##############################
    #          Statics           #
    ##############################
    R_SENTENCE = u'[^.?!]+'
    R_WORDS = u'[A-ZÀÂÇÉÈÊËÎÏÔÛÙÜŸÑÆŒ]?[a-zàâçéèêëîïôûùüÿñæœ\-]+\'*(?i)'

    R_WORD_SHORT = '^.{3,9}$'
    R_WORD_LONG = '^.{10,}$'

    ##############################
    #          Module            #
    ##############################
    def __init__(self):
        super().__init__()

        # files and paths
        self.abspath = os.path.dirname(os.path.abspath(__file__))
        self.relpathdb = 'res/particles.json'
        self.pathdb = os.path.join(self.abspath, self.relpathdb)

        # lulz
        self.particles = self.init_particles()
        self.processes = [
            self.process_all,
            self.process_sentences,
            self.process_word,
            self.process_character
        ]


    def process(self, text, db):
        super().process()
        tips = []
        for p in self.processes:
            tips += p(text)
        return tips


    def process_all(self, text):
        t = []
        for particle in self.particles_generator('all'):
            for m in re.compile(particle['regex']).finditer(text):
                t += create_tip_m(particle['category_id'], m)
        return t


    def process_sentences(self, text):
        t = []
        for sentence in re.compile(self.R_SENTENCE).finditer(text):
            offset = sentence.start()
            for particle in self.particles_generator('sent'):
                for m in re.compile(particle['regex']).finditer(sentence.group()):
                    t += create_tip_m(particle['category_id'], m)
        return t

    def process_word(self, text):
        t = []
        for word in re.compile(self.R_WORDS).finditer(text):
            for particle in self.particles_generator('word'):
                for m in re.compile(particle['regex']).finditer(word.group()):
                    t += create_tip_m(int(particle['category_id']), m, word.start())
        return t

    def process_character(self, text):
        t = []
        for particle in self.particles_generator('char'):
            for m in re.compile(particle['regex']).finditer(text):
                t += create_tip_m(particle['category_id'], m)
        return t



    ##############################
    #          Utils             #
    ##############################
    def init_particles(self):
        with open(self.pathdb) as datas:
            return json.load(datas)['particles']

    def particles_generator(self, particle_type):
        return (particle for particle in self.particles if particle['type'] == particle_type)
