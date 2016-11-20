# -*- coding: utf8 -*-

import sqlite3
import re


# Requêtage des docs texte


def escape_quote(x):
    return re.sub("'", "''", x)

def get_connection():
    conn = sqlite3.connect('../collecte/target/text/docs_sample.db')
    return conn

def get_quotes(conn, word):
    cur = conn.cursor()
    cur.execute("select doc_id, quote from quote where word = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res

def get_cowords(conn, word):
    cur = conn.cursor()
    cur.execute("select word2 from coword where word1 = '%s'" % word)
    res = cur.fetchall()
    cur.close()
    return res
