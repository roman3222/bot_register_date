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
    bot.register_next_step_handler(message, authorization, user_data)


def generate_random_filename(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def create_session():
    driver = ChromiumPage()
    return driver


def authorization(message, user_data):
    user_data['date'] = message.text

    driver = create_session()

    driver.get(url=url)
    time.sleep(40)

    login_input = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input.input(user_data['login'])
    time.sleep(4)

    password_input = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    password_input.input(user_data['password'])
    time.sleep(5)

    agree_button = driver.ele('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
    agree_button.click()
    time.sleep(4)

    login_button = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton')
    login_button.click()
    time.sleep(25)

    # file_name = generate_random_filename() + '.png'
    # driver.get_screenshot('/home/roman/projects/visa_bot_record/screen', file_name)
    try:
        test = driver.ele('@allow:cross-origin-isolated').ele('@class:ctp-checkbox-label')
        button = test.ele('@class:mark')
        button.click()
        time.sleep(13)
    except ElementNotFoundError as error:
        print(f'Элемент не найден:{error}')

    # give_date = driver.ele('@class:leftPanelText')
    # time.sleep(12)
    # date = give_date.text
    # date.replace(',', '')

    continue_button = driver.ele('@href:/selectvisapriority')
    continue_button.click()
    time.sleep(13)

    give_date = driver.ele('@class:leftPanelText')
    time.sleep(4)
    date = give_date.text
    date.replace(',', '')
    print(date)

    # avalaible_date = driver.ele()
    # bot.register_next_step_handler(message, tracking_date, user_data, driver, date)


# def tracking_date(message, user_data, driver, date):
#     driver.click_element('a[href="/selectvisapriority"]')
#     time.sleep(13)
#     print(date)
#     print(user_data)

def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
