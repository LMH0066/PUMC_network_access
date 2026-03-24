import argparse
import socket
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def check_network_connection():
    try:
        socket.create_connection(("www.baidu.com", 443), timeout=3)
        return True
    except OSError:
        print("目前网络处于离线状态")
        return False


def run(url, username, password, need_keep, tolerance):
    tolerance = float("inf") if tolerance == -1 else tolerance
    _tolerance = 0

    while _tolerance < tolerance:
        driver = None  # 初始化 driver
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")

            # 使用 webdriver_manager 自动处理驱动
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)

            print("Starting session...")

            while True:
                if check_network_connection():
                    time.sleep(1)
                    _tolerance = 0
                    if not need_keep:
                        _tolerance = tolerance
                        break
                    continue
                driver.get(url)
                time.sleep(10)

                driver.find_element(By.ID, "username").send_keys(username)
                driver.find_element(By.ID, "password").send_keys(password)
                driver.find_element(By.ID, "login-account").click()

                _tolerance = 0
                print("Login successful")

                if not need_keep:
                    _tolerance = tolerance
                    break
                time.sleep(60)  # 保持登录时，避免死循环请求

        except WebDriverException as e:
            _tolerance += 1
            print(f"WebDriver error: {e}")
            time.sleep(5)
        finally:
            if driver:
                driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="http://124.17.100.50/")
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--need_keep", type=bool, default=False)
    parser.add_argument("--tolerance", type=int, default=-1)
    args = parser.parse_args()

    run(args.url, args.username, args.password, args.need_keep, args.tolerance)
