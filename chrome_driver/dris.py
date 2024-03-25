import time
import os
import telebot
import string
import re
import logging
import random
import multiprocessing
from telebot.types import Message
from telebot import types
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from DrissionPage.common import Keys
from dotenv import load_dotenv
from data import proxy

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
    pattern = r'^([A-Z][a-z]+)\s\d{1,2},\s\d{2},\s([A-Z][a-z]+)\s\d{1,2},\s\d{2}$'
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

    bot.register_next_step_handler(message, start_process, user_data)


@bot.message_handler(commands=['setting_date'])
def start_setting_date(message):
    change_date_for_user(message)


def change_date_for_user(message):
    if users:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for user in users:
            button = types.InlineKeyboardButton(text=user, callback_data=user)
            keyboard.add(button)
        bot.send_message(message.chat.id, 'Отправьте username для которого вы хотите изменить дату',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Сейчас нет активных пользователей, /help')


@bot.callback_query_handler(func=lambda call: True)
def process_username_input(call):
    user_id = call.message.chat.id
    if user_id in searching_user and searching_user[user_id]:
        username = call.data
        if username in date_for_users:
            bot.send_message(user_id, 'Укажите диапазон даты для записи (Формат: May 12, 24)')
            bot.register_next_step_handler(call.message, process_date_input, username)
        else:
            bot.send_message(user_id, 'Пользователь с таким username не найден')


def process_date_input(message, username):
    user_id = message.chat.id
    if user_id in searching_user and searching_user[user_id]:
        if check_date_format(message.text):
            user_date = message.text
            date_for_users[username] = user_date
            bot.send_message(user_id, f'Дата успешно изменена для пользователя {username}')
        else:
            bot.send_message(user_id, 'Неверный формат даты. Пожалуйста, введите дату в формате May 12, 24')
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
        return


def input_authorization(driver: ChromiumPage, user_data: dict):
    """
    Авторизация аккаунта
    :param driver:
    :param user_data:
    :return:
    """
    driver.wait.ele_loaded('#id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input.input(user_data['login'])

    password_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    password_input.input(user_data['password'])

    driver.actions.click('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')

    driver.actions.type(Keys.ENTER)


def check_cloudflare(driver: ChromiumPage):
    """
    Проверка cloudflare
    :param driver: объект класса ChromiumPage
    :return:
    """
    try:
        driver.wait.ele_loaded('#allow:cross-origin-isolated')
        test = driver.ele('@allow:cross-origin-isolated').ele('@class:ctp-checkbox-label')
        driver.wait.ele_loaded('#class:mark')
        button = test.ele('@class:mark')
        button.click()
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


def get_list_date(date: dict, user_data: dict) -> list:
    """
    Функция для формирования саиска с датой пользователя
    :param date: словарь date_for_user
    :param user_data: словарь с данными пользователя
    """
    date_user = date[user_data['username']].replace(',', '').split(' ')
    return date_user


def check_available_date(date_users: dict, driver: ChromiumPage(), user_data, message) -> bool:
    """
    Проверяем соответствие первой открытой даты диапазону дат пользователя
    :date_users: global dict(date_for_users)
    :driver: objects browser
    """

    while True:
        try:
            driver.wait.ele_loaded('#class:leftPanelText')
            give_date = driver.ele('@class:leftPanelText').text
            logging.info(f'{give_date}')
            date = give_date.translate(str.maketrans('', '', string.punctuation))
            date_list = date.split(' ')

            date_user = get_list_date(date_users, user_data)
            start_day, end_day = int(date_user[1]), int(date_user[2]) + 1  # Первая дата
            start, end = int(date_user[4]), int(date_user[5]) + 1  # Вторая дата
            # Проверка, что обе даты присутствуют в списке
            if date_list[5] == date_user[0] and start_day <= int(date_list[6]) <= end_day:
                logging.info(f"Отслежена дата для {user_data['username']} на {date_user[0]}")
                return True
            elif date_list[5] == date_user[3] and start <= int(date_list[6]) <= end:
                logging.info(f"Отслежена дата для {user_data['username']} на {date_user[3]}")
                return True
            else:
                offset_x = random.randint(300, 500)
                offset_y = random.randint(250, 300)
                cont = random.randint(1, 3)
                driver.actions.move(offset_x=offset_x, offset_y=offset_y, duration=cont)
                driver.actions.up(random.randint(20, 50))
                driver.actions.db_click()

                user = random.choice(list(users.values()))
                user.actions.type(Keys.F5)
                time.sleep(random.randint(32, 50))
        except Exception as error:
            logging.error(f"В функции check_available_date - {error}")
            action_finally(driver, user_data)
            record_in_date(message, user_data)


def page_calendar(driver: ChromiumPage):
    """
    Переход на страницу с календарём
    :param driver:
    :return:
    """
    driver.wait.ele_loaded('#href:/selectvisapriority')
    driver.actions.click('@href:/selectvisapriority')

    driver.wait.ele_loaded('#id:j_id0:SiteTemplate:theForm:SelectedVisaPriority:0')
    driver.actions.click('@id:j_id0:SiteTemplate:theForm:SelectedVisaPriority:0')

    driver.actions.click('@name:j_id0:SiteTemplate:theForm:j_id170')

    driver.wait.ele_loaded('@class:ui-datepicker-group ui-datepicker-group-first')


def record_in_first_date(driver: ChromiumPage, user_data: dict, message: Message) -> bool:
    """
    Проврка наличия свободных мест на выделеной дате
    :param driver:
    :param user_data:
    :param message:
    :return:
    """
    date = get_list_date(date_for_users, user_data)
    month_user = {date[0], date[3]}
    first_month = driver.ele('@class:ui-datepicker-group ui-datepicker-group-first')
    month_calendar = first_month.ele('@class:ui-datepicker-month').text

    if month_calendar not in month_user:
        driver.actions.click('tag:a@href:/ApplicantHome')
        check_available_date(date_for_users, driver, user_data, message)
        return False

    available = driver.ele('@id:thePage:SiteTemplate:theForm:calendarTableMessage')
    free_space = available.ele('tag:td', index=8).text
    free_date = available.ele('tag:td', index=7).text

    if free_space >= user_data['applicants']:
        driver.actions.click('tag:input@type:checkbox')
        parent_ele = driver.ele('tag:span@id:thePage:SiteTemplate:theForm:calendarTableMessage')
        schedule_button = parent_ele.ele('tag:input@id:thePage:SiteTemplate:theForm:addItem')
        # schedule_button.click()
        logging.info('Нажата кнопка записи в first_date')
        name = user_data['username']
        bot.send_message(message.chat.id, f"{name} был записан на {free_date}")
        logging.info(f'{name} был записан на {free_date}')
        return True
    else:
        record_in_next_date(driver, message, user_data)


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

    need_date = get_list_date(date_for_users, user_data)
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
                                # schedule_button.click()
                                logging.info('Нажата кнопка записи в next_date')
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
    del date_for_users[username]
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
        get_options_date(user_data)  # Словарь {'username': 'date'}
        username = user_data['username']
        options = ChromiumOptions().auto_port(True)
        options.set_proxy(random.choice(proxy))
        users[username] = ChromiumPage(options)
        users[username].get(url=url)  # Получаем страницу авторизации
        input_authorization(users[username], user_data)  # Ввод данных авторизации, нажимаем кнопку войти
        check_cloudflare(users[username])  # Проверка cloudflare
        if check_available_date(date_for_users, users[username], user_data, message):
            page_calendar(users[username])  # Переходим на страницу с календарём свободных дат
            if record_in_first_date(users[username], user_data, message):  # Если первая дата подходит по критериям
                action_finally(users[username], user_data)
    except Exception as error:
        logging.error(f"Ошибка при выполнении record_in_data - {error}")
        username = user_data['username']
        action_finally(users[username], user_data)
        record_in_date(message, user_data)


def start_process(message, user_data):
    user_data['applicants'] = message.text
    p = multiprocessing.Process(target=record_in_date, args=(message, user_data))
    p.start()
    p.join()


def main():
    try:
        bot.polling(none_stop=True)
    except Exception as error:
        logging.error(f'{error}')
        main()


if __name__ == '__main__':
    main()
