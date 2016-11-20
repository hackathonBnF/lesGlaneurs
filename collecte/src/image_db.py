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
    conn.execute('create table if not exists keyword (image_id integer, word varchar(50));')
    conn.execute('create table if not exists color (image_id integer, color varchar(50));')
    conn.execute('create unique index if not exists myindex1 on keyword (image_id, word);')
    conn.execute('create unique index if not exists myindex2 on color (image_id, color);')
    conn.execute('create table if not exists quote (image_id integer, url vachar(50), quote varchar(1000));')

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

def create_color(conn, image_id, color):
    conn.execute("insert OR IGNORE into color (image_id, color) values (%d, '%s')" % (image_id, color))
    conn.commit()

def create_keyword(conn, image_id, word):
    conn.execute("insert OR IGNORE into keyword (image_id, word) values (%d, '%s')" % (image_id, word))
    conn.commit()

def create_quote(conn, image_id, url, quote):
    url = re.sub("'", "''", url)
    quote = re.sub("'", "''", quote)
    conn.execute("insert into quote (image_id, url, quote) values (%d, '%s', '%s')" % (image_id, url, quote))
    conn.commit()

