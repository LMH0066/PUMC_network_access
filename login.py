import argparse
import time

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


def run(url, username, password, need_keep, tolerance):
    _tolerance = 0
    while _tolerance < tolerance:
        try:
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            driver = webdriver.Firefox(options=options)
            print('start')
            while True:
                driver.get(url)
                time.sleep(10)  # 需要完整加载
                name = driver.find_element(By.ID, "username")
                _tolerance = 0
                if name.text:
                    time.sleep(1)
                    continue
                name.send_keys(username)
                pwd =  driver.find_element(By.ID, "password")
                pwd.send_keys(password)

                login =  driver.find_element(By.ID, "login-account")
                login.click()
                time.sleep(1)
                print('ok')

                if not need_keep:
                    _tolerance = tolerance
                    break
        except WebDriverException as e:
            _tolerance += 1
            print("An error occurred:", e)
            time.sleep(2)
        finally:
            driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', type=str, default='https://124.17.100.50/')
    parser.add_argument('--username', type=str)
    parser.add_argument('--password', type=str)
    parser.add_argument('--need_keep', type=bool, default=False)
    parser.add_argument('--tolerance', type=int, default=3)

    args = parser.parse_args()

    run(args.url, args.username, args.password, args.need_keep, args.tolerance)