import telebot
import database.config as config
import database.pydantic_models as pydantic_models
import client
import json
from math import ceil
bot = telebot.TeleBot(config.bot_token)

#приветствие в зависимости от времени
PagCount = 4

def make_hello_greet(date):
    import time
    opts = {"hey": ('привет', 'здравствуйте', 'доброе утро', 'добрый день', 'добрый вечер', 'доброй ночи')}
    now_hour = int(time.strftime("%H", time.localtime(date)))
    if now_hour > 4 and now_hour <= 12 :
        greet = opts["hey"][2]
    if now_hour > 12 and now_hour <= 16 :
        greet = opts["hey"][3]
    if now_hour > 16 and now_hour <= 24 :
        greet = opts["hey"][4]
    if now_hour >= 0 and now_hour <= 4 :
        greet = opts["hey"][5]
    return greet + ','





@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        client.create_user({"tg_ID":message.from_user.id, "nick":message.from_user.username})
    except Exception as Ex:
        #bot.send_message(message.chat.id, f'Возникла ошибка: {Ex.args}')
        pass
    # создаем объект для работы с кнопками (row_width - определяет количество кнопок по ширине)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # создаем каждую кнопку таким образом
    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')

    markup.add(btn1, btn2, btn3)

    greet = make_hello_greet(message.date)  # приветствие в зависимости от времени суток телеграм-пользователя
    text = f'{greet.capitalize()} {message.from_user.full_name}, я твой бот-криптокошелек, \n ' 'у меня ты можешь хранить и отправлять биткоины'

    # теперь добавляем объект с кнопками к отправляемому пользователю сообщению в аргумент "reply_markup"
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Кошелек')
def wallet(message):
    wallet = client.get_user_wallet_by_tg_id(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')  # мы создали ещё одну кнопку, которую надо обработать
    markup.add(btn1)
    text = f'Ваш баланс: {wallet["balance"]/100000000} BTC\n' \
           f'Ваш адрес: {wallet["address"]}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='История')
def history(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    transactions = client.get_user_transactions(client.get_user_by_tg_id(message.from_user.id)['id'])  # сюда мы загрузим транзакции
    text = f'Ваши транзакции: \n{transactions}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Меню')
def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)

    text = f'Главное меню'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Я в консоли')
def print_me(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    print(message.from_user.to_dict())
    text = f'Ты: {message.from_user.to_dict()}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Админка")
def admin_panel(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Общий баланс')
    btn2 = telebot.types.KeyboardButton('Все юзеры')
    btn3 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1, btn2, btn3)
    text = f'Админ-панель'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# делаем проверку на админ ли боту пишет проверяем текст сообщения
# @bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Все юзеры")
# def all_users(message):
#     text = f'Юзеры:'
#     users = client.get_users()
#     inline_markup = telebot.types.InlineKeyboardMarkup()  # создаем объект с инлайн-разметкой
#     for user in users:  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
#         inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["tg_ID"]}',
#                                                              callback_data=f"user_{user['tg_ID']}"))
#         # в коллбеке у нас будет текст, который содержит айди юзеров
#     bot.send_message(message.chat.id, text,
#                      reply_markup=inline_markup)  # прикрепляем нашу разметку к ответному сообщению
#
#
# # в качестве условия для обработки принимает только лямбда-функции
# @bot.callback_query_handler(func=lambda call: True)  # хендлер принимает объект Call
# def callback_query(call):
#     query_type = call.data.split('_')[0]  # получаем тип запроса
#     users = client.get_users()
#     if query_type == 'user':
#         user_id = call.data.split('_')[1]  # получаем айди юзера из нашей строки
#         inline_markup = telebot.types.InlineKeyboardMarkup()
#         for user in users:
#             if str(user['tg_ID']) == user_id:
#                 inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data='users'),
#                                   telebot.types.InlineKeyboardButton(text="Удалить юзера",
#                                                                      callback_data=f'delete_user_{user_id}'))
#
#                 bot.edit_message_text(text=f'Данные по юзеру:\n'
#                                            f'ID: {user["tg_ID"]}\n'
#                                            f'Ник: {user.get("nick")}\n'
#                                            f'Баланс: {client.get_user_balance_by_id(user["id"])}',
#                                       chat_id=call.message.chat.id,
#                                       message_id=call.message.message_id,
#                                       reply_markup=inline_markup)
#                 print(f"Запрошен {user}")
#                 break
#
#     if query_type == 'users':
#         inline_markup = telebot.types.InlineKeyboardMarkup()
#         for user in users:
#             # к каждой кнопке прикручиваем в callback_data айди юзера, чтобы можно было идентифицировать нажатую кнопку
#             inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["tg_ID"]}',
#                                                                  callback_data=f"user_{user['tg_ID']}"))
#         bot.edit_message_text(text="Юзеры:",
#                               chat_id=call.message.chat.id,
#                               message_id=call.message.message_id,
#                               reply_markup=inline_markup)  # прикрепляем нашу разметку к ответному сообщению
#
#     if query_type == 'delete' and call.data.split('_')[1] == 'user':
#
#         user_id = int(call.data.split('_')[2])  # получаем и превращаем наш айди в число
#         for i, user in enumerate(users):
#             if user['tg_ID'] == user_id:
#                 print(f'Удален Юзер: {users[i]}')
#                 client.delete_user(users.pop(i)['id'])
#         inline_markup = telebot.types.InlineKeyboardMarkup()
#         for user in users:
#             inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["tg_ID"]}',
#                                                                  callback_data=f"user_{user['tg_ID']}"))
#         bot.edit_message_text(text="Юзеры:",
#                               chat_id=call.message.chat.id,
#                               message_id=call.message.message_id,
#                               reply_markup=inline_markup)  # прикрепляем нашу разметку к ответному сообщению
#


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Все юзеры")
def all_users(message):
    users = users = client.get_users()
    count = ceil(len(users) / 4)
    page = 1

    text = f'Юзеры:'


    inline_markup = telebot.types.InlineKeyboardMarkup()  # создаем объект с инлайн-разметкой

    inline_markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='unseen'))

    inline_markup.add(telebot.types.InlineKeyboardButton(text=f'1/{count}', callback_data=f' '),telebot.types.InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page+1) + ",\"CountPage\":" + str(count) + "}"))



    for i in range(0, min(PagCount, len(users))):
        user = users[i]
        inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["nick"]}',
                                                      callback_data=f"user_{user['id']}_{page}_{count}"))
        # так как мы добавляем кнопки по одной, то у нас юзеры будут в 3 строчки
        # в коллбеке у нас будет текст, который содержит айди юзеров
    bot.send_message(message.chat.id, text,
                     reply_markup=inline_markup)  # прикрепляем нашу разметку к ответному сообщению


# в качестве условия для обработки принимает только лямбда-функции
@bot.callback_query_handler(func=lambda call: True)  # хендлер принимает объект Call
def callback_query(call):
    query_type = call.data.split('_')[0]  # получаем тип запроса
    users = client.get_users()
    if query_type == 'users':
        inline_markup = telebot.types.InlineKeyboardMarkup()  # создаем объект с инлайн-разметкой

        page = int(call.data.split('_')[1])  # получаем страницу пользователя
        count = ceil(len(users) / 4)



        page = min(page, count)
        page = max(1, page)

        inline_markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='unseen'))

        inline_markup.add(telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                          telebot.types.InlineKeyboardButton(text=f'Вперёд --->',
                                                             callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                                 page + 1) + ",\"CountPage\":" + str(count) + "}"))
        for i in range((page - 1) * PagCount, min(page * PagCount,
                                                  len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
            user = users[i]
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["nick"]}',
                                                          callback_data=f"user_{user['id']}_{page}_{count}"))
        bot.edit_message_text(f'Страница {page} из {count}', reply_markup=inline_markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

    if query_type == 'user':
        user_id = call.data.split('_')[1]  # получаем айди юзера из нашей строки

        page = call.data.split('_')[2] #получаем страницу пользователя
        count = call.data.split('_')[3]

        inline_markup = telebot.types.InlineKeyboardMarkup()
        for user in users:
            if str(user['id']) == user_id:
                inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data=f'users_{page}_{count}'),
                                  telebot.types.InlineKeyboardButton(text="Удалить юзера",
                                                                     callback_data=f'delete_user_{user_id}_{page}_{count}'))

                bot.edit_message_text(text=f'Данные по юзеру:\n'
                                           f'ID: {user["id"]}\n'
                                           f'Ник: {user["nick"]}\n'
                                           f'Баланс: {client.get_user_balance_by_id(user["id"])}',
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=inline_markup)
                print(f"Запрошен {user}")
                break






    if query_type == 'delete' and call.data.split('_')[1] == 'user':
        user_id = int(call.data.split('_')[2])  # получаем и превращаем наш айди в число
        page = int(call.data.split('_')[3])
        count = int(call.data.split('_')[4])

        for i, user in enumerate(users):
            if user['id'] == user_id:
                ans = f'Удален юзер:\n' + f'ID: {user["id"]}\n' + f'Ник: {user["nick"]}\n' + f'Баланс: {client.get_user_balance_by_id(user["id"])}'
                print(ans)
                users.pop(i)

        markup = telebot.types.InlineKeyboardMarkup()


        markup.add(telebot.types.InlineKeyboardButton(text= 'Все юзеры', callback_data=f'users_{page}_{count}'))

        bot.edit_message_text(ans, reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)



    if 'pagination' in query_type:
        # Расспарсим полученный JSON

        json_string = json.loads(query_type)
        count = json_string['CountPage']
        page = json_string['NumberPage']

        count = ceil(len(users) / 4)

        # Пересоздаем markup
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
        # markup для первой страницы

        if page > count:
            page = count
        if page < 1:
            page = 1

        if page == 1:
            markup.add(telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       telebot.types.InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
            for i in range ((page - 1) * PagCount, min(page * PagCount, len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
                user = users[i]
                markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["nick"]}',
                                                                     callback_data=f"user_{user['id']}_{page}_{count}"))
        # markup для второй страницы
        elif page == count:
            markup.add(telebot.types.InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
            for i in range((page - 1) * PagCount, min(page * PagCount,
                                               len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
                user = users[i]
                markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
                                                              callback_data=f"user_{user['id']}_{page}_{count}"))
        # markup для остальных страниц
        else:
            markup.add(telebot.types.InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       telebot.types.InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
            for i in range((page - 1) * PagCount, min(page * PagCount,
                                               len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
                user = users[i]
                markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["nick"]}',
                                                              callback_data=f"user_{user['id']}_{page}_{count}"))
        bot.edit_message_text(f'Страница {page} из {count}', reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    if query_type == 'unseen':
        bot.delete_message(call.message.chat.id, call.message.message_id)




@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Общий баланс")
def total_balance(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    btn2 = telebot.types.KeyboardButton('Админка')
    markup.add(btn1, btn2)
    balance = client.get_total_balance()
    text = f'Общий баланс: {balance/100000000} BTC'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# тут мы создадим простейший конечный автомат для обработки диалога с отправкой транзакции
states_list = ["ADDRESS", "AMOUNT", "CONFIRM"]
states_of_users = {}


@bot.message_handler(regexp='Перевести')
def start_transaction(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите адрес кошелька куда хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # тут мы даём юзеру состояние при котором ему будет возвращаться следующее сообщение
    states_of_users[message.from_user.id] = {"STATE":"ADDRESS"}


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'ADDRESS')
def get_amount_of_transaction(message):
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите сумму в сатоши, которую хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # тут мы даём юзеру состояние при котором ему будет возвращаться следующее сообщение
    states_of_users[message.from_user.id]["STATE"] = "AMOUNT"
    states_of_users[message.from_user.id]["ADDRESS"] = message.text


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'AMOUNT')
def get_confirmation_of_transaction(message):
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    if message.text.isdigit():
        text = f'Вы хотите перевести {message.text} сатоши,\n' \
               f'на биткоин-адрес {states_of_users[message.from_user.id]["ADDRESS"]}: '
        confirm = telebot.types.KeyboardButton('Подтверждаю')
        markup.add(confirm)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        # тут мы даём юзеру состояние при котором ему будет возвращаться следующее сообщение
        states_of_users[message.from_user.id]["STATE"] = "CONFIRM"
        states_of_users[message.from_user.id]["AMOUNT"] = int(message.text)
    else:
        text = f'Вы ввели не число, попробуйте заново: '
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'CONFIRM')
def get_hash_of_transaction(message):
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    elif message.text == "Подтверждаю":
        try:
            bot.send_message(message.chat.id, f" Ваша транзакция: " + str(client.create_transaction(message.from_user.id,
                                             states_of_users[message.from_user.id]['ADDRESS'],
                                             states_of_users[message.from_user.id]['AMOUNT'])))
        except:
            bot.send_message(message.chat.id, "ошибка транзакции")
        del states_of_users[message.from_user.id]
        menu(message)


# запускаем бота этой командой:
bot.infinity_polling()

# old code

# def make_hello_greet(date):
#     import time
#     opts = {"hey": ('привет', 'здравствуйте', 'доброе утро', 'добрый день', 'добрый вечер', 'доброй ночи')}
#     now_hour = int(time.strftime("%H", time.localtime(date)))
#     if now_hour > 4 and now_hour <= 12 :
#         greet = opts["hey"][2]
#     if now_hour > 12 and now_hour <= 16 :
#         greet = opts["hey"][3]
#     if now_hour > 16 and now_hour <= 24 :
#         greet = opts["hey"][4]
#     if now_hour >= 0 and now_hour <= 4 :
#         greet = opts["hey"][5]
#     return greet + ','
#
#
#
#
#
# @bot.message_handler(commands=['start'])
# def start_message(message):
#     try:
#         client.create_user({"tg_ID":message.from_user.id, "nick":message.from_user.username})
#     except Exception as Ex:
#         #bot.send_message(message.chat.id, f'Возникла ошибка: {Ex.args}')
#         pass
#     # создаем объект для работы с кнопками (row_width - определяет количество кнопок по ширине)
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#
#     # создаем каждую кнопку таким образом
#     btn1 = telebot.types.KeyboardButton('Кошелек')
#     btn2 = telebot.types.KeyboardButton('Перевести')
#     btn3 = telebot.types.KeyboardButton('История')
#
#     markup.add(btn1, btn2, btn3)
#
#     greet = make_hello_greet(message.date)  # приветствие в зависимости от времени суток телеграм-пользователя
#     text = f'{greet.capitalize()} {message.from_user.full_name}, я твой бот-криптокошелек, \n ' 'у меня ты можешь хранить и отправлять биткоины'
#
#     # теперь добавляем объект с кнопками к отправляемому пользователю сообщению в аргумент "reply_markup"
#     bot.send_message(message.chat.id, text, reply_markup=markup)



# @bot.message_handler(regexp='Кошелек')
# def wallet(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Меню')  # мы создали ещё одну кнопку, которую надо обработать
#     markup.add(btn1)
#     balance = 0  # сюда мы будем получать баланс через наш API
#     text = f'Ваш баланс: {balance}'
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# @bot.message_handler(regexp='Перевести')
# def transaction(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Меню')
#     markup.add(btn1)
#     text = f'Введите адрес кошелька куда хотите перевести: '
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# @bot.message_handler(regexp='История')
# def history(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Меню')
#     markup.add(btn1)
#     transactions = ['1', '2', '3']  # сюда мы загрузим транзакции
#     text = f'Ваши транзакции{transactions}'
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# @bot.message_handler(regexp='Меню')
# def menu(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Кошелек')
#     btn2 = telebot.types.KeyboardButton('Перевести')
#     btn3 = telebot.types.KeyboardButton('История')
#     markup.add(btn1, btn2, btn3)
#
#     text = f'Главное меню'
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# @bot.message_handler(regexp='Я в консоли')
# def print_me(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Меню')
#     markup.add(btn1)
#     print(message.from_user.to_dict())
#     text = f'Ты: {message.from_user.to_dict()}'
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# @bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Админка")
# def admin_panel(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Общий баланс')
#     btn2 = telebot.types.KeyboardButton('Все юзеры')
#     btn3 = telebot.types.KeyboardButton('Меню')
#     markup.add(btn1, btn2, btn3)
#     text = f'Админ-панель'
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# users = config.fake_database['users']
#
#
# # делаем проверку на админ ли боту пишет проверяем текст сообщения
#
# @bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Все юзеры")
# def all_users(message):
#     count = ceil(len(users) / 4)
#     page = 1
#
#     text = f'Юзеры:'
#
#
#     inline_markup = telebot.types.InlineKeyboardMarkup()  # создаем объект с инлайн-разметкой
#
#     inline_markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
#
#     inline_markup.add(telebot.types.InlineKeyboardButton(text=f'1/{count}', callback_data=f' '),telebot.types.InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(page+1) + ",\"CountPage\":" + str(count) + "}"))
#
#
#
#     for i in range(0, min(PagCount, len(users))):
#         user = users[i]
#         inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
#                                                       callback_data=f"user_{user['id']}_{page}_{count}"))
#         # так как мы добавляем кнопки по одной, то у нас юзеры будут в 3 строчки
#         # в коллбеке у нас будет текст, который содержит айди юзеров
#     bot.send_message(message.chat.id, text,
#                      reply_markup=inline_markup)  # прикрепляем нашу разметку к ответному сообщению
#
#
# # в качестве условия для обработки принимает только лямбда-функции
# @bot.callback_query_handler(func=lambda call: True)  # хендлер принимает объект Call
# def callback_query(call):
#     query_type = call.data.split('_')[0]  # получаем тип запроса
#
#     if query_type == 'users':
#         inline_markup = telebot.types.InlineKeyboardMarkup()  # создаем объект с инлайн-разметкой
#
#         page = int(call.data.split('_')[1])  # получаем страницу пользователя
#         count = ceil(len(users) / 4)
#
#
#
#         page = min(page, count)
#         page = max(1, page)
#
#         inline_markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
#
#         inline_markup.add(telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
#                           telebot.types.InlineKeyboardButton(text=f'Вперёд --->',
#                                                              callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
#                                                                  page + 1) + ",\"CountPage\":" + str(count) + "}"))
#         for i in range((page - 1) * PagCount, min(page * PagCount,
#                                                   len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
#             user = users[i]
#             inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
#                                                           callback_data=f"user_{user['id']}_{page}_{count}"))
#         bot.edit_message_text(f'Страница {page} из {count}', reply_markup=inline_markup, chat_id=call.message.chat.id,
#                               message_id=call.message.message_id)
#
#     if query_type == 'user':
#         user_id = call.data.split('_')[1]  # получаем айди юзера из нашей строки
#
#         page = call.data.split('_')[2] #получаем страницу пользователя
#         count = call.data.split('_')[3]
#
#         inline_markup = telebot.types.InlineKeyboardMarkup()
#         for user in users:
#             if str(user['id']) == user_id:
#                 inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data=f'users_{page}_{count}'),
#                                   telebot.types.InlineKeyboardButton(text="Удалить юзера",
#                                                                      callback_data=f'delete_user_{user_id}_{page}_{count}'))
#
#                 bot.edit_message_text(text=f'Данные по юзеру:\n'
#                                            f'ID: {user["id"]}\n'
#                                            f'Имя: {user["name"]}\n'
#                                            f'Ник: {user["nick"]}\n'
#                                            f'Баланс: {user["balance"]}',
#                                       chat_id=call.message.chat.id,
#                                       message_id=call.message.message_id,
#                                       reply_markup=inline_markup)
#                 print(f"Запрошен {user}")
#                 break
#
#
#
#
#
#
#     if query_type == 'delete' and call.data.split('_')[1] == 'user':
#         user_id = int(call.data.split('_')[2])  # получаем и превращаем наш айди в число
#         page = int(call.data.split('_')[3])
#         count = int(call.data.split('_')[4])
#
#         for i, user in enumerate(users):
#             if user['id'] == user_id:
#                 ans = f'Удален юзер:\n' + f'ID: {user["id"]}\n' + f'Имя: {user["name"]}\n' + f'Ник: {user["nick"]}\n' + f'Баланс: {user["balance"]}'
#                 print(ans)
#                 users.pop(i)
#
#         markup = telebot.types.InlineKeyboardMarkup()
#
#
#         markup.add(telebot.types.InlineKeyboardButton(text= 'Все юзеры', callback_data=f'users_{page}_{count}'))
#
#         bot.edit_message_text(ans, reply_markup=markup, chat_id=call.message.chat.id,
#                               message_id=call.message.message_id)
#
#
#
#     if 'pagination' in query_type:
#         # Расспарсим полученный JSON
#
#         json_string = json.loads(query_type)
#         count = json_string['CountPage']
#         page = json_string['NumberPage']
#
#         count = ceil(len(users) / 4)
#
#         # Пересоздаем markup
#         markup = telebot.types.InlineKeyboardMarkup()
#         markup.add(telebot.types.InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
#         # markup для первой страницы
#
#         if page > count:
#             page = count
#         if page < 1:
#             page = 1
#
#         if page == 1:
#             markup.add(telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
#                        telebot.types.InlineKeyboardButton(text=f'Вперёд --->',
#                                             callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
#                                                 page + 1) + ",\"CountPage\":" + str(count) + "}"))
#             for i in range ((page - 1) * PagCount, min(page * PagCount, len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
#                 user = users[i]
#                 markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
#                                                                      callback_data=f"user_{user['id']}_{page}_{count}"))
#         # markup для второй страницы
#         elif page == count:
#             markup.add(telebot.types.InlineKeyboardButton(text=f'<--- Назад',
#                                             callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
#                                                 page - 1) + ",\"CountPage\":" + str(count) + "}"),
#                        telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
#             for i in range((page - 1) * PagCount, min(page * PagCount,
#                                                len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
#                 user = users[i]
#                 markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
#                                                               callback_data=f"user_{user['id']}_{page}_{count}"))
#         # markup для остальных страниц
#         else:
#             markup.add(telebot.types.InlineKeyboardButton(text=f'<--- Назад',
#                                             callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
#                                                 page - 1) + ",\"CountPage\":" + str(count) + "}"),
#                        telebot.types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
#                        telebot.types.InlineKeyboardButton(text=f'Вперёд --->',
#                                             callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
#                                                 page + 1) + ",\"CountPage\":" + str(count) + "}"))
#             for i in range((page - 1) * PagCount, min(page * PagCount,
#                                                len(users))):  # в цикле создаем 3 кнопки и добавляем их поочередно в нашу разметку
#                 user = users[i]
#                 markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
#                                                               callback_data=f"user_{user['id']}_{page}_{count}"))
#         bot.edit_message_text(f'Страница {page} из {count}', reply_markup=markup, chat_id=call.message.chat.id,
#                               message_id=call.message.message_id)
#     if query_type == 'unseen':
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#
#
#
# @bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Общий баланс")
# def total_balance(message):
#     markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = telebot.types.KeyboardButton('Меню')
#     btn2 = telebot.types.KeyboardButton('Админка')
#     markup.add(btn1, btn2)
#     balance = 0
#     for user in users:
#         balance += user['balance']
#     text = f'Общий баланс: {balance}'
#     bot.send_message(message.chat.id, text, reply_markup=markup)
#
#
# # запускаем бота этой командой:
# bot.infinity_polling()