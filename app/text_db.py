# -*- coding: utf8 -*-

import sqlite3
import re


# Requêtage des docs texte


def escape_quote(x):
    return re.sub("'", "''", x)

def get_connection():
    conn = sqlite3.connect('../collecte/target/text/docs.db')
    return conn

def get_connection_i():
    conn_i = sqlite3.connect('../collecte/target/image/images.db')
    return conn_i

def get_quotes(conn, word):
    cur = conn.cursor()
    cur.execute("select id_ark, quote, '' as url, 0 as width, 0 as height from quote join doc on quote.doc_id=doc.id where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res

def get_quotes_i(conn_i, word):
    cur = conn_i.cursor()
    cur.execute("select id_ark, quote, url, width, height from keyword join quote on keyword.image_id=quote.image_id join image on image.id=quote.image_id where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res

def get_cowords(conn, word):
    cur = conn.cursor()
    cur.execute("select word2 from coword where word1 = '%s'" % word)
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]
