import pytest
from test_utils import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.chrome import ChromeDriverManager


class TestWebsite:
    # 1. Check browser configuration in browser_setup_and_teardown
    # 2. Run 'Selenium Tests' configuration
    # 3. Test report will be created in reports/ directory

    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        options = Options()
        # options.add_experimental_option("detach", True)

        self.browser = webdriver.Chrome(options=options)

        self.browser.maximize_window()
        self.browser.implicitly_wait(10)
        self.browser.get("https://in-info-web18.luddy.indianapolis.iu.edu/interface/login/login.php?site=default")

        """this test checks login functionality"""
        self.browser.find_element(By.ID, 'authUser').send_keys(get_user())
        self.browser.find_element(By.ID, "clearPass").send_keys(get_pass())
        self.browser.find_element(By.ID, "login-button").submit()

        assert "https://in-info-web18.luddy.indianapolis.iu.edu/interface/main/tabs/main.php?" in self.browser.current_url

        # Close all open tabs first
        for tabClose in self.browser.find_elements(By.CSS_SELECTOR, 'span[class="fa fa-fw fa-xs fa-times"]'):
            tabClose.click()

        yield

        self.browser.close()
        self.browser.quit()

    def test_search_found_patient(self):
        """this test checks any box search functionality"""
        self.browser.find_element(By.ID, 'anySearchBox').send_keys('Abdul')
        self.browser.find_element(By.ID, 'search_globals').click()

        searchTable = self.browser.find_element(By.NAME, 'fin')
        assert searchTable is not None

        self.browser.implicitly_wait(5)

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        patient1Found = self.browser.find_element(By.ID, "pid_1")
        assert patient1Found is not None

    def test_search_not_found_patient(self):
        self.browser.find_element(By.ID, 'anySearchBox').clear()
        self.browser.find_element(By.ID, 'anySearchBox').send_keys('Xyz')
        self.browser.find_element(By.ID, 'search_globals').click()

        searchTableFound = self.browser.find_element(By.NAME, 'fin')
        assert searchTableFound is not None

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        assert not len(self.browser.find_elements(By.ID, "pid_1"))
