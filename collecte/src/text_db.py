# -*- coding: utf8 -*-

import sqlite3
import re


# Indexation des docs texte

def get_connection():
    conn = sqlite3.connect('../target/text/docs.db')
    create_db(conn)
    return conn

def create_db(conn):
    conn.execute('create table if not exists doc (id integer primary key autoincrement not null, id_ark varchar(50), words integer, crdate varchar(50));')
    conn.execute('create table if not exists coword (doc_id integer, word1 varchar(50), word2 varchar(50));')
    conn.execute('create table if not exists quote (doc_id integer, word vachar(50), quote varchar(1000));')


def create_doc(conn, ark, words, crdate):
    if get_doc(conn, ark) is None:
        conn.execute("insert into doc (id_ark, words, crdate) values ('%s', %d, '%s')" % (ark, words, crdate))
        conn.commit()
    return get_doc(conn, ark)

def get_doc(conn, ark):
    cur = conn.cursor()
    cur.execute("select id from doc where id_ark = '%s'" % ark)
    id = cur.fetchone()
    cur.close()
    return None if id is None else id[0]

def create_coword(conn, doc_id, word1, word2):
    word1 = re.sub("'", "''", word1)
    word2 = re.sub("'", "''", word2)
    conn.execute("insert into coword (doc_id, word1, word2) values (%d, '%s', '%s')" % (doc_id, word1, word2))
    conn.execute("insert into coword (doc_id, word1, word2) values (%d, '%s', '%s')" % (doc_id, word2, word1))
    conn.commit()

def create_quote(conn, doc_id, word, quote):
    word = re.sub("'", "''", word)
    quote = re.sub("'", "''", quote)
    conn.execute("insert into quote (doc_id, word, quote) values (%d, '%s', '%s')" % (doc_id, word, quote))
    conn.commit()

