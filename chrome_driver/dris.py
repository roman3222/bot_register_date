import time
import os
import telebot
import string
import random
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('token'))

url = 'https://portal.ustraveldocs.com'

driver = {}


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
    bot.send_message(message.chat.id, 'Укажите диапазон даты для записи(Формат: March 1,10)')
    bot.register_next_step_handler(message, record_in_date, user_data)


def def_get_username(message):
    global driver

    driver['username'] = message.text


def get_applicants(message):
    global driver

    driver['applicants'] = message.text



def create_session():
    # driver = ChromiumPage()
    # return driver


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
    date.replace(',', '')
    print(date)


def record_in_date(message, user_data):
    """
    Отслеживание и запись на свободную дату
    :param message:
    :param user_data:
    :return:
    """
    start_time = time.time()

    user_data['date'] = message.text

    driver = create_session()

    driver.get(url=url)
    # driver.wait(1)

    input_authorization(driver, user_data)

    check_cloudflare(driver)

    page_calendar(driver)

    get_first_available_date(driver)

    end_time = time.time()

    print(start_time - end_time)


def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
