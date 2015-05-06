import os
import urllib2
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
import tempfile
import shutil
import sys
from django.shortcuts import render
from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
from tethys_apps.base.persistent_store import get_persistent_store_engine as gpse
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine


def get_persistent_store_engine(persistent_store_name):
    """
    Returns an SQLAlchemy engine object for the persistent store name provided.
    """
    # Derive app name
    app_name = os.path.split(os.path.dirname(__file__))[1]

    # Get engine
    return gpse(app_name, persistent_store_name)

def getGeoSvrUrlBase(request, base_url):

    print "geoserver domain: " + base_url
    return base_url

    current_site = get_current_site(request);
    domain_with_port = current_site.domain
    print "original domain: " + domain_with_port
    idx_cut = domain_with_port.find(':')
    if idx_cut != -1:
        domain_name = domain_with_port[:idx_cut]
    else:
        domain_name = domain_with_port
    print "domain: " + domain_name
    geosvr_url_base = 'http://' + domain_name + ":8181"
    print "geoserver domain: " + geosvr_url_base

    return geosvr_url_base

def addZippedShp2Geoserver(geosvr_url_base, uname, upwd, ws_name, store_name, zippedTif_full_path, res_url):

        try:
            # Specifying the full REST url
            geosvr_url_full = geosvr_url_base+"/geoserver/rest/"
            print "GeoServer REST Full URL: "+ geosvr_url_full
            print "Connect to Geoserver"

            # First get the engine
            spatial_dataset_engine = GeoServerSpatialDatasetEngine(endpoint=geosvr_url_full, username=uname, password=upwd)
            print "Connected"

            response = None
            # Creating the workspace
            result = spatial_dataset_engine.create_workspace(workspace_id=ws_name, uri=res_url)
            if result['success']:
                print "Create workspace " + ws_name + " successfully"
            else:
                print "Create workspace " + ws_name + " failed"
            print result

            store_id = ws_name+":"+store_name

            # Path to the shapefile base
            coverage_file = zippedTif_full_path
            print  zippedTif_full_path

            # Creating a workspace for registering a shapefile in the geoserver
            result = spatial_dataset_engine.create_shapefile_resource(store_id=store_id, shapefile_base=coverage_file)

            # Check if it was successful
            if result['success']:
                print "Create store " + store_name + " successfully"
            else:
                print "Create store " + store_name + " failed"
            print result

            # Debugging
            spatial_dataset_engine.list_layers(debug=True)

            return True
        except:
            print ("addZippedShp2Geoserver() error")
            raise Exception("addZippedShp2Geoserver() error")


def getMapParas(geosvr_url_base, wsName, layerName):

    try:

        #Retriving the map data from the geoserver using WMS
        geosvr_ulr_wms = geosvr_url_base+"/geoserver/wms/"
        layer = wsName + ":" + layerName
        print geosvr_ulr_wms
        print layer

        #Specifying the map details
        map_view_options = {'height': '400px',
                    'width': '100%',
                    'controls': ['ZoomSlider',
                                 'Rotate',
                                 'FullScreen',
                                 'ScaleLine',
                                 {'ZoomToExtent': {'projection': 'EPSG:4326',
                                                   'extent': [-135, 22, -55, 54]
                                                  }},
                                 {'MousePosition': {'projection': 'EPSG:4326'}},
                    ],
                    'layers': [{'WMS': {'url': geosvr_ulr_wms,
                                        'params': {'LAYERS': layer, 'TILED': False},
                                        'serverType': 'geoserver'}
                                },
                    ],
                    'view': {'projection': 'EPSG:4326',
                             'center': [-100, 40], 'zoom': 3.5,
                             'maxZoom': 18, 'minZoom': 1},
                    'base_map': 'OpenStreetMap'
        }


        return map_view_options
    except:
        print ("getMapParas() error")
        raise Exception("getMapParas() error")
