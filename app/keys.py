from telebot import types


parts_names = {
    'night': 'Ночь',
    'day': 'День',
    'morning': 'Утро',
    'evening': 'Вечер'
}


def get_parts_keys(cur_part, source, day):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    t_list = []
    c_list = []

    for part in parts_names.keys():
        btn_txt = parts_names[part]
        if part == cur_part:
            btn_txt += '✅'
        t_list.append(btn_txt)
        c_list.append(part)

    btn1 = types.InlineKeyboardButton(text=t_list[0], callback_data='source_'+day+'_'+source+'_'+c_list[0])
    btn2 = types.InlineKeyboardButton(text=t_list[1], callback_data='source_'+day+'_'+source+'_'+c_list[1])
    btn3 = types.InlineKeyboardButton(text=t_list[2], callback_data='source_'+day+'_'+source+'_'+c_list[2])
    btn4 = types.InlineKeyboardButton(text=t_list[3], callback_data='source_'+day+'_'+source+'_'+c_list[3])
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard
