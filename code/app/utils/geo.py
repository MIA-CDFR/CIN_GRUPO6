import osmnx as ox

from shapely.geometry import Point
from geopy.distance import geodesic


def get_geocode_by_address(address, city="Porto, Portugal") -> Point:
    try:
        point = ox.geocode(address + ", " + city)
        return Point(point[1], point[0])
    except:
        raise ValueError(f"Não foi possivel encontrar: {address}")


def get_km_distance(origin: Point, destination: Point):
    return geodesic((origin.y, origin.x), (destination.y, destination.x)).km


def get_m_distance(origin: Point, destination: Point):
    return geodesic((origin.y, origin.x), (destination.y, destination.x)).m
