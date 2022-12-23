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
        self.__proxy = self.__get_proxy(proxy)
        self.timeout = 30

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

    def watch(self):
        while True:
            try:
                requests.get(
                    url=self.__r_url,
                    # headers=self.__headers,
                    cookies=self.__cookies,
                    verify=True,
                    proxies=self.__proxy
                )
                timeout = int(self.__r_url.split("rtn=")[-1].split("&")[0]) - int(
                    self.__r_url.split("rti=")[-1].split("&")[0])
                time.sleep(timeout)
            except Exception as _e:
                print(_e, self.__proxy)



def start(viewer):
    viewer.watch()


if __name__ == '__main__':
    try:
        while True:
            processes = []
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
                process = Process(target=start, args=(viewer,))
                processes.append(process)
                process.start()
                time.sleep(random.randint(1, 3))

            print(len(processes))
            db.close()

            for process in processes:
                process.join()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
