import argparse
import ipaddress
import subprocess
import time
from urllib.parse import urljoin

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def create_driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-features=HttpsFirstBalancedModeAutoEnable")
    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
    driver.set_page_load_timeout(20)
    return driver


def fetch_text(url):
    """Bound DNS, connect and transfer time; bypass unrelated proxy settings."""
    result = subprocess.run(
        ["curl", "--noproxy", "*", "--fail", "--silent", "--show-error",
         "--connect-timeout", "3", "--max-time", "5", url],
        capture_output=True, text=True, timeout=7,
    )
    if result.returncode:
        raise OSError("HTTP probe failed")
    return result.stdout


def portal_state(url):
    try:
        text = fetch_text(urljoin(url, "/cgi-bin/rad_user_info")).strip()
        if text == "not_online_error":
            return "offline"
        fields = text.split(",")
        if len(fields) > 8 and fields[0]:
            ipaddress.ip_address(fields[8])
            return "online"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def check_network_connection():
    for url in ("https://www.baidu.com/", "https://www.ncbi.nlm.nih.gov/"):
        try:
            if fetch_text(url).strip():
                return True
        except (OSError, subprocess.TimeoutExpired):
            pass
    return False


def ensure_connection(url, username, password):
    state = portal_state(url)
    if state == "online":
        connected = check_network_connection()
        print("校园网在线；外网 HTTPS 正常" if connected else
              "校园网已认证，但外网 HTTPS/DNS 异常；不重复登录", flush=True)
        return connected
    if state == "unknown":
        print("校园网认证状态查询失败；暂不提交账号密码", flush=True)
        return False

    driver = None
    try:
        driver = create_driver()
        driver.get(url)
        wait = WebDriverWait(driver, 20, poll_frequency=1)
        user_input = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
        user_input.clear()
        user_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        wait.until(EC.element_to_be_clickable((By.ID, "login-account"))).click()
        # A click alone proves nothing: wait for the server-side authenticated state.
        wait.until(lambda _: portal_state(url) == "online")
        if check_network_connection():
            print("Login successful：校园网认证及外网 HTTPS 均已核验", flush=True)
            return True
        print("校园网认证已通过，但外网 HTTPS/DNS 仍异常", flush=True)
    except WebDriverException as error:
        # Do not emit browser dumps that might contain credentials.
        print("登录未核验成功：" + type(error).__name__, flush=True)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                pass
    return False


def run(url, username, password, need_keep, tolerance):
    failures = 0
    while tolerance == -1 or failures < tolerance:
        connected = ensure_connection(url, username, password)
        failures = 0 if connected else failures + 1
        if not need_keep:
            return connected
        time.sleep(60 if connected else min(60 * failures, 300))
    return False


def parse_bool(value):
    if value.lower() in ("true", "1", "yes"):
        return True
    if value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError("expected True or False")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="http://124.17.100.50/")
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--need_keep", type=parse_bool, nargs="?", const=True, default=False)
    parser.add_argument("--tolerance", type=int, default=-1)
    args = parser.parse_args()
    if args.tolerance != -1 and args.tolerance < 1:
        parser.error("--tolerance must be -1 or a positive integer")
    try:
        success = run(args.url, args.username, args.password, args.need_keep, args.tolerance)
    except KeyboardInterrupt:
        raise SystemExit(0)
    raise SystemExit(0 if success else 1)
