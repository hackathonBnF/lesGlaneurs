# -*- coding: utf8 -*-

import sqlite3
import re


# Requêtage des docs texte


def escape_quote(x):
    return re.sub("'", "''", x)

def get_connection():
    conn = sqlite3.connect('../collecte/target/text/docs.db')
    return conn

def get_quotes(conn, word):
    cur = conn.cursor()
    cur.execute("select doc_id, quote from quote where word = '%s'" % word)
    rows = cur.fetchall()
    cur.close()
    return rows

def get_cowords(conn, word):
    cur = conn.cursor()
    cur.execute("select word2 from coword where word1 = '%s'" % word)
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]
