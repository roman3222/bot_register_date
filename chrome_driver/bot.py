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
    'http://46.3.232.21:8000',
    'http://46.3.232.186:8000',
    'http://46.3.235.24:8000',
    'http://46.3.234.235:8000',
    'http://45.129.171.156:8000',
    'http://45.129.171.66:8000',
    'http://45.129.171.165:8000',
]

url = 'https://portal.ustraveldocs.com'

drive = {}


def get_driver():
    global drive
    options = ChromiumOptions()
    options.set_proxy(proxy[-1])
    options.auto_port(True)
    driver = ChromiumPage(addr_or_opts=options)
    drive['link'] = driver
    return driver


def check(driver):
    driver.get(url=url)
    driver.wait.ele_loaded('#id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    login_input.input("ivan_petr22@mail.ru")

    password_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    password_input.input("1234lera")

    driver.actions.click('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')

    driver.actions.type(Keys.ENTER)

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
            offset_x = random.randint(300, 500)
            offset_y = random.randint(250, 300)
            cont = random.randint(3, 7)
            driver.actions.move(offset_x=offset_x, offset_y=offset_y, duration=cont)
            driver.actions.up(random.randint(120, 430))
            driver.actions.db_click()
            driver.actions.type(Keys.F5)
            time.sleep(random.randint(75, 113))
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
