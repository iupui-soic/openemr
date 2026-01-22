import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_and_js_click,
    js_click,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestWebsite_logout:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_logout(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        # Click the username/profile icon - try multiple selectors
        username_selectors = [
            (By.ID, 'username'),
            (By.CSS_SELECTOR, '#username'),
            (By.XPATH, "//*[@id='username']"),
        ]

        clicked = False
        for by, selector in username_selectors:
            try:
                element = WebDriverWait(self.browser, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                js_click(self.browser, element)
                clicked = True
                break
            except Exception:
                continue

        assert clicked, "Could not find username element to click"
        wait_for_page_load(self.browser)

        # Find and click the logout button - try multiple selectors
        logout_selectors = [
            (By.XPATH, '//a[contains(@data-bind, "logout")]'),
            (By.XPATH, '//a[contains(text(), "Logout")]'),
            (By.XPATH, '//a[contains(@href, "logout")]'),
            (By.LINK_TEXT, 'Logout'),
        ]

        clicked = False
        for by, selector in logout_selectors:
            try:
                element = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                js_click(self.browser, element)
                clicked = True
                break
            except Exception:
                continue

        assert clicked, "Could not find logout button"
        wait_for_page_load(self.browser)

        # Wait for the URL to contain "login" (redirected to login page)
        WebDriverWait(self.browser, DEFAULT_TIMEOUT).until(EC.url_contains("login"))

        assert "login" in self.browser.current_url, f"Logout failed for server: {config.url}"
