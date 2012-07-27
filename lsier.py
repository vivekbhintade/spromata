import gensim
from spromata.make_keywords import *

def make_lsi_search(documents, d2t=keywordify, sd2t=keywordify, num_topics=250):
    texts = map(d2t, documents)
    print "TEXTS: %s" % texts[:5]
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word)==1)
    texts = map(lambda ws: filter(lambda w: w not in tokens_once, ws), texts)

    print "Creating dictionary"
    dictionary = gensim.corpora.Dictionary(texts)
    #dictionary.save('/Users/sean/all_from_me.dict')
#dictionary = gensim.corpora.Dictionary.load('/Users/sean/all_from_me.dict')

    print "Creating corpus"
    corpus = [dictionary.doc2bow(text) for text in texts]
    #gensim.corpora.MmCorpus.serialize('/Users/sean/all_from_me.mm', corpus)
#corpus = gensim.corpora.MmCorpus('/Users/sean/all_from_me.mm')

    print "Calculating LSI"
    lsi = gensim.models.lsimodel.LsiModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
    #lsi.print_topics(10)

    print "Calculating similarity matrix"
    index = gensim.similarities.MatrixSimilarity(lsi[corpus])
    #index.save('/Users/sean/all_from_me.index')
#index = gensim.similarities.MatrixSimilarity.load('/Users/sean/all_from_me.index')

    def search(document):
        text = sd2t(document)
        vec_bow = dictionary.doc2bow(text)
        vec_lsi = lsi[vec_bow]
        sims = index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        sim_docs = [documents[s[0]] for s in sims]
        return sim_docs
    return search

#me_chat_documents = filter(None, map(lambda d: d.strip(), open('/Users/sean/all_from_me.txt').readlines()))
