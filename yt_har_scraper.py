from faceUA import FakeAgent
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import time
import datetime

ip = "192.168.2.144"

chrome_options = [
    '--disable-browser-side-navigation',
    '--disable-gpu',
    '--disable-infobars',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--enable-javascript',
    '--disable-dev-shm-usage',
    '--disable-blink-features=AutomationControlled',
    '--ignore-certificate-errors-spki-list',
    '--ignore-ssl-errors',
    # '--start-maximized',
    '--ignore-certificate-errors'
]

capabilities = {
    "browserName": "chrome",
    "browserVersion": "106.0",
    "selenoid:options": {
        "enableVNC": True,
        "enableVideo": False
    }
}


class YtHarScraper:
    def __init__(self, proxy, port, mobile=False):
        self.__mobile = mobile

        options = webdriver.ChromeOptions()

        proxy = proxy.split(":")
        proxy = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"

        selenium_wire_options = {
            'auto_config': False,
            'addr': ip,
            'port': port,
            'proxy': {
                'http': proxy,
                'https': proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }

        options.add_argument(f"--proxy-server={ip}:{port}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if self.__mobile:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": FakeAgent().get_agent(mobile=True)
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        else:
            options.add_argument('--user-agent=%s' % FakeAgent().get_agent())

        for option in chrome_options:
            options.add_argument(option)

        self.driver = webdriver.Remote(
            command_executor=f"http://{ip}:4444/wd/hub",
            desired_capabilities=capabilities,
            options=options,
            seleniumwire_options=selenium_wire_options
        )
        self.actions = webdriver.ActionChains(self.driver)

    def load(self, url):
        if self.driver:
            self.driver.get(url)

            time.sleep(3)

    def _click(self, el):
        try:
            self.actions.move_to_element(el).perform()
            time.sleep(0.2)
            el = WebDriverWait(self.driver, 1).until(ec.element_to_be_clickable(el))
            self.actions.click().perform()
            time.sleep(0.2)
        except Exception as _ex:
            print(_ex)

    def play(self):
        for _ in range(10):
            play_button = self.driver.find_elements(by=By.CSS_SELECTOR, value='button.ytp-play-button[title*=Смотреть]')
            play_button.extend(
                self.driver.find_elements(by=By.CSS_SELECTOR, value='button.ytp-play-button[title*=Play]'))

            pause_button = self.driver.find_elements(by=By.CSS_SELECTOR,
                                                     value='button.ytp-play-button[title*=Пауза]')
            pause_button.extend(
                self.driver.find_elements(by=By.CSS_SELECTOR, value='button.ytp-play-button[title*=Pause]'))

            if play_button or pause_button:
                if play_button:
                    self._click(play_button[0])
                return
            time.sleep(1)

    def play_m(self):
        for _ in range(15):
            play_button = self.driver.find_elements(
                by=By.XPATH,
                value='//div[@class="ytp-cued-thumbnail-overlay" and not(contains(@style, "display: none"))]/button'
            )
            if self.driver.find_elements(
                    by=By.XPATH,
                    value='//div[@class="ytp-cued-thumbnail-overlay" and (contains(@style, "display: none"))]'
            ):
                return
            if play_button:
                self._click(play_button[0])
                time.sleep(1)
                return
            time.sleep(1)

    def get_cookies(self):
        if self.driver:
            return self.driver.get_cookies()

    def get_timeout(self, url):
        try:
            timeout = int(url.split("rtn=")[-1].split("&")[0]) - int(url.split("rti=")[-1].split("&")[0])
        except:
            timeout = 0
        return timeout

    def get_har(self):
        if self.__mobile:
            self.play_m()
        else:
            self.play()

        begin_time = datetime.datetime.now()

        while True:
            for request in self.driver.requests[-20:]:
                if "watchtime" in request.url and request.date > begin_time:
                    if self.get_timeout(request.url) == 40:
                        return request, self.driver.get_cookies()
                    elif self.get_timeout(request.url) > 40:
                        self.driver.delete_all_cookies()
                        self.driver.refresh()
                        return self.get_har()

    def quit(self):
        if self.driver:
            self.driver.quit()
