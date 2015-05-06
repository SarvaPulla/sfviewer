import urllib2
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
import tempfile
import shutil
import os
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from utilities import *
from django.template.defaulttags import csrf_token

url_base='http://{0}.hydroshare.org/django_irods/download/?path={1}/{2}'

# Default Geoserver Url
geosvr_url_base='http://127.0.0.1:8181'

def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'shapefileviewer/home.html', context)


def map(request):
    """
    Controller for map page.
    """
    # Getting all the necessary variables for initiating the process of adding a file to the Geoserver

    filename= request.GET['filename']
    res_id= request.GET['res_id']
    branch= request.GET['branch']

    # make a temp directory
    temp_dir = tempfile.mkdtemp()
    print "temp folder created at " + temp_dir
    try:
        # The url format for identifying the HydroShare resource file
        url_wml = url_base.format(branch,res_id,filename)
        print "HS_REST_API: " + url_wml

        # Opening the url

        response = urllib2.urlopen(url_wml)
        print "downloading " + url_wml
        shp_obj = response.read()
        print "download complete"

        # Downloading the file from HydroShare and then adding it to the temp dir
        zipped_shp_full_path = temp_dir + "/"+ filename
        # Saving the zip file to the temp dir
        f = file(zipped_shp_full_path, "w")
        # Writes the mem space 'in_memory_zip' to a file.
        f.write(shp_obj)
        f.close()

        zip_crc=None

        # Unzipping the file as adding a shpfile to Geosrvr requires you to upload a shpfile only
        # This is a problem with the tethys functionality. Once that is fixed, this step will not be necessary
        with zipfile.ZipFile(zipped_shp_full_path, "r") as z:
            z.extractall(temp_dir)
            zip_info = z.getinfo(filename[:-3]+'shp')
            zip_crc1 = str(zip_info.CRC)
            print "CRC: " + zip_crc1
            zip_crc=zip_crc1

        print geosvr_url_base

        # Specifying the folder with the shapefiles. It is formatted this way for tethys' sake. filname[:-4] removes
        # everything .zip
        zip_file_full_path= temp_dir + '/'+filename[:-4]

        rslt = False

        #A dding the shpfile to the Geoserver
        rslt = addZippedShp2Geoserver(geosvr_url_base, 'admin', 'geoserver', res_id, zip_crc, zip_file_full_path, url_wml)

        # Once its successfully added using the getMapParas the shp file retrieved from the Geoserver
        if(rslt):
            map_view_options = getMapParas(geosvr_url_base, res_id, zip_crc)
            context = {"map_view_options": map_view_options, "filename": filename}
        else:
            context = {}

        return render(request, 'shapefileviewer/map.html', context)

    except:
        raise Http404("Cannot locate the requested shapefile. Please check your URL and try again.")

    finally:
        # Deleting the temp dir once its task is done
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            temp_dir=None