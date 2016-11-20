# -*- coding: utf8 -*-

import sqlite3
import re


# Requêtage des docs texte


def escape_quote(x):
    return re.sub("'", "''", x)

def get_connection():
    conn = sqlite3.connect('../collecte/target/text/docs_sample.db')
    return conn

def get_connection_i():
    conn_i = sqlite3.connect('../collecte/target/images/images_sample.db')
    return conn_i

def get_quotes(conn, word):
    cur = conn.cursor()
    cur.execute("select doc_id, quote, '', 0 , 0 from quote where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res

def get_quotes_i(conn_i, word):
    cur = conn_i.cursor()
    cur.execute("select quote.image_id, quote, url, width, height from keyword join quote on keyword.image_id=quote.image_id join image on image.id=quote.image_id where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res

def get_cowords(conn, word):
    cur = conn.cursor()
    cur.execute("select word2 from coword where word1 = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res
