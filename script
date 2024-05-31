import telebot  # Библиотека для работы с Telegram Bot API
import time
import sys
import re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from opros import surveys  # Импорт определений опросов
from transliterate import translit

def print_colored(text, color):
    colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'purple': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    sys.stdout.write(colors[color] + text + colors['reset'] + '\n')


def normalize_and_transliterate(survey_name):
    # Проверка на максимальную длину
    if len(survey_name) > 64:
        return None, "Название опроса слишком длинное. Максимальная длина - 64 символа."
    
    # Проверка на недопустимые символы
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789 .()-"!?')
    for char in survey_name:
        if char.lower() not in allowed_chars:
            return None, f"Название опроса содержит недопустимый символ '{char}'.  Пожалуйста, используйте только буквы, цифры, пробелы и символы .()-'"
    
    # Проверка на минимальное количество букв (хотя бы 4 буквы)
    if len(re.findall(r'[a-zA-Zа-яА-Я]', survey_name)) < 4:
        return None, "Название опроса должно содержать хотя бы 4 буквы."
    
    # Нормализация: удаление нежелательных символов и замена пробелов на тире
    normalized_title = re.sub(r'[^a-zA-Zа-яА-Я0-9 ]', '', survey_name)
    normalized_title = normalized_title.replace(' ', '-')
    # Транслитерация на английский язык
    transliterated_title = translit(normalized_title, 'ru', reversed=True)
    # Добавление суффикса
    final_survey_id = transliterated_title.lower() + "_survey"
    return final_survey_id, None


class User:
    def __init__(self, nickname, chat_id):
        self.nickname = nickname  # Никнейм пользователя
        self.chat_id = chat_id  # ID чата пользователя
        self.completed_surveys = {}  # Словарь для хранения ответов на пройденные опросы
        self.answers_guessing = {}  # Словарь для угадывания ответов других пользователей
        self.state = None  # Добавлено состояние пользователя
        self.current_survey = None  # Текущий опрос, который выбрал пользователь
        self.current_question_index = 0  # Индекс текущего вопроса в опросе
        self.start_command_sent = False  # Отслеживание первой отправки /start
        self.temporary_surveys = {}  # Инициализация временных опросов
        self.temporary_surveys_guessing = {}  # Хранилище для угадывания ответов
        self.in_yes_no_choice = False  # Добавлено для управления состоянием выбора "Да" или "Нет"
        self.guessing = False  # Новое поле для управления состоянием "Угадать ответы друга"
        self.guessing_survey = None  # Идентификатор текущего опроса для угадывания
        self.last_bot_message_id = None  # Новое поле для хранения message_id последнего сообщения бота
        self.show_limited_friends = True  # Новая переменная для 5-ти пользователей
        self.creating_survey_data = None  # Данные создаваемого опроса
        self.creating_survey_questions = []  # Список вопросов и вариантов ответов создаваемого опроса

        # Добавление отладки для отслеживания инициализации состояния
        print_colored(f"User initialized with no state: {nickname}", 'cyan')

class Answer:
    def __init__(self):
        self.responses = []  # Список ответов на вопросы опроса

    def add_response(self, response):
        self.responses.append(response)  # Добавление ответа в список



class SurveyBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.users = {}  # Словарь пользователей по никнейму
        self.waiting_for_nickname = set()  # Сет для отслеживания, кто должен ввести никнейм



        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            if message.chat.id in [user.chat_id for user in self.users.values()]:
                # Пользователь уже зарегистрирован
                sent_msg = self.bot.send_message(message.chat.id, "Ты уже зарегистрирован!")
                time.sleep(2)
                self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                
            elif message.chat.id in self.waiting_for_nickname:
                # Пользователь уже вызвал /start, но не ввёл никнейм
                sent_msg = self.bot.send_message(message.chat.id, "Ты уже написал /start, теперь введи никнейм")
                time.sleep(2)
                self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            else:
                # Пользователь еще не зарегистрирован и не ожидает ввода никнейма
                self.waiting_for_nickname.add(message.chat.id)
                self.bot.send_message(message.chat.id, "Введите свой никнейм для регистрации")



        @self.bot.message_handler(func=lambda message: True)
        def handle_messages(message):
            if message.chat.id in self.waiting_for_nickname:
                user_message_id = message.message_id  # Сохранение ID сообщения пользователя
                nickname = message.text.strip()

                if re.match(r'^[\w\s]{1,16}$', nickname) and nickname not in self.users:
                    user = User(nickname, message.chat.id)
                    self.users[nickname] = user
                    self.waiting_for_nickname.remove(message.chat.id)
                    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    markup.add('Пройти опрос', 'Угадать ответы друга')
                    self.bot.send_message(message.chat.id, f"Привет {nickname}, выбери режим:", reply_markup=markup)
                    print_colored(f"Пользователь {nickname} зарегистрировался", 'green')

                elif len(nickname) > 16:
                    msg = self.bot.send_message(message.chat.id, "Максимальная длина никнейма составляет 16 символов!")
                    print_colored(f"Пользователь {message.chat.id} пытается зарегистрироваться с слишком длинным никнеймом: {nickname}", 'red')
                    time.sleep(2)
                    self.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
                    self.bot.delete_message(chat_id=message.chat.id, message_id=user_message_id)

                elif nickname in self.users:
                    msg = self.bot.send_message(message.chat.id, "Этот никнейм уже занят, введите другой")
                    print_colored(f"Пользователь {message.chat.id} пытается зарегистрироваться под никнеймом {nickname}, но этот никнейм уже занят", 'red')
                    time.sleep(2)
                    self.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
                    self.bot.delete_message(chat_id=message.chat.id, message_id=user_message_id)

                else:
                    msg = self.bot.send_message(message.chat.id, "Неправильное имя никнейма, используйте буквы, цифры, нижнее подчеркивание и пробелы. Попробуйте ещё раз.")
                    print_colored(f"Пользователь {message.chat.id} ввел невалидный никнейм: {nickname}", 'red')
                    time.sleep(3)
                    self.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
                    self.bot.delete_message(chat_id=message.chat.id, message_id=user_message_id)

            # Обработка сообщений от уже зарегистрированных пользователей
            else:
                user = next((user for user in self.users.values() if user.chat_id == message.chat.id), None)
                if user:

                    # Объявление sent_msg
                    sent_msg = None  

                    if user.in_yes_no_choice:
                        # Обработка состояния выбора "Да" или "Нет"
                        temp_msg = self.bot.send_message(message.chat.id, "Сначала выберите Да или Нет")
                        time.sleep(2)
                        self.bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
                        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                        return  # Прекращаем обработку текущего сообщения
                    # Обработка сообщений в состоянии 'taking_survey'
                    if user.state == 'taking_survey' or user.state == 'guessing_answers':
                        # Реагировать только на ответы опроса и кнопку "Назад"
                        if message.text not in ["Назад"] + [option for question in surveys[user.current_survey].questions for option in question.options]:
                            temp_msg = self.bot.send_message(message.chat.id, "Сначала заверши текущий опрос или выйди из него")
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                            return  # Прекращаем обработку текущего сообщения

                    if user.guessing:
                        input_text = message.text.strip()
                        print_colored(f"User {user.nickname} entered text: '{input_text}' with message_id={message.message_id}", 'cyan')

                        if user.state == 'choosing_friend_survey':
                            # Если пользователь уже выбирает опрос друга, не обрабатываем текст как никнейм
                            temp_msg = self.bot.send_message(message.chat.id, "Выберите опрос друга или нажмите на кнопку 'Назад'")
                            print_colored(f"Bot sent: 'Выберите опрос друга или нажмите на кнопку 'Назад'' with message_id={temp_msg.message_id}", 'blue')
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
                            print_colored(f"Deleted message with message_id={temp_msg.message_id}", 'yellow')
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                            print_colored(f"Deleted message with message_id={message.message_id}", 'yellow')

                        elif not re.match(r'^[\w\s]{1,16}$', input_text):
                            temp_msg = self.bot.send_message(message.chat.id, "Никнейм содержит неправильные символы или слишком длинный. Попробуйте ещё раз.")
                            print_colored(f"Bot sent: 'Никнейм содержит неправильные символы или слишком длинный. Попробуйте ещё раз.' with message_id={temp_msg.message_id}", 'blue')
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
                            print_colored(f"Invalid nickname: Deleted message with message_id={temp_msg.message_id}", 'yellow')
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                            print_colored(f"Invalid nickname: Deleted message with message_id={message.message_id}", 'yellow')

                        elif input_text == user.nickname:
                            temp_msg = self.bot.send_message(message.chat.id, "Вы ввели свой собственный никнейм. Пожалуйста, введите никнейм другого пользователя.")
                            print_colored(f"Bot sent: 'Вы ввели свой собственный никнейм. Пожалуйста, введите никнейм другого пользователя.' with message_id={temp_msg.message_id}", 'blue')
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
                            print_colored(f"Deleted self-nickname message with message_id={temp_msg.message_id}", 'yellow')
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                            print_colored(f"Deleted self-nickname message with message_id={message.message_id}", 'yellow')

                        elif input_text not in self.users:
                            temp_msg = self.bot.send_message(message.chat.id, "Такого пользователя нет, проверьте правильность никнейма.")
                            print_colored(f"Bot sent: 'Такого пользователя нет, проверьте правильность никнейма.' with message_id={temp_msg.message_id}", 'blue')
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=temp_msg.message_id)
                            print_colored(f"Deleted non-existent user message with message_id={temp_msg.message_id}", 'yellow')
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                            print_colored(f"Deleted non-existent user message with message_id={message.message_id}", 'yellow')

                        else:
                            friend_user = self.users[input_text]
                            print_colored(f"User {user.nickname} entered valid friend nickname '{input_text}' with message_id={message.message_id}", 'cyan')
                            if friend_user.completed_surveys:
                                user.state = 'choosing_friend_survey'
                                # При попытке удалить сообщение
                                if user.last_bot_message_id:
                                    try:
                                        self.bot.delete_message(chat_id=message.chat.id, message_id=user.last_bot_message_id)
                                        print_colored(f"Successfully deleted bot's message with message_id={user.last_bot_message_id}", 'yellow')
                                        user.last_bot_message_id = None  # Сброс после успешного удаления
                                    except telebot.apihelper.ApiTelegramException as e:
                                        print_colored(f"Failed to delete message: {e.description} with message_id={user.last_bot_message_id}", 'red')

                                markup = InlineKeyboardMarkup()
                                for survey_id in friend_user.completed_surveys.keys():
                                    survey_title = surveys[survey_id].title
                                    markup.add(InlineKeyboardButton(survey_title, callback_data=f"guess_survey:{friend_user.nickname}:{survey_id}"))
                                markup.add(InlineKeyboardButton("Назад", callback_data="cancel_guessing"))
                                
                                # Удаление предыдущего сообщения пользователя
                                self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                                print_colored(f"Successfully deleted user's previous message with message_id={message.message_id}", 'yellow')
                                sent_msg = self.bot.send_message(user.chat_id, "Какой тест хотите угадать?", reply_markup=markup)
                                print_colored(f"Bot sent message: 'Какой тест хотите угадать?' with message_id={sent_msg.message_id}", 'blue')
                                print_colored(f"User {user.nickname} is now choosing a survey to guess from {friend_user.nickname}", 'green')
                            else:
                                temp_msg = self.bot.send_message(user.chat_id, "У этого пользователя нет завершенных опросов.")
                                print_colored(f"Bot sent message: 'У этого пользователя нет завершенных опросов.' with message_id={temp_msg.message_id}", 'blue')
                                time.sleep(2)
                                self.bot.delete_message(chat_id=user.chat_id, message_id=temp_msg.message_id)
                                self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                                print_colored(f"Successfully deleted message with message_id={temp_msg.message_id}", 'yellow')
                                user.state = 'guessing'
                        return


                        


                    if message.text == 'Пройти опрос':
                        user.state = 'choosing_survey'
                        print_colored(f"    Пользователь {user.nickname} выбрал режим \"Пройти опрос\"", 'white')
                        markup = InlineKeyboardMarkup()
                        # Добавление кнопок для каждого опроса
                        for survey_id, survey in surveys.items():
                            markup.add(InlineKeyboardButton(survey.title, callback_data='survey_' + survey_id))
                        # Добавление кнопки "Назад"
                        markup.add(InlineKeyboardButton("Назад", callback_data='go_back'))
                        sent_msg = self.bot.send_message(message.chat.id, "Выбери опрос:", reply_markup=markup)
                        
                    elif message.text == 'Угадать ответы друга':
                        if len(self.users) > 1:  # Проверяем, есть ли другие зарегистрированные пользователи
                            user.guessing = True
                            user.state = 'guessing'  # Переводим пользователя в состояние "guessing"
                            markup = InlineKeyboardMarkup()


                            # Создание кнопок для первых пяти зарегистрированных пользователей, кроме самого пользователя
                            other_users = [u for u in self.users.values() if u.nickname != user.nickname]
                            for other_user in other_users[:5]:  # Берем только первых пять пользователей
                                markup.add(InlineKeyboardButton(other_user.nickname, callback_data=f'guess_{other_user.nickname}'))

                            markup.add(InlineKeyboardButton("Назад", callback_data='go_back'))
                            sent_msg = self.bot.send_message(message.chat.id, "Выберите друга или введите вручную:", reply_markup=markup)
                            user.last_bot_message_id = sent_msg.message_id  # Сохраняем ID сообщения
                            print_colored(f"Sent message for choosing a friend with message_id={sent_msg.message_id}", 'yellow')
                            print_colored(f"{user.nickname} перешел в режим угадывания ответов", 'green')
                        else:  # Если зарегистрирован только один пользователь
                            msg = self.bot.send_message(message.chat.id, "Ты первый из зарегистрированных пользователей. Подожди пока кто-то еще зарегистрируется и пройдет опрос")
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
                            print_colored(f"Deleted message with message_id={message.message_id}", 'yellow')
                            print_colored(f"Информационное сообщение для {user.nickname} удалено по истечении времени", 'yellow')



                    elif user.state == 'creating_survey':
                        survey_name = message.text.strip()
                        survey_id, error = normalize_and_transliterate(survey_name)
                        if error:
                            print_colored(f"        Ошибка при создании опроса пользователем {user.nickname}: {error}", "red")
                            sent_msg = self.bot.send_message(message.chat.id, f"Ошибка: {error}")  
                            time.sleep(3)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                        elif survey_id in surveys:
                            print_colored(f"        Ошибка при создании опроса пользователем {user.nickname}: название опроса уже занято", "red")
                            sent_msg = self.bot.send_message(message.chat.id, "Название опроса уже занято. Введите другое название:")
                            time.sleep(2)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                        else:
                            print_colored(f"        Пользователь {user.nickname} создал опрос с названием {survey_name}", "green")
                            user.creating_survey_data['title'] = survey_name

                            # Удаление сообщений
                            print_colored(f"        Удаляем сообщение пользователя с ID {message.message_id}", "yellow") 
                            self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)  # Удаляем сообщение пользователя

                            print_colored(f"        ID последнего сообщения бота: {user.last_bot_message_id}", "yellow")
                            if user.last_bot_message_id:  # Проверяем, было ли предыдущее сообщение бота
                                print_colored(f"        Удаляем сообщение бота с ID {user.last_bot_message_id}", "yellow")
                                self.bot.delete_message(chat_id=message.chat.id, message_id=user.last_bot_message_id)  # Удаляем сообщение бота
                                user.last_bot_message_id = None  # <-- Сбрасываем ID 
                            else:
                                print_colored("        ID последнего сообщения бота не найден", "red")

                            # Форматирование и отправка шаблона с именем опроса 
                            message_text = f"""Введите вопросы и варианты ответа на ваш опрос "{survey_name}". 
Вот шаблон:
"
1) Какая твоя любимая еда?
Пицца, роллы, картошка, пельмени
2)Что ты любишь смотреть?
Аниме, фильмы, сериалы
"
"""
                            markup = InlineKeyboardMarkup()
                            markup.add(InlineKeyboardButton("Назад", callback_data='go_back_creating'))

                            # Отправка сообщения и сохранение ID 
                            sent_msg = self.bot.send_message(message.chat.id, message_text, reply_markup=markup)
                            print_colored(f"        Отправлено сообщение с ID {user.last_bot_message_id}", "yellow")

                            # Проверка sent_msg перед сохранением ID 
                            if sent_msg: 
                                user.last_bot_message_id = sent_msg.message_id  

                            user.state = 'creating_question'

                    elif user.state == 'choosing_survey':
                        # Пользователь в состоянии выбора опроса, но отправил некорректное сообщение
                        sent_msg = self.bot.send_message(message.chat.id, 'Такого опроса нет, выбери существующий опрос или нажми на кнопку "Назад"')
                        time.sleep(2)
                        self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                        
                    else:
                        # Обработка сообщений, которые не подходят ни под одну категорию
                        sent_msg = self.bot.send_message(message.chat.id, "Такого режима нет, пожалуйста, выберите один из предложенных вариантов.")
                        time.sleep(2)
                        self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

                else:
                    print_colored(f"Пользователь {message.chat.id} пытается взаимодействовать с ботом перед регистрацией", 'red')
                    sent_msg = self.bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, введите команду /start")
                    time.sleep(2)
                    # Удаление сообщения бота с предупреждением
                    self.bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
                    # Удаление сообщения пользователя, если оно не является командой /start
                    if message.text.strip() != '/start':
                        self.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

                # Обработка нажатия кнопок в inline-режиме
                @self.bot.callback_query_handler(func=lambda call: True)
                def handle_query(call):
                    user = next((user for user in self.users.values() if user.chat_id == call.message.chat.id), None)
                    if not user:
                        # Если пользователь не найден, отправить сообщение о необходимости регистрации
                        self.bot.answer_callback_query(call.id, "Пожалуйста, сначала зарегистрируйтесь, используя команду /start.")
                        return  # Прекращаем обработку запроса
                    
                    # Обработка нажатия на кнопку "Назад" в состоянии выбора опроса друга
                    if call.data == "cancel_guessing":
                        print_colored(f"Пользователь {user.nickname} нажал на кнопку 'Назад' и возвращается к выбору друга.", 'red')
                        user.state = 'guessing'  # Возвращение к состоянию выбора друга
                        markup = InlineKeyboardMarkup()
                        other_users = [u for u in self.users.values() if u.nickname != user.nickname][:5]  # Берем первых пять пользователей, кроме самого пользователя
                        for other_user in other_users:
                            markup.add(InlineKeyboardButton(other_user.nickname, callback_data=f'guess_{other_user.nickname}'))
                        markup.add(InlineKeyboardButton("Назад", callback_data='go_back'))
                        # Удаление старого сообщения и отправка нового
                        self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        sent_msg = self.bot.send_message(call.message.chat.id, "Выберите друга или введите вручную:", reply_markup=markup)
                        user.last_bot_message_id = sent_msg.message_id  # Обновляем last_bot_message_id
                        print_colored(f"Sent new message with ID {sent_msg.message_id} for choosing a friend again.", 'green')
                        return  # Завершаем обработку

                    try:
                        # Обработка выбора друга для угадывания ответов
                        if call.data.startswith('guess_'):
                            friend_nickname = call.data[6:]  # извлекаем никнейм друга после префикса 'guess_'
                            friend_user = self.users.get(friend_nickname)
                            if friend_user and friend_user.completed_surveys:
                                user.state = 'choosing_friend_survey'
                                print_colored(f"Handling friend selection for guessing with friend_nickname={friend_nickname}", 'cyan')
                                markup = InlineKeyboardMarkup()
                                for survey_id in friend_user.completed_surveys.keys():
                                    survey_title = surveys[survey_id].title
                                    markup.add(InlineKeyboardButton(survey_title, callback_data=f"guess_survey:{friend_user.nickname}:{survey_id}"))
                                markup.add(InlineKeyboardButton("Назад", callback_data="cancel_guessing"))
                                # Удаление предыдущего сообщения перед отправкой нового
                                self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                                print_colored(f"Deleted previous message in friend guessing with message_id={call.message.message_id}", 'red')
                                self.bot.send_message(user.chat_id, "Какой тест хотите угадать?", reply_markup=markup)
                                print_colored(f"Пользователь {user.nickname} перешел к выбору теста для угадывания от {friend_user.nickname}", 'green')

                            elif call.data.startswith('guess_survey:'):
                                _, friend_nickname, survey_id = call.data.split(':')
                                user.state = 'guessing_answers'  # Установка состояния для угадывания ответов
                                user.guessing_survey = f"guess_survey:{friend_nickname}:{survey_id}"  # "Исправлено" Сохранение ID опроса для угадывания

                                print_colored(f"User {user.nickname} is now guessing survey {survey_id} from {friend_nickname}", 'cyan')

                                # Переходим к первому вопросу опроса
                                start_survey(call, user)

    
                            elif friend_user:
                                if not friend_user.completed_surveys:
                                    temp_msg = self.bot.send_message(user.chat_id, "У этого пользователя нет завершенных опросов.")
                                    time.sleep(2)  # Задержка перед удалением сообщения
                                    self.bot.delete_message(chat_id=user.chat_id, message_id=temp_msg.message_id)
                                    user.state = 'guessing'  # Возвращаем пользователя к состоянию выбора друга
                                else:
                                    user.state = 'choosing_friend_survey'
                                    markup = InlineKeyboardMarkup()
                                    for survey_id in friend_user.completed_surveys.keys():
                                        survey_title = surveys[survey_id].title
                                        markup.add(InlineKeyboardButton(survey_title, callback_data=f"guess_survey:{friend_user.nickname}:{survey_id}"))
                                    markup.add(InlineKeyboardButton("Назад", callback_data="cancel_guessing"))
                                    self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                                    self.bot.send_message(user.chat_id, "Какой тест хотите угадать?", reply_markup=markup)
                            else:
                                temp_msg = self.bot.send_message(user.chat_id, "Пользователь не найден, попробуйте еще раз.")
                                time.sleep(2)  # Задержка перед удалением сообщения
                                self.bot.delete_message(chat_id=user.chat_id, message_id=temp_msg.message_id)
                                user.state = 'guessing'  # Возвращаем пользователя к состоянию выбора друга

                        else:
                            # Другие обработчики для различных callback данных
                            pass
                    finally:
                        # Этот вызов подтверждает обработку callback запроса
                        self.bot.answer_callback_query(call.id)    
                    
                    if call.data.startswith('repeat_survey_no'):
                        print_colored(f"  Пользователь {user.nickname} отказался повторно проходить опрос", 'red')
                        # Сброс состояния пользователя
                        user.state = None
                        user.in_yes_no_choice = False  # Сброс специального состояния
                        self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        return  # Прекращаем обработку и удаляем сообщение
                    
                    elif call.data.startswith('repeat_survey_yes'):
                        user.in_yes_no_choice = False  # Сброс состояния выбора "Да" или "Нет" перед началом опроса
                        survey_id = call.data.split(':')[1]
                        print_colored(f"        Пользователь {user.nickname} решил повторно пройти опрос {surveys[survey_id].title}", 'green')
                        
                        # Инициализируем или очищаем временное хранилище только для текущего опроса
                        user.temporary_surveys[survey_id] = []
                        
                        user.current_survey = survey_id
                        user.current_question_index = 0
                        survey = surveys[survey_id]
                        question = survey.questions[0]
                        total_questions = len(survey.questions)
                        
                        markup = InlineKeyboardMarkup()
                        for option in question.options:
                            markup.add(InlineKeyboardButton(option, callback_data=f"answer:{survey_id}:0:{option}"))
                        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_survey_list"))
                        
                        formatted_question_text = f"Вопрос 1/{total_questions}: {question.text}"
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                text=formatted_question_text, reply_markup=markup)
                        
                    elif call.data == "confirm_yes" or call.data == "confirm_no":
                        user.in_yes_no_choice = False  # Деактивация специального состояния
                        print_colored(f"Пользователь {user.nickname} выбрал {'повторить' if call.data == 'confirm_yes' else 'не повторять'} опрос", 'green')
                        if call.data == "confirm_yes":
                            # Логика для продолжения опроса или действия
                            pass
                        else:
                            # Логика для отказа от действия и возможного возврата в начальное меню
                            pass
                        return    



                    if call.data.startswith('survey_'):
                        start_survey(call, user)
                    elif call.data.startswith('answer:'):
                        handle_answer(call, user)
                    elif call.data.startswith('go_back_question'):
                        # Обработка возврата к предыдущему вопросу
                        if user.current_question_index > 0:
                            previous_question_index = user.current_question_index
                            user.current_question_index -= 1
                            # Удаление последнего сохраненного ответа из временного хранилища
                            if user.temporary_surveys[user.current_survey]:
                                user.temporary_surveys[user.current_survey].pop()
                            process_next_question(user, surveys[user.current_survey], user.current_survey, user.current_question_index, call.message.message_id)
                            print_colored(f"          Пользователь {user.nickname} нажал на кнопку \"Назад\" на {previous_question_index + 1} вопросе и снова отвечает на {user.current_question_index + 1} вопрос", 'red')

                        else:
                            # Если это первый вопрос, отправляем список опросов
                            self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                            send_survey_list(user)
                            print_colored("      Пользователь нажал на \"Назад\" на первом опросе и вышел к списку опросов", 'red')
                            user.state = 'choosing_survey'  # Сброс состояния пользователя при возврате к списку опросов
                    elif call.data == 'back_to_survey_list':
                        # Обработка возврата непосредственно к списку опросов с первого вопроса
                        self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        send_survey_list(user)
                        user.state = 'choosing_survey'  # Установка состояния пользователя при возврате к списку опросов
                        print_colored("      Пользователь нажал на \"Назад\" на первом опросе и вышел к списку опросов", 'red')
                    
                    # Обработка кнопки "Назад"
                    if call.data == 'go_back':
                        if user.guessing:
                            user.guessing = False  # Выход из режима "Угадать ответы друга"
                            print_colored(f"Пользователь {user.nickname} нажал на кнопку \"Назад\" в режиме \"Угадать ответы друга\" и вышел в начальное меню", 'red')
                        elif user.state == 'choosing_survey':
                            user.state = None  # Выход из режима "Пройти опрос"
                            print_colored(f"Пользователь {user.nickname} нажал на кнопку \"Назад\" в режиме \"Пройти опрос\" и вышел в начальное меню", 'red')
                        self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        return
                    
                    # Обработка нажатия на кнопку "Назад" в состоянии создания опроса
                    if call.data == 'go_back_creating':
                        print_colored(f"        Пользователь {user.nickname} нажал кнопку \"Назад\" и вернулся к вводу названия опроса", "red")
                        
                        # Удаление сообщения пользователя
                        try:
                            self.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        except telebot.apihelper.ApiTelegramException as e:
                            print_colored(f"Ошибка удаления сообщения пользователя: {str(e)}", 'red')

                        # Удаление последнего сообщения бота, если оно существует
                        if user.last_bot_message_id:
                            try:
                                self.bot.delete_message(chat_id=call.message.chat.id, message_id=user.last_bot_message_id)
                                user.last_bot_message_id = None
                            except telebot.apihelper.ApiTelegramException as e:
                                print_colored(f"Ошибка удаления последнего сообщения бота: {str(e)}", 'red')

                        # Очистка данных и отправка сообщения
                        user.creating_survey_data = {'title': None, 'questions': []}
                        user.state = 'creating_survey'
                        markup = InlineKeyboardMarkup()
                        markup.add(InlineKeyboardButton("Назад", callback_data='go_back_creating'))
                        sent_msg = self.bot.send_message(call.message.chat.id, "Введите название опроса:", reply_markup=markup)

                        if sent_msg:
                            user.last_bot_message_id = sent_msg.message_id

                        return

        

        def send_survey_list(user):
            """ Отправляет пользователю список доступных опросов """
            markup = InlineKeyboardMarkup()
            for survey_id, survey in surveys.items():
                markup.add(InlineKeyboardButton(survey.title, callback_data='survey_' + survey_id))
            markup.add(InlineKeyboardButton("Назад", callback_data='go_back'))
            self.bot.send_message(user.chat_id, "Выбери опрос:", reply_markup=markup)


        def start_survey(call, user):
            """ Начинает опрос, отправляя первый вопрос пользователю. """
            data_parts = call.data.split(':')
            if len(data_parts) == 3:
                # Это формат из режима "Угадать ответы друга"
                _, _, survey_id = data_parts
            elif len(data_parts) == 1:
                # Это формат из обычного выбора опроса
                survey_id = data_parts[0][len('survey_'):]
            else:
                print_colored("Ошибка: некорректный формат данных в callback.", 'cyan')
                return  # Завершение работы функции, если формат данных не соответствует ожидаемому

            user.current_survey = survey_id
            user.current_question_index = 0

            if user.state == 'guessing_answers':
                # Инициализация хранилища для угадывания
                user.temporary_surveys_guessing[survey_id] = []
                print_colored(f"Инициализировано хранилище для угадывания для {user.nickname} для опроса {survey_id}", 'cyan')
            else:
                # Инициализация временного хранилища для обычного прохождения
                if survey_id not in user.completed_surveys:  # Проверка, проходил ли пользователь опрос ранее
                    user.temporary_surveys[survey_id] = []
                print_colored(f"Инициализировано временное хранилище для {user.nickname} для опроса {survey_id}", 'cyan')
                user.state = 'taking_survey'    

            # Проверка, проходил ли пользователь этот опрос ранее
            if survey_id in user.completed_surveys and user.state != 'guessing_answers':
                user.in_yes_no_choice = True
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("Да", callback_data=f"repeat_survey_yes:{survey_id}"),
                        InlineKeyboardButton("Нет", callback_data="repeat_survey_no"))
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                        text="Ты уже проходил этот опрос. Хочешь еще раз его пройти?", reply_markup=markup)
                return  # Остановка выполнения, ожидание решения пользователя

            # Отправка первого вопроса опроса
            if survey_id in surveys:
                survey = surveys[survey_id]
                question = survey.questions[user.current_question_index]
                total_questions = len(survey.questions)
                markup = InlineKeyboardMarkup()
                for option in question.options:
                    markup.add(InlineKeyboardButton(option, callback_data=f"answer:{survey_id}:{user.current_question_index}:{option}"))
                markup.add(InlineKeyboardButton("Назад", callback_data="back_to_survey_list"))
                formatted_question_text = f"Вопрос 1/{total_questions}: {question.text}"
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=formatted_question_text, reply_markup=markup)
                print_colored(f"Пользователь {user.nickname} начал проходить опрос '{survey.title}'", 'green')




        def handle_answer(call, user):
            """ Обрабатывает ответ пользователя и решает, нужно ли переходить к следующему вопросу или завершать опрос. """
            parts = call.data.split(':')
            survey_id, question_index, selected_option = parts[1], int(parts[2]), parts[3]
            survey = surveys[survey_id]

            # Убедитесь, что используете правильное хранилище в зависимости от состояния пользователя
            if user.state == 'guessing_answers':
                if survey_id not in user.answers_guessing:
                    user.answers_guessing[survey_id] = []
                storage = user.temporary_surveys_guessing 
            else:
                if survey_id not in user.temporary_surveys:
                    user.temporary_surveys[survey_id] = []
                storage = user.temporary_surveys

            # Добавление выбранного варианта ответа в соответствующее хранилище
            storage[survey_id].append((question_index, selected_option))

            # Логирование сохранённого ответа
            print_colored(f"Ответ пользователя {user.nickname} на вопрос {question_index + 1} ('{survey.questions[question_index].text}') сохранен временно: '{selected_option}'", 'blue')
            print_colored(f"            {user.nickname}: Вопрос {question_index + 1}: \"{survey.questions[question_index].text}\" - ответ: \"{selected_option}\"", 'white')
            
            # Переход к следующему вопросу или завершение опроса
            process_next_question(user, survey, survey_id, question_index + 1, call.message.message_id)





        def process_next_question(user, survey, survey_id, question_index, message_id):
            """ Отправляет следующий вопрос или завершает опрос, если вопросы закончились. """
            total_questions = len(survey.questions)  # Получаем общее количество вопросов в опросе
            if question_index < total_questions:
                question = survey.questions[question_index]
                user.current_question_index = question_index
                markup = InlineKeyboardMarkup()
                for option in question.options:
                    markup.add(InlineKeyboardButton(option, callback_data=f"answer:{survey_id}:{question_index}:{option}"))
                # Добавление кнопки "Назад" для последующих вопросов
                markup.add(InlineKeyboardButton("Назад", callback_data="go_back_question"))
                # Форматирование текста вопроса с номером вопроса и общим количеством вопросов
                formatted_question_text = f"Вопрос {question_index + 1}/{total_questions}: {question.text}"
                self.bot.edit_message_text(chat_id=user.chat_id, message_id=message_id, text=formatted_question_text, reply_markup=markup)
            else:
                # Опрос завершен, обработка результатов
                if user.state == 'guessing_answers':
                    # Упрощённое условие для переноса ответов
                    if survey_id in user.temporary_surveys_guessing:
                        user.answers_guessing[survey_id] = user.temporary_surveys_guessing[survey_id]
                        user.temporary_surveys_guessing.pop(survey_id, None)
                    # Вывод отладки для угадывания
                    debug_answers_guessing(user, survey_id)

                    # Извлечение имени друга и названия опроса
                    friend_nickname = user.guessing_survey.split(':')[1]
                    survey_title = surveys[survey_id].title
                    
                    friend_user = self.users.get(friend_nickname)

                    # Вызов функции для подсчета результата и отправки сообщений
                    calculate_and_send_guessing_results(user, survey_id, friend_user)  # <-- Добавлено
                    
                    # Формирование нового текста сообщения
                    new_text = f"Ваши догадки на опрос '{survey_title}' от пользователя '{friend_nickname}' сохранены"

                    # Отправка сообщения с новым текстом
                    self.bot.edit_message_text(chat_id=user.chat_id, message_id=message_id, text=new_text)

                    user.guessing = False  # Выход из режима угадывания
                    user.state = None  # Перевод пользователя в начальное меню
                    print_colored(f"Пользователь {user.nickname} вернулся в начальное меню", "green")
                else:
                    # Обработка завершения обычного опроса
                    if survey_id in user.temporary_surveys and user.temporary_surveys[survey_id]:
                        user.completed_surveys[survey_id] = user.temporary_surveys[survey_id]
                        print_colored(f"Ответы пользователя {user.nickname} на опрос {survey.title} обновлены и сохранены.", 'cyan')
                        user.temporary_surveys.pop(survey_id, None)
                    else:
                        print_colored(f"Нет временных ответов для сохранения для пользователя {user.nickname}.", 'red')
                    # Вывод отладочной информации о сохраненных ответах
                    if survey_id in user.completed_surveys:
                        print_colored(f"Реальные ответы пользователя {user.nickname} на опрос {survey.title} доступны для проверки.", 'green')
                    else:
                        print_colored(f"Реальные ответы пользователя {user.nickname} на опрос {survey.title} не найдены.", 'red')
                    # Вывод отладки для обычного прохождения опроса
                    debug_survey_completion(user, survey_id)
                    print_colored(f"Содержимое completed_surveys для {user.nickname}: {user.completed_surveys}", "purple")  # <-- Добавлено отладочное сообщение

                    # Очистка состояния пользователя
                    self.bot.edit_message_text(chat_id=user.chat_id, message_id=message_id, text=f"Ваши ответы на {survey.title} сохранены.")
                    user.current_survey = None
                    user.current_question_index = 0
                    user.state = None
                    print_colored(f"Пользователь {user.nickname} завершил прохождение опроса {survey.title}.", 'green')


        def debug_answers_guessing(user, survey_id):
            """ Вывод угаданных и реальных ответов. """
            guessing_answers = user.answers_guessing.get(survey_id, [])
            print_colored(f"Значение guessing_survey: {user.guessing_survey}", "red")
            friend_nickname = user.guessing_survey.split(':')[1] # Извлечение имени друга из guessing_survey
            friend_user = self.users.get(friend_nickname)
            print_colored(f"Содержимое completed_surveys для {friend_user.nickname}: {friend_user.completed_surveys}", "purple")  # <-- Добавлено отладочное сообщение
            real_answers = friend_user.completed_surveys.get(survey_id, [])  # Получение реальных ответов друга
            print_colored("Угаданные ответы:", 'purple')
            for index, (q_index, guessed_answer) in enumerate(guessing_answers):
                question_text = surveys[survey_id].questions[q_index].text
                print_colored(f"Вопрос {index + 1}: {question_text} - Угадан ответ: {guessed_answer}", 'cyan')
            print_colored("Реальные ответы:", 'blue')
            if real_answers:
                for index, (q_index, real_answer) in enumerate(real_answers):
                    question_text = surveys[survey_id].questions[q_index].text
                    print_colored(f"Вопрос {index + 1}: {question_text} - Реальный ответ: {real_answer}", 'green')
            else:
                print_colored("Реальные ответы не найдены.", 'red')





        def debug_survey_completion(user, survey_id):
            """ Выводит в отладку информацию об опросах, которые прошел пользователь, и его ответах. """
            response_log = ""  # Инициализация переменной
            completed_survey_info = user.completed_surveys.get(survey_id, [])
            for question_index, answer in completed_survey_info:
                question_text = surveys[survey_id].questions[question_index].text
                response_log += f"{user.nickname}: \"{question_text}\" - ответ: \"{answer}\"\n"
            print_colored(response_log, 'cyan')

        def calculate_and_send_guessing_results(user, survey_id, friend_user):
            print_colored(f"        Функция calculate_and_send_guessing_results запущена для пользователя {user.nickname}", "cyan")
            guessing_answers = user.answers_guessing.get(survey_id, [])
            real_answers = friend_user.completed_surveys.get(survey_id, [])
            correct_answers = sum(1 for guess, real in zip(guessing_answers, real_answers) if guess[1] == real[1])
            total_questions = len(real_answers)
            percentage = 0
            if total_questions > 0:
                percentage = round((correct_answers / total_questions) * 100)
            
            print_colored(f"        Процент угаданных ответов: {percentage}%", "cyan")

            user_message_text = f"Вы угадали {percentage}% всех вопросов из теста '{surveys[survey_id].title}' от пользователя '{friend_user.nickname}'\n\n"
            friend_message_text = f"'{user.nickname}' прошел ваш тест '{surveys[survey_id].title}' на {percentage}%\n\n"

            friend_message_text += f"Ваши ответы:\n"
            user_message_text += f"Ответы {friend_user.nickname}:\n"
            for index, (question_index, answer) in enumerate(real_answers):
                question_text = surveys[survey_id].questions[question_index].text
                user_message_text += f"{index + 1}. \"{question_text}\" - {answer}\n"
                friend_message_text += f"{index + 1}. \"{question_text}\" - {answer}\n"

            friend_message_text += f"\nОтветы {user.nickname}:\n"
            user_message_text += f"\nВаши ответы:\n"
            for index, (question_index, answer) in enumerate(guessing_answers):
                question_text = surveys[survey_id].questions[question_index].text
                user_message_text += f"{index + 1}. \"{question_text}\" - {answer}\n"
                friend_message_text += f"{index + 1}. \"{question_text}\" - {answer}\n"

            self.bot.send_message(user.chat_id, user_message_text)
            self.bot.send_message(friend_user.chat_id, friend_message_text)

    def run(self):
        self.bot.polling()  # Запуск бота для обработки сообщений




# Настройки и запуск бота
if __name__ == "__main__":
    TOKEN = '7075209422:AAFYS_VK1KpEmoV_XMMcxwOAnWryPRltOgw'
    survey_bot = SurveyBot(TOKEN)
    survey_bot.run()
