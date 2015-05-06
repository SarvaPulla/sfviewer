from tethys_apps.base import TethysAppBase, url_map_maker
from tethys_apps.base import PersistentStore
from tethys_apps.base import SpatialDatasetService


class ShapefileViewer(TethysAppBase):
    """
    Tethys app class for Shapefile Viewer.
    """

    name = 'Shapefile Viewer'
    index = 'shapefileviewer:home'
    icon = 'shapefileviewer/images/icon.gif'
    package = 'shapefileviewer'
    root_url = 'shapefileviewer'
    color = '#0066FF'

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='shapefileviewer',
                           controller='shapefileviewer.controllers.home'),
                    UrlMap(name='map',
                           url='shapefileviewer/map',
                           controller='shapefileviewer.controllers.map')
        )

        return url_maps


    def spatial_dataset_services(self):
        """
        Adding the sole spatial dataset service
        """

        spatial_dataset_services = (SpatialDatasetService(name='default_geoserver',
                                                          type='geoserver',
                                                          endpoint='http://127.0.0.1:8181/geoserver/rest',
                                                          username='admin',
                                                          password='geoserver'
        ),
        )

        return spatial_dataset_services