from settings import GEO_TOKEN
import requests


class GeocoderError(Exception):
    pass


def _get_city(feature_member):
    city_name = feature_member['GeoObject']['name']
    if not city_name:
        raise GeocoderError
    return city_name


def _get_geocoder_data(city='', lon='', lat='', is_coords=False):
    url = 'https://geocode-maps.yandex.ru/1.x/?apikey=%s&results=1&geocode=%s, %s&format=json'
    if is_coords:
        url = url % (GEO_TOKEN, lon, lat)
    else:
        url = url % (GEO_TOKEN, city, '')
    headers = {'Referer': 'yandex.ru'}
    r = requests.get(url, headers=headers)
    data = r.json()
    featureMembers = data['response']['GeoObjectCollection']['featureMember']
    if featureMembers == []:
        raise GeocoderError
    return featureMembers[0]


def get_city_by_coordinates(lon, lat):
    try:
        feature_member = _get_geocoder_data(lon=lon, lat=lat, is_coords=True)
        city = _get_city(feature_member)
    except GeocoderError:
        return None
    return city


def get_coorditates_by_city(city):
    try:
        feature_member = _get_geocoder_data(city=city, is_coords=False)
        points = feature_member['GeoObject']['Point']['pos']
        longitude, latitude = points.split()
        city = _get_city(feature_member)
    except GeocoderError:
        return None
    return longitude, latitude, city
