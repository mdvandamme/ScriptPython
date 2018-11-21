# -*- coding: utf-8 -*-
"""
/*
 * This file is part of the GeOxygene project source files.
 * 
 * GeOxygene aims at providing an open framework which implements OGC/ISO
 * specifications for the development and deployment of geographic (GIS)
 * applications. It is a open source contribution of the COGIT laboratory at the
 * Institut Géographique National (the French National Mapping Agency).
 * 
 * See: http://oxygene-project.sourceforge.net
 * 
 * Copyright (C) 2005 Institut Géographique National
 * 
 * This library is free software; you can redistribute it and/or modify it under
 * the terms of the GNU Lesser General Public License as published by the Free
 * Software Foundation; either version 2.1 of the License, or any later version.
 * 
 * This library is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
 * details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library (see file LICENSE if present); if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307 USA
 */


Created on September 2018
@author: Marie-Dominique Van Damme
@version 1.0

"""

import sys
sys.path.append('.')

cle = 'pratique'
login = ''
passwd = ''


import Capabilities as metadata
import Resolution as res

import matplotlib.pyplot as plt
from PIL import Image

from pyproj import Proj, transform

import urllib.request



def visu_image(images, titles):
    
    f, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, sharey=True)
    f.set_figheight(15)
    f.set_figwidth(15)

    # 
    ax1.set_title(titles[0])
    ax1.imshow(images[0]) 

    # maps
    ax2.set_title(titles[1])
    ax2.imshow(images[1]) 
    
    ax3.set_title(titles[2])
    ax3.imshow(images[2]) 
    
    ax4.set_title(titles[3])
    ax4.imshow(images[3]) 


def visu_une_image(image):
    
    f, (ax1) = plt.subplots(1, 1, sharey=True)
    #f.set_figheight(5)
    #f.set_figwidth(5)

    # 
    ax1.set_title('concat')
    ax1.imshow(image) 
    
    
def getImage(zoom, X, Y, NomLayer):
    
    global login, passwd

    cap = metadata.Capabilities(cle, zoom, NomLayer)
    # print ("Layer name : " + cap.getTitleLayer())
    # Tester si le niveau de zoom est valide
    if not cap.isZoomValid():
        return None
        #sys.exit(0)

    format = cap.getFormat()
    #print (format)
    (X0, Y0) = cap.getTopLeftCorner()


    url = "http://wxs.ign.fr/" + cle + "/geoportail/wmts"
    url = url + "?LAYER=" + NomLayer + "&"
    url = url + "EXCEPTIONS=text/xml&FORMAT=" + format + "&SERVICE=WMTS&VERSION=1.0.0&"
    url = url + "REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&"

    sourceCrs = Proj(init='epsg:2154')
    destCrs   = Proj(init='epsg:3857')

    X, Y = transform(sourceCrs, destCrs, X, Y)

    d = 256 * res.RES[zoom]
    dx = X - X0
    dy = Y0 - Y
     
    TILECOL   = int(float(dx) / float(d))
    TILEROW  = int(dy / d)
   
    url = url + "TILEMATRIX=" + str(zoom) + "&TILEROW=" + str(TILEROW) + "&TILECOL=" + str(TILECOL)

    # create a password manager
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    # Add the username and password.
    password_mgr.add_password(None, url, login, passwd)
    
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib.request.build_opener(handler)

    # use the opener to fetch a URL
    conn = opener.open(url)
    img = Image.open(conn)
    return img


proxy = urllib.request.ProxyHandler({
    'http': 'proxy.ign.fr:3128',
    'https': 'proxy.ign.fr:3128'
})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)

zoom = 13
X = 164891.8
Y = 6860739.8

NomLayer = "ORTHOIMAGERY.ORTHOPHOTOS"
image1 = getImage(zoom, X, Y, NomLayer)
if image1 == None:
    print ('Erreur ortho')

NomLayer = "GEOGRAPHICALGRIDSYSTEMS.PLANIGN"
image2 = getImage(zoom, X, Y, NomLayer)
if image2 == None:
    print ('Erreur image 2')
    
NomLayer = "GEOGRAPHICALGRIDSYSTEMS.MAPS"
image3 = getImage(zoom, X, Y, NomLayer)
if image3 == None:
    print ('Erreur image 3')
    
NomLayer = "GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.ROUTIER"
image4 = getImage(zoom, X, Y, NomLayer)
if image4 == None:
    print ('Erreur image 4')


titles= ['Photographies aériennes', 'Plans IGN', 'Cartes IGN', 'Cartes SCAN Express Routier']
images = [image1, image2, image3, image4]
visu_image (images, titles)


