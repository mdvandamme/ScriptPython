# -*- coding: utf-8 -*-
"""
Script qui extrait depuis l'API Camptocamp les itinéraires de randonnées, puis les intègre dans ElasticSearch.
Données sur Isère et Savoie.
L'index et le mapping sont déjà créés.

Isère = 14328
Savoie = 14295    

Attention l'API ne permet pas de récupérer plus de 10000 lignes même si le résultat en a plus.

Created on Sep 09 2017
@author: Marie-Dominique Van Damme
"""

from pyproj import Proj, transform
import urllib.request
import json
import pyes

region = "14295"


esurl = "127.0.0.1:9200"
esindex = "itineraires"
estype = "itineraire"
conn = pyes.ES(esurl, timeout=60, bulk_size=10)

proxy = urllib.request.ProxyHandler({
#    'http': 'proxy.ign.fr:3128',
#    'https': 'proxy.ign.fr:3128'
})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)

inProj = Proj(init='epsg:3857')
outProj = Proj(init='epsg:4326')

url = 'https://api.camptocamp.org/routes?limit=5&a=' + region
response = urllib.request.urlopen(url)
data = json.load(response)
total = data['total']

nbiter = int(total / 30) + 1  
offset = 0
for j in range (nbiter):
    print ("---------- page " + str(j) + " ( " + str(offset) + " ) ")
    
    url = 'https://api.camptocamp.org/routes?a=' + region + '&offset=' + str(offset) + '&limit=30'
    responseListe = urllib.request.urlopen(url)
    dataListe = json.load(responseListe)
    
    for d in range(len(dataListe['documents'])):
        #feature = dataListe['documents'][d]
        
        docid = dataListe['documents'][d]['document_id']
        
        activite = dataListe['documents'][d]['activities']
        
        if activite[0] != "slacklining" and docid != 913948:
        
            urlId = 'https://api.camptocamp.org/routes/' + str(docid)
            responseId = urllib.request.urlopen(urlId)
            feature = json.load(responseId)
            
            title = feature['locales'][0]['title']
            titlefr = ""
            for t in range(len(feature['locales'])):
                lang = feature['locales'][t]['lang']
                if lang == "fr":
                    titlefr = feature['locales'][t]['title']
            if titlefr != "":
                title = titlefr
            
            remarks = feature['locales'][0]['remarks']
            remarksfr = ""
            for t in range(len(feature['locales'])):
                lang = feature['locales'][t]['lang']
                if lang == "fr":
                    remarksfr = feature['locales'][t]['remarks']
            if remarksfr != "":
                remarks = remarksfr
                
            description = feature['locales'][0]['description']
            descriptionfr = ""
            for t in range(len(feature['locales'])):
                lang = feature['locales'][t]['lang']
                if lang == "fr":
                    descriptionfr = feature['locales'][t]['description']
            if descriptionfr != "":
                description = descriptionfr
                
            elevation_max = feature['elevation_max']
            if elevation_max == None:
                elevation_max = -1
            
            elevation_min = -1
            if feature['elevation_min'] != None:
                elevation_min = feature['elevation_min']
            
            height_diff_up = feature['height_diff_up']
            if height_diff_up == None:
                height_diff_up = -1
            
            durations = feature['durations']
            if durations == None:
                durations = -1
                
            if "glacier_gear" in feature:
                glacier_gear = feature['glacier_gear']
            #if glacier_gear == None:
            else:
                glacier_gear = ""
            
            route_types = feature['route_types']
            orientations = feature['orientations']
            
            f = dict()
            f["docid"] = docid
            f["title"] = title
            f["elevation_max"] = elevation_max
            f["elevation_min"] = elevation_min
            f["height_diff_up"] = height_diff_up
            f["durations"] = durations
            f["route_types"] = route_types
            f["activite"] = activite
            f["remarks"] = remarks
            f["description"] = description
            f["orientations"] = orientations
            f["glacier_gear"] = glacier_gear
            
            # Récupère la géométrie
            if feature['geometry']['geom_detail'] != None:
                coords = json.loads(feature['geometry']['geom_detail']) 
                if coords['type'] == "LineString":
                    loc = dict()
                    loc["type"] = "LineString"
                    
                    tabcoordI = coords['coordinates']
                    if len(tabcoordI) < 100:
                        print (str(docid) + "-" + str(len(tabcoordI)))
                        tabcoordF = []
                        for i in range(len(tabcoordI)):
                            point = tabcoordI[i]
                            lon = point[0]
                            lat = point[1]
                            x2,y2 = transform(inProj, outProj, lon, lat)
                            tabcoordF.append([x2, y2])
                        
                        loc["coordinates"] = tabcoordF
                        f["location"] = loc
                    else:
                        print ("trop de vertex : " + str(len(tabcoordI)))
	
            # Ways
            if "associations" in feature:
                if "waypoints" in feature["associations"]:
                    ways = feature["associations"]["waypoints"]
                    
                    tw = []
                    for s in range(len(ways)):
                        way = ways[s]
                        
                        geom = json.loads(way['geometry']['geom']) # Récupère la géométrie
                        lon = geom["coordinates"][0]
                        lat = geom["coordinates"][1]
                        x2,y2 = transform(inProj, outProj, lon, lat)
                        
                        elevation = -1
                        if "elevation" in way:
                            elevation = way["elevation"]
                        
                        t = dict()
                        t["docid"] = way["document_id"]
                        t["elevation"] = elevation
                        t["waypoint_type"] = way["waypoint_type"]
                        t["location"] = dict()
                        t["location"]["type"] = "Point"
                        t["location"]["coords"] = dict()
                        t["location"]["coords"]["lat"] = y2
                        t["location"]["coords"]["lon"] = x2
                        t["title"] = way["locales"][0]["title"]
                        tw.append(t)
                    
                    f["ways"] = tw
                    
                    
            data = json.dumps(f)
            conn.index(data, esindex, estype, docid)
    
    offset = offset + 30


print ("fin : " + str(offset))
