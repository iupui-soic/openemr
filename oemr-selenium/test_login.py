import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers import (
    read_configurations_from_file,
    read_urls_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_for_element,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestWebsite_login:
    @pytest.fixture(autouse=True)
    def login_page_setup(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_valid_admin_and_user_credentials(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

    @pytest.mark.parametrize("url", read_urls_from_file("secret.json"))
    def test_invalid_credentials(self, url):
        self.browser.get(url)
        wait_for_page_load(self.browser)

        wait_for_element(self.browser, By.ID, 'authUser').send_keys("abc")
        wait_for_element(self.browser, By.ID, "clearPass").send_keys("abc")
        wait_for_element(self.browser, By.ID, "login-button").submit()
        wait_for_page_load(self.browser)

        # Try multiple XPaths for the error message (different OpenEMR versions)
        error_selectors = [
            "//div[contains(@class, 'text-center') and contains(@class, 'login-failure')]/p[contains(@class, 'text-danger')]",
            '//*[@id="login_form"]/div/div[2]/div[1]/p',
            "//div[contains(@class, 'bg-danger') and contains(@class, 'login-failure')]",
            "//div[contains(@class, 'alert-danger')]",
            "//*[contains(@class, 'text-danger')]",
        ]

        error_message_element = None
        for selector in error_selectors:
            try:
                error_message_element = WebDriverWait(self.browser, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if error_message_element and error_message_element.is_displayed():
                    break
            except Exception:
                continue

        assert error_message_element is not None and error_message_element.is_displayed(), \
            "Error message not displayed for invalid credentials"
