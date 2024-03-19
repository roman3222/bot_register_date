# import os
import datetime
# import random
import time
# import telebot
import string
# import undetected_chromedriver as uc
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium_stealth import stealth
# from selenium.webdriver.chrome.service import Service
# from dotenv import load_dotenv
# from fake_useragent import UserAgent
from DrissionPage import ChromiumPage, ChromiumOptions

#
# load_dotenv()
#
# bot = telebot.TeleBot(os.getenv('token'))
#
# url = 'https://portal.ustraveldocs.com/'
# url2 = 'https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html'
# url3 = 'https://www.vindecoderz.com/EN/check-lookup/ZDMMADBMXHB001652'
# user_agent = UserAgent()
#
#
# @bot.message_handler(commands=['start'])
# def get_login(message):
#     bot.send_message(message.chat.id, f'Укажите адрес электронной почты для авторизации')
#     bot.register_next_step_handler(message, get_password)
#
#
# def get_password(message):
#     user_data = {'login': message.text}
#     bot.send_message(message.chat.id, f'Укажите пароль')
#     bot.register_next_step_handler(message, authorization, user_data)
#
#
# def create_options():
#     options = webdriver.ChromeOptions()
#     options.add_argument(f'user-agent={user_agent.random}')
#     # options.add_argument("start-maximized")
#     # options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     # options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     return options
#
#
# def create_session():
#     options = create_options()
#     service = Service('/home/roman/projects/visa_bot_record/chrome_driver/chromedriver')
#     driver = webdriver.Chrome(
#         options=options,
#         service=service
#     )
#
#     stealth(driver,
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             platform="Win32",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True,
#             )
#
#     driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         'source': '''
#             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
#             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
#             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
#       '''
#
#     })
#     return driver
#
#
# def generate_random_filename(length=10):
#     letters = string.ascii_lowercase
#     return ''.join(random.choice(letters) for _ in range(length))
#
#
# def authorization(message, user_data):
#     user_data['password'] = message.text
#
#     driver = create_session()
#
#     driver.get(url=url)
#     time.sleep(50)
#
# login_input = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username'))
# )
# login_input.clear()
# login_input.send_keys(user_data['login'])
# time.sleep(3)
#
# # Явные ожидания для ожидания появления поля ввода пароля
# password_input = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password'))
# )
# password_input.clear()
# password_input.send_keys(user_data['password'])
# time.sleep(3)
#
# agree_button = driver.find_element(By.NAME, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
# agree_button.click()
# time.sleep(3)
#
# login_button = driver.find_element(By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton')
# login_button.click()
# time.sleep(30)
#
#
# def main():
#     bot.polling(none_stop=True)
#
#
# if __name__ == '__main__':
#     main()


# options = ChromiumOptions().auto_port()

# data = {}
#
# queue_users = [
#     {'username': 'ola', 'applicants': 1},
#     {'username': 'lolo', 'applicants': 5},
#     {'username': 'lala', 'applicants': 3},
#     {'username': 'lilo', 'applicants': 3},
#     {'username': 'lala', 'applicants': 5}
# ]
#
# queue_users.sort(key=lambda k: k['applicants'])
# queue_users.reverse()
# print(queue_users)

# username = check_applicants[0]['username']
# username2 = check_applicants[1]['username']
#
#
# def get_session():
#     options = ChromiumOptions().auto_port()
#
#     data[username] = ChromiumPage(options)
#     data[username2] = ChromiumPage(options)
#     return data[username], data[username2]
#
#
# def get_page():
#     get_session()
#     for key in data:
#         if key == check_applicants[0]['username']:
#             data[username].get('https://www.youtube.com/')
#             return True
#         else:
#             return False
#
#
# if get_page():
#     check_applicants.pop(0)
#     get_session()
#     get_page()


# s = 'First Available Appointment Is Tuesday November 30 2024'
# user_date = {'tatjanavg': 'May 12, 23', 'tata': 'October 12, 31'}
#
# lst = s.split(' ')
#
# date = user_date['tata'].replace(',', '').split(' ')
# start_day, end_day = int(date[1]), int(date[2]) + 1
#
# need_date = {date[0]: list(range(start_day, end_day))}
#
# if lst[5] in date and start_day <= int(lst[6]) <= end_day:
#     print('True')
# else:
#     print('False')

# tup = (1, 2, 3)
#
#
# def change_tup():
#     global tup
#     for i in range(1, 15):
#         tup += (i,)
#
# change_tup()
#
# print(tup)

# date_user = [1, 20]
# user = {'tatjanavg': 'October 12, 21'}
# start_day, end_day = int(date_user[0]), int(date_user[1]) + 1

# date = ['1', '19']
#
# num_date = [num for num in range(int(date[0]), int(date[1]) + 1)]
#
# print(num_date)


driver = ChromiumPage()

driver.get('https://www.youtube.com/')

driver.wait.load_start()

driver.ele('@gdfgfd').ele

shorts = driver.ele('@style:width: 100%; height: 100%; display: block; fill: currentcolor;')

sons = shorts.children()

print(sons)