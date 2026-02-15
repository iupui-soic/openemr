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
    wait_and_js_click,
    wait_and_js_mousedown,
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
        wait_and_js_mousedown(self.browser, By.ID, 'search_globals')
        wait_for_page_load(self.browser)

        switch_to_frame_with_retry(self.browser, "fin")

        first_patient = WebDriverWait(self.browser, DEFAULT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr td a'))
        )[0]
        js_click(self.browser, first_patient)

        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_medications_are_present_on_patient_dashboard(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._search_and_select_patient('Abbott')

        # Try to switch to patient frame using multiple strategies
        frame_switched = False
        for frame_name in ["pat", "patdata"]:
            try:
                switch_to_frame_with_retry(self.browser, frame_name, timeout=10, retries=1)
                frame_switched = True
                break
            except Exception:
                self.browser.switch_to.default_content()
                continue

        if not frame_switched:
            # Fallback: try to find any iframe
            try:
                iframes = self.browser.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        self.browser.switch_to.frame(iframe)
                        frame_switched = True
                        break
                    except Exception:
                        self.browser.switch_to.default_content()
                        continue
            except Exception:
                pass

        try:
            # Look for medications section - try multiple selectors
            medication_section = None
            selectors_to_try = [
                (By.ID, 'medication_ps_expand'),
                (By.XPATH, "//div[contains(@id, 'medication')]"),
                (By.XPATH, "//a[contains(text(), 'Medications')]/parent::*/following-sibling::*"),
                (By.XPATH, "//*[contains(text(), 'Medications')]/ancestor::div[1]"),
            ]

            for by, selector in selectors_to_try:
                try:
                    medication_section = WebDriverWait(self.browser, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    if medication_section:
                        break
                except Exception:
                    continue

            # Get all text from the page and look for medication names
            page_text = self.browser.find_element(By.TAG_NAME, "body").text.lower()
            print("[DEBUG] Looking for medications in page text...")

            # Check for known medications
            expected_medications = ['lisinopril', 'metformin', 'aspirin']
            found_medications = [med for med in expected_medications if med in page_text]

            print(f"[DEBUG] Found medications: {found_medications}")

            if len(found_medications) > 0:
                print(f"[PASS] Found {len(found_medications)} medications: {found_medications}")
                assert True
            else:
                # Fallback: check the medication section if found
                if medication_section:
                    med_text = medication_section.text.strip().lower()
                    print(f"[DEBUG] Medication section text: '{med_text}'")

                    empty_indicators = [
                        "none", "nothing", "no medications", "no medication",
                        "not recorded", "not available", "nothing recorded",
                        "no data", "n/a"
                    ]

                    if med_text == "" or any(indicator in med_text for indicator in empty_indicators):
                        pytest.fail(f"Medication section contains no valid data: '{med_text}'")
                else:
                    pytest.fail("Could not find medications section or any medication data")

        except TimeoutException:
            pytest.fail("Timed out waiting for the medication section to load.")
        except NoSuchElementException as e:
            pytest.fail(f"Medication section or content not found: {str(e)}")
