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
    def setup_browser(self, browser_fixture):
        # self.browser is set via shared browser_fixture in test_utils.py
        pass


    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_patient_using_search_bar(self, config):
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

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_not_found_patient_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = self.browser.find_element(By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('12000')
        self.browser.find_element(By.ID, 'search_globals').click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fin")))
        wait_for_page_load(self.browser)

        results_text = self.browser.find_element(By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) == 0, f"Expected 0 results but found: {results_text}"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_patient_using_finder(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)


        self.browser.find_element(By.XPATH, '//div[@class="menuLabel px-1" and text()="Finder"]').click()
        wait_for_page_load(self.browser)

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)
        wait_for_page_load(self.browser)

        search_box = self.browser.find_element(By.CSS_SELECTOR, 'input.form-control.form-control-sm')
        search_box.clear()
        search_box.send_keys("100")
        search_box.send_keys(Keys.RETURN)
        wait_for_page_load(self.browser)

        results_text = self.browser.find_element(By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) > 0, f"Search returned zero results: {results_text}"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_not_found_patient_using_finder(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self.browser.find_element(By.XPATH, '//div[@class="menuLabel px-1" and text()="Finder"]').click()
        wait_for_page_load(self.browser)

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)
        wait_for_page_load(self.browser)

        search_box = self.browser.find_element(By.CSS_SELECTOR, 'input.form-control.form-control-sm')
        search_box.clear()
        search_box.send_keys("12000")
        search_box.send_keys(Keys.RETURN)
        wait_for_page_load(self.browser)

        results_text = self.browser.find_element(By.ID, "pt_table_info").text

        match = re.search(r'Showing (\d+)', results_text)
        assert match, "Could not find 'Showing X' in results text!"

        assert int(match.group(1)) == 0, f"Expected 0 results but found: {results_text}"

