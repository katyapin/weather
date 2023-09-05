from data import db
from services.modules import yandex, gismeteo
from datetime import datetime, time


def get_weather(lon, lat, city, date, source, part=None):
    history_obj = db.get_or_create_weather_history(city, lon, lat, date)
    db_res = db.get_weather_detail(history_obj['stat_id'], source)

    if db_res:
        return _fetch_result_text(db_res, history_obj, source, part)

    yandex.fill_yandex_weather(history_obj)
    gismeteo.fill_gismeteo_weather(history_obj)

    db_res = db.get_weather_detail(history_obj['stat_id'], source)
    return _fetch_result_text(db_res, history_obj, source, part)


def _fetch_result_text(wheather_details, history_obj, source, cur_part):
    if cur_part is None:
        cur_part = _current_part()
    result = '📍 %s \n📅 %s\nℹ️ %s\n%s'

    for instance in wheather_details:
        if instance['part'] == cur_part:
            current_stroke = _set_sub_stroke(instance)

    date = datetime.strptime(history_obj['dt'], '%Y-%m-%d').strftime('%d.%m.%Y')
    source_stroke = _get_source_rus(source)
    result = result % (history_obj['city'], date, source_stroke, current_stroke)
    return result, cur_part


def _current_part():
    time_now = datetime.now().time()
    if time(0, 0, 0) < time_now <= time(6, 0, 0):
        return 'night'
    if time(6, 0, 0) < time_now <= time(12, 0, 0):
        return 'morning'
    if time(12, 0, 0) < time_now <= time(18, 0, 0):
        return 'day'
    if time(18, 0, 0) < time_now <= time(0, 0, 0):
        return 'evening'


def _get_source_rus(source):
    if source == 'yandex':
        return 'Яндекс'
    if source == 'gismeteo':
        return 'Гисметео'


def _set_sub_stroke(obj):
    sub_stroke = '\n➖ Температура: %s°C.\n➖ Осадки: %s.\n➖ Направление ветра: %s\n\
➖ Скорость ветра: %s м/с\n➖ Давление: %s мм\n➖ Влажность: %s \n'
    result = sub_stroke % (obj['temp_avg'], obj['prec_type'], obj['wind_dir'].title(),
                           obj['wind_speed'], obj['pressure_mm'], str(obj['humidity']) + '%')
    return result
