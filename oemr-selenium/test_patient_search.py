import pytest
import re
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_for_element,
    wait_and_js_click,
    wait_and_js_mousedown,
    switch_to_frame_with_retry,
    wait_for_datatable_filter,
    js_click,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestWebsite_patient_search:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    def _open_finder(self):
        """Open the Patient Finder via menu."""
        wait_for_page_load(self.browser)

        # On desktop, menu is visible. On mobile, need to click toggle first.
        # Try to click toggle if it exists and is visible
        try:
            toggle = self.browser.find_element(By.CSS_SELECTOR, "button.navbar-toggler")
            if toggle.is_displayed():
                js_click(self.browser, toggle)
                wait_for_page_load(self.browser)
        except Exception:
            pass  # Toggle doesn't exist or isn't visible - menu is already visible

        # Find and click Finder menu item
        finder_selectors = [
            (By.XPATH, "//div[contains(@class, 'menuLabel') and contains(text(), 'Finder')]"),
            (By.XPATH, "//div[contains(text(), 'Finder')]"),
            (By.XPATH, "//*[contains(@class, 'menuLabel')][contains(., 'Finder')]"),
            (By.LINK_TEXT, "Finder"),
        ]

        clicked = False
        for by, selector in finder_selectors:
            try:
                element = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                js_click(self.browser, element)
                clicked = True
                break
            except Exception:
                continue

        if not clicked:
            raise Exception("Could not find Finder menu item")

        wait_for_page_load(self.browser)

    def _switch_to_finder_frame(self):
        """Switch to the Finder iframe."""
        # Try multiple strategies to find the iframe
        iframe_selectors = [
            (By.CSS_SELECTOR, "#framesDisplay > div > iframe"),
            (By.CSS_SELECTOR, "iframe[name='fin']"),
            (By.NAME, "fin"),
            (By.TAG_NAME, "iframe"),
        ]

        for by, selector in iframe_selectors:
            try:
                iframe = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((by, selector))
                )
                self.browser.switch_to.frame(iframe)
                wait_for_page_load(self.browser)
                return
            except Exception:
                continue

        raise Exception("Could not find Finder iframe")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_patient_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = wait_for_element(self.browser, By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('100')
        wait_and_js_mousedown(self.browser, By.ID, 'search_globals')
        wait_for_page_load(self.browser)

        switch_to_frame_with_retry(self.browser, "fin")

        results_text = wait_for_element(self.browser, By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) > 0, f"Search returned zero results: {results_text}"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_not_found_patient_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = wait_for_element(self.browser, By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('12000')
        wait_and_js_mousedown(self.browser, By.ID, 'search_globals')
        wait_for_page_load(self.browser)

        switch_to_frame_with_retry(self.browser, "fin")

        results_text = wait_for_element(self.browser, By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) == 0, f"Expected 0 results but found: {results_text}"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_patient_using_finder(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._open_finder()
        self._switch_to_finder_frame()

        # Find search box with multiple strategies
        search_selectors = [
            (By.CSS_SELECTOR, 'input.form-control.form-control-sm'),
            (By.CSS_SELECTOR, 'input[type="search"]'),
            (By.XPATH, "//input[contains(@class, 'form-control')]"),
        ]

        search_box = None
        for by, selector in search_selectors:
            try:
                search_box = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                break
            except Exception:
                continue

        assert search_box is not None, "Could not find search box in Finder"

        search_box.clear()
        search_box.send_keys("100")
        search_box.send_keys(Keys.RETURN)
        wait_for_page_load(self.browser)

        results_text = wait_for_element(self.browser, By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) > 0, f"Search returned zero results: {results_text}"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_not_found_patient_using_finder(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._open_finder()
        self._switch_to_finder_frame()

        # Find search box with multiple strategies
        search_selectors = [
            (By.CSS_SELECTOR, 'input.form-control.form-control-sm'),
            (By.CSS_SELECTOR, 'input[type="search"]'),
            (By.XPATH, "//input[contains(@class, 'form-control')]"),
        ]

        search_box = None
        for by, selector in search_selectors:
            try:
                search_box = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((by, selector))
                )
                break
            except Exception:
                continue

        assert search_box is not None, "Could not find search box in Finder"

        search_box.clear()
        search_box.send_keys("12000")
        search_box.send_keys(Keys.RETURN)
        wait_for_page_load(self.browser)

        # Wait for DataTable async filtering to complete before checking results
        results_text = wait_for_datatable_filter(self.browser)

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) == 0, f"Expected 0 results but found: {results_text}"