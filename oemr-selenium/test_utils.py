import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from dataclasses import dataclass
from typing import List
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@dataclass
class ServerConfig:
    server_name: str
    url: str
    username: str
    password: str

    def __repr__(self):
        return f"ServerConfig(server={self.url})"

def read_configurations_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    configurations = []
    for server_name, user_data in data["SERVERS"].items():
        url = user_data['url']
        users = user_data['users']
        for user in users:
            config = ServerConfig(
                server_name=server_name,
                url=url,
                username=user['username'],
                password=user['password']
            )
            configurations.append(config)
    return configurations

def sanitize_test_name(config: ServerConfig):
    return f"server-{config.url}"

def read_urls_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    servers_data = data.get("SERVERS", {})
    urls = [server_data['url'] for server_data in servers_data.values()]
    return urls

def get_expected_url_after_login(server_name, file_path='secret.json'):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    servers = data.get("SERVERS", {})
    return servers.get(server_name, {}).get('expected_url_after_login', '')

def login(browser, username, password, login_url, server_name, file_path='secret.json'):
    expected_url_after_login = get_expected_url_after_login(server_name, file_path)
    browser.get(login_url)
    browser.find_element(By.ID, 'authUser').send_keys(username)
    browser.find_element(By.ID, "clearPass").send_keys(password)
    browser.find_element(By.ID, "login-button").submit()
    tabs_to_close = browser.find_elements(By.CSS_SELECTOR, 'span[class="fa fa-fw fa-xs fa-times"]')
    for tab_close in tabs_to_close:
        tab_close.click()
    return expected_url_after_login in browser.current_url

def read_admin_configurations_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    first_user_configurations = []
    for server_name, user_data in data["SERVERS"].items():
        url_value = user_data['url']
        if user_data['users']:
            first_user = user_data['users'][0]
            username = first_user['username']
            password = first_user['password']
            first_user_configurations.append((server_name, url_value, username, password))
    return first_user_configurations

def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return typeof jQuery == "undefined" || jQuery.active == 0')
    )

def init_browser():
    options = Options()
    if os.environ.get('HEADLESS', 'false').lower() == 'true':
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.implicitly_wait(10)
    return browser

@pytest.fixture
def browser_fixture(request):
    browser = init_browser()
    request.instance.browser = browser
    yield
    browser.quit()
