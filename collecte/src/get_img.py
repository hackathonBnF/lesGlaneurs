# -*- coding: utf8 -*-


# Récupération du texte OCR d'un corpus


import cStringIO
import httplib
import re
import urllib
import xml.etree.ElementTree as xtree
from dico import KEYWORD
import image_db as db
from PIL import Image, ImageOps
import colorthief
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

conn = db.get_connection()

HOST = 'gallica.bnf.fr'

xtree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
NAMESPACES = {'dc': 'http://purl.org/dc/elements/1.1/', 'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/', 'srw': 'http://www.loc.gov/zing/srw/'}

# TODO : pagination

# Récupération de la liste
def get_list_docs(mot, page):
    url = '/SRU?operation=searchRetrieve&version=1.2&startRecord=' + str((page-1)*50+1) + '&maximumRecords=50&page=' + str(page) + '&collapsing=true&exactSearch=false&query='\
          + urllib.quote('(gallica adj "' + mot + '") and (dc.type all "image") and (provenance adj "bnf.fr")')
    print url
    gallica = httplib.HTTPConnection(HOST)
    gallica.request('GET', url)
    return gallica.getresponse().read()

# http://gallica.bnf.fr/iiif/ark:/12148/btv1b90017179/f15/0,1900,2400,1200/full/0/native.jpg
# {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}

# Récupération du texte d'un doc
def get_img(mot, page):
    doc = get_list_docs(mot, page)
    tree = xtree.ElementTree()
    root = tree.parse(cStringIO.StringIO(doc))
    nodes = root.findall('srw:records/srw:record', NAMESPACES)
    numberOfRecords = root.findall('srw:numberOfRecords', NAMESPACES)[0].text
    nextRecordPosition = root.findall('srw:nextRecordPosition', NAMESPACES)[0].text
    print numberOfRecords, nextRecordPosition

    url = ''
    if numberOfRecords > 0:
        for node in nodes:
            ark = node.find('srw:recordData/oai_dc:dc/dc:identifier', NAMESPACES)
            if ark is None or not is_valid_ark(ark.text):
                print ' -> Bad ID'
                continue
            ark_id = ark_to_url(ark.text)
            if db.get_image(conn, ark_id) is not None:
                print ' -> Already in'
                continue

            date = node.find('srw:recordData/oai_dc:dc/dc:date', NAMESPACES)
            datetext = date.text if date is not None else None
            quote = node.find('srw:recordData/oai_dc:dc/dc:title', NAMESPACES)
            quotetext = quote.text.split(':')[0] if quote is not None else None

            #url = '/iiif' + ark.text + '/f1/full/full/0/native.jpg'
            url = ark.text + '.thumbnail'
            #url = ark.text + '.highres'

            filename = '../target/image/thumb/' + re.sub('/|:', '_', ark_id) + '.jpeg'

            urllib.urlretrieve(url, filename)


            # insert image to DB
            with Image.open(filename) as im:
                width, height = im.size
                image_id = db.create_image(conn, ark_id, width, height, datetext)
                db.create_keyword(conn, image_id, mot)
                db.create_quote(conn, image_id, url, quotetext)
                ct = colorthief.ColorThief(filename)
                for color in ct.get_palette(color_count=6, quality=1):
                    cc = get_closest_color(color)
                    if cc not in ['Black', 'White', 'Gray', 'Silver']:
                        db.create_color(conn, image_id, cc)
                # sample image to 5 colors
                #result = ImageOps.posterize(im, 1)
                #result = im.convert(mode='P', colors=8)
                #result.convert("RGB").save(filename + '.jpeg')
        if int(nextRecordPosition)<int(numberOfRecords)+50:
            get_img(mot, page+1)

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
        mycolor_lab = convert_color(sRGBColor(mycolor[0], mycolor[1], mycolor[2]), LabColor)
        rgbc_lab = convert_color(sRGBColor(rgbc[0], rgbc[1], rgbc[2]), LabColor)
        dist = delta_e_cie2000(mycolor_lab, rgbc_lab)
        if dist < min_dist:
            min_dist = dist
            best_color = color
    return best_color

def ark_to_url(ark):
    '''
    Convertit un ID ARK en URL sans hôte
    :param ark:
    :return:
    '''
    return re.sub('^http://' + HOST, '', ark)


def is_valid_ark(ark):
    return ark.startswith('http://' + HOST)

for mots in KEYWORD.keys():
    for mot in KEYWORD[mots]:
        print mot
        get_img(mot, 1)