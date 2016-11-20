# -*- coding: utf8 -*-

import sqlite3
import re


# Requêtage des docs texte & image
# Il faudrait fusionner avec le code de collecte mais bon...


def escape_quote(x):
    '''
    Double les apostrophes éventuelles de la chaîne x, pour l'inclure dans une requête SQL
    :param x: La chaîne d'origine
    :return: La même avec les apostrophes doublées
    '''
    return re.sub("'", "''", x)

def get_connection():
    '''
    :return: Connexion à la base textes
    '''
    conn = sqlite3.connect('../collecte/target/text/docs.db')
    return conn

def get_connection_i():
    '''
    :return: Connexion à la base images
    '''
    conn_i = sqlite3.connect('../collecte/target/image/images.db')
    return conn_i


def get_quotes(conn, word):
    '''
    Récupère les citations texte contenant un mot
    Le schéma de sortie est complété pour être homogène avec get_quotes_i()
    :param conn: Connexion
    :param word: Le mot
    :return: La liste des citations, avec les références (tuples)
    '''
    cur = conn.cursor()
    cur.execute("select id_ark, quote, '' as url, 0 as width, 0 as height, words from quote join doc on quote.doc_id=doc.id where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res


def get_quotes_i(conn_i, word):
    '''
    Récupère les citations images associées à un mot
    :param conn_i: Connexion
    :param word: Le mot
    :return: La liste des citations, avec les références (tuples)
    '''
    cur = conn_i.cursor()
    cur.execute("select id_ark, quote, url, width, height, 0 as words from keyword join quote on keyword.image_id=quote.image_id join image on image.id=quote.image_id where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res


def get_cowords(conn, word):
    '''
    Récupère les co-mots d'un mot donné
    :param conn: Connexion à la base texte
    :param word: Premier mot de la paire
    :return: La liste des co-mots de word
    '''
    cur = conn.cursor()
    cur.execute("select word2 from coword where word1 = '%s'" % word)
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]
