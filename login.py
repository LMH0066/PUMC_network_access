import argparse
import os
import socket
import time

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, WebDriverException


def check_network_connection():
    try:
        socket.create_connection(("www.baidu.com", 443), timeout=3)
        return True
    except OSError:
        print("目前网络处于离线状态")
        return False


def run(url, username, password, need_keep, tolerance):
    _tolerance = 0
    if check_network_connection():
        os.environ['SE_DRIVER_MIRROR_URL'] = 'https://mirrors.huaweicloud.com/geckodriver/'
    else:
        os.environ['SE_OFFLINE'] = 'true'
    while _tolerance < tolerance:
        try:
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            driver = webdriver.Firefox(options=options)
            print('start')
            while True:
                if check_network_connection():
                    time.sleep(1)
                    _tolerance = 0
                    if not need_keep:
                        _tolerance = tolerance
                        break
                    continue
                driver.get(url)
                time.sleep(10)  # 需要完整加载
                driver.find_element(By.ID, "username").send_keys(username)
                driver.find_element(By.ID, "password").send_keys(password)
                driver.find_element(By.ID, "login-account").click()
                _tolerance = 0
                time.sleep(1)
                print('ok')

                if not need_keep:
                    _tolerance = tolerance
                    break
        except ElementNotInteractableException as e:
            _tolerance = 0
            time.sleep(2)
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