import time
import os
import telebot
import string
import re
import threading
import logging
from telebot.types import Message
from telebot import types
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from dotenv import load_dotenv

logging.basicConfig(filename='logger/bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

bot = telebot.TeleBot(os.getenv('token'))

url = 'https://portal.ustraveldocs.com'

users = {}

date_for_users = {}

check_date = []

searching_user = {}


@bot.message_handler(commands=['start'])
def get_login(message):
    bot.send_message(message.chat.id, f'Укажите адрес электронной почты для авторизации')
    bot.register_next_step_handler(message, get_password)


def get_password(message):
    user_data = {'login': message.text}
    bot.send_message(message.chat.id, f'Укажите пароль')
    bot.register_next_step_handler(message, get_date_range, user_data)


@bot.message_handler(commands=['help'])
def get_help(message: Message):
    bot.send_message(
        message.chat.id,
        '/start - Старт бота\n/setting_date - Изменить дату для пользователя\n/show_active_users - '
        'Просмотр активных пользователей'
    )


def get_date_range(message, user_data):
    user_data['password'] = message.text
    bot.send_message(message.chat.id, 'Укажите диапазон даты для записи(Формат: May 12, 24)')
    bot.register_next_step_handler(message, def_get_username, user_data)


def check_date_format(date_string):
    pattern = r'^[A-Z][a-z]+\s\d{1,2},\s\d{2}$'
    return re.match(pattern, date_string) is not None


def def_get_username(message, user_data):
    if check_date_format(message.text):
        user_data['date'] = message.text  # Обновляем данные в user_data
        bot.send_message(message.chat.id, 'Укажите никнейм пользователя')
        bot.register_next_step_handler(message, get_applicants, user_data)
    else:
        bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, введите дату в формате May 12,24')
        bot.register_next_step_handler(message, def_get_username, user_data)  # Повторный ввод даты здесь


def get_applicants(message, user_data):
    bot.send_message(message.chat.id, 'Укажите колличество заявителей в аккаунте')
    user_data['username'] = message.text

    bot.register_next_step_handler(message, start_record_in_date_thread, user_data)


@bot.message_handler(commands=['setting_date'])
def change_date_for_user(message):
    if users:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for user in users:
            button = types.InlineKeyboardButton(text=user, callback_data=user)
            keyboard.add(button)
        bot.send_message(message.chat.id, 'Оправьте username для которого вы хотите изменить дату',
                         reply_markup=keyboard)
        searching_user[message.chat.id] = True
    else:
        bot.send_message(message.chat.id, 'Сейчас нет активных пользователей, /help')

    def process_username_input(username_message: Message):
        """
        Проверка наличия пользователя и формата даты
        :return:
        """
        user_id = username_message.chat.id
        if user_id in searching_user and searching_user[user_id]:
            username = username_message.text
            if username in date_for_users:
                bot.send_message(message.chat.id, 'Укажите диапазон даты для записи(Формат: May 12, 24)')
                bot.register_next_step_handler(username_message, process_date_input, username)
            else:
                bot.send_message(message.chat.id, 'Пользователь с таким username не найден')
                bot.register_next_step_handler(username_message, process_username_input)
            searching_user[user_id] = False

        bot.register_next_step_handler(message, process_username_input)


def process_date_input(message: Message, username: str):
    """
    Проверка и изменение даты для пользователя
    :return:
    """
    user_id = message.chat.id
    if user_id in searching_user and searching_user[user_id]:
        if check_date_format(message.text):
            user_date = message.text
            date_for_users[username] = user_date
            print(date_for_users)
        else:
            bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, введите дату в формате May 12, 24')
            bot.register_next_step_handler(message, process_date_input, username)


@bot.message_handler(commands=['show_active_users'])
def get_active_users(message: Message):
    if users:
        for user in users.keys():
            bot.send_message(
                message.chat.id,
                f'{user}\n'
            )
    else:
        bot.send_message(message.chat.id, 'Сейчас нет активных пользователей /help')


def input_authorization(driver: ChromiumPage, user_data: dict):
    """
    Авторизация аккаунта
    :param driver:
    :param user_data:
    :return:
    """
    login_input = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input.input(user_data['login'])
    time.sleep(1)

    password_input = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    password_input.input(user_data['password'])
    time.sleep(1)

    agree_button = driver.ele('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
    agree_button.click()
    time.sleep(1)

    login_button = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton')
    login_button.click()
    driver.wait.ele_loaded('#cross-origin-isolated')


def check_cloudflare(driver: ChromiumPage):
    """
    Проверка cloudflare
    :param driver: объект класса ChromiumPage
    :return:
    """
    try:
        test = driver.ele('@allow:cross-origin-isolated').ele('@class:ctp-checkbox-label', timeout=3)
        button = test.ele('@class:mark')
        button.click()
        driver.wait.ele_loaded('@class:leftPanelText')
    except ElementNotFoundError as error:
        logging.info(f"Проверки не было - {error}")


def get_options_date(user_data: dict):
    """
    Функция для записи диапазона дат для аккаунтов
    :param user_data:
    :return:
    """
    global date_for_users

    date_for_users[user_data['username']] = user_data['date']


def check_available_date(date_users: dict, driver: ChromiumPage(), user_data, message) -> bool:
    """
    Проверяем соответствие первой открытой даты диапазону дат пользователя
    :date_users: global dict(date_for_users)
    :driver: objects browser
    """
    if driver.ele('@class:leftPanelText') is None:
        bot.send_message(
            message.chat.id,
            f"Не правильно указан логин или пароль нажмите /start для повторного входа({user_data['username']})"
        )
        driver.quit()
        del users[user_data['username']]

    while True:
        try:
            give_date = driver.ele('@class:leftPanelText')
            logging.info(f"Успешная авторизация для {user_data['username']}")
            date = give_date.text
            date = date.translate(str.maketrans('', '', string.punctuation))
            date_list = date.split(' ')

            date_user = date_users[user_data['username']].replace(',', '').split(' ')
            start_day, end_day = int(date_user[1]), int(date_user[2]) + 1
            # Проверка, что обе даты присутствуют в списке
            if date_list[5] in date_user and start_day <= int(date_list[6]) <= end_day:
                return True
            else:
                time.sleep(3)
                driver.refresh()
        except Exception as error:
            logging.error(f"Ошибка в check_available_date - {error}")
            driver.quit()
            del users[user_data['username']]
            bot.register_next_step_handler(message, get_login)
            break

    return False


def page_calendar(driver: ChromiumPage):
    """
    Переход на страницу с календарём
    :param driver:
    :return:
    """
    schedule_page = driver.ele('@href:/selectvisapriority')
    schedule_page.click()
    time.sleep(3)

    status_resident = driver.ele('@id:j_id0:SiteTemplate:theForm:SelectedVisaPriority:0')
    status_resident.click()

    continue_button = driver.ele('@name:j_id0:SiteTemplate:theForm:j_id170')
    continue_button.click()
    driver.wait.ele_loaded('@class:ui-datepicker-group ui-datepicker-group-first')


def record_in_first_date(driver: ChromiumPage, user_data: dict, message: Message) -> bool:
    available = driver.ele('@id:thePage:SiteTemplate:theForm:calendarTableMessage')
    free_space = available.ele('tag:td', index=8)
    free_date = available.ele('tag:td', index=7).text

    if free_space.text >= user_data['applicants']:
        box = driver.ele('tag:input@type:checkbox')
        box.click()
        parent_ele = driver.ele('tag:span@id:thePage:SiteTemplate:theForm:calendarTableMessage')
        schedule_button = parent_ele.ele('tag:input@id:thePage:SiteTemplate:theForm:addItem')
        name = user_data['username']
        bot.send_message(message.chat.id, f"{name} был записан на {free_date}")
        logging.info(f'{name} был записан')
        return True

    return False


def record_in_next_date(driver: ChromiumPage, message, user_data: dict):
    """
    Функция для получения всех свободных дат
    :return:
    """
    global check_date

    lst_class = [
        driver.ele('@class:ui-datepicker-group ui-datepicker-group-first'),
        driver.ele('@class:ui-datepicker-group ui-datepicker-group-middle'),
        driver.ele('@class:ui-datepicker-group ui-datepicker-group-last'),
    ]

    need_date = date_for_users[user_data['username']].replace(',', '').split(' ')
    num_date = [num for num in range(int(need_date[1]), int(need_date[2]) + 1)]

    try:
        should_break = False
        for lst in lst_class:
            month = lst.ele('@class:ui-datepicker-month').text
            if month in need_date:
                for day in lst.eles('tag:a@href'):
                    need_day = day.text
                    if need_day not in check_date:
                        check_date.append(need_day)
                        if int(need_day) in num_date:
                            day.click()
                            time.sleep(2)
                            mather = driver.ele('@id:thePage:SiteTemplate:theForm:calendarTableMessage')
                            date = mather.ele('tag:td', index=8)
                            if int(date.text) >= int(user_data['applicants']):
                                box = driver.ele('tag:input@type:checkbox')
                                box.click()
                                check_date.clear()
                                parent_ele = driver.ele('tag:span@id:thePage:SiteTemplate:theForm:calendarTableMessage')
                                schedule_button = parent_ele.ele('tag:input@id:thePage:SiteTemplate:theForm:addItem')
                                name = user_data['username']
                                bot.send_message(
                                    message.chat.id,
                                    f"{name} был записан на {month} - {need_day}"
                                )
                                logging.info(f'{name} - был записан')
                                should_break = True
                                break
            if should_break:
                break
    except Exception as error:
        logging.error(f"Ошибка при выполнении record_in_next_data - {error}")
        record_in_next_date(driver, message, user_data)


def action_finally(driver: ChromiumPage, user_data: dict):
    driver.quit()
    username = user_data['username']
    del users[username]


def record_in_date(message, user_data):
    """
    Отслеживание и запись на свободную дату
    :param message: объект Message
    :param user_data: словарь с данными пользователя
    :return:
    """
    global users

    try:
        user_data['applicants'] = message.text
        get_options_date(user_data)  # Словарь {'username': 'date'}
        username = user_data['username']
        options = ChromiumOptions().auto_port()
        users[username] = ChromiumPage(options)
        users[username].get(url=url)  # Получаем страницу авторизации
        input_authorization(users[username], user_data)  # Ввод данных авторизации, нажимаем кнопку войти
        check_cloudflare(users[username])  # Проверка cloudflare
        if check_available_date(date_for_users, users[username], user_data, message):
            users[username].wait.ele_loaded('/selectvisapriority')
            page_calendar(users[username])  # Переходим на страницу с календарём свободных дат
            if record_in_first_date(users[username], user_data, message):
                action_finally(users[username], user_data)
                print(users)
            else:
                record_in_next_date(users[username], message, user_data)
                action_finally(users[username], user_data)
    except Exception as error:
        logging.error(f"Ошибка при выполнении record_in_data - {error}")
        username = user_data['username']
        users[username].quit()
        del users[username]
        record_in_date(message, user_data)


def start_record_in_date_thread(message: Message, user_data: dict):
    """
    Запуск record_in_date в отдельном потоке
    :param message: объект Message
    :param user_data: словарь с данными пользователя
    :return:
    """
    threading.Thread(target=record_in_date, args=(message, user_data)).start()


def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
