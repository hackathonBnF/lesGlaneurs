# -*- coding: utf8 -*-


# Récupération du texte OCR d'un corpus


import cStringIO
import httplib
import re
import urllib
import xml.etree.ElementTree as xtree
import dico

QUERY = '('
HOST = 'gallica.bnf.fr'

for mots in KEYWORD:
    for mot in mots:
        print mot


xtree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/', 'srw': 'http://www.loc.gov/zing/srw/'}

# TODO : pagination

# Récupération de la liste
def get_list_docs(query, page):
    url = '/SRU?operation=searchRetrieve&version=1.2&startRecord=' + str((page-1)*50+1) + '&maximumRecords=50&page=' + str(page) + '&collapsing=true&exactSearch=false&query='\
          + urllib.quote(QUERY + 'and (dc.type all "image") and (provenance adj "bnf.fr")')
    print url
    gallica = httplib.HTTPConnection(HOST)
    gallica.request('GET', url)
    return gallica.getresponse().read()

# http://gallica.bnf.fr/iiif/ark:/12148/btv1b90017179/f15/0,1900,2400,1200/full/0/native.jpg
# {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}

# Récupération du texte d'un doc
def get_img(page):
    doc = get_list_docs(QUERY, page)
    tree = xtree.ElementTree()
    root = tree.parse(cStringIO.StringIO(doc))
    nodes = root.findall('srw:records/srw:record/srw:recordData/oai_dc:dc/dc:identifier', namespaces)
    numberOfRecords = root.findall('srw:numberOfRecords', namespaces)[0].text
    nextRecordPosition = root.findall('srw:nextRecordPosition', namespaces)[0].text
    print numberOfRecords, nextRecordPosition

    url = ''
    for node in nodes:
        if re.match(r'^http', node.text):
            id = re.sub('^http://' + HOST, '', node.text)
            #url = '/iiif' + id + '/f1/full/full/0/native.jpg'
            url = id + '.thumbnail'
            #url = id + '.highres'
            #print url
            #gallica = httplib.HTTPConnection(HOST)
            #gallica.request('GET', url)
            filename = '../target/image/' + re.sub('/|:', '_', id) + '.jpeg'
            print filename
            #print "==========="
            urllib.urlretrieve("http://gallica.bnf.fr" + url, filename)
            #with open(filename, 'wb') as f:
            #    f.write(gallica.getresponse().read())
            #ct = ColorThief(filename)
            #for color in ct.get_palette(color_count=10):
            #    cc = get_closest_color(color)
            #    if cc not in ['Black','White','Gray','Maroon','Silver','Olive']:
            #        print cc
    if int(nextRecordPosition) < int(numberOfRecords) + 50:
        get_img(page+1)

def get_closest_color(mycolor):
    mapping_color = {
        'Black': (0,0,0),
        'White': (255,255,255),
        'Red':(255,0,0),
        'Lime':(0,255,0),
        'Blue':(0,0,255),
        'Yellow':(255,255,0),
        'Cyan':(0,255,255),
        'Magenta':(255,0,255),
        'Silver':(192,192,192),
        'Gray':(128,128,128),
        'Maroon':(128,0,0),
        'Olive':(128,128,0),
        'Green':(0,128,0),
        'Purple':(128,0,128),
        'Teal':(0,128,128),
        'Navy':(0,0,128)
    }
    min_dist = 200000
    for color, rgbc in mapping_color.items():
        dist = sum((mycolor[i] - rgbc[i]) ** 2 for i in range(3))
        if dist < min_dist:
            min_dist = dist
            best_color = color
    return best_color

get_img(1)