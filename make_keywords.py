import re
import random
import Stemmer
from functional import *
import re, htmlentitydefs

stemmer = Stemmer.Stemmer('english')

STOP_WORDS = (
    "a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,"
    "be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,"
    "ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,"
    "i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,"
    "my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,"
    "say,says,she,should,since,so,some,than,that,the,their,them,then,there,"
    "these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,"
    "which,while,who,whom,why,will,with,would,yet,you,your,"
    "http,www,com,"
    "etsy,shop,product,item"
).split(',')

wordify = lambda s: re.findall('[a-z0-9\']+', s.lower())
goodwords = lambda ws: [w for w in ws if w not in STOP_WORDS and len(w) > 2]

def get_keywords(*word_sources):
    return goodwords(stemmer.stemWords(set( wordify(' '.join(word_sources)) )))

def composer(*fns):
    fns = list(fns)
    last = fns.pop(-1)
    return foldr(compose, last, fns)

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#": # character reference
            try:
                if text[:3] == "&#x": return unichr(int(text[3:-1], 16))
                else: return unichr(int(text[2:-1]))
            except ValueError: pass
        else: # named entity
            try: text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError: pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def encode(text): return unicode(text)

keywordify = composer(goodwords, stemmer.stemWords, wordify, unescape, encode)
