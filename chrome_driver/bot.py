# import time
# import random
# from data import proxy
# from DrissionPage import ChromiumPage, ChromiumOptions
# from DrissionPage.common import Keys
# from DrissionPage.errors import ElementNotFoundError
# #
# #
# options = ChromiumOptions().auto_port(True)
# options.set_proxy(random.choice(proxy))
#
# driver = ChromiumPage(addr_or_opts=options)
#
# driver.get('https://portal.ustraveldocs.com')
# time.sleep(10)
# driver.refresh()
#
#
# driver.wait.ele_loaded('#id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
# login_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
# login_input.input('stesheva2012@mail.ru')
#
# password_input = driver.actions.click('@id:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
# password_input.input('USA2024!')
#
# driver.actions.click('@name:loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
#
# driver.actions.type(Keys.ENTER)
#
# try:
#     driver.wait.ele_loaded('#allow:cross-origin-isolated')
#     test = driver.ele('@allow:cross-origin-isolated').ele('@class:ctp-checkbox-label')
#     driver.wait.ele_loaded('#class:mark')
#     button = test.ele('@class:mark')
#     button.click()
# except ElementNotFoundError as error:
#     print(error)
#
#
# driver.wait.ele_loaded('#tag:a@class=container')
# driver.actions.click('tag:a@@text():Continue')
driver.actions.click('tag:input@type=radio')
driver.actions.click('tag:input@class=button continue ui-button ui-widget ui-state-default ui-corner-all')
#
# time.sleep(10)
#
# # codec = driver.run_js_loaded("getScheduleEntries('12-11-2024')")
#
# # driver.run_js_loaded("initializeDatepicker();")
#
# time.sleep(2)
#
# date_text = "31-10-2024"
#
# # driver.run_js_loaded(f"$('#datepicker').datepicker('setDate', '{date_text}');")
#
# free_slots = driver.run_js(f"return getScheduleEntries();", date_text)
#
#
# print(free_slots)
