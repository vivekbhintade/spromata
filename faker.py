from spromata.markov import *
import re
import nltk

print "Generating Markov model..."
mk = Markov(nltk.corpus.brown.words())
gen_text = lambda l: mk.generate_markov_text(l)
fix_punc = lambda s: re.sub("(')\s", '\\1', re.sub('\s+([^\w])', '\\1', s))

fake_sentence = lambda: re.sub('^[^\w]+', '', fix_punc(gen_text(random.randint(30,50))))
fake_word = lambda: random.choice(gen_text(random.randint(10,30)).split(' '))
