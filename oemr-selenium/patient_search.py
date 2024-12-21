import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *

class TestWebsite_patient_search:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        options = Options()
        if os.environ.get('HEADLESS', 'false').lower() == 'true':
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Chrome(options=options)
        # self.browser.maximize_window()
        self.browser.implicitly_wait(10)

        yield  # This allows the subsequent test methods to run
        self.browser.close()
        self.browser.quit()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_patient_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"

        self.browser.find_element(By.ID, 'anySearchBox').send_keys('Abdul')
        self.browser.find_element(By.ID, 'search_globals').click()

        searchTable = self.browser.find_element(By.NAME, 'fin')
        assert searchTable is not None

        self.browser.implicitly_wait(5)

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        patient1Found = self.browser.find_elements(By.ID, "pid_1")
        patient154Found = self.browser.find_elements(By.ID, "pid_154")
        assert patient1Found or patient154Found, "Neither pid_1 nor pid_154 found"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_not_found_patient_using_search_bar(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"

        self.browser.find_element(By.ID, 'anySearchBox').clear()
        self.browser.find_element(By.ID, 'anySearchBox').send_keys('Xyz')
        self.browser.find_element(By.ID, 'search_globals').click()

        searchTableFound = self.browser.find_element(By.NAME, 'fin')
        assert searchTableFound is not None

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        assert not len(self.browser.find_elements(By.ID, "pid_1")) and not len(self.browser.find_elements(By.ID, "pid_154"))

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_found_patient_using_finder(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"

        hamburger_menu = self.browser.find_element(By.XPATH, '//*[@id="mainBox"]/nav/button')
        hamburger_menu. click()

        finder_element = self.browser.find_element(By.XPATH, '//div[@class="menuLabel px-1" and text()="Finder"]')
        finder_element.click()

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        # Assuming you have located the input element using an appropriate selector
        search_box = self.browser.find_element(By.CLASS_NAME, 'form-control.search_init')

        self.browser.implicitly_wait(10)

        # Input text into the search box
        search_box.send_keys("Abdul")

        patient1Found = self.browser.find_elements(By.ID, "pid_1")
        patient154Found = self.browser.find_elements(By.ID, "pid_154")
        assert patient1Found or patient154Found, "Neither pid_1 nor pid_154 found"

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_search_not_found_patient_using_finder(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"

        hamburger_menu = self.browser.find_element(By.XPATH, '//*[@id="mainBox"]/nav/button')
        hamburger_menu.click()

        finder_element = self.browser.find_element(By.XPATH, '//div[@class="menuLabel px-1" and text()="Finder"]')
        finder_element.click()

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        # Assuming you have located the input element using an appropriate selector
        search_box = self.browser.find_element(By.CLASS_NAME, 'form-control.search_init')

        self.browser.implicitly_wait(10)

        # Input text into the search box
        search_box.send_keys("xyz")

        assert not len(self.browser.find_elements(By.ID, "pid_1")) and not len(self.browser.find_elements(By.ID, "pid_154"))
