from data import db
from settings import bot
from services import weather
from datetime import datetime
import keys
import random


def send_notices():
    datetime_now = datetime.now()
    time_hour = datetime_now.time().hour
    users = db.get_users_notices(time_hour)
    if not users:
        return

    for user in users:
        print(user)
        if user['yandex'] == user['gismeteo']:
            source = random.choice(['yandex', 'gismeteo'])
        elif user['yandex'] > user['gismeteo']:
            source = 'yandex' 
        else:
            source = 'gismeteo'
        answer, part = weather.get_weather(user['lon'], user['lat'], user['city'], datetime_now, source)
        keyboard = keys.get_parts_keys(part, source, 'today')
        bot.send_message(int(user['chat_id']), answer, reply_markup=keyboard)
