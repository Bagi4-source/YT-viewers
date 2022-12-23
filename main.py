import json
from yt_har_scraper import YtHarScraper
from db import DataBase
from threading import Thread


def parse(proxies, port):
    print(len(proxies))

    for i in range(len(proxies)):
        print("Iter:", i + 1)
        scraper = YtHarScraper(proxies[i], port, mobile=True)
        try:
            scraper.load(f"https://m.youtube.com/watch?v={token}")

            har, cookies = scraper.get_har()

            main_cookies = {}
            for cookie in cookies:
                if cookie.get('name') in ['YSC', 'VISITOR_INFO1_LIVE', 'PREF', 'GPS']:
                    main_cookies[cookie.get('name')] = cookie.get('value')

            main_headers = {}
            for header, value in har.headers.items():
                main_headers[header] = value

            db = DataBase("accounts.db")
            db.add(har.url, json.dumps(main_headers), json.dumps(main_cookies), proxies[i], token)
            db.close()
        finally:
            scraper.quit()


if __name__ == '__main__':
    count = int(input("Count: "))
    token = input("ID: ")

    proxies = []

    with open(file="proxy.txt", mode="r") as file:
        for line in file.readlines():
            line = line.strip()
            if line:
                proxies.append(line)

    count = min(count, len(proxies))

    threads = []
    k = count // 5
    for i in range(5):
        x = Thread(target=parse, args=(proxies[i * k: (i + 1) * k], 8090 + i,))
        threads.append(x)
        x.start()

    for x in threads:
        x.join()
