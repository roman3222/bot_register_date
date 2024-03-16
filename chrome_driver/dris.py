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
    bot.send_message(message.chat.id, 'Укажите диапазон даты для записи(Формат: May 12,24)')
    bot.register_next_step_handler(message, def_get_username, user_data)


def check_date_format(date_string):
    pattern = r'^[A-Z][a-z]+\s+\d+,\d+$'
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
    time.sleep(4)


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
    # ('@class:ui-datepicker-calendar')
    for i in driver.eles('@class:ui-datepicker-month'):
        for date in driver.eles('tag:td@onclick'):
            fir_date = date('tag:a').text
            available_date[i.text] = fir_date
            print(available_date)


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
    page_calendar(users[username])  # Переходим на страницу с календарём свободных дат
    get_first_available_date(users[username])  # Получаем информацию о ближайшей открытой дате
    get_calendar_date(users[username])
    start_time = time.time()
    end_time = time.time()
    print()
    print(start_time - end_time)
    # print(users)
    # print(queue_users)
    # print(user_data)
    # print(date_for_users)


def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
