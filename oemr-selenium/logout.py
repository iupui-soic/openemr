import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *

class TestWebsite_logout:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        options = Options()
        if os.environ.get('HEADLESS', 'false').lower() == 'true':
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Chrome(options=options)
        self.browser.maximize_window()
        self.browser.implicitly_wait(10)

        yield
        self.browser.close()
        self.browser.quit()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_logout(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"

        # Click the username/profile icon
        self.browser.find_element(By.ID, 'username').click()

        # Find and click the logout button
        logout_element = self.browser.find_element(By.XPATH, '//li[@class="menuLabel"][last()]')
        logout_element.click()

        # Wait for the URL to change to the expected login URL
        expected_url = config.url
        WebDriverWait(self.browser, 10).until(EC.url_to_be(expected_url))

        # Assert the current URL after logout
        assert self.browser.current_url == expected_url, f"Logout failed for server: {config.url}"
