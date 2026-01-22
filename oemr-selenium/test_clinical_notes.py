import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_for_element,
    wait_for_clickable,
    wait_and_js_click,
    switch_to_frame_with_retry,
    js_click,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestWebsite_vitals:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    def _search_and_select_patient(self, patient_name="Abbott"):
        """Search for a patient and click the first result."""
        search_box = wait_for_element(self.browser, By.ID, 'anySearchBox')
        search_box.clear()
        search_box.send_keys(patient_name)
        wait_and_js_click(self.browser, By.ID, 'search_globals')
        wait_for_page_load(self.browser)

        switch_to_frame_with_retry(self.browser, "fin")

        first_patient = WebDriverWait(self.browser, DEFAULT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr td a'))
        )[0]
        js_click(self.browser, first_patient)

        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

    def _handle_modal_popup(self):
        """Handle any modal popup that might block interactions."""
        try:
            WebDriverWait(self.browser, 3).until(
                EC.presence_of_element_located((By.ID, "modalframe"))
            )
            self.browser.switch_to.frame("modalframe")
            close_button = wait_for_clickable(self.browser, By.ID, "close", timeout=5)
            js_click(self.browser, close_button)
            self.browser.switch_to.default_content()
            wait_for_page_load(self.browser)
        except (NoSuchElementException, TimeoutException):
            pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_clinical_notes_is_present_in_encounters(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._search_and_select_patient('Abbott')

        # Try to click Past Encounters
        try:
            pastEncounters = wait_for_clickable(self.browser, By.ID, "pastEncounters", timeout=5)
            js_click(self.browser, pastEncounters)
        except Exception:
            print("'Past Encounters' was blocked, checking for popups...")
            self._handle_modal_popup()

            try:
                pastEncounters = wait_for_clickable(self.browser, By.ID, "pastEncounters", timeout=5)
                js_click(self.browser, pastEncounters)
            except Exception:
                pass

        wait_for_page_load(self.browser)

        # Click latest encounter - try multiple selectors
        encounter_selectors = [
            '//*[@id="attendantData"]/div/div[2]/div[1]/div/ul/li[1]/a[1]',
            '//ul[contains(@class, "encounter")]//li[1]//a',
            '//a[contains(@onclick, "encounter")]',
        ]

        for selector in encounter_selectors:
            try:
                latestEncounter = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                js_click(self.browser, latestEncounter)
                break
            except Exception:
                continue

        wait_for_page_load(self.browser)

        # Switch to first iframe - try multiple strategies
        iframe_selectors = [
            '//*[@id="framesDisplay"]/div[3]/iframe',
            '//iframe[contains(@name, "enc")]',
            '#framesDisplay iframe',
        ]

        for selector in iframe_selectors:
            try:
                if selector.startswith('//') or selector.startswith('/'):
                    firstIframe = WebDriverWait(self.browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    firstIframe = WebDriverWait(self.browser, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                self.browser.switch_to.frame(firstIframe)
                break
            except Exception:
                continue

        wait_for_page_load(self.browser)

        # Switch to second iframe
        try:
            secondIframe = wait_for_element(self.browser, By.XPATH, '//*[@id="enctabs-1"]/iframe')
            self.browser.switch_to.frame(secondIframe)
            wait_for_page_load(self.browser)
        except Exception:
            pass

        try:
            clinical_notes_divs = self.browser.find_elements(
                By.XPATH, "//div[starts-with(@id, 'clinical_notes~')]"
            )
            assert clinical_notes_divs, \
                "Clinical Notes section not found (no div with id starting with 'clinical_notes~')."

            clinical_notes_found_with_data = False

            for div in clinical_notes_divs:
                try:
                    section_element = div.find_element(
                        By.XPATH, ".//section[contains(@class, 'mb-3')]"
                    )
                    section_text = section_element.text.strip()

                    print(f"Clinical Notes content preview: {section_text[:100]}")

                    if section_text:
                        clinical_notes_found_with_data = True
                        break
                except NoSuchElementException:
                    continue

            assert clinical_notes_found_with_data, \
                "Clinical Notes section found, but no content present in <section class='mb-3'>."

            print("Clinical Notes are present and contain data.")

        except AssertionError as ae:
            pytest.fail(str(ae))
        except Exception as e:
            pytest.fail(f"Error while checking Clinical Notes: {str(e)}")
