# import os
# import random
import time
# import telebot
# import string
# import undetected_chromedriver as uc
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium_stealth import stealth
# from selenium.webdriver.chrome.service import Service
# from dotenv import load_dotenv
# from fake_useragent import UserAgent
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




