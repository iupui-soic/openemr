import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_utils import *

class TestBPValues:
    @pytest.fixture(autouse=True)
    def setup_browser(self, browser_fixture):
        # self.browser is set via shared browser_fixture in test_utils.py
        pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_bp_systolic_and_diastolic_present(self, config):
        assert login(self.browser, config.username, config.password, config.url, config.server_name), "Login failed"
        wait_for_page_load(self.browser)

        search_box = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "anySearchBox")))
        search_box.clear()
        search_box.send_keys("a")
        self.browser.find_element(By.ID, "search_globals").click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fin")))
        first_patient = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tr td a"))
        )
        self.browser.execute_script("arguments[0].scrollIntoView(true);", first_patient)
        first_patient.click()

        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.ID, "pastEncounters"))).click()
        wait_for_page_load(self.browser)
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="attendantData"]/div/div[2]/div[1]/div/ul/li[1]/a[1]'))
        ).click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.XPATH, '//*[@id="framesDisplay"]/div[3]/iframe'))
        self.browser.switch_to.frame(self.browser.find_element(By.XPATH, '//*[@id="enctabs-1"]/iframe'))
        self.browser.find_element(By.XPATH, '//*[@id="category_Clinical"]').click()
        wait_for_page_load(self.browser)
        self.browser.find_element(By.XPATH, '//div[@id="navbarSupportedContent"]//a[contains(@onclick, "formname=vitals")]').click()
        wait_for_page_load(self.browser)
        self.browser.switch_to.parent_frame()
        self.browser.switch_to.frame(self.browser.find_element(By.XPATH, '//*[@id="enctabs-1001"]/iframe'))
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table')))

        systolic_value = ""
        diastolic_value = ""

        try:
            systolic_cell = self.browser.find_element(
                By.XPATH, '//tr[td[@id="bps"]]/td[contains(@class, "historicalvalues")]'
            )
            systolic_value = systolic_cell.text.strip()
            print("Systolic value found:", systolic_value)
        except Exception as e:
            print("Could not find systolic:", e)

        try:
            diastolic_cell = self.browser.find_element(
                By.XPATH, '//tr[td[@id="bpd"]]/td[contains(@class, "historicalvalues")]'
            )
            diastolic_value = diastolic_cell.text.strip()
            print("Diastolic value found:", diastolic_value)
        except Exception as e:
            print("Could not find diastolic:", e)

        assert systolic_value != "", "Systolic BP value is missing"
        assert diastolic_value != "", "Diastolic BP value is missing"

