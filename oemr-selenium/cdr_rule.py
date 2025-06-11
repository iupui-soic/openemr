# Complete cdr_rule.py with Full-Page Load Check Added
import time
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
    def scroll_and_wait_for_size(self, element):
            self.browser.execute_script("arguments[0].scrollIntoView(true);", element)
            WebDriverWait(self.browser, 5).until(
                lambda d: element.size['height'] > 0 and element.size['width'] > 0
            )
            time.sleep(0.5)
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
    def test_cdr_rule_validation(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        adminMenu = WebDriverWait(self.browser, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        self.scroll_and_wait_for_size(adminMenu)
        adminMenu.click()
        time.sleep(0.5)

        practiceMenu = WebDriverWait(self.browser, 1).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/div'))
        )
        self.scroll_and_wait_for_size(practiceMenu)
        practiceMenu.click()
        time.sleep(0.5)

        rules = WebDriverWait(self.browser, 1).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/ul/li[2]/div'))
        )
        self.scroll_and_wait_for_size(rules)
        rules.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 3).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "#framesDisplay iframe"))
        )



