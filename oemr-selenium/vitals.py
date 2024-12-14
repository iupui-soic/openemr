import pytest
import os
from selenium import webdriver
from selenium.common import NoSuchElementException, NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert


class TestWebsite_vitals:
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

    @pytest.mark.parametrize("server_name, url, username, password", read_configurations_from_file("secret.json"))
    def test_vitals_is_present_on_patient_dashboard(self, server_name, url, username, password):
        success = login(self.browser, username, password, url, server_name)
        assert success, f"Login failed for server {server_name}"

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

        (patient1Found or patient154Found)[0].click()

        self.browser.switch_to.default_content()

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)

        container_div = self.browser.find_element(By.ID, 'container_div')

        main_divs = container_div.find_elements(By.CLASS_NAME, 'main.mb-5')

        for div in main_divs:
            try:
                class_row = div.find_element(By.CLASS_NAME, 'row')

                card_sections = class_row.find_elements(By.CSS_SELECTOR, 'section.card.mb-2')

                # If there are sections, interact with the last one
                if card_sections:
                    last_card_section = card_sections[-1]

                    vitals_expand_div = last_card_section.find_element(By.ID, 'vitals_ps_expand')
                    vitals_id = vitals_expand_div.find_element(By.ID, 'vitals')

                    span_text = vitals_expand_div.find_element(By.CLASS_NAME, 'text')

                    link_to_click = span_text.find_element(By.PARTIAL_LINK_TEXT,
                                                           'Click here to view and graph all vitals.')
                    link_to_click.click()
                    # Switch to the alert and accept/dismiss it
                    try:
                        alert = Alert(self.browser)
                        alert.accept()
                    except NoAlertPresentException:
                        # case where there is no alert
                        pass

                    break
            except NoSuchElementException:
                pass

    @pytest.mark.parametrize("server_name, url, username, password", read_configurations_from_file("secret.json"))
    def test_vitals_validation_in_encounters(self, server_name, url, username, password):
        success = login(self.browser, username, password, url, server_name)
        assert success, f"Login failed for server {server_name}"

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

        (patient1Found or patient154Found)[0].click()

        self.browser.switch_to.default_content()

        pastEncounters = self.browser.find_element(By.ID, "pastEncounters")
        pastEncounters.click()

        latestEncounter = self.browser.find_element(By.XPATH, '//*[@id="attendantData"]/div/div[2]/div[1]/div/ul/li['
                                                              '1]/a[1]')
        latestEncounter.click()

        self.browser.implicitly_wait(5)

        # Accessing the nested iframes
        firstIframe = self.browser.find_element(By.XPATH, '//*[@id="framesDisplay"]/div[3]/iframe')
        # Waiting for the iframe contents to load
        self.browser.implicitly_wait(5)
        self.browser.switch_to.frame(firstIframe)

        secondIframe = self.browser.find_element(By.XPATH, '//*[@id="enctabs-1"]/iframe')
        # Waiting for the iframe contents to load
        self.browser.implicitly_wait(5)
        self.browser.switch_to.frame(secondIframe)

        # hamburger_menu = self.browser.find_element(By.XPATH, '/html/body/nav/nav/button')
        # hamburger_menu.click()

        clinicalTab = self.browser.find_element(By.XPATH, '//*[@id="category_Clinical"]')
        clinicalTab.click()

        vitals = self.browser.find_element(By.XPATH, '//div[@id="navbarSupportedContent"]//a[contains(@onclick, "formname=vitals")]')

        vitals.click()

        self.browser.switch_to.parent_frame()

        # Switching to the vitals iframe
        vitalsIframe = self.browser.find_element(By.XPATH, '//*[@id="enctabs-1001"]/iframe')
        # Waiting for the iframe contents to load
        self.browser.implicitly_wait(5)
        self.browser.switch_to.frame(vitalsIframe)

        # Waiting for the input field to be visible and interactable
        WeightinputField = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "weight_input_usa"))
        )

        # Entering invalid value to bypass keypress prevention
        self.browser.execute_script("arguments[0].value = 'abc';", WeightinputField)

        # Triggering the validation logic manually
        WeightinputField.click()
        WeightinputField.send_keys(" ")

        # Saving the validation message
        validation_message = self.browser.execute_script(
            "return arguments[0].validationMessage;", WeightinputField)

        expected_message = "Please enter a valid integer."
        assert validation_message == expected_message

        # Entering a valid input

        HeightinputField = self.browser.find_element(By.ID, 'height_input_usa')
        HeightinputField.send_keys("123")

        # Saving the validation message
        validation_message = self.browser.execute_script(
            "return arguments[0].validationMessage;", HeightinputField)

        expected_message = ""
        assert validation_message == expected_message
