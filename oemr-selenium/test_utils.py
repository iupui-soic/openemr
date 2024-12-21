import json

from selenium.webdriver.common.by import By
import json
from dataclasses import dataclass
from typing import List




@dataclass
class ServerConfig:
    server_name: str
    url: str
    username: str
    password: str

    def __repr__(self):
        # Only show server name in test output, hide credentials
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

    # Adjusted to access the "SERVERS" key directly
    servers_data = data.get("SERVERS", {})
    urls = [server_data['url'] for server_data in servers_data.values()]

    return urls


# Added this function to access the url after logging in from secret.json
# to replace the hard coded value
def get_expected_url_after_login(server_name, file_path='secret.json'):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    servers = data.get("SERVERS", {})
    return servers.get(server_name, {}).get('expected_url_after_login', '')

def login(browser, username, password, login_url, server_name, file_path='secret.json'):
    # Fetch the expected URL after login for this specific server
    expected_url_after_login = get_expected_url_after_login(server_name, file_path)

    browser.get(login_url)
    browser.find_element(By.ID, 'authUser').send_keys(username)
    browser.find_element(By.ID, "clearPass").send_keys(password)
    browser.find_element(By.ID, "login-button").submit()

    # Close any open tabs or overlays
    tabs_to_close = browser.find_elements(By.CSS_SELECTOR, 'span[class="fa fa-fw fa-xs fa-times"]')
    for tab_close in tabs_to_close:
        tab_close.click()

    # Return True if the current URL matches the expected URL
    return expected_url_after_login in browser.current_url


def read_admin_configurations_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    first_user_configurations = []

    # Iterate over each server in the "SERVERS" dictionary
    for server_name, user_data in data["SERVERS"].items():
        url_value = user_data['url']

        # Check if there are users defined for the server and it's not an empty list
        if user_data['users']:
            first_user = user_data['users'][0]  # Get the first user
            username = first_user['username']
            password = first_user['password']

            # Include server_name in the returned tuple
            first_user_configurations.append((server_name, url_value, username, password))

    return first_user_configurations

