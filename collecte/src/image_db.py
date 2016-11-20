# -*- coding: utf8 -*-

import sqlite3
import re


# Indexation des images

def get_connection():
    conn = sqlite3.connect('../target/image/images.db')
    create_db(conn)
    return conn

def create_db(conn):
    conn.execute('create table if not exists image (id integer primary key autoincrement not null, id_ark varchar(50), width integer, height integer, crdate varchar(50));')
    conn.execute('create table if not exists keyword (doc_id integer, keyword varchar(50));')
    conn.execute('create table if not exists color (doc_id integer, color integer);')


def create_image(conn, ark, width, height, crdate):
    if get_image(conn, ark) is None:
        conn.execute("insert into image (id_ark, width, height, crdate) values ('%s', %d, %d, '%s')" % (ark, width, height, crdate))
        conn.commit()
    return get_image(conn, ark)

def get_image(conn, ark):
    cur = conn.cursor()
    cur.execute("select id from image where id_ark = '%s'" % ark)
    id = cur.fetchone()
    cur.close()
    return None if id is None else id[0]

def create_color(conn, doc_id, color):
    conn.execute("insert into color (doc_id, color) values (%d, '%s')" % (doc_id, color))
    conn.commit()

def create_keyword(conn, doc_id, word):
    conn.execute("insert into color (doc_id, color) values (%d, '%s')" % (doc_id, word))
    conn.commit()

