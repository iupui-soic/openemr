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
    def setup_browser(self): yield from browser_setup_and_teardown(self)

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_medications_are_present_on_patient_dashboard(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        search_box = self.browser.find_element(By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys('a')
        self.browser.find_element(By.ID, 'search_globals').click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "fin"))
        )
        wait_for_page_load(self.browser)

        first_patient = self.browser.find_elements(By.CSS_SELECTOR, 'tr td a')[0]
        first_patient.click()
        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "pat"))
        )
        wait_for_page_load(self.browser)

        try:
            medication_section = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, 'medication_ps_expand'))
            )

            if "collapse show" not in medication_section.get_attribute("class"):
                card_header = medication_section.find_element(By.XPATH, "./preceding-sibling::h6")
                card_header.click()
                wait_for_page_load(self.browser)

            med_elements = medication_section.find_elements(By.CLASS_NAME, 'font-weight-normal')
            med_text = " ".join([med.text.strip().lower() for med in med_elements if med.text.strip()])
            print(f"[DEBUG] Medication text found: '{med_text}'")

            empty_indicators = [
                "none", "nothing", "no medications", "no medication",
                "not recorded", "not available", "nothing recorded",
                "no data", "n/a"
            ]

            if med_text == "" or any(indicator in med_text for indicator in empty_indicators):
                pytest.fail(f"Medication section contains no valid data: '{med_text}'")
            else:
                assert True

        except TimeoutException as e:
            pytest.fail("Timed out waiting for the medication section to load.")
        except NoSuchElementException as e:
            pytest.fail(f"Medication section or content not found: {str(e)}")

