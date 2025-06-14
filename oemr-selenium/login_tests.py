import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *


class TestWebsite_login:
    @pytest.fixture(autouse=True)
    def setup_browser(self): yield from browser_setup_and_teardown(self)

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_valid_admin_and_user_credentials(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

    @pytest.mark.parametrize("url", read_urls_from_file("secret.json"))
    def test_invalid_credentials(self, url):
        self.browser.get(url)
        wait_for_page_load(self.browser)

        self.browser.find_element(By.ID, 'authUser').send_keys("abc")
        self.browser.find_element(By.ID, "clearPass").send_keys("abc")
        self.browser.find_element(By.ID, "login-button").submit()
        wait_for_page_load(self.browser)

        # Try both XPaths for the error message
        error_message_element = None
        try:
            # First XPath (11k Instance)
            error_message_element = self.browser.find_element(By.XPATH, "//div[contains(@class, 'text-center') and contains(@class, 'login-failure')]/p[contains(@class, 'text-danger')]")
        except:
            try:
                # Second XPath (7.0.2 Instance)
                error_message_element = self.browser.find_element(By.XPATH, '//*[@id="login_form"]/div/div[2]/div[1]/p')
            except:
                try:
                    # Third XPath (7.0.0 Instance)
                    error_message_element = self.browser.find_element(By.XPATH, "//div[contains(@class, 'bg-danger') and contains(@class, 'login-failure')]")
                except:
                    pass  # None of the XPaths worked

        # Check if the error message element was found and is displayed
        assert error_message_element is not None and error_message_element.is_displayed(), "Error message not displayed for invalid credentials"

