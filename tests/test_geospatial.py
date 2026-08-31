import numpy as np

from ayus.geospatial import GeoBounds, pixel_to_lonlat, routes_to_geojson
from ayus.image_processing import GridSpec


def test_pixel_to_lonlat_maps_image_corners():
    bounds = GeoBounds(36.0, 37.0, 37.0, 38.0)
    assert pixel_to_lonlat(0, 0, 101, 201, bounds) == (36.0, 38.0)
    assert pixel_to_lonlat(100, 200, 101, 201, bounds) == (37.0, 37.0)


def test_geojson_contains_route_lines():
    grid = GridSpec(20, 30, 2, 3, np.array([0, 10, 20]), np.array([0, 10, 20, 30]))
    document = routes_to_geojson([[(0, 0), (1, 2)]], grid, GeoBounds(36.0, 37.0, 37.0, 38.0))
    assert document["type"] == "FeatureCollection"
    assert document["features"][0]["geometry"]["type"] == "LineString"
