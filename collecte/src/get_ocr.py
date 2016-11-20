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
import codecs
import random

HOST = 'gallica.bnf.fr'

xtree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')

NAMESPACES = {'dc': 'http://purl.org/dc/elements/1.1/', 'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/', 'srw': 'http://www.loc.gov/zing/srw/'}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', 'Referer': 'http://gallica.bnf.fr/ark:/12148/bpt6k5834013m/f1n271.texteBrut'}

UTF8 = codecs.lookup('utf-8')

IGNORE = nltk.corpus.stopwords.words('french') + ['les', 'qu', 'tout']

conn = db.get_connection()


words = [
    u'amour',
    u'voyage',
    u'rêve',
    u'joie',
    u'affamé',
    u'voyageur',
    u'tristesse',
    u'bourré',
    u'danse',
	u'carnaval',
	u'humour',
	u'cirque',
	u'kermesse',
	u'guinguette',
	u'caricature',
	u'commémoration',
	u'anniversaire',
	u'mort',
	u'gisant',
	u'spleen',
	u'macabre',
	u'vérole',
	u'vomir',
	u'choléra',
	u'vermine',
	u'peste',
	u'souris',
	u'vache',
	u'tortue',
	u'chat',
	u'zoo',
	u'loutre',
	u'vagabond',
	u'baluchon',
    u'malade',
    u'rêveur',
    u'bisounours',
    u'séduction',
    u'courtisanes',
    u'érotique',
    u'coquine',
    u'coquin',
    u'baiser',
    u'bacchanale',
    u'fouet',
    u'prostituée',
    u'cocotte',
    u'baiser',
    u'coeur brisé',
    u'noce',
    u'colérique',
    u'vilain',
    u'guillotine',
    u'torture',
    u'assassinat',
    u'supplice',
    u'sacrebleu',
    u'ivre',
	u'bacchus',
	u'nausée',
	u'alcool',
	u'boire',
	u'absinthe',
	u'ivrogne',
	u'gueux',
	u'boissons',
    u'baluchon',
	u'exotiques',
	u'paysages',
	u'traversée',
	u'train',
	u'avion',
	u'hippomobile',
	u'hôtel particulier',
	u'trajet',
	u'gourmandise',
    u'songe',
	u'ripaille',
    u'cauchemar',
	u'glouton',
    u'opium',
	u'gargantua',
	u'chimère',
	u'festin',
	u'rêveur',
    u'cocagne',
	u'rêves',
	u'paresse'
]

random.shuffle(words)

def get_list_docs(word1, word2, limit=3):
    '''
    Récupère une liste de documents OCRisés à partir de mots
    :param query: Les mots
    :return: Un document XML de résultat
    '''
    print 'Get docs for ' + word1 + ' & ' + word2
    query = '(gallica all "' + word1 + '" and gallica all "' + word2 + '")'
    filter = 'sdewey all "84" and ocr.quality all "texte disponible"'
    url = '/SRU?operation=searchRetrieve&version=1.2&startRecord=0&maximumRecords=' + str(limit) + '&page=1&collapsing=true&exactSearch=false&query=' + urllib.quote(UTF8.encode(query)[0]) + '&filter=' + urllib.quote(filter)
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


def process_body(id, body, date, word1, word2):
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

    # Quote
    sents = nltk.sent_tokenize(body)
    quotes1 = [sent for sent in sents if sent.find(word1) >= 0]
    quotes2 = [sent for sent in sents if sent.find(word2) >= 0]

    # Save to DB
    doc_id = db.create_doc(conn, id, len(text), '' if date is None else date.text)
    db.create_coword(conn, doc_id, word1, word2)

    for quote in quotes1:
        db.create_quote(conn, doc_id, word1, quote)
    for quote in quotes2:
        db.create_quote(conn, doc_id, word2, quote)
    print ' -> ' + str(len(quotes1) + len(quotes2)) + ' quotes'

    print ' -> doc_id = ' + str(doc_id)



def save_ocr(doc_list, word1, word2):
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

        ark_id = ark_to_url(ark.text)

        if db.get_doc(conn, ark_id) is not None:
            print ' -> Already in'
            continue

        date = node.find('srw:recordData/oai_dc:dc/dc:date', NAMESPACES)

        print 'Get OCR for ' + ark_id
        url = ark_id + '/.texteBrut'
        gallica = httplib.HTTPConnection(HOST)
        gallica.request('GET', url)
        resp = gallica.getresponse()
        if resp.status == 200:
            process_body(ark_id, UTF8.decode(resp.read())[0], date, word1, word2)
        else:
            print ' -> Bad status'


for i in xrange(len(words)):
    for j in xrange(len(words)):
        if j <= i:
            continue
        docs = get_list_docs(words[i], words[j], limit=10)
        save_ocr(docs, words[i], words[j])


print 'Done'