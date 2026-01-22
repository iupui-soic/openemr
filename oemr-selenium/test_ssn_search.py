import pytest
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_for_element,
    wait_and_js_click,
    switch_to_frame_with_retry,
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

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_ssn_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = wait_for_element(self.browser, By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('100')
        wait_and_js_click(self.browser, By.ID, 'search_globals')
        wait_for_page_load(self.browser)

        switch_to_frame_with_retry(self.browser, "fin")

        results_text = wait_for_element(self.browser, By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) > 0, f"Search returned zero results: {results_text}"

        first_row = wait_for_element(self.browser, By.CSS_SELECTOR, "#pt_table tbody tr")
        ssn_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

        if ssn_pattern.search(first_row.text):
            print("SSN found in the first row.")
        else:
            assert False, "SSN not found in the first row of the search results!"
