import random
from fake_useragent import UserAgent
from DrissionPage import ChromiumPage



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


acts = [
    'tag:a@text()=Update Profile',
    'tag:a@text()=Provide Feedback',
    'tag:a@text()=Group Scheduling Request',
    'tag:a@text()=Home',
]