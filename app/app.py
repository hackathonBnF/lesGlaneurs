# -*- coding: utf8 -*-


from flask import Flask, render_template
import random
import text_db as db

app = Flask(__name__)
app.debug = True

def get_any_n(seq, n):
    random.shuffle(seq)
    return seq[:n]


def get_quotes_for_word(conn, word, n=4):
    return get_any_n(db.get_quotes(conn, word), n)

def get_cowords_for_word(conn, word, n=4):
    return get_any_n(db.get_cowords(conn, word), n)

def get_quotes_for_words(conn, words):
    return [random.choice(db.get_quotes(conn, word)) for word in words]

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
    return 'Hello'

@app.route('/momentum/<word>')
def momentum(word):
    conn = db.get_connection()

    rows = []
    # Première ligne : citations du mot choisi
    rows.append(get_quotes_for_word(conn, word))

    # Deuxième ligne : co-mots et citations associées
    words2 = get_cowords_for_word(conn, word)
    rows.append(get_quotes_for_words(conn, words2))

    # Troisième & quatrième lignes : co-co-(co-)mots et citations
    words3 = get_cowords_for_words_excluding(conn, words2, [word])
    rows.append(get_quotes_for_words(conn, words3))
    words4 = get_cowords_for_words_excluding(conn, words3, [word] + words2)
    rows.append(get_quotes_for_words(conn, words4))

    # Transformation en bande (colonnes)
    bands = [[row[i] for row in rows] for i in xrange(4)]

    return render_template('index.html', word=word, bands=bands)

if __name__ == '__main__':
    app.run()
