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

class TestWebsite_cdr_code_check:
    @pytest.fixture(autouse=True)
    def setup_browser(self, browser_fixture):
        # self.browser is set via shared browser_fixture in test_utils.py
        pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_code_list_validation(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        iframe = self.browser.find_element(By.NAME, "cod")
        self.browser.switch_to.frame(iframe)

        expected_options = [
            "CPT4 Procedure/Service",
            "HCPCS Procedure/Service",
            "CVX Immunization",
            "ICD10 Diagnosis",
            "SNOMED Diagnosis",
            "SNOMED Clinical Term",
            "SNOMED Procedure",
            "LOINC",
            "PHIN Questions",
            "NCI CONCEPT ID",
            "CQM Valueset",
            "OID Valueset"
        ]

        select_element = self.browser.find_element(By.CSS_SELECTOR, 'select[name="filter[]"]')
        actual_options = [option.text.strip() for option in select_element.find_elements(By.TAG_NAME, 'option')]

        for expected in expected_options:
            assert expected in actual_options, f"{expected} is not present in the dropdown"

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cpt4_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "CPT4 Procedure/Service":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] CPT4 results not loaded properly. Found: {result_text}"
        print(f"[PASS] CPT4 has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cvx_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "CVX Immunization":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] CVX results not loaded properly. Found: {result_text}"
        print(f"[PASS] CVX has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_icd10_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "ICD10 Diagnosis":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] ICD10 results not loaded properly. Found: {result_text}"
        print(f"[PASS] ICD10 has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_snomed_diag_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "SNOMED Diagnosis":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] SNOMED Diagnosis results not loaded properly. Found: {result_text}"
        print(f"[PASS] SNOMED Diagnosis has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_snomed_clinical_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "SNOMED Clinical Term":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] SNOMED Clinical Term results not loaded properly. Found: {result_text}"
        print(f"[PASS] SNOMED Clinical Term has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_snomed_proc_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "SNOMED Procedure":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] SNOMED Procedure results not loaded properly. Found: {result_text}"
        print(f"[PASS] SNOMED Procedure has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_loinc_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "LOINC":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] LOINC results not loaded properly. Found: {result_text}"
        print(f"[PASS] LOINC has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_nci_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "NCI CONCEPT ID":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 15 of" in result_text, f"[FAIL] NCI CONCEPT ID results not loaded properly. Found: {result_text}"
        print(f"[PASS] NCI CONCEPT ID has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cqm_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "CQM Valueset":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] CQM Valueset results not loaded properly. Found: {result_text}"
        print(f"[PASS] CQM Valueset has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_oid_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        actions = ActionChains(self.browser)

        adminMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/div'))
        )
        actions.move_to_element(adminMenu).perform()
        wait_for_page_load(self.browser)

        codingMenu = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/div'))
        )
        actions.move_to_element(codingMenu).perform()
        wait_for_page_load(self.browser)

        codesOption = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainMenu"]/div/div[10]/div/ul/li[5]/div/ul/li[1]/div'))
        )
        codesOption.click()
        wait_for_page_load(self.browser)

        self.browser.switch_to.frame(self.browser.find_element(By.NAME, "cod"))
        wait_for_page_load(self.browser)

        dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="filter[]"]'))
        )
        for option in dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == "OID Valueset":
                option.click()
                break

        search_button = self.browser.find_element(By.CSS_SELECTOR, 'input[value="Search"]')
        search_button.click()
        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

        result_text = self.browser.find_element(By.XPATH, '//div[@class="col-md text-right"]').text.strip()

        assert "1 - 100 of" in result_text, f"[FAIL] OID Valueset results not loaded properly. Found: {result_text}"
        print(f"[PASS] OID Valueset has results. Text: {result_text}")

        self.browser.switch_to.default_content()









