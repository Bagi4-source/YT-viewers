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
        self.__headers = headers
        self.__r_url = r_url
        proxy = proxy.split(":")
        self.__proxy = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        self.timeout = 30


    async def watch(self):
        await asyncio.sleep(random.randint(1, 10))
        try:
            while True:
                async with aiohttp.ClientSession(cookies=self.__cookies) as session:
                    async with session.get(
                            url=self.__r_url,
                            ssl=True,
                            proxy=self.__proxy
                    ) as r:
                        print(r.status)
                await asyncio.sleep(40)
        except Exception as _e:
            print(_e, self.__proxy)


if __name__ == '__main__':
    try:
        while True:
            viewers = []
            db = DataBase('../accounts.db')
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

            print('start')
            coroutines = [viewer.watch() for viewer in viewers[:4]]
            loop.run_until_complete(asyncio.gather(*coroutines))

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
