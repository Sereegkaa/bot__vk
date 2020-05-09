# -*- coding: utf-8 -*-
import random

import requests
import vk_api
from vk_api import longpoll
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3

geocode_key = "40d1649f-0493-4b70-98ba-98533de7710b"
weather_key = "735a880881174d6285c1e29b46c54fa9"
search_text = '%D0%BC%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%20%D0%BF%D1%80%D0%BE%D0%B4%D1%83%' \
              'D0%BA%D1%82%D0%BE%D0%B2'

products = ''
foods = []
numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
attachment = []
flag = False

vk_session = vk_api.VkApi(
    token='7743b35a5831ccea3966be434897942479514635d681b8b72285b76547191672c4fb3670a10802db84b12')
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 194438446)

con = sqlite3.connect("food.db")
cur = con.cursor()


# создает inline либо стандартную клавиатуру
def create_keyborad(ev):
    if 'inline_keyboard' in ev.client_info.keys():
        keyboard = VkKeyboard(inline=True)
    else:
        keyboard = VkKeyboard(one_time=True)
    return keyboard


# получает список продуктов для всех возможных рецептов
def get_all_products():
    global cur
    result = [x[0].split(',') for x in cur.execute("SELECT products FROM food_list").fetchall()]
    a = result.copy()
    result = []
    for x in a:
        for y in x:
            result.append(y)
    return '\n'.join(set(result))


# добавляет продукт к уже введённым
def add_product(ev):
    global products
    x = ev
    for ev in longpoll.listen():
        if ev.type == VkBotEventType.MESSAGE_NEW and ev.obj.message['from_id'] == x.obj.message[
            'from_id']:
            if ev.message['text'].lower() in ['начать', 'привет', 'здравствуй', 'здравствуйте',
                                              'приветик', 'назад', 'заново', 'начать сначала',
                                              'салам', 'хай']:
                start(vk, ev)

            tmp = products.split(',')
            tmp.append(ev.message['text'])
            products = ','.join(sorted(tmp))
            return


# удаляет продукт
def del_product(ev):
    global products
    x = ev
    for ev in longpoll.listen():
        if ev.type == VkBotEventType.MESSAGE_NEW and ev.obj.message['from_id'] == x.obj.message[
            'from_id']:
            if ev.message['text'].lower() in ['начать', 'привет', 'здравствуй', 'здравствуйте',
                                              'приветик', 'назад', 'заново', 'начать сначала',
                                              'салам', 'хай']:
                start(vk, ev)

            tmp = products.split(',')
            try:
                tmp.remove(ev.message['text'])
            except Exception:
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 message=get_all_products() +
                                         "\n\nПеречислите через запятую продукты&#129365;"
                                         "&#129371;&#129472;, которые у Вас есть",
                                 random_id=random.randint(0, 2 ** 64))
            products = ','.join(sorted(tmp))
            return


# Вы правильно ввели продукты?
def check_products(vk, ev):
    keyboard = create_keyborad(ev)
    keyboard.add_button("Да", color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button("Добавить продукт", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Убрать продукт", color=VkKeyboardColor.NEGATIVE)

    vk.messages.send(user_id=ev.obj.message['from_id'],
                     message=f"Проверьте продукты которые Вы ввели, всё правильно?)\n\n{products}",
                     random_id=random.randint(0, 2 ** 64),
                     keyboard=keyboard.get_keyboard())
    x = ev
    for ev in longpoll.listen():
        if ev.type == VkBotEventType.MESSAGE_NEW and ev.obj.message['from_id'] == x.obj.message[
            'from_id']:
            if ev.message['text'].lower() in ['начать', 'привет', 'здравствуй', 'здравствуйте',
                                              'приветик', 'назад', 'заново', 'начать сначала',
                                              'салам', 'хай']:
                start(vk, ev)
                return 'not'

            if ev.message['text'].lower() == 'добавить продукт':
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 message="Введите название продукта, который хотите "
                                         "добавить&#10004;",
                                 random_id=random.randint(0, 2 ** 64))
                add_product(ev)
                return True

            if ev.message['text'].lower() == 'убрать продукт':
                keyboard = create_keyborad(ev)
                keyboard.add_button("Да", color=VkKeyboardColor.DEFAULT)
                keyboard.add_line()
                keyboard.add_button("Добавить продукт", color=VkKeyboardColor.POSITIVE)

                if len(products.split(',')) > 1:
                    vk.messages.send(user_id=ev.obj.message['from_id'],
                                     message="Введите название продукта, который хотите "
                                             "убрать&#10006;",
                                     random_id=random.randint(0, 2 ** 64))
                    del_product(ev)
                    return True
                else:
                    vk.messages.send(user_id=ev.obj.message['from_id'],
                                     message=f"Нельзя убрать единственный продукт!",
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=keyboard.get_keyboard())
                    vk.messages.send(user_id=ev.obj.message['from_id'],
                                     message=f"Проверьте продукты которые Вы ввели, всё правильно?)"
                                             f"\n\n{products}",
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=keyboard.get_keyboard())

            else:
                return False


# стартовая функция
def start(vk, ev):
    global longpoll, products

    keyboard = create_keyborad(ev)
    keyboard.add_button('Возможные продукты', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Мои рецепты', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Все рецепты', color=VkKeyboardColor.DEFAULT)

    vk.messages.send(user_id=ev.obj.message['from_id'],
                     message="Перечислите через запятую продукты&#129365;"
                             "&#129371;&#129472;, которые есть у Вас и я подберу"
                             "&#128270; рецепт блюда&#128523;, которое можно из них "
                             "приготовить&#127828;&#127859;\n\nЕсли что-то пойдет не так&#128546;, "
                             "Вы в любой момент можете написать 'Начать сначала'&#128260;",
                     random_id=random.randint(0, 2 ** 64),
                     keyboard=keyboard.get_keyboard())

    ev_now = ''
    x = ev
    for ev in longpoll.listen():
        if ev.type == VkBotEventType.MESSAGE_NEW and ev.obj.message['from_id'] == x.obj.message[
            'from_id']:

            if ev.message['text'].lower() in ['начать', 'привет', 'здравствуй', 'здравствуйте',
                                              'приветик', 'назад', 'заново', 'начать сначала',
                                              'салам', 'хай']:
                start(vk, ev)

            elif ev.message['text'] == 'Возможные продукты':
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 message=get_all_products() +
                                         "\n\nПеречислите через запятую продукты&#129365;"
                                         "&#129371;&#129472;, которые у Вас есть",
                                 random_id=random.randint(0, 2 ** 64))

            elif ev.message['text'].lower() == 'мои рецепты':
                print("---my foods---")
                return 'my_foods', ev

            elif ev.message['text'].lower() == 'все рецепты':
                ev_now = ev
                break

            else:
                ev_now = ev
                break
    print(ev.obj)
    products = ','.join(sorted(ev.message['text'].replace(' ', '').lower().split(',')))
    get_foods(vk, ev_now)


# получает рецепт по введенным продуктам
def get_foods(vk, ev):
    global products, foods, attachment

    a = check_products(vk, ev)
    print(a)
    if a != 'not':
        if a:
            check_products(vk, ev)

    foods_id = []
    tmp = sorted(products.split(','))
    result = cur.execute("""SELECT * FROM food_list WHERE is_open=1""").fetchall()

    for x in result:
        if len(set(sorted(x[2].split(','))).intersection(set(tmp))) >= len(x[2].split(',')):
            foods_id.append(x[0])
    print(tuple(foods_id))
    foods_id = tuple(foods_id)
    if len(foods_id) == 1:
        result = cur.execute(f"""SELECT * FROM food_list WHERE id={foods_id[0]}""").fetchall()
    elif foods_id:
        result = cur.execute(f"""SELECT * FROM food_list WHERE id IN{foods_id}""").fetchall()
    else:
        result = None

    if result:
        foods = [x[1] for x in result]
        attachment = [x[3] for x in result]
        foods_zip = list(zip(numbers, [x[1] for x in result]))
        message = "Выберите, что хотите приготовить&#128298;:\n"
        for x in foods_zip:
            message = message + x[0] + ' ' + x[1] + '\n'
        print(f"""---{list(foods_zip)}---""")
        vk.messages.send(user_id=ev.obj.message['from_id'],
                         message=message,
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard_number(ev, len(foods_zip)).get_keyboard())
        flag = False
    else:
        keyboard = create_keyborad(ev)
        keyboard.add_location_button()
        vk.messages.send(user_id=ev.obj.message['from_id'],
                         message="У Вас недостаточно продуктов&#128532;\nОтправьте своё "
                                 "местоположение и покажу Вам ближайшие магазины :)",
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard.get_keyboard())


# создает клаиватуру с цифрами
def keyboard_number(ev, n):
    keyboard = create_keyborad(ev)
    for i in range(n):
        keyboard.add_button(numbers[i])
        if i in [2, 5, 8] and i != (n - 1):
            keyboard.add_line()
    return keyboard


# работа с геопозицией
def geo(longpoll, vk, ev):
    global geocode_key, weather_key
    geopos = str(ev.message['geo']['coordinates']['longitude']) + ',' + str(
        ev.message['geo']['coordinates']['latitude'])
    lon, lat = geopos.split(',')

    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={geocode_key}&geocode={geopos}&format=json"
    response = requests.get(geocoder_request)
    toponym = ''
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
    else:
        vk.messages.send(user_id=ev.obj.message['from_id'],
                         message="Произошла какая-то ошибка\nПопробуйте отправить местоположение ещё раз)",
                         random_id=random.randint(0, 2 ** 64))

    keyboard = create_keyborad(ev)
    keyboard.add_location_button()
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={geopos}&spn=0.002,0.002&l=map&pt={geopos},ya_ru"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        vk.messages.send(user_id=ev.obj.message['from_id'],
                         keyboard=keyboard.get_keyboard(),
                         message="Произошла какая-то ошибка\nПопробуйте отправить местоположение ещё раз)",
                         random_id=random.randint(0, 2 ** 64))
    map_file = "map.png"
    keyboard = create_keyborad(ev)
    keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
    with open(map_file, "wb") as file:
        file.write(response.content)
    upload = vk_api.VkUpload(vk)
    photo = upload.photo_messages('map.png')
    owner_id = photo[0]['owner_id']
    photo_id = photo[0]['id']
    access_key = photo[0]['access_key']
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(user_id=ev.obj.message['from_id'],
                     message=f"{toponym}\nЯ правильно определил Ваш адрес&#127969;?",
                     attachment=attachment,
                     keyboard=keyboard.get_keyboard(),
                     random_id=random.randint(0, 2 ** 64))

    keyboard = create_keyborad(ev)
    keyboard.add_location_button()
    x = ev
    for ev in longpoll.listen():
        if ev.type == VkBotEventType.MESSAGE_NEW and ev.obj.message['from_id'] == x.obj.message[
            'from_id']:
            if ev.message['text'].lower() in ['начать', 'привет', 'здравствуй', 'здравствуйте',
                                              'приветик', 'назад', 'заново', 'начать сначала',
                                              'салам', 'хай']:
                start(vk, ev)

            if ev.message['text'] == 'Нет':
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 keyboard=keyboard.get_keyboard(),
                                 message="Попробуйте отправить местоположение ещё раз)",
                                 random_id=random.randint(0, 2 ** 64))
            elif 'geo' in ev.message.keys():
                geo(longpoll, vk, ev)
            else:
                break

    weather_request = f"https://api.weatherbit.io/v2.0/current?key={weather_key}&lang=ru&lat={lat}&lon={lon}"
    weather = dict(*requests.get(weather_request).json()["data"])
    vk.messages.send(user_id=ev.obj.message['from_id'],
                     message=f"""На улице неплохая погодка&#9925; чтобы прогуляться до магазина"""
                             f"""&#128694;:)\n\nТемпература: {round(float(weather['temp']))}°C\nОщущается как: """
                             f"""{round(float(weather['app_temp']))}°C\nВетер: {weather['wind_cdir_full']}, """
                             f"""{round(float(weather['wind_spd']))}м/c\nВлажность: """
                             f"""{round(float(weather['rh']))}%\nОблачность: """
                             f"""{round(float(weather['clouds']))}%\n\nP.S. Не забудьте взять """
                             f"""пропуск для похода в магазина по номеру:\n8 (800) 450-48-58""",
                     random_id=random.randint(0, 2 ** 64))

    keyboard = create_keyborad(ev)
    keyboard.add_openlink_button(label='Магазины рядом',
                                 link=f"https://yandex.ru/maps/?text={search_text}&ll={str(geo)}&z=14")
    vk.messages.send(user_id=ev.obj.message['from_id'],
                     message="Вот ближайшие к Вам магазины :)",
                     random_id=random.randint(0, 2 ** 64),
                     keyboard=keyboard.get_keyboard())


# вкладка мои рецепты
def my_foods(vk, ev):
    global foods, attachment
    global flag
    result = cur.execute(
        f"""SELECT * FROM food_list WHERE user_id={ev.obj.message['from_id']}""").fetchall()
    print(result)

    keyboard = create_keyborad(ev)
    keyboard.add_button('Назад')

    if not result:
        vk.messages.send(user_id=ev.obj.message['from_id'],
                         keyboard=keyboard.get_keyboard(),
                         message="Здесь будут отображаться Ваши собственные&#129396; рецепты и "
                                 "рецепты, которые Вы сохранили&#129488;.\nНо пока здесь "
                                 "пусто&#128532;",
                         random_id=random.randint(0, 2 ** 64))

        for ev in longpoll.listen():
            if ev.type == VkBotEventType.MESSAGE_NEW:
                if ev.message['text'].lower() == 'назад':
                    return False, ev
    else:
        foods = [x[1] for x in result]
        attachment = [x[3] for x in result]
        foods_zip = list(zip(numbers, [x[1] for x in result]))
        message = "Ваши рецепты&#128298;:\n"
        for x in foods_zip:
            message = message + x[0] + ' ' + x[1] + '\n'
        print(f"""---{list(foods_zip)}---""")

        keyboard = keyboard_number(ev, len(foods_zip))
        keyboard.add_line()
        keyboard.add_button('Очистить', color=VkKeyboardColor.NEGATIVE)

        vk.messages.send(user_id=ev.obj.message['from_id'],
                         message=message,
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard.get_keyboard())
        flag = True
        return True, ev


# сохранение рецепта в "мои рецепты"
def food_save(food, vk, ev):
    global con, cur

    keyboard = create_keyborad(ev)
    keyboard.add_button('Найти новый рецепт', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Мои рецепты', color=VkKeyboardColor.PRIMARY)

    result = cur.execute("""SELECT * FROM food_list WHERE name=?""", (food[0],)).fetchall()
    tmp = (result[0][1], result[0][2], result[0][3], False, food[1])
    print('\n', tmp)
    result = cur.execute(
        f"""INSERT INTO food_list (name, products, link_photo, is_open, user_id) VALUES (?,?,?,?,?)""",
        tmp)
    con.commit()
    vk.messages.send(user_id=food[1],
                     keyboard=keyboard.get_keyboard(),
                     message="""Рецепт успешно сохранён в "Мои рецепты".""",
                     random_id=random.randint(0, 2 ** 64))
    for ev in longpoll.listen():
        if ev.type == VkBotEventType.MESSAGE_NEW:
            if ev.message['text'].lower() in ['найти новый рецепт', 'начать сначала']:
                start(vk, ev)

            elif ev.message['text'].lower() == 'мои рецепты':
                a = my_foods(vk, ev)
                if not a[0]:
                    start(vk, a[1])

            else:
                keyboard = create_keyborad(ev)
                keyboard.add_button('Начать сначала')
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 message="Я Вас не понимаю&#129320;\nВы можете начать сначала&#128521;",
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard.get_keyboard())


# главная фукнция
def main():
    global vk_session, vk, longpoll, weather_key, search_text, products, foods, attachment, con, cur
    keyboard = VkKeyboard
    msg = ''

    for ev in longpoll.listen():
        # print(f"""foods:\n{foods}\n\nattachment:\n{attachment}""")
        if ev.type == VkBotEventType.MESSAGE_NEW:
            print(ev.obj)
            vk = vk_session.get_api()
            if ev.message['text'].lower() in ['начать', 'привет', 'здравствуй', 'здравствуйте',
                                              'приветик', 'заново', 'начать сначала',
                                              'салам', 'хай', 'сначала']:
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 message="Здравствуйте",
                                 random_id=random.randint(0, 2 ** 64))

                tmp = start(vk, ev)
                if tmp:
                    if tmp[0] == 'my_foods':
                        print('my foods')
                        a = my_foods(vk, tmp[1])
                        if not a[0]:
                            start(vk, a[1])

            elif 'geo' in ev.message.keys():
                geo(longpoll, vk, ev)

            elif ev.message['text'].lower() == 'найти новый рецепт':
                start(vk, ev)

            elif ev.message['text'].lower() == 'очистить':
                keyboard = create_keyborad(ev)
                keyboard.add_button('Сначала')

                cur.execute(f"""DELETE FROM food_list WHERE user_id='{ev.message['from_id']}'""")
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 keyboard=keyboard.get_keyboard(),
                                 message="Ваши рецепты очищены",
                                 random_id=random.randint(0, 2 ** 64))
                con.commit()

            elif ev.message['text'].lower() == 'назад':
                a = my_foods(vk, ev)
                if not a[0]:
                    start(vk, a[1])

            elif ev.message['text'] in numbers:
                # print(foods, attachment, sep="\n")
                keyboard1 = create_keyborad(ev)
                keyboard1.add_button('Найти новый рецепт', color=VkKeyboardColor.PRIMARY)
                if not flag:
                    keyboard1.add_line()
                    keyboard1.add_button('Сохранить рецепт', color=VkKeyboardColor.POSITIVE)
                else:
                    keyboard1.add_line()
                    keyboard1.add_button('Назад')

                msg = (foods[numbers.index(ev.message['text'])], ev.message['from_id'])

                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 keyboard=keyboard1.get_keyboard(),
                                 message=msg[0],
                                 random_id=random.randint(0, 2 ** 64),
                                 attachment=attachment[numbers.index(ev.message['text'])])

            elif ev.message['text'].lower() == 'сохранить рецепт':
                food_save(msg, vk, ev)

            else:
                keyboard = create_keyborad(ev)
                keyboard.add_button('Начать сначала')
                vk.messages.send(user_id=ev.obj.message['from_id'],
                                 message="Я Вас не понимаю&#129320;\nВы можете начать сначала&#128521;",
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard.get_keyboard())


if __name__ == '__main__':
    main()
