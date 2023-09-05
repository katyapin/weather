from data import db
from settings import bot, sched
from services import geocoder, weather, notices
from telebot import types
from datetime import datetime, timedelta
import keys


def main_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Получить прогноз"))
    keyboard.add(types.KeyboardButton(text="Изменить местоположение"))
    keyboard.add(types.KeyboardButton(text="Настроить уведомление"))
    return keyboard


def request_loc_btns():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    return keyboard


def main_menu_message(message, user):
    answer = '📍 %s\n🔔 уведомление: %s\n\n⬇️Выберите действие⬇️'
    if user['notice_time']:
        notices = 'ежедневно в ' + str(user['notice_time']).rjust(2, '0') + ':00'
    else:
        notices = 'отключено'
    answer = answer % (user['city'], notices)
    btn = main_menu()
    bot.send_message(message.chat.id, answer, reply_markup=btn)


def time_keys():
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    for i in range(8):
        num = i * 3
        t1 = str(num).rjust(2, '0') + ':00'
        t2 = str(num+1).rjust(2, '0') + ':00'
        t3 = str(num+2).rjust(2, '0') + ':00'
        btn1 = types.InlineKeyboardButton(text=t1, callback_data='set_notice_'+t1)
        btn2 = types.InlineKeyboardButton(text=t2, callback_data='set_notice_'+t2)
        btn3 = types.InlineKeyboardButton(text=t3, callback_data='set_notice_'+t3)
        keyboard.add(btn1, btn2, btn3)

    keyboard.add(types.InlineKeyboardButton(text='Отменить', callback_data='set_notice_cancel'))
    return keyboard


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = db.get_user(message.chat.id)
    if user:
        main_menu_message(message, user)
    else:
        db.create_user(message.chat.id)
        answer = 'Я магический бот, который предсказывает БУДУЩЕЕ...\nну погоду.\n\nОтправь своё местоположение '\
                 'чтобы получить магический прогноз. Можешь также ввести название города.'
        btn = request_loc_btns()
        bot.register_next_step_handler(message, change_localion)
        bot.send_message(message.chat.id, answer, reply_markup=btn)


@bot.message_handler(func=lambda msg: msg.text == 'Настроить уведомление')
def set_schedule(message):
    answer = 'Бот будет присылать вам прогноз погоды ежедневно, выберите время, когда вы хотите его получать'
    bot.send_message(message.chat.id, answer, reply_markup=time_keys())


@bot.message_handler(func=lambda msg: msg.text == 'Изменить местоположение')
def change_city(message):
    answer = 'Введите название города или отправьте местоположение'
    bot.send_message(message.chat.id, answer, reply_markup=request_loc_btns())
    bot.register_next_step_handler(message, change_localion)


@bot.message_handler(func=lambda msg: msg.text == 'Получить прогноз')
def get_forecast(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Сегодня", callback_data='day_today'))
    keyboard.add(types.InlineKeyboardButton(text="Завтра", callback_data='day_tomorrow'))
    answer = 'Выберите день'
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)


def err_city_message(message):
    answer = 'Мы не смогли найти ваш город 😔\nПопробуйте ещё раз.'
    bot.send_message(message.chat.id, answer, reply_markup=request_loc_btns())


def change_localion(message):
    if message.location:
        lon, lat = message.location.longitude, message.location.latitude
        city = geocoder.get_city_by_coordinates(lon, lat)
        if not city:
            err_city_message(message)
            return
    else:
        city_text = message.text
        result = geocoder.get_coorditates_by_city(city_text)
        if not result:
            err_city_message(message)
            return
        lon, lat, city = result

    db.set_user_coords(message.chat.id, lon, lat, city)
    user = db.get_user(message.chat.id)
    main_menu_message(message, user)


@bot.callback_query_handler(func=lambda call: call.data.startswith('day'))
def choose_day(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    day = call.data.split('_')[1]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(text="Яндекс", callback_data='source_'+day+'_yandex_choice'))
    keyboard.add(types.InlineKeyboardButton(text="Гисметео", callback_data='source_'+day+'_gismeteo_choice'))

    answer = 'Выберите источник'
    bot.send_message(call.message.chat.id, answer, reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data.startswith('source'))
def choose_source(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    call_data = call.data.split('_')
    day = call_data[1]
    source = call_data[2]
    last = call_data[-1]
    if last == 'choice':
        db.update_user_choices(call.message.chat.id, source)
        cur_part = None
    else:
        cur_part = last

    dt = datetime.today()
    if day == 'tomorrow':
        dt = dt + timedelta(days=1)

    user = db.get_user(call.message.chat.id)
    answer, part = weather.get_weather(user['lon'], user['lat'], user['city'], dt, source, cur_part)
    keyboard = keys.get_parts_keys(part, source, day)
    bot.send_message(call.message.chat.id, answer, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_notice_'))
def set_notice(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    time = call.data.split('_')[-1]
    if time == 'cancel':
        db.set_user_notice(call.message.chat.id, None)
        answer = 'Вы отключили ежедневное уведомление'
    else:
        time_int = int(time.split(':')[0])
        db.set_user_notice(call.message.chat.id, time_int)
        answer = 'Вы успешно настроили расписание на %s' % (time)
    bot.send_message(call.message.chat.id, answer)


if __name__ == '__main__':
    notices.send_notices()
    # sched.add_job(notices.send_notices, 'cron', hour='0-23')
    # sched.start()
    bot.infinity_polling()
