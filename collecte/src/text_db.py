# -*- coding: utf8 -*-

import sqlite3
import re


# Indexation des docs texte

def get_connection():
    '''
    Récupère une connexion à la base texte
    :return: Connexion
    '''
    conn = sqlite3.connect('../target/text/docs.db')
    create_db(conn)
    return conn


def create_db(conn):
    '''
    Initialise les tables de la base, si elles n'existent pas
    :param conn: Connexion
    '''
    conn.execute('create table if not exists doc (id integer primary key autoincrement not null, id_ark varchar(50), words integer, crdate varchar(50));')
    conn.execute('create table if not exists coword (doc_id integer, word1 varchar(50), word2 varchar(50));')
    conn.execute('create table if not exists quote (doc_id integer, word vachar(50), quote varchar(1000));')


def create_doc(conn, ark, words, crdate):
    '''
    Crée un document s'il n'existe pas déjà
    :param conn:
    :param ark:
    :param words:
    :param crdate:
    :return: L'ID (numérique interne à la base) du document
    '''
    if get_doc(conn, ark) is None:
        conn.execute("insert into doc (id_ark, words, crdate) values ('%s', %d, '%s')" % (ark, words, crdate))
        conn.commit()
    return get_doc(conn, ark)[0]


def get_doc(conn, ark):
    '''
    Récupère l'ID technique d'un document à partir de son Ark
    Permet de vérifier s'il existe déjà
    :param conn: Connexion
    :param ark: Ark
    :return: L'ID du document ou None
    '''
    cur = conn.cursor()
    cur.execute("select id from doc where id_ark = '%s'" % ark)
    id = cur.fetchone()
    cur.close()
    return id


def create_coword(conn, doc_id, word1, word2):
    '''
    Ajoute une paire de mots. L'ajout est fait dans les 2 sens
    :param conn: Connexion
    :param doc_id: ID du document où la paire est rencontrée
    :param word1: Mot 1
    :param word2: Mot 2
    '''
    word1 = re.sub("'", "''", word1)
    word2 = re.sub("'", "''", word2)
    conn.execute("insert into coword (doc_id, word1, word2) values (%d, '%s', '%s')" % (doc_id, word1, word2))
    conn.execute("insert into coword (doc_id, word1, word2) values (%d, '%s', '%s')" % (doc_id, word2, word1))
    conn.commit()


def create_quote(conn, doc_id, word, quote):
    '''
    Ajoute une citation texte
    :param conn: Connexion
    :param doc_id: ID du document d'où la citation est extraite
    :param word: Mot ayant servi à isoler la citation
    :param quote: Citation
    '''
    word = re.sub("'", "''", word)
    quote = re.sub("'", "''", quote)
    conn.execute("insert into quote (doc_id, word, quote) values (%d, '%s', '%s')" % (doc_id, word, quote))
    conn.commit()

