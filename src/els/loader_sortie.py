# -*- coding: utf-8 -*-
"""
Script qui extrait depuis l'API Camptocamp les sorties, puis les intègre dans ElasticSearch.
Données sur Isère.
L'index et le mapping sont déjà créés.

Isère = 14328
Savoie = 14295    page 139 4170

Attention l'API ne permet pas de récupérer plus de 10000 lignes même si le résultat en a plus.

Created on Aug 25 2017
@author: MDVan-Damme
"""

from pyproj import Proj, transform
import urllib.request
import json
import pyes

esurl = "127.0.0.1:9200"
esindex = "sorties"
estype = "sortie"
conn = pyes.ES(esurl, timeout=60, bulk_size=10)

proxy = urllib.request.ProxyHandler({
#    'http': 'proxy.ign.fr:3128',
#    'https': 'proxy.ign.fr:3128'
})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)

inProj = Proj(init='epsg:3857')
outProj = Proj(init='epsg:4326')

url = 'https://api.camptocamp.org/outings?limit=30&a=14295'
response = urllib.request.urlopen(url)
data = json.load(response)
total = data['total']

#nbiter = int(total / 30) + 1  
nbiter = 333
#nbiter = 664 
offset = 0
#offset = 9960
debut = 0
#debut = 333
for j in range (debut, nbiter):
    print ("---------- page " + str(j) + " ( " + str(offset) + " ) ")
    
    url = 'https://api.camptocamp.org/outings?a=14295&offset=' + str(offset) + '&limit=30'
    responseListe = urllib.request.urlopen(url)
    #print response.url
    dataListe = json.load(responseListe)
    
    for d in range(len(dataListe['documents'])):
        feature = dataListe['documents'][d]
        
        docid = dataListe['documents'][d]['document_id']
        condrating = dataListe['documents'][d]['condition_rating']
        if condrating == None:
            condrating = ""
        quality = dataListe['documents'][d]['quality']
        if quality == None:
            quality = ""
        datestart = dataListe['documents'][d]['date_start']
        if datestart == None:
            datestart = ""
        dateend = dataListe['documents'][d]['date_end']
        if dateend == None:
            dateend = ""
        
        # TODO : tableau
        activite = dataListe['documents'][d]['activities']
        
        
        geom = json.loads(feature['geometry']['geom']) # Récupère la géométrie
        lon = geom["coordinates"][0]
        lat = geom["coordinates"][1]
        x2,y2 = transform(inProj,outProj,lon,lat)
        
        title = dataListe['documents'][d]['locales'][0]['title']
        titlefr = ""
        for t in range(len(dataListe['documents'][d]['locales'])):
            lang = dataListe['documents'][d]['locales'][t]['lang']
            if lang == "fr":
                titlefr = dataListe['documents'][d]['locales'][t]['title']
        if titlefr != "":
            title = titlefr
        
        url = 'https://api.camptocamp.org/outings/' + str(docid)
        response = urllib.request.urlopen(url)
        data = json.load(response)
        
        description = data['locales'][0]['description']
        if description == None:
            description = ""
        route_description = data['locales'][0]['route_description']
        if route_description == None:
            route_description = ""
        access_comment = data['locales'][0]['access_comment']
        if access_comment == None:
            access_comment = ""
        timing = data['locales'][0]['timing']
        if timing == None:
            timing = ""
        participant_count = data['participant_count']
        if participant_count == None:
            participant_count = -1

        f = dict()
        f["docid"] = docid
        f["title"] = title
        f["date_start"] = datestart
        f["date_end"] = dateend
        f["condition_rating"] = condrating
        f["quality"] = quality
        f["description"] = description
        f["route_description"] = route_description
        f["access_comment"] = access_comment
        f["timing"] = timing
        f["participant_count"] = participant_count
        
        f["location"] = dict()
        f["location"]["coords"] = dict()
        f["location"]["coords"]["lat"] = y2
        f["location"]["coords"]["lon"] = x2
        data = json.dumps(f)

        conn.index(data, esindex, estype, docid)

    offset = offset + 30


print ("fin : " + str(offset))
