"""Module to create interactive map of closest film creating places"""
import folium
from geopy import point
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from haversine import haversine
from geopy.exc import GeocoderUnavailable
import argparse


parser = argparse.ArgumentParser(description='Build a map with closest films')
parser.add_argument("year", type=int, help='necessary year')
parser.add_argument("coord1", type=float, help='first coordinate')
parser.add_argument("coord2", type=float, help='Second coordinate')
parser.add_argument("path", type=str, help='Path to the file with database')
args = parser.parse_args()


def read_file_info(path, expected_year):
    """Read info from the data base and saves it in a right format

    :param path: path to the database
    :type path: str
    :param expected_year: year needed to be calculated
    :type expected_year: int
    :return: films in correct format
    :rtype: set
    """
    films = set()
    with open(path, 'r', encoding='utf-8') as file:
        for i in range(14):
            file.readline()
        geolocator = Nominatim(user_agent="main.py")
        for line in file:
            point = line.find('(')
            if point == -1:
                break
            else:
                name = line[:point-1]
                year = line[point+1:point+5]
                try:
                    year = int(year)
                except ValueError:
                    continue
                if year == expected_year:
                    line = line[::-1]
                    position = line[line.find(',')+1: line.find('\t')]
                    position = position[::-1]
                    try:
                        location = geolocator.geocode(position)
                        films.add((name, year, (location.latitude,
                                                location.longitude)))
                    except AttributeError:
                        continue
                    except GeocoderUnavailable:
                        continue
    return films


def find_closest(point, films):
    """Creates list of 10 most closest places of shooting films

    :param point: point from which calculate distance
    :type point: tuple
    :param films: necessary films
    :type films: set
    :return: 10 closest points
    :rtype: list
    """
    closest = []
    for film in films:
        closest.append((film[0], film[2], round(haversine(film[2], point))))
        closest = sorted(closest, key=lambda x: x[2])
        if len(closest) > 10:
            closest = closest[:10]
    return closest


def map_generation(point, closest):
    """Generates a map with necessary points

    :param point: position of user
    :type point: tuple
    :param closest: 10 closest points
    :type closest: list
    """
    map = folium.Map(location=point, zoom_start=10)
    for film in closest:
        map.add_child(folium.Marker(location=film[1], popup=film[0],
                                    icon=folium.Icon()))
        map.save('Map_1.html')
    return map


if __name__ == '__main__':
    point = (args.coord1, args.coord2)
    films = read_file_info(args.path, args.year)
    closest = find_closest(point, films)
    map_generation(point, closest)
