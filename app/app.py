# -*- coding: utf8 -*-


from flask import Flask, render_template
import random
import text_db as db

app = Flask(__name__)
app.debug = True

def get_any_n(seq, n):
    random.shuffle(seq)
    return seq[:n]

@app.route('/')
def index():
    return 'Hello'

@app.route('/momentum/<word>')
def momentum(word):
    conn = db.get_connection()

    # Première bande : citations du mot choisi
    band1 = get_any_n(db.get_quotes(conn, word), 4)
    print 'BAND 1 - %d quotes' % len(band1)

    # Deuxième bande : citations de co-mots de celui choisi
    words2 = get_any_n(db.get_cowords(conn, word), 4)
    print 'BAND 2 - %d words' % len(words2)
    band2 = [random.choice(db.get_quotes(conn, word2)) for word2 in words2]
    print 'BAND 2 - %d quotes' % len(band2)

    # Troisième bande : citations de co-mots des co-mots
    words3 = []
    for word2 in words2:
        candidates = db.get_cowords(conn, word2)
        random.shuffle(candidates)
        candidates = [cand for cand in candidates if cand != word]
        words3.append(candidates[0])
    print 'BAND 3 - %d words' % len(words3)
    band3 = [random.choice(db.get_quotes(conn, word3)) for word3 in words3]
    print 'BAND 3 - %d quotes' % len(band3)

    return render_template('index.html', word=word, band1=band1, band2=band2, band3=band3)

if __name__ == '__main__':
    app.run()
