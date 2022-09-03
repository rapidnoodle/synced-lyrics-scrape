from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import pychrome
import dotenv
import json
import time
import os

dotenv.load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def waitUntilLocated(by=By.CLASS_NAME, search="spotify-logo--text"):
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((by, search)))


def login():
    driver.get(
        "https://accounts.spotify.com/en/login?continue=https%3A%2F%2Fopen.spotify.com%2F")

    waitUntilLocated(By.ID, "login-button")

    email = driver.find_element(By.ID, "login-username")
    password = driver.find_element(By.ID, "login-password")
    submit = driver.find_element(By.ID, "login-button")

    email.send_keys(EMAIL)
    password.send_keys(PASSWORD)
    submit.click()

    waitUntilLocated()


def response_received(**kwargs):
    response = kwargs.get("response")
    url = response.get("url")

    prefix = "https://spclient.wg.spotify.com/color-lyrics/v2/track/"
    if prefix not in url:
        return

    try:
        data = json.loads(
            tab.Network.getResponseBody(
                requestId=kwargs.get("requestId")
            )["body"].replace("\"", "\"")
        )["lyrics"]["lines"]

        for line in data:
            del line["syllables"]
            del line["endTimeMs"]
    except:
        return

    with open("output.json", "r+") as file:
        file_data = json.load(file)

        offset = len(prefix)
        key = "Key" + url[offset:offset + 10]
        if key in file_data:
            return

        print("Outputting Key: " + key)
        file_data[key] = data

        file.seek(0)
        json.dump(file_data, file, indent=4)


options = webdriver.ChromeOptions()
options.add_argument("--remote-debugging-port=8000")
driver = webdriver.Chrome(options=options)

browser = pychrome.Browser(url="http://localhost:8000")
tab = browser.list_tab()[0]
tab.start()

tab.Network.enable()
tab.Network.responseReceived = response_received

login()

driver.get("https://open.spotify.com/playlist/6Enre249js2Pkz1KK5rRrQ")
waitUntilLocated()

time.sleep(10)

for i in range(10):
    next = driver.find_element(By.CLASS_NAME, "mnipjT4SLDMgwiDCEnRC")
    next.click()
    time.sleep(3)
    try:
        get_lyrics = driver.find_element(By.CLASS_NAME, "ZMXGDTbwxKJhbmEDZlYy")
        get_lyrics.click()
    except:
        pass
    time.sleep(2)

tab.stop()

while True:
    time.sleep(1)
