import os, sys, xmpp
import codecs

if len(sys.argv) < 2:
    print "Syntax: xsend user text"
    sys.exit(0)

user = sys.argv[1]
text = ' '.join(sys.argv[2:])

from lsier import *
from make_keywords import *
import random
keywordify = composer(goodwords, stemmer.stemWords, wordify)
me_chat_documents = filter(None, map(lambda d: unescape(d.strip()), codecs.open('/Users/sean/all_from_me.txt', 'r', 'utf-8').read().split('\n')))
chat_search = make_lsi_search(me_chat_documents)

import nltk

SEP = ' BBREAKK '
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')
content_text = SEP.join(me_chat_documents)
tokenized_content = tokenizer.tokenize(content_text)
markov_model = nltk.NgramModel(3, tokenized_content)

def echo_back(c, m):
    print "GOT M: %s" % m
    m_text = m.getBody()
    m_user = m.getFrom()
    relevant_chats = chat_search(m.getBody())
    chat_text = random.choice(relevant_chats[:10])
    r_raw = ' '.join(markov_model.generate(50, tokenizer.tokenize(chat_text)[:2]))
    r_text = r_raw[:r_raw.index(SEP)]
    mecho = xmpp.Message(m_user, r_text)
    c.send(mecho)

jid="drsproboto@gmail.com"
jid=xmpp.protocol.JID(jid)
client = xmpp.Client('gmail.com')
client.connect(server=('talk.google.com', 5223))
client.auth(jid.getNode(), '3*cGeO9)antil')
client.RegisterHandler('message', echo_back)
client.sendInitPresence()

message = xmpp.Message(user, text)
message.setAttr('type', 'chat')
client.send(message)

while client.Process(1):
    pass
