import pytest
import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *


class TestWebsite_cdr_rule:
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

    # This test will only run for admin user
    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cdr_rule_validation(self, config):
        # Log in to the server using the credentials
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"

        adminMenu = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div')

        actions = ActionChains(self.browser)

        actions.move_to_element(adminMenu).perform()

        practiceMenu = self.browser.find_element(By.XPATH,
                                                 '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/div')

        actions.move_to_element(practiceMenu).perform()

        rules = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/ul/li[2]/div')
        rules.click()