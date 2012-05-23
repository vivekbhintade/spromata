import random
from nltk.corpus import wordnet as wn

def semantistroll(e, l=0):
    print '    '*l + e.name
    choices = e.hyponyms() + e.hypernyms()
    if len(choices) > 4: return semantistroll(random.choice(choices), l+1)
    return e
s = semantistroll

def ss(w):
    syns = wn.synsets(w)
    return [s(syn) for syn in syns]

e = wn.synset('entity.n.01')
p = wn.synset('psychological_feature.n.01')
