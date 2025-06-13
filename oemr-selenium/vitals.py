import pytest
import os
from selenium import webdriver
from selenium.common import NoSuchElementException, NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
from test_utils import *
import re

class TestWebsite_vitals:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        options = Options()
        if os.environ.get('HEADLESS', 'false').lower() == 'true':
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument('--window-size=1920,1080')
            options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Chrome(options=options)
        self.browser.maximize_window()
        self.browser.implicitly_wait(10)
        yield
        self.browser.close()
        self.browser.quit()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_vitals_is_present_on_patient_dashboard(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = self.browser.find_element(By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('a')
        self.browser.find_element(By.ID, 'search_globals').click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fin")))
        wait_for_page_load(self.browser)

        first_patient = self.browser.find_elements(By.CSS_SELECTOR, 'tr td a')[0]
        first_patient.click()
        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

        iframe = self.browser.find_element(By.CSS_SELECTOR, '#framesDisplay > div > iframe')
        self.browser.switch_to.frame(iframe)
        wait_for_page_load(self.browser)

        container_div = self.browser.find_element(By.ID, 'container_div')
        main_divs = container_div.find_elements(By.CLASS_NAME, 'main.mb-5')
        for div in main_divs:
            try:
                class_row = div.find_element(By.CLASS_NAME, 'row')
                card_sections = class_row.find_elements(By.CSS_SELECTOR, 'section.card.mb-2')
                if card_sections:
                    last_card_section = card_sections[-1]
                    vitals_expand_div = last_card_section.find_element(By.ID, 'vitals_ps_expand')
                    link_to_click = vitals_expand_div.find_element(By.PARTIAL_LINK_TEXT,
                                                                   'Click here to view and graph all vitals.')
                    link_to_click.click()
                    wait_for_page_load(self.browser)
                    try:
                        alert = Alert(self.browser)
                        alert.accept()
                    except NoAlertPresentException:
                        pass
                    break
            except NoSuchElementException:
                pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_vitals_validation_in_encounters(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "anySearchBox"))
        )
        search_box.clear()
        search_box.send_keys('a')
        self.browser.find_element(By.ID, 'search_globals').click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fin")))
        wait_for_page_load(self.browser)

        first_patient = WebDriverWait(self.browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr td a'))
        )[0]
        first_patient.click()
        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

        try:
            pastEncounters = WebDriverWait(self.browser, 5).until(
                EC.element_to_be_clickable((By.ID, "pastEncounters"))
            )
            pastEncounters.click()
        except Exception as e:
            print(f"'Past Encounters' was blocked, checking for popups...")

            try:
                WebDriverWait(self.browser, 3).until(EC.presence_of_element_located((By.ID, "modalframe")))
                self.browser.switch_to.frame("modalframe")

                close_button = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.ID, "close"))
                )
                close_button.click()
                self.browser.switch_to.default_content()
                wait_for_page_load(self.browser)

                pastEncounters = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.ID, "pastEncounters"))
                )
                pastEncounters.click()
            except (NoSuchElementException, TimeoutException) as e:
                print(e)

        wait_for_page_load(self.browser)

        latestEncounter = self.browser.find_element(By.XPATH, '//*[@id="attendantData"]/div/div[2]/div[1]/div/ul/li[1]/a[1]')
        latestEncounter.click()
        wait_for_page_load(self.browser)

        firstIframe = self.browser.find_element(By.XPATH, '//*[@id="framesDisplay"]/div[3]/iframe')
        self.browser.switch_to.frame(firstIframe)
        wait_for_page_load(self.browser)

        secondIframe = self.browser.find_element(By.XPATH, '//*[@id="enctabs-1"]/iframe')
        self.browser.switch_to.frame(secondIframe)
        wait_for_page_load(self.browser)

        clinicalTab = self.browser.find_element(By.XPATH, '//*[@id="category_Clinical"]')
        clinicalTab.click()
        wait_for_page_load(self.browser)

        vitals = self.browser.find_element(By.XPATH, '//div[@id="navbarSupportedContent"]//a[contains(@onclick, "formname=vitals")]')
        vitals.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.parent_frame()

        vitalsIframe = self.browser.find_element(By.XPATH, '//*[@id="enctabs-1001"]/iframe')
        self.browser.switch_to.frame(vitalsIframe)
        wait_for_page_load(self.browser)

        WeightinputField = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "weight_input_usa"))
        )
        self.browser.execute_script("arguments[0].value = 'abc';", WeightinputField)
        WeightinputField.click()
        WeightinputField.send_keys(" ")

        validation_message = self.browser.execute_script(
            "return arguments[0].validationMessage;", WeightinputField)
        assert validation_message == "Please enter a valid integer."

        HeightinputField = self.browser.find_element(By.ID, 'height_input_usa')
        HeightinputField.send_keys("123")
        validation_message = self.browser.execute_script(
            "return arguments[0].validationMessage;", HeightinputField)
        assert validation_message == ""

