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


Récupère pour un zoom et un layer :
    les zooms autorisés
    le format
    les coordonnées du coin supérieur gauche


"""

from urllib.request import urlopen
from xml.dom.minidom import parse


class Capabilities:
    
    # Constructor.
    def __init__(self, cle, zoom, nomlayer):
        
        URL_CAPABILITIES = "http://wxs.ign.fr/" + cle + "/geoportail/wmts?"
        URL_CAPABILITIES = URL_CAPABILITIES + "SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"
        # print (URL_CAPABILITIES)
        
        self.nomlayer = nomlayer
        self.zoom = zoom
        
        with urlopen(URL_CAPABILITIES) as conn:
            #print ("connexion etablie")
            domCap = parse(conn)
            
            # On initialise les paramètres d'origine
            self.X0 = 0 # -20037508
            self.Y0 = 0 # 20037508
            self.ScaleDenominator = 0
            self.initTopLeftCorner(domCap, self.zoom)

            # 
            self.zoomAllowed = list()
            self.initLayer(domCap, self.nomlayer)


    def getTopLeftCorner(self):
        return (self.X0, self.Y0)

    def getLayerList(self):
        return self.zoomAllowed
    
    def getFormat(self):
        return self.format
    
    def getTitleLayer(self):
        return self.title
    
    def isZoomValid(self):
        return self.zoom in self.zoomAllowed
   
    def getScaleDenominator(self):
        return self.ScaleDenominator
    

    def initTopLeftCorner(self, domCap, zoom):
        """
            Initialise l'origine du niveau de zoom :
                - TopLeftCorner
                - TileWidth, TileHeight
                - MatrixWidth, MatrixHeight
        """
        
        nodelistTileMS = domCap.getElementsByTagName("TileMatrixSet")
        for nodeTileMatrixSet in nodelistTileMS:
            #if nodeTileMatrixSet.nodeType == nodeTileMatrixSet.TEXT_NODE:
            nodelistIdentifier = nodeTileMatrixSet.getElementsByTagName("ows:Identifier")
            #for nodeIdentifier in nodelistIdentifier:
                #if nodeIdentifier.nodeType == nodeIdentifier.TEXT_NODE:
            if len(nodelistIdentifier) > 0:
                identifier = nodelistIdentifier[0].firstChild.nodeValue
                
                if identifier == 'PM':
                    nodelistTileMatrix = nodeTileMatrixSet.getElementsByTagName("TileMatrix")
                    for nodeTileMatrix in nodelistTileMatrix:
                        
                        zoomElement = nodeTileMatrix.getElementsByTagName("ows:Identifier")
                        zoomTile = zoomElement[0].firstChild.nodeValue
                        if str(zoom) == zoomTile:
                            topLeftCornerElement = nodeTileMatrix.getElementsByTagName("TopLeftCorner")
                            topLeftCorner = topLeftCornerElement[0].firstChild.nodeValue
                            coord = topLeftCorner.split(" ")
                            self.X0 = float(coord[0])
                            self.Y0 = float(coord[1])
    
                            scaleDenominatorElement = nodeTileMatrix.getElementsByTagName("ScaleDenominator")
                            topLeftCorner = scaleDenominatorElement[0].firstChild.nodeValue
                            self.ScaleDenominator = float(topLeftCorner)
                
                            # MatrixWidth
                            # MatrixHeight
                            # TileWidth
                            # TileHeight
        

    def initLayer(self, domCap, nomlayer):
        """
            Initialise les metadonnees du layer :
                - Title
                - Format
                - TileMatrixSetLimits
        """

        layerNodelist = domCap.getElementsByTagName("Layer")
        for layerNode in layerNodelist:
            
            identifierElement = layerNode.getElementsByTagName("ows:Identifier")
            if self.nomlayer == identifierElement[0].firstChild.nodeValue:
            
                titleElement = layerNode.getElementsByTagName("ows:Title")
                self.title = titleElement[0].firstChild.nodeValue
            
                formatElement = layerNode.getElementsByTagName("Format")
                self.format = formatElement[0].firstChild.nodeValue
    
                tileMatrixNodelist = layerNode.getElementsByTagName("TileMatrix")
                for tileMatrixNode in tileMatrixNodelist:
                    self.zoomAllowed.append(int(tileMatrixNode.firstChild.nodeValue))

