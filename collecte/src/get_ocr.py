# -*- coding: utf8 -*-


# Récupération du texte OCR d'un corpus


import httplib
import urllib
import xml.etree.ElementTree as xtree
import cStringIO
import re
import text_db as db
import nltk
from nltk.collocations import *
from bs4 import BeautifulSoup

HOST = 'gallica.bnf.fr'

xtree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')

NAMESPACES = {'dc': 'http://purl.org/dc/elements/1.1/', 'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/', 'srw': 'http://www.loc.gov/zing/srw/'}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', 'Referer': 'http://gallica.bnf.fr/ark:/12148/bpt6k5834013m/f1n271.texteBrut'}


IGNORE = nltk.corpus.stopwords.words('french') + ['les', 'qu', 'tout']

conn = db.get_connection()

# TODO : pagination


def get_list_docs(words, limit=3):
    '''
    Récupère une liste de documents OCRisés à partir de mots
    :param query: Les mots (chaîne)
    :return: Un document XML de résultat
    '''
    print 'Get docs for ' + words
    query = '(gallica all "' + words + '")'
    url = '/SRU?operation=searchRetrieve&version=1.2&startRecord=0&maximumRecords=' + str(limit) + '&page=1&collapsing=true&exactSearch=false&query=' + urllib.quote(query) + '&filter=ocr.quality%20all%20%22texte%20disponible%22'
    gallica = httplib.HTTPConnection(HOST)
    gallica.request('GET', url)
    return gallica.getresponse().read()



def ark_to_url(ark):
    '''
    Convertit un ID ARK en URL sans hôte
    :param ark:
    :return:
    '''
    return re.sub('^http://' + HOST, '', ark)


def is_valid_ark(ark):
    return ark.startswith('http://' + HOST)


def process_body(id, body, date, word):
    '''
    Traite le corps d'un document
    :param body:
    :return:
    '''
    filename = '../target/text/' + re.sub('/', '_', id)

    # Retire l'en-tête HTML
    body = re.sub('^.*<br><br>', '', body)

    # Passe en texte brut
    bs = BeautifulSoup(body)
    body = bs.get_text().lower()

    # Vire les apostrophes
    body = re.sub("'", ' ', body)

    # Conversion en texte NLTK
    text = nltk.word_tokenize(body)

    # Vire les mots trop petits ou à ignorer
    # (apply_word_filter marche pas ?)
    text = [w for w in text if len(w) > 3 and w not in IGNORE]

    # Cowords
    finder = BigramCollocationFinder.from_words(text)
    finder.apply_freq_filter(2)
    colloc = finder.nbest(nltk.collocations.BigramAssocMeasures.likelihood_ratio, n=50)

    # Quote
    quotes = [sent for sent in nltk.sent_tokenize(body) if sent.find(word) >= 0]

    # Save to DB
    doc_id = db.create_doc(conn, id, len(text), '' if date is None else date.text)
    for word1, word2 in colloc:
        db.create_coword(conn, doc_id, word1, word2)
    print ' -> ' + str(len(colloc)) + ' cowords'

    for quote in quotes:
        db.create_quote(conn, doc_id, word, quote)
    print ' -> ' + str(len(quotes)) + ' quotes'

    print ' -> doc_id = ' + str(doc_id)



def get_ocr(doc_list, word):
    '''
    Récupère et indexe les OCR issus d'une requête
    :param doc_list: Un doc XML de résultat
    :return:
    '''
    tree = xtree.ElementTree()
    root = tree.parse(cStringIO.StringIO(doc_list))
    nodes = root.findall('srw:records/srw:record', NAMESPACES)
    url = ''
    filenames = []
    for node in nodes:
        ark = node.find('srw:recordData/oai_dc:dc/dc:identifier', NAMESPACES)
        if ark is None or not is_valid_ark(ark.text):
            print ' -> Bad ID'
            continue

        date = node.find('srw:recordData/oai_dc:dc/dc:date', NAMESPACES)

        print 'Get OCR for ' + ark.text
        id = ark_to_url(ark.text)
        url = id + '/.texteBrut'
        gallica = httplib.HTTPConnection(HOST)
        gallica.request('GET', url)
        resp = gallica.getresponse()
        if resp.status == 200:
            process_body(id, resp.read(), date, word)
        else:
            print ' -> Bad status'


word = 'diable'
get_ocr(get_list_docs(word), word)

print 'Done'