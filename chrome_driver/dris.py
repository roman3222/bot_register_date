import time
import os
import telebot
import string
import re
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('token'))

url = 'https://portal.ustraveldocs.com'

users = {}

queue_users = []

date_for_users = {}


@bot.message_handler(commands=['start'])
def get_login(message):
    bot.send_message(message.chat.id, f'Укажите адрес электронной почты для авторизации')
    bot.register_next_step_handler(message, get_password)


def get_password(message):
    user_data = {'login': message.text}
    bot.send_message(message.chat.id, f'Укажите пароль')
    bot.register_next_step_handler(message, get_date_range, user_data)


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
    global queue_users
    bot.send_message(message.chat.id, 'Укажите колличество заявителей в аккаунте')
    user_data['username'] = message.text

    bot.register_next_step_handler(message, record_in_date, user_data)


@bot.message_handler(commands=['setting_date'])
def change_date_for_user(message):
    bot.send_message(message.chat.id, 'Оправьте username для которого вы хотите изменить дату')

    def process_username_input(username_message):
        username = username_message.text
        if username in date_for_users:
            bot.send_message(message.chat.id, 'Укажите диапазон даты для записи(Формат: May 12, 24)')
            bot.register_next_step_handler(username_message, process_date_input, username)
        else:
            bot.send_message(message.chat.id, 'Пользователь с таким username не найден')
            bot.register_next_step_handler(username_message, process_username_input)

    bot.register_next_step_handler(message, process_username_input)


def process_date_input(message, username):
    if check_date_format(message.text):
        user_date = message.text
        date_for_users[username] = user_date
        print(date_for_users)
    else:
        bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, введите дату в формате May 12, 24')
        bot.register_next_step_handler(message, process_date_input, username)


def input_authorization(driver, user_data):
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


def check_cloudflare(driver):
    """
    Проверка cloudflare
    :param driver:
    :return:
    """
    try:
        test = driver.ele('@allow:cross-origin-isolated').ele('@class:ctp-checkbox-label')
        button = test.ele('@class:mark')
        button.click()
        driver.wait.ele_loaded('#/selectvisapriority')
    except ElementNotFoundError as error:
        print(f'Элемент не найден:{error}')


def get_first_available_date(driver):
    """
    Получаем ближайшую свободную дату
    :param driver:
    :return:
    """

    give_date = driver.ele('@class:leftPanelText')
    time.sleep(4)
    date = give_date.text
    date = date.translate(str.maketrans('', '', string.punctuation))
    date_list = date.split(' ')
    return date_list


def page_calendar(driver):
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


def get_options_date(user_data):
    """
    Функция для записи диапазона дат для аккаунтов
    :param user_data:
    :return:
    """
    global date_for_users

    date_for_users[user_data['username']] = user_data['date']


def get_calendar_date(driver):
    """
    Функция для получения всех свободных дат
    :return:
    """
    available_date = {}
    lst_class = [
        driver.eles('@class:ui-datepicker-group ui-datepicker-group-first'),
        driver.eles('@class:ui-datepicker-group ui-datepicker-group-middle'),
        driver.eles('@class:ui-datepicker-group ui-datepicker-group-last')
    ]

    for lst in lst_class:
        for first in lst:
            month = first('@class:ui-datepicker-month').text
            for ava_day in first.eles('tag:td@onclick'):
                day = ava_day('tag:a').text
                if month not in available_date:
                    available_date[month] = []
                available_date[month].append(day)
    print(available_date)


def check_available_date(date: dict, driver: ChromiumPage(), user_data: dict) -> bool:
    """
    Функция для проверки соответствия открытой дате на сайте нужной дате для пользователя
    :param date: Словарь date_for_users
    :param driver: объект ChromiumPage
    :param user_data:
    :return:
    """
    first_date = get_first_available_date(driver)

    date_user = date[user_data['username']].replace(',', '').split(' ')
    start_day, end_day = int(date_user[1]), int(date_user[2]) + 1

    # Проверка, что обе даты присутствуют в списке
    if first_date[5] in date_user and start_day <= int(first_date[6]) <= end_day:
        return True
    else:
        return False


def record_in_date(message, user_data):
    """
    Отслеживание и запись на свободную дату
    :param message:
    :param user_data:
    :return:
    """
    global users
    global queue_users

    user_data['applicants'] = message.text
    get_options_date(user_data)  # Словарь {'username': 'date'}
    # Формируем список для очереди аккаунтов
    queue_users.append({'username': user_data['username'], 'applicants': user_data['applicants']})
    username = user_data['username']
    options = ChromiumOptions().auto_port()
    users[username] = ChromiumPage(options)
    users[username].get(url=url)  # Получаем страницу авторизации
    input_authorization(users[username], user_data)  # Ввод данных авторизации, нажимаем кнопку войти
    check_cloudflare(users[username])  # Проверка cloudflare
    # page_calendar(users[username])  # Переходим на страницу с календарём свободных дат
    # get_calendar_date(users[username])
    if check_available_date(date_for_users, users[username], user_data):
        print('Найдено соответствие')


def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
