import time
import logging
import random

from fake_useragent import UserAgent
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from DrissionPage.common import Keys

logging.basicConfig(filename='logger/check.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ua = UserAgent()

proxy = [
    'http://45.133.227.68:8000',
    'http://193.56.188.205:8000',
    'http://45.129.4.105:8000',
]

url = 'https://portal.ustraveldocs.com'

drive = {}


def get_driver():
    global drive
    options = ChromiumOptions()
    options.set_proxy(random.choice(proxy))
    options.auto_port(True)
    driver = ChromiumPage(addr_or_opts=options)
    drive['link'] = driver
    return driver


def check(driver):
    driver.get(url=url)
    driver.wait.ele_loaded('#id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input.input("ivan_petr22@mail.ru")

    password_input = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    password_input.input("1234lera")

    agree_button = driver.ele('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
    agree_button.click()

    login_button = driver.ele('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton')
    login_button.click()

    try:
        driver.wait.ele_loaded('#allow:cross-origin-isolated')
        test = driver.ele('@allow:cross-origin-isolated').ele('@class:ctp-checkbox-label')
        driver.wait.ele_loaded('#class:mark')
        button = test.ele('@class:mark')
        button.click()
    except ElementNotFoundError as error:
        logging.info(f"Проверки не было - {error}")


def cheat_text():
    try:
        driver = get_driver()
        check(driver)
        while True:
            start = time.time()
            driver.wait.ele_loaded('#class:leftPanelText')
            give_date = driver.ele('@class:leftPanelText').text
            logging.info(f'{give_date}')
            cont = random.randint(3, 7)
            driver.actions.move(offset_x=random.randint(20, 40), offset_y=random.randint(20, 45), duration=cont)
            driver.actions.up(random.randint(20, 50))
            driver.actions.db_click()
            driver.refresh(ignore_cache=True)
            time.sleep(random.randint(67, 113))
            end = time.time()
            res = start - end
            logging.info(f"{res}")
    except Exception as e:
        logging.error(f"{e}")
        drive['link'].quit()
        del drive['link']
        cheat_text()


def main():
    cheat_text()


if __name__ == '__main__':
    main()
