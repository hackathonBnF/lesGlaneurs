# -*- coding: utf8 -*-

from flask import Flask, render_template

import random
import text_db as db
import urllib
import codecs
from ressources.dico import KEYWORD

UTF8 = codecs.lookup('utf-8')

# Nombre de mots lus en une minute (au pif !)
WORDS_PER_MIN = 600

# Probabilité d'avoir une image (vs un extrait de texte) en tirant une citation au hasard
IMAGE_PROBABILITY = .8


def read_time(nwords):
    '''
    Conversion d'un nombre de mots en temps de lecture
    :param nwords: Nombre de mots
    :return: Une chaîne avec le temps estimé, en heures et minutes
    '''
    nwords = int(nwords)
    minutes = int(nwords / WORDS_PER_MIN)
    hours = int(minutes / 60)
    time = ''
    if hours > 0:
        minutes %= 60
        time = '%dh' % hours
    time += ' %dmin' % minutes
    return time


# Application Flask
app = Flask(__name__)

# Encodage URL avec conversion UTF-8 à la volée
app.jinja_env.filters['quote'] = lambda x: urllib.quote(UTF8.encode(x)[0])

# Calcul du temps de lecture
app.jinja_env.filters['read_time'] = read_time

app.debug = True



def get_any_n(seq, n):
    '''
    Choisit n éléments au hasard parmi une séquence
    :param seq: La séquence
    :param n: Le nombre d'éléments
    :return: n éléments pris au hasard dans seq
    '''
    random.shuffle(seq)
    return seq[:n]


def get_quotes_for_word(conn, word, n=4):
    '''
    Retourne n citations texte parmi celles qui comportent un mot donné
    :param conn: Connexion à la base texte
    :param word: Mot à chercher
    :param n: Nombre de citations à retourner
    :return: n citations prises au hasard parmi celles qui comportent word
    '''
    return get_any_n(db.get_quotes(conn, word), n)


def get_cowords_for_word(conn, word, n=4):
    '''
    Retourne n mots associés à word
    :param conn: Connexion à la base texte
    :param word: Mot de la paire à chercher
    :param n: Nombre de mots à retourner
    :return: n mots associés à word, pris au hasard
    '''
    return get_any_n(db.get_cowords(conn, word), n)


def get_quotes_for_words(conn, conn_i, words):
    '''
    Retourne des citations texte ou image, associés aux mots words (une citation par mot)
    Tient compte de la probabilité pour les images
    :param conn: Connexion à la base texte
    :param conn_i: Connexion à la base image
    :param words: Mots à chercher
    :return: Une liste avec une citation par mot
    '''
    quotes = []
    for word in words:
        # On commence par chercher les images
        # Si on en trouve et si la probabilité est atteinte, on pioche dedans
        # Sinon on se rabat sur les textes, pour lesquels on est sûr de trouver des citations pour le mot
        candidates = db.get_quotes_i(conn_i, word)
        if random.random() < IMAGE_PROBABILITY and len(candidates) > 0:
            quotes.append(random.choice(candidates))
        else:
            quotes.append(random.choice(db.get_quotes(conn, word)))
    return quotes


def get_cowords_for_words_excluding(conn, words, excluded):
    '''
    Retourne des mots (co-mots) associés à une liste de mots donnée, en excluant certains autres mots
    Un mot par mot de words
    :param conn: Connexion à la base texte
    :param words: Liste de mots des paires à associer
    :param excluded: Liste de mots à exclure
    :return: Liste de mots
    '''
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
    '''
    Point d'entrée de l'application
    :param word: Mot de départ de la recherche
    :return: Une page
    '''

    # Connexions aux bases (sqlite3 veut que les connexions soient créées dans le thread qui les utilise, on
    # ne peut pas les garder en variables globales)
    conn = db.get_connection()
    conn_i = db.get_connection_i()

    # Lignes des premiers affichages
    # On raisonne en lignes car les associations de mots se font de haut en bas, même si la disposition des
    # éléments à l'écran est ensuite faite en colonnes (on transforme tout à la fin)
    rows = []

    # Paires de mots liant 2 lignes consécutives
    cowords = []

    # Première ligne : citations (texte uniquement mais c'est parce que c'est plus simple) du mot choisi
    rows.append(get_quotes_for_word(conn, word))

    # Deuxième ligne : co-mots et citations associées
    # Le 1er élément de chaque paire de co-mots est le mot d'entrée
    words2 = get_cowords_for_word(conn, word)
    cowords.append([(word, word2) for word2 in words2])
    rows.append(get_quotes_for_words(conn, conn_i, words2))

    # Troisième & quatrième lignes : co-co-(co-)mots et citations associées
    # Le 1er élément de chaque paire de co-mots n'est plus constant, c'est le 2ème co-mot de la paire au-dessus
    words3 = get_cowords_for_words_excluding(conn, words2, [word])
    cowords.append(zip(words2, words3))
    rows.append(get_quotes_for_words(conn, conn_i, words3))

    words4 = get_cowords_for_words_excluding(conn, words3, [word] + words2)
    cowords.append(zip(words3, words4))
    rows.append(get_quotes_for_words(conn, conn_i, words4))

    # Transformation en bandes (colonnes)
    bands = [[row[i] for row in rows] for i in xrange(4)]
    word_pairs = [[pair[i] for pair in cowords] for i in xrange(4)]

    conn.close()

    # Affiche le résultat
    return render_template('index.html', bands=bands, word_pairs=word_pairs, last_words=words4)


@app.route('/next/<word>')
def next_word(word):
    '''
    Route utilisée pour récupérer dynamiquement une nouvelle rangée d'éléments à la suite de ceux déjà affichés
    En pratique cette route sera appelée une fois par colonne, à chaque fois qu'elle devra s'enrichir
    :param word: Le dernier mot de la colonne appelante -> c'est le 1er d'une paire de co-mots
    :return: Un fragment de page
    '''

    # Connexions aux bases. Même topo que pour la route principale
    conn = db.get_connection()
    conn_i = db.get_connection_i()

    # Choisit un nouveau co-mot au hasard pour le mot précédent
    word2 = random.choice(db.get_cowords(conn, word))

    # Choisit une citation au hasard pour le nouveau co-mot - image ou texte
    quote = None
    if random.random() < IMAGE_PROBABILITY:
        choices = db.get_quotes_i(conn_i, word2)
        if len(choices) > 0:
            quote = random.choice(choices)
    if quote is None:
        quote = random.choice(db.get_quotes(conn, word2))
    conn.close()

    # Affiche le résultat
    return render_template('fragment.html', quote=quote, word=word2, previous_word=word)


if __name__ == '__main__':
    app.run()
