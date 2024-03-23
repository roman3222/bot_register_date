import asyncio
import aiohttp
import random
import ipaddress
from aiocfscrape import CloudflareScraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()

headers = ua.random


url = "https://www.myip.com/"

proxy = 'https://BBScy5:Ejuq2b@217.29.63.2:13136'


# async def start():
#     async with CloudflareScraper() as session:
#         async with session.get(url=url, proxy=proxy) as response:
#             if response.ok:
#                 response_text = await response.read()
#                 soup = BeautifulSoup(response_text, "html.parser")
#                 site = soup.find("div", {"class": "texto_1"})
#                 ip = site.text
#                 print(ip)

async def check():
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, proxy=proxy) as response:
            res = await response.read()
            soup = BeautifulSoup(res, "html.parser")
            site = soup.find("span", {"id": "ip"})
            port = soup.find("img", {"class": "icono"}).text
            ip = site.text
            ip_address = ipaddress.ip_address(ip)
            readable_ipv6 = ip_address.exploded
            print(readable_ipv6)


def main():
    asyncio.run(check())


if __name__ == "__main__":
    main()
