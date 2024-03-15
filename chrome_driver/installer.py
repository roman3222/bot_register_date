# import os
# import random
# import time
# import telebot
# import string
# import undetected_chromedriver as uc
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from dotenv import load_dotenv
# # from seleniumbase import Driver
# from fake_useragent import UserAgent
#
# load_dotenv()
#
# bot = telebot.TeleBot(os.getenv('token'))
#
# url = 'https://portal.ustraveldocs.com'
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
#     options = uc.ChromeOptions()
#     options.add_argument(f'user-agent={user_agent.random}')
#     return options
#
#
# def create_session():
#     options = create_options()
#     driver = uc.Chrome(
#         options=options
#     )
#
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
#     time.sleep(5)
#
#     login_input = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username'))
#     )
#     login_input.clear()
#     login_input.send_keys(user_data['login'])
#     time.sleep(3)
#
#     # Явные ожидания для ожидания появления поля ввода пароля
#     password_input = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password'))
#     )
#     password_input.clear()
#     password_input.send_keys(user_data['password'])
#     time.sleep(3)
#
#     agree_button = driver.find_element(By.NAME, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
#     agree_button.click()
#     time.sleep(3)
#
#     login_button = driver.find_element(By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton')
#     login_button.click()
#     time.sleep(30)
#
#
# def main():
#     bot.polling(none_stop=True)
#
#
# if __name__ == '__main__':
#     main()
