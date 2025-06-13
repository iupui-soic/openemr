# Complete cdr_rule.py with Full-Page Load Check Added

import pytest
import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *

class TestWebsite_cdr_rule:

    @pytest.fixture(autouse=True)
    def setup_browser(self, browser_fixture):
        # self.browser is set via shared browser_fixture in test_utils.py
        pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cdr_rule_validation(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        adminMenu = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div')
        actions = ActionChains(self.browser)
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        practiceMenu = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/div')
        actions.move_to_element(practiceMenu).perform()
        wait_for_page_load(self.browser)

        rules = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/ul/li[2]/div')
        rules.click()
        wait_for_page_load(self.browser)
