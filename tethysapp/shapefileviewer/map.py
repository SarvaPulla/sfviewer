from django.shortcuts import render
from django.http import JsonResponse

from .model import SessionMaker, ShapeFile
import json
import datetime

def map(request):
    """
    Controller for map page.
    """
    # Create a session
    session = SessionMaker()
    
    #Query DB for gage object
    id = 1
    site = session.query(ShapeFile).filter(ShapeFile.id==id).one()
    
    #Transform into GeoJSON format
    geometries = []
    
    site_geometry = dict(type="Point",
        coordinates=[site.latitude, site.longitude],
                        properties={"value": site.value})
    geometries.append(site_geometry)

    geojson_sites = {"type": "GeometryCollection",
                     "geometries": geometries}

    
    return render(request, 'shapefileviewer/map.html', context)