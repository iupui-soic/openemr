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
            options.add_argument("--disable-dev-shm-usage")

        self.browser = webdriver.Chrome(options=options)
        self.browser.maximize_window()
        self.browser.implicitly_wait(10)
        yield
        self.browser.close()
        self.browser.quit()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_clinical_notes_is_present_in_encounters(self, config):
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
            except (NoSuchElementException, TimeoutException):
                pass

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

        clinical_notes = self.browser.find_elements(By.XPATH, "//div[starts-with(@id, 'clinical_notes~')]")
        wait_for_page_load(self.browser)

        try:
            clinical_notes_divs = self.browser.find_elements(By.XPATH, "//div[starts-with(@id, 'clinical_notes~')]")
            assert clinical_notes_divs, "Clinical Notes section not found (no div with id starting with 'clinical_notes~')."

            clinical_notes_found_with_data = False

            for div in clinical_notes_divs:
                try:
                    section_element = div.find_element(By.XPATH, ".//section[contains(@class, 'mb-3')]")
                    section_text = section_element.text.strip()

                    print(f"Clinical Notes content preview: {section_text[:100]}")

                    if section_text:
                        clinical_notes_found_with_data = True
                        break
                except NoSuchElementException:
                    continue

            assert clinical_notes_found_with_data, "Clinical Notes section found, but no content present in <section class='mb-3'>."

            print("Clinical Notes are present and contain data.")

        except AssertionError as ae:
            pytest.fail(str(ae))
        except Exception as e:
            pytest.fail(f"Error while checking Clinical Notes: {str(e)}")


