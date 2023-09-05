import pygismeteo
from data import db
from datetime import datetime


gm = pygismeteo.Gismeteo()


def fill_gismeteo_weather(weather_stat_obj):
    lon = weather_stat_obj['lon']
    lat = weather_stat_obj['lat']
    date = weather_stat_obj['dt']

    date_now_dt = datetime.today().date()
    date_hist_dt = datetime.strptime(date, '%Y-%m-%d').date()
    days_delta = (date_hist_dt - date_now_dt).days
    slice_1, slice_2 = 4 * days_delta, 4 * days_delta + 4

    weather_data = _get_weather_data(lon, lat, slice_1, slice_2)
    for data in weather_data:
        db.create_weather_history_detail(stat_id=weather_stat_obj['stat_id'],
                                         source='gismeteo',
                                         part=_get_part(data.date.utc),
                                         temp_avg=data.temperature.air.c,
                                         wind_speed=data.wind.speed.m_s,
                                         wind_dir=_get_wind_dir(data.wind.direction.scale_8),
                                         pressure_mm=data.pressure.mm_hg_atm,
                                         humidity=data.humidity.percent,
                                         prec_type=_get_prec_type(data.precipitation.type))


def _get_weather_data(lon, lat, slice_1, slice_2):
    results = gm.step6.by_coordinates(latitude=lat, longitude=lon, days=3)
    return results[slice_1: slice_2]


def _get_part(date_utc):
    time = date_utc.split(' ')[1]
    if time.startswith('00'):
        return 'night'
    if time.startswith('06'):
        return 'morning'
    if time.startswith('12'):
        return 'day'
    if time.startswith('18'):
        return 'evening'


def _get_wind_dir(scale):
    if scale == 0:
        return 'Штиль'
    if scale == 1:
        return 'Северный'
    if scale == 2:
        return 'Северо-восточный'
    if scale == 3:
        return 'Восточный'
    if scale == 4:
        return 'Юго-восточный'
    if scale == 5:
        return 'Южный'
    if scale == 6:
        return 'Юго-западный'
    if scale == 7:
        return 'Западный'
    if scale == 8:
        return 'Северо-западный'


def _get_prec_type(prec):
    if prec == 0:
        return 'Нет осадков'
    if prec == 1:
        return 'Дождь'
    if prec == 2:
        return 'Снег'
    if prec == 3:
        return 'Смешанные осадки'
