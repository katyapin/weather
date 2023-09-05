import requests
from settings import WEATHER_TOKEN
from data import db


def fill_yandex_weather(weather_stat_obj):
    lon = weather_stat_obj['lon']
    lat = weather_stat_obj['lat']
    date = weather_stat_obj['dt']

    forecasts = _get_weather_data(lat, lon)
    for forecast in forecasts:
        if forecast['date'] == date:
            _fill_forecast(forecast, weather_stat_obj['stat_id'])


def _get_weather_data(lat, lon):
    url = 'https://api.weather.yandex.ru/v2/forecast?lat=%s&lon=%s&lang=ru_RU&limit=3&hours=false&extra=true'
    url = url % (str(lat), str(lon))
    header = {"X-Yandex-API-Key": WEATHER_TOKEN}
    r = requests.get(url, headers=header)
    return r.json()['forecasts']


def _fill_forecast(forecast, stat_id):
    parts = forecast['parts']
    parts.pop('day_short')
    parts.pop('night_short')

    for part_name in parts.keys():
        part_data = parts[part_name]
        db.create_weather_history_detail(stat_id=stat_id,
                                         source='yandex',
                                         part=part_name,
                                         temp_avg=part_data['temp_avg'],
                                         wind_speed=part_data['wind_speed'],
                                         wind_dir=_get_wind_dir(part_data['wind_dir']),
                                         pressure_mm=part_data['pressure_mm'],
                                         humidity=part_data['humidity'],
                                         prec_type=_get_precipitation(part_data['prec_type']))


def _get_wind_dir(wind_dir):
    if wind_dir == 'nw':
        return 'северо-западное'
    if wind_dir == 'n':
        return 'северное'
    if wind_dir == 'ne':
        return 'северо-восточное'
    if wind_dir == 'e':
        return 'восточное'
    if wind_dir == 'se':
        return 'юго-восточное'
    if wind_dir == 's':
        return 'южное.'
    if wind_dir == 'sw':
        return 'юго-западное'
    if wind_dir == 'w':
        return 'западное'
    if wind_dir == 'c':
        return 'штиль'


def _get_precipitation(prec_type):
    if prec_type == 0:
        return 'Без осадков'
    if prec_type == 1:
        return 'Дождь'
    if prec_type == 2:
        return 'Дождь со снегом'
    if prec_type == 3:
        return 'Снег'
