# -*- coding: utf8 -*-


# Récupération du texte OCR d'un corpus


import httplib
import urllib
import xml.etree.ElementTree as xtree
import cStringIO
import re

QUERY = '((dc.creator all "Baudelaire, Charles" or dc.contributor all "Baudelaire, Charles" ) and dc.title all "Les fleurs du mal " )'
HOST = 'gallica.bnf.fr'



# TODO : pagination


# Récupération de la liste
def get_list_docs(query):
    url = '/SRU?operation=searchRetrieve&version=1.2&startRecord=0&maximumRecords=15&page=1&collapsing=true&exactSearch=false&query=' + urllib.quote(QUERY) + '&filter=ocr.quality%20all%20%22texte%20disponible%22'
    gallica = httplib.HTTPConnection(HOST)
    gallica.request('GET', url)
    return gallica.getresponse().read()


xtree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/', 'srw': 'http://www.loc.gov/zing/srw/'}

# Récupération du texte d'un doc
def get_ocr(doc):
    tree = xtree.ElementTree()
    root = tree.parse(cStringIO.StringIO(doc))
    nodes = root.findall('srw:records/srw:record/srw:recordData/oai_dc:dc/dc:identifier', namespaces)
    url = ''
    for node in nodes:
        id = re.sub('^http://' + HOST, '', node.text)
        url = id + '/.texteBrut'
        gallica = httplib.HTTPConnection(HOST)
        gallica.request('GET', url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', 'Referer': 'http://gallica.bnf.fr/ark:/12148/bpt6k5834013m/f1n271.texteBrut'})
        filename = '../target/text/' + re.sub('/', '_', id)
        with open(filename, 'w') as f:
            f.write(gallica.getresponse().read())


get_ocr(get_list_docs(QUERY))