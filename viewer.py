import datetime
import json
import random
import time
import requests
import sqlite3
from multiprocessing import Process
from db import DataBase
import asyncio
import aiohttp


class Viewer:
    def __init__(self, video_url, cookies, headers, r_url, proxy):
        self.__video_url = video_url
        self.__cookies = cookies
        self.__headers = self.__get_headers(headers)
        self.__r_url = r_url.replace('muted=1', 'muted=0')
        # self.__proxy = self.__get_proxy(proxy)
        proxy = proxy.split(":")
        self.__proxy = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        self.timeout = 30

    def __get_headers(self, headers):
        result = {}
        for header, value in headers.items():
            if "sec-" not in header and "cookie" != header:
                result[header] = value
        return result

    def __get_proxy(self, proxy):
        proxy_url = ""
        if "http" not in proxy:
            if proxy.split(":"):
                proxy = proxy.split(":")
            if len(proxy) == 2:
                proxy_url = f"http://{proxy[0]}:{proxy[1]}"
            elif len(proxy) == 4:
                proxy_url = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        else:
            proxy_url = proxy

        return {
            "http": proxy_url,
            "https": proxy_url
        }

    async def watch(self):
        try:
            async with aiohttp.ClientSession(cookies=self.__cookies) as session:
                async with session.get(
                        url=self.__r_url,
                        ssl=True,
                        proxy=self.__proxy
                ) as r:
                    pass
        except Exception as _e:
            print(_e, self.__proxy)


def start(viewer):
    viewer.watch()


if __name__ == '__main__':
    try:

        viewers = []
        db = DataBase('accounts.db')
        # db.clear()
        rows = db.get_all()
        for row in rows:
            viewer = Viewer(
                video_url=f"https://www.youtube.com/watch?v={row[5]}",
                cookies=json.loads(row[2]),
                headers=json.loads(row[3]),
                proxy=row[4],
                r_url=row[1]
            )
            viewers.append(viewer)

        db.close()
        loop = asyncio.get_event_loop()

        while True:
            print('start')
            coroutines = [viewer.watch() for viewer in viewers[:5]]
            loop.run_until_complete(asyncio.gather(*coroutines))
            loop.run_until_complete(asyncio.sleep(40))

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
