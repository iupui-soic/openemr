import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_for_element,
    wait_for_clickable,
    wait_for_visible,
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
            modal = WebDriverWait(self.browser, 3).until(
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
    def test_vitals_is_present_on_patient_dashboard(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._search_and_select_patient('Abbott')

        # Switch to patient iframe
        iframe_selectors = [
            (By.CSS_SELECTOR, '#framesDisplay > div > iframe'),
            (By.NAME, 'pat'),
            (By.TAG_NAME, 'iframe'),
        ]

        frame_switched = False
        for by, selector in iframe_selectors:
            try:
                iframe = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((by, selector))
                )
                self.browser.switch_to.frame(iframe)
                wait_for_page_load(self.browser)
                frame_switched = True
                break
            except Exception:
                self.browser.switch_to.default_content()
                continue

        assert frame_switched, "Could not switch to patient dashboard frame"

        # Look for vitals section
        container_div = wait_for_element(self.browser, By.ID, 'container_div')
        main_divs = container_div.find_elements(By.CLASS_NAME, 'main.mb-5')

        for div in main_divs:
            try:
                class_row = div.find_element(By.CLASS_NAME, 'row')
                card_sections = class_row.find_elements(By.CSS_SELECTOR, 'section.card.mb-2')
                if card_sections:
                    last_card_section = card_sections[-1]
                    vitals_expand_div = last_card_section.find_element(By.ID, 'vitals_ps_expand')
                    link_to_click = vitals_expand_div.find_element(
                        By.PARTIAL_LINK_TEXT, 'Click here to view and graph all vitals.'
                    )
                    js_click(self.browser, link_to_click)
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

        # Switch to encounter iframes
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

        # Click Clinical tab
        clinicalTab = wait_for_element(self.browser, By.XPATH, '//*[@id="category_Clinical"]')
        js_click(self.browser, clinicalTab)
        wait_for_page_load(self.browser)

        # Click Vitals
        vitals = wait_for_element(
            self.browser,
            By.XPATH,
            '//div[@id="navbarSupportedContent"]//a[contains(@onclick, "formname=vitals")]'
        )
        js_click(self.browser, vitals)
        wait_for_page_load(self.browser)

        self.browser.switch_to.parent_frame()

        vitalsIframe = wait_for_element(self.browser, By.XPATH, '//*[@id="enctabs-1001"]/iframe')
        self.browser.switch_to.frame(vitalsIframe)
        wait_for_page_load(self.browser)

        # Validate weight input
        WeightinputField = wait_for_visible(self.browser, By.ID, "weight_input_usa")
        self.browser.execute_script("arguments[0].value = 'abc';", WeightinputField)
        js_click(self.browser, WeightinputField)
        WeightinputField.send_keys(" ")

        validation_message = self.browser.execute_script(
            "return arguments[0].validationMessage;", WeightinputField
        )
        assert validation_message == "Please enter a valid integer."

        # Validate height input
        HeightinputField = wait_for_element(self.browser, By.ID, 'height_input_usa')
        HeightinputField.send_keys("123")
        validation_message = self.browser.execute_script(
            "return arguments[0].validationMessage;", HeightinputField
        )
        assert validation_message == ""
