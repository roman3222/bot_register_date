import time
import os
import telebot
import string
import re
import logging
import random
import multiprocessing
from data import proxy
from telebot import types
from multiprocessing import Manager
from telebot.types import Message
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from DrissionPage.common import Keys
from dotenv import load_dotenv

logging.basicConfig(filename='logger/bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

bot = telebot.TeleBot(os.getenv('token'))

url = 'https://portal.ustraveldocs.com'

manager = Manager()

users = {}

date_for_users = manager.dict()

check_date = []

months_list = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

lock_browser = multiprocessing.Lock()

next_step_signal = multiprocessing.Event()


@bot.message_handler(commands=['start'])
def get_login(message):
    user_id = os.getenv('developer_id')
    if message.from_user.id == int(user_id):
        bot.send_message(message.chat.id, f'Укажите адрес электронной почты для авторизации')
        bot.register_next_step_handler(message, get_password)


def cancel_act(message):
    if message.text == '/cancel':
        return True


def get_password(message):
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    else:
        user_data = {'login': message.text}
        bot.send_message(message.chat.id, f'Укажите пароль')
        bot.register_next_step_handler(message, get_date_range, user_data)


@bot.message_handler(commands=['help'])
def get_help(message: Message):
    user_id = os.getenv('developer_id')
    if message.from_user.id == int(user_id):
        bot.send_message(
            message.chat.id,
            '/start - Старт бота\n/change_date - Изменить дату для пользователя\n/show_active_users - '
            'Просмотр активных пользователей\n/menu - Меню с командами'
        )


def get_date_range(message, user_data):
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    else:
        user_data['password'] = message.text
        bot.send_message(message.chat.id, 'Укажите диапазон даты для записи(Формат: May 12, 24)')
        bot.register_next_step_handler(message, get_username, user_data)


def check_date_format(date_string):
    pattern = r'^([A-Z][a-z]+)\s\d{1,2},\s\d{2},\s([A-Z][a-z]+)\s\d{1,2},\s\d{2}$'
    for month in months_list:
        if re.match(pattern, date_string) is not None and month in date_string:
            return True


def check_string(text):
    lst_string = text.replace(',', '').split(' ')
    set_months = {lst_string[0], lst_string[3]}
    count = 0
    for month in months_list:
        if month in set_months:
            count += 1
            if count == 2:
                return True


def get_username(message, user_data):
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    elif check_date_format(message.text) and check_string(message.text):
        user_data['date'] = message.text  # Обновляем данные в user_data
        bot.send_message(message.chat.id, 'Укажите никнейм пользователя')
        bot.register_next_step_handler(message, get_applicants, user_data)
    else:
        bot.send_message(
            message.chat.id,
            'Неверный формат даты. Пожалуйста, введите дату в формате May 12, 24, June 1, 21'
        )
        bot.register_next_step_handler(message, get_username, user_data)  # Повторный ввод даты здесь


def get_applicants(message, user_data):
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    else:
        bot.send_message(message.chat.id, 'Укажите колличество заявителей в аккаунте')
        user_data['username'] = message.text
        bot.register_next_step_handler(message, get_middle, user_data, 'start')


@bot.message_handler(commands=['show_active_users'])
def get_active_users(message: Message):
    user_id = os.getenv('developer_id')
    if message.from_user.id == int(user_id):
        for user, date in date_for_users.items():
            bot.send_message(
                message.chat.id,
                f'{user} - {date}\n'
            )


@bot.message_handler(commands=['file'])
def get_log_file(message):
    user_id = os.getenv('developer_id')
    if message.from_user.id == int(user_id):
        file = 'logger/bot.log'
        with open(file, 'rb') as f:
            bot.send_document(user_id, f)


@bot.message_handler(commands=['change_date'])
def change_date(message: Message):
    """
    Изменение даты для пользователя
    :param message: объект Message
    """
    user_id = os.getenv('developer_id')
    if message.from_user.id == int(user_id):
        global date_for_users

        if cancel_act(message):
            bot.register_next_step_handler(message, show_menu)
            return
        keyboard = types.ReplyKeyboardMarkup(row_width=1)
        for user in date_for_users.keys():
            button = types.KeyboardButton(user)
            keyboard.add(button)
            if date_for_users:
                bot.send_message(
                    message.chat.id,
                    'Укажите username для которого вы хотите изменить дату',
                    reply_markup=keyboard
                )
                bot.register_next_step_handler(message, check_username)

            else:
                bot.send_message(message.chat.id, 'Нет активных пользователей')
                bot.register_next_step_handler(message, show_menu)
                return


def check_username(message):
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    else:
        username = message.text
        bot.send_message(message.chat.id, 'Пожалуйста, введите дату в формате May 12, 24, June 1, 21')
        bot.register_next_step_handler(message, check_date_username, username)


def check_date_username(message: Message, username: str):
    """
    Проверка формата даты
    :param message: объект Message
    :param username: имя пользователя для которого изменяем дату
    :return:
    """
    global date_for_users
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    else:
        date = message.text
        if check_date_format(date) and check_string(date):
            date_for_users[username] = date
            print(date_for_users)
        else:
            bot.send_message(
                message.chat.id,
                'Неверный формат даты. Пожалуйста, введите дату в формате May 12, 24, June 1, 21'
            )
            bot.register_next_step_handler(message, check_date_username, username)


@bot.message_handler(commands=['menu'])
def show_menu(message):
    user_id = os.getenv('developer_id')
    if message.from_user.id == int(user_id):
        keyboard = types.ReplyKeyboardMarkup(row_width=1)
        button1 = types.KeyboardButton('/start')
        button2 = types.KeyboardButton('/help')
        button3 = types.KeyboardButton('/cancel')
        button4 = types.KeyboardButton('/show_active_users')
        button5 = types.KeyboardButton('/change_date')
        keyboard.add(button1, button2, button3, button4, button5)

        bot.send_message(message.chat.id, "Меню:", reply_markup=keyboard)


def input_authorization(driver: ChromiumPage, user_data: dict):
    """
    Авторизация аккаунта
    :param driver: объект класса ChromiumPage
    :param user_data: словарь с данными пользователя
    :return:
    """
    if driver.ele('tag:h2@text()=Подтвердите, что вы человек, выполнив указанное действие.'):
        check_cloudflare(driver)
    driver.wait.ele_loaded('#id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input.input(user_data['login'])

    password_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    password_input.input(user_data['password'])

    driver.actions.click('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')

    driver.actions.type(Keys.ENTER)
    logging.info(f"Авторизация {user_data['username']}")


def check_cloudflare(driver: ChromiumPage):
    """
    Проверка cloudflare
    :param driver: объект класса ChromiumPage
    """
    try:
        # parent = driver.ele('tag:iframe@allow:cross-origin-isolated; fullscreen')
        # child = parent.ele('tag:label@class:ctp-checkbox-label')
        driver.wait.ele_loaded('#tag:iframe@src:')
        parent = driver.ele('tag:iframe@src:')
        button = parent.ele('tag:span@class:mark')
        button.click()
    except ElementNotFoundError as error:
        logging.info(f"Проверки не было - {error}")


def get_options_date(user_data: dict):
    """
    Запись даты в словарь date_for_users
    :param user_data: словарь с данными пользователя
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


def check_is_ele(driver: ChromiumPage, user_data: dict, message: Message) -> bool:
    """
    Проверка доступной даты на сайте
    :param driver: объект ChromiumPage
    :param user_data: словарь данных пользователя
    :param message: объект Message
    :return: True or False
    """
    if driver.wait.ele_loaded('tag:div@class=message errorM3'):
        action_finally(driver, user_data, message)
        logging.info(f"Не верные данные для {user_data['username']}")
        bot.send_message(
            message.chat.id,
            f"Не верно указан логин или пароль для {user_data['username']}, попробуйте снова")
    else:
        while driver.wait.ele_loaded('#class:leftPanelText') is not True:
            if driver.wait.ele_loaded('tag:h1@text()=Sorry, you have been blocked'):
                driver.refresh()
            with lock_browser:
                logging.info(f"{user_data['username']} - зашёл в блокировку")
                if next_step_signal.is_set():
                    logging.info(f"{user_data['username']} - поймал сигнал")
                    return True
                logging.info("Информация о свободной дате отсутствует, ожидаем ...")
                time.sleep(random.randint(70, 115))
                driver.refresh()
                logging.info(f"В check_is_ele страницу обновил {user_data['username']}")
                logging.info(f"{user_data['username']} вышел из блокировки")
                if driver.wait.ele_loaded('@class:leftPanelText'):
                    next_step_signal.set()
                    return True


def check_date_on_page(text_ele: str, date_users: dict, user_data: dict) -> bool:
    """
    Проверка совпадения даты
    :param text_ele: Информация о доступной дате
    :param date_users: словарь с датами пользователей
    :param user_data: словарь с данными пользователя
    :return: True or False
    """
    date = text_ele.translate(str.maketrans('', '', string.punctuation))
    date_list = date.split(' ')

    date_user = get_list_date(date_users, user_data)
    start_day, end_day = int(date_user[1]), int(date_user[2])  # Первая дата
    start, end = int(date_user[4]), int(date_user[5])  # Вторая дата
    # Проверка, что обе даты присутствуют в списке
    if date_list[5] == date_user[0] and start_day <= int(date_list[6]) <= end_day:
        logging.info(f"Отслежена дата для {user_data['username']} на {date_user[0]}")
        return True
    elif date_list[5] == date_user[3] and start <= int(date_list[6]) <= end:
        logging.info(f"Отслежена дата для {user_data['username']} на {date_user[3]}")
        return True


def check_available_date(date_users: dict, driver: ChromiumPage(), user_data, message) -> bool:
    """
    Ослеживание даты
    :date_users: global dict(date_for_users)
    :driver: objects ChromiumPage
    :user_data: словарь с данными пользователя
    """
    global users
    while True:
        if driver.wait.ele_loaded('tag:h1@text()=Sorry, you have been blocked', timeout=4):
            driver.refresh()
        give_date = driver.ele('@class:leftPanelText').text
        if check_date_on_page(give_date, date_users, user_data):
            logging.info(f"Для {user_data['username']} есть дата {give_date}")
            return True
        else:
            with lock_browser:
                logging.info(f"{user_data['username']} зашёл в блокировку")
                offset_x = random.randint(300, 500)
                offset_y = random.randint(250, 300)
                cont = random.randint(5, 10)
                driver.actions.move(offset_x=offset_x, offset_y=offset_y, duration=cont)
                driver.actions.up(random.randint(20, 50))
                time.sleep(random.randint(65, 94))
                driver.refresh()
                logging.info(f"Страницу обновил - {user_data['username']}")

            logging.info(f"{user_data['username']} вышел из блокировки")
            driver.wait.ele_loaded('#class:leftPanelText', timeout=3)
            text = driver.ele('@class:leftPanelText').text
            if check_date_on_page(text, date_users, user_data):
                logging.info(f"Для {user_data['username']} есть дата {give_date}")
                return True
            logging.info(f'{text}')


def page_calendar(driver: ChromiumPage):
    """
    Переход на страницу с календарём
    :param driver: объект ChromiumPage
    :return:
    """
    driver.wait.ele_loaded('#tag:a@class=container')
    driver.actions.click('tag:a@@text():Continue')
    if driver.ele('tag:input@type=radio'):
        driver.actions.click('tag:input@type=radio')
        driver.actions.click('tag:input@class=button continue ui-button ui-widget ui-state-default ui-corner-all')


def record_in_first_date(driver: ChromiumPage, user_data: dict, message: Message) -> bool:
    """
    Проврка наличия свободных мест на выделеной дате
    :param driver: объект ChromiumPage
    :param user_data: словарь с данными пользователя
    :param message: объект Message
    :return:
    """
    global date_for_users
    date = get_list_date(date_for_users, user_data)
    month_user = {date[0], date[3]}
    first_month = driver.ele('@class:ui-datepicker-group ui-datepicker-group-first')
    month_calendar = first_month.ele('@class:ui-datepicker-month').text

    if month_calendar not in month_user:
        logging.info(f"В first_available для {user_data['username']} доступной даты не обнаружено")
        driver.actions.click('tag:a@@text():Home')
        return False

    available = driver.ele('@id:thePage:SiteTemplate:theForm:calendarTableMessage')
    free_space = available.ele('tag:td', index=8).text
    free_date = available.ele('tag:td', index=7).text

    if free_space >= user_data['applicants']:
        driver.actions.click('tag:input@type:checkbox')
        parent_ele = driver.ele('tag:span@id:thePage:SiteTemplate:theForm:calendarTableMessage')
        schedule_button = parent_ele.ele('tag:input@id:thePage:SiteTemplate:theForm:addItem')
        schedule_button.click()
        logging.info('Нажата кнопка записи в first_date')
        name = user_data['username']
        bot.send_message(message.chat.id, f"{name} был записан на {free_date}")
        logging.info(f'{name} был записан на {free_date}')
        return True

    return False


def record_in_next_date(driver: ChromiumPage, message, user_data: dict, retries=60):
    """
    Функция для получения всех свободных дат
    :param driver: объект ChromiumPage
    :param user_data: словарь с данными пользователя
    :param message: объект Message
    :param retries: int(колличество попыток)
    :return:
    """
    global check_date
    global date_for_users
    lst_class = [
        driver.ele('@class:ui-datepicker-group ui-datepicker-group-first'),
        driver.ele('@class:ui-datepicker-group ui-datepicker-group-middle'),
        driver.ele('@class:ui-datepicker-group ui-datepicker-group-last'),
    ]

    date = get_list_date(date_for_users, user_data)
    month_date = {
        date[0]: [num for num in range(int(date[1]), int(date[2]))],
        date[3]: [num for num in range(int(date[4]), int(date[5]))],
    }

    try:
        should_break = False
        for lst in lst_class:
            month = lst.ele('@class:ui-datepicker-month').text
            if month in month_date:
                for day in lst.eles('tag=a@@href:@@class=ui-state-default'):
                    need_day = day.text
                    if need_day not in check_date:
                        check_date.append(need_day)
                        if int(need_day) in month_date[month]:
                            driver.actions.click(day)
                            time.sleep(random.randint(2, 4))
                            mather = driver.ele('@id:thePage:SiteTemplate:theForm:calendarTableMessage')
                            free_place = mather.ele('tag:td', index=8).text
                            if int(free_place) >= int(user_data['applicants']):
                                driver.actions.click('tag:input@type:checkbox')
                                parent_ele = driver.ele('tag:span@id:thePage:SiteTemplate:theForm:calendarTableMessage')
                                schedule_button = parent_ele.ele('tag:input@id:thePage:SiteTemplate:theForm:addItem')
                                schedule_button.click()
                                logging.info('Нажата кнопка записи в next_date')
                                name = user_data['username']
                                bot.send_message(
                                    message.chat.id,
                                    f"{name} был записан на {month} - {need_day}"
                                )
                                logging.info(f'{name} - был записан на {month} - {need_day}')
                                action_finally(driver, user_data, message)
                                should_break = True
                                break
            if should_break:
                check_date.clear()
                break
        if not should_break:
            logging.info(f"Для {user_data['username']} не найдено даты")
            driver.actions.click('tag:a@@text():Home')
            return False
    except Exception:
        if retries > 0:
            record_in_next_date(driver, message, user_data, retries - 1)
        else:
            logging.info(f"Превышено количество попыток в record_next_date для {user_data['username']}")


def action_finally(driver: ChromiumPage, user_data: dict, message, retries=10):
    """
    Выполение финальных действий в случае успеха
    :param driver: объект ChromiumPage
    :param user_data: словарь с данными пользователя
    :param message: объект Message
    :param retries: int(колличество попыток)
    """
    global users
    global date_for_users
    try:
        driver.quit()
        username = user_data['username']
        del date_for_users[username]
        del users[username]
    except RuntimeError as error:
        logging.error(f"Ошибка в action_finally - {error}")
        if retries > 0:
            action_finally(driver, user_data, users, retries - 1)
        else:
            logging.error("Превышено количество попыток. Завершение работы.")


def record_in_date(message, user_data):
    """
    Отслеживание и запись на свободную дату
    :param message: объект Message
    :param user_data: словарь с данными пользователя
    """
    global users
    global date_for_users
    try:
        get_options_date(user_data)  # Словарь {'username': 'date'}
        username = user_data['username']
        options = ChromiumOptions().auto_port(True)
        options.set_proxy(random.choice(proxy))
        options.headless(on_off=True)
        users[username] = ChromiumPage(options)
        users[username].retry_time = 10
        users[username].get(url=url)  # Получаем страницу авторизации
        input_authorization(users[username], user_data)  # Ввод данных авторизации, нажимаем кнопку войти
        check_cloudflare(users[username])  # Проверка cloudflare
        if check_is_ele(users[username], user_data, message):
            if check_available_date(date_for_users, users[username], user_data, message):
                page_calendar(users[username])  # Переходим на страницу с календарём свободных дат
                if record_in_first_date(users[username], user_data, message):  # Если первая дата подходит по критериям
                    action_finally(users[username], user_data, message)
                else:
                    check_available_date(date_for_users, users[username], user_data, message)
                if record_in_next_date(users[username], message, user_data):
                    action_finally(users[username], user_data, message)
                else:
                    check_available_date(date_for_users, users[username], user_data, message)
    except Exception as error:
        next_step_signal.clear()
        logging.error(f"Ошибка в record_in_date - {error}")
        username = user_data['username']
        users[username].quit()
        del users[username]
        del date_for_users[username]
        logging.error(f"Процесс для {user_data['username']} был завершён")
        get_middle(message, user_data, 'restart')


def get_middle(message: Message, user_data: dict, command: str):
    """
    Промежуточная функция для запуска нового процесса или record_in_date в том же процессе
    :param message: объект Message
    :param user_data: словарь с данными пользователя
    :param command: команда restart
    """
    if command == 'restart':
        record_in_date(message, user_data)
    else:
        start_process(message, user_data)


def start_process(message: Message, user_data: dict):
    """
    Запуск record_in_date в отдельном процессе
    :param message: объект Message
    :param user_data: словарь с данными пользователя
    """
    global users
    if cancel_act(message):
        bot.register_next_step_handler(message, show_menu)
        return
    else:
        user_data['applicants'] = message.text
        connect = multiprocessing.Process(
            target=record_in_date,
            args=(message, user_data)
        )

        connect.start()
        logging.info(f"Процесс для {user_data['username']} был запущен")


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
