# -*- coding: utf8 -*-

from flask import Flask, render_template

import random
import text_db as db
import urllib
import codecs
from ressources.dico import KEYWORD

UTF8 = codecs.lookup('utf-8')

app = Flask(__name__)
app.jinja_env.filters['quote'] = lambda x: urllib.quote(UTF8.encode(x)[0])
app.debug = True

def get_any_n(seq, n):
    random.shuffle(seq)
    return seq[:n]


def get_quotes_for_word(conn, word, n=4):
    return get_any_n(db.get_quotes(conn, word), n)

def get_cowords_for_word(conn, word, n=4):
    return get_any_n(db.get_cowords(conn, word), n)

def get_quotes_for_words(conn, conn_i, words):
    quotes = []
    for word in words:
        candidates = db.get_quotes_i(conn_i, word)
        if random.random() > 0.5 and len(candidates) > 0:
            quotes.append(random.choice(candidates))
        else:
            quotes.append(random.choice(db.get_quotes(conn, word)))
    return quotes


def get_cowords_for_words_excluding(conn, words, excluded):
    cowords = []
    for word in words:
        candidates = db.get_cowords(conn, word)
        random.shuffle(candidates)
        candidates = [cand for cand in candidates if cand not in excluded]
        cowords.append(candidates[0])
    return cowords


@app.route('/')
def index():
    word_list = []
    for mots in KEYWORD.keys():
        for mot in KEYWORD[mots]:
            word_list.append(mot.decode('utf-8'))
    random.shuffle(word_list)
    print word_list
    return render_template('index0.html', words=word_list)

@app.route('/momentum/<word>')
def momentum(word):
    conn = db.get_connection()
    conn_i = db.get_connection_i()

    rows = []
    # Première ligne : citations du mot choisi
    rows.append(get_quotes_for_word(conn, word))

    # Deuxième ligne : co-mots et citations associées
    words2 = get_cowords_for_word(conn, word)
    rows.append(get_quotes_for_words(conn, conn_i, words2))

    # Troisième & quatrième lignes : co-co-(co-)mots et citations
    words3 = get_cowords_for_words_excluding(conn, words2, [word])
    rows.append(get_quotes_for_words(conn, conn_i, words3))
    words4 = get_cowords_for_words_excluding(conn, words3, [word] + words2)
    rows.append(get_quotes_for_words(conn, conn_i, words4))

    # Transformation en bande (colonnes)
    bands = [[row[i] for row in rows] for i in xrange(4)]

    conn.close()

    return render_template('index.html', word=word, bands=bands, last_words=words4)


@app.route('/next/<word>')
def next_word(word):
    conn = db.get_connection()
    conn_i = db.get_connection_i()

    # Une quote et un co-word
    word2 = random.choice(db.get_cowords(conn, word))
    quote = get_quotes_for_words(conn, conn_i, [word2])[0]

    conn.close()

    return render_template('fragment.html', quote=quote, word=word2)


if __name__ == '__main__':
    app.run()
