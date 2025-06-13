import pytest
import os
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *
import re

class TestWebsite_patient_search:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        options = Options()
        if os.environ.get('HEADLESS', 'false').lower() == 'true':
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument('--window-size=1920,1080')
            options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(10)
        yield
        self.browser.quit()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_ssn_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = self.browser.find_element(By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('100')
        self.browser.find_element(By.ID, 'search_globals').click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fin")))
        wait_for_page_load(self.browser)

        results_text = self.browser.find_element(By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) > 0, f"Search returned zero results: {results_text}"

        first_row = self.browser.find_element(By.CSS_SELECTOR, "#pt_table tbody tr")
        ssn_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

        if ssn_pattern.search(first_row.text):
            print("SSN found in the first row.")
        else:
            assert False, "SSN not found in the first row of the search results!"
