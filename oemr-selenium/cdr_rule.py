# Complete cdr_rule.py with Full-Page Load Check Added

import pytest
import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cdr_rule_validation(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        adminMenu = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div')
        hover_script = """
            var element = arguments[0];
            var event = new MouseEvent('mouseover', {bubbles: true, cancelable: true});
            element.dispatchEvent(event);
            """
        self.browser.execute_script(hover_script, adminMenu)
        wait_for_page_load(self.browser)

        practiceMenu = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/div')
        self.browser.execute_script(hover_script, practiceMenu)
        wait_for_page_load(self.browser)

        rules = self.browser.find_element(By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[4]/div/ul/li[2]/div')
        self.browser.execute_script("arguments[0].click();", rules)
        wait_for_page_load(self.browser)

        pap_link = None
        try:
            pap_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Pap Smear")
        except:
            frames = self.browser.find_elements(By.TAG_NAME, "iframe")
            for frame in frames:
                try:
                    self.browser.switch_to.frame(frame)
                    pap_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Pap Smear")
                    if pap_link:
                        break
                except:
                    self.browser.switch_to.default_content()

        if not pap_link:
            raise AssertionError("Could not find Pap Smear link")

        self.browser.execute_script("arguments[0].click();", pap_link)
        wait_for_page_load(self.browser)

        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        assert "Cancer Screening: Pap Smear" in page_text or "Pap" in page_text, "Rule detail page not loaded"
        assert "Reminder" in page_text or "Clinical" in page_text, "Missing reminder information"
        assert "Female" in page_text or "Age" in page_text, "Missing criteria information"

        try:
            add_button = None
            try:
                add_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'add')]")
            except:
                try:
                    add_button = self.browser.find_element(By.XPATH, "//a[contains(text(), 'add')]")
                except:
                    try:
                        inclusion_section = self.browser.find_element(By.XPATH, "//*[contains(text(), 'Inclusion/Exclusion')]")
                        add_button = inclusion_section.find_element(By.XPATH, ".//following::*[contains(text(), 'add')][1]")
                    except:
                        frames = self.browser.find_elements(By.TAG_NAME, "iframe")
                        for frame in frames:
                            try:
                                self.browser.switch_to.frame(frame)
                                add_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'add')] | //a[contains(text(), 'add')]")
                                if add_button:
                                    break
                            except:
                                self.browser.switch_to.default_content()
            if not add_button:
                raise AssertionError("Could not find 'add' button for Inclusion/Exclusion criteria")
            self.browser.execute_script("arguments[0].click();", add_button)
            wait_for_page_load(self.browser)

            age_min_link = self.browser.find_element(By.LINK_TEXT, "Age min")
            self.browser.execute_script("arguments[0].click();", age_min_link)
            wait_for_page_load(self.browser)

            age_input = None
            try:
                age_input = self.browser.find_element(By.XPATH, "//input[@type='text' or @type='number'][1]")
            except:
                try:
                    age_input = self.browser.find_element(By.TAG_NAME, "input")
                except:
                    raise AssertionError("Could not find Age Min input field")

            age_input.clear()
            age_input.send_keys("abc")
            wait_for_page_load(self.browser)

            age_input.clear()
            age_input.send_keys("18")
            wait_for_page_load(self.browser)
            input_value = age_input.get_attribute("value")
            assert input_value == "18", f"Expected Age Min to be '18', but got '{input_value}'"

            cancel_button = self.browser.find_element(By.XPATH, "//button[text()='Cancel'] | //a[text()='Cancel']")
            self.browser.execute_script("arguments[0].click();", cancel_button)
            wait_for_page_load(self.browser)

            page_text = self.browser.find_element(By.TAG_NAME, "body").text
            assert "Rule Detail" in page_text or "Cancer Screening: Pap Smear" in page_text, "Did not return to Rule Detail page after Cancel"

            add_button_2 = None
            try:
                add_button_2 = self.browser.find_element(By.XPATH, "//button[contains(text(), 'add')]")
            except:
                try:
                    add_button_2 = self.browser.find_element(By.XPATH, "//a[contains(text(), 'add')]")
                except:
                    try:
                        inclusion_section = self.browser.find_element(By.XPATH, "//*[contains(text(), 'Inclusion/Exclusion')]")
                        add_button_2 = inclusion_section.find_element(By.XPATH, ".//following::*[contains(text(), 'add')][1]")
                    except:
                        frames = self.browser.find_elements(By.TAG_NAME, "iframe")
                        for frame in frames:
                            try:
                                self.browser.switch_to.frame(frame)
                                add_button_2 = self.browser.find_element(By.XPATH, "//button[contains(text(), 'add')] | //a[contains(text(), 'add')]")
                                if add_button_2:
                                    break
                            except:
                                self.browser.switch_to.default_content()
            if not add_button_2:
                raise AssertionError("Could not find 'add' button for the second test")
            self.browser.execute_script("arguments[0].click();", add_button_2)
            wait_for_page_load(self.browser)

            sex_link = self.browser.find_element(By.LINK_TEXT, "Sex")
            self.browser.execute_script("arguments[0].click();", sex_link)
            wait_for_page_load(self.browser)

            sex_dropdown = None
            try:
                sex_dropdown = self.browser.find_element(By.XPATH, "//select[contains(@id, 'sex') or contains(@name, 'sex')]")
            except:
                try:
                    sex_dropdown = self.browser.find_element(By.XPATH, "//label[contains(text(), 'Sex')]/..//select")
                except:
                    try:
                        sex_dropdown = self.browser.find_element(By.TAG_NAME, "select")
                    except:
                        raise AssertionError("Could not find Sex dropdown field")

            sex_dropdown.click()
            wait_for_page_load(self.browser)

            options = sex_dropdown.find_elements(By.TAG_NAME, "option")
            option_texts = [opt.text for opt in options]
            assert "Female" in option_texts or "female" in str(option_texts).lower()

            for option in options:
                if "Female" in option.text or "female" in option.text.lower():
                    option.click()
                    break
            wait_for_page_load(self.browser)

            cancel_button_2 = self.browser.find_element(By.XPATH, "//button[text()='Cancel'] | //a[text()='Cancel']")
            self.browser.execute_script("arguments[0].click();", cancel_button_2)
            wait_for_page_load(self.browser)

            clinical_targets_add_button = self.browser.find_element(By.XPATH, "//*[contains(text(), 'Clinical targets')]//a[contains(text(),'add')]")
            self.browser.execute_script("arguments[0].click();", clinical_targets_add_button)
            wait_for_page_load(self.browser)

            lifestyle_link = self.browser.find_element(By.LINK_TEXT, "Lifestyle")
            self.browser.execute_script("arguments[0].click();", lifestyle_link)
            wait_for_page_load(self.browser)

            lifestyle_dropdown = self.browser.find_element(By.TAG_NAME, "select")
            options = lifestyle_dropdown.find_elements(By.TAG_NAME, "option")
            option_texts = [opt.text for opt in options]
            assert "Tobacco" in option_texts, "Tobacco option not found in Lifestyle dropdown"

            for option in options:
                if "Tobacco" in option.text:
                    option.click()
                    break
            wait_for_page_load(self.browser)

            cancel_button_3 = self.browser.find_element(By.XPATH, "//a[text()='Cancel']")
            self.browser.execute_script("arguments[0].click();", cancel_button_3)
            wait_for_page_load(self.browser)

        except Exception:
            raise
