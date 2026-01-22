import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    navigate_to_menu,
    switch_to_frame_with_retry,
    get_element_text_with_retry,
    select_dropdown_option,
    wait_and_js_click,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestWebsite_cdr_code_check:
    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    def _navigate_to_codes_page(self):
        """Navigate to Admin > Coding > Codes page."""
        navigate_to_menu(self.browser, ["Admin", "Coding", "Codes"])
        switch_to_frame_with_retry(self.browser, "cod")

    def _search_code_type(self, code_type):
        """Select a code type from dropdown and click Search."""
        select_dropdown_option(
            self.browser,
            (By.CSS_SELECTOR, 'select[name="filter[]"]'),
            code_type
        )

        # Click search button
        wait_and_js_click(self.browser, By.CSS_SELECTOR, 'input[value="Search"]')
        wait_for_page_load(self.browser)

        # Wait for results
        WebDriverWait(self.browser, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="col-md text-right"]'))
        )
        wait_for_page_load(self.browser)

    def _verify_code_results(self, code_name):
        """Verify that code search returned results."""
        result_text = get_element_text_with_retry(
            self.browser,
            By.XPATH,
            '//div[@class="col-md text-right"]'
        )

        assert "1 -" in result_text and "of" in result_text, \
            f"[FAIL] {code_name} results not loaded properly. Found: {result_text}"
        print(f"[PASS] {code_name} has results. Text: {result_text}")

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_code_list_validation(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()

        # These are the code types available in OpenEMR (must be enabled in Admin > Coding > Code Types)
        expected_options = [
            "CPT4 Procedure/Service",
            "HCPCS Procedure/Service",
            "CVX Immunization",
            "ICD10 Diagnosis",
            "SNOMED Diagnosis",
            "SNOMED Clinical Term",
            "SNOMED Procedure",
            "RXCUI Medication",
            "LOINC",
            "PHIN Questions",
            "NCI CONCEPT ID",
            "CQM Valueset",
            "OID Valueset",
        ]

        select_element = self.browser.find_element(By.CSS_SELECTOR, 'select[name="filter[]"]')
        actual_options = [option.text.strip() for option in select_element.find_elements(By.TAG_NAME, 'option')]

        missing_options = []
        for expected in expected_options:
            if expected not in actual_options:
                missing_options.append(expected)

        if missing_options:
            print(f"Missing code types: {missing_options}")

        assert len(missing_options) == 0, f"Missing code types: {missing_options}"

        self.browser.switch_to.default_content()

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cpt4_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("CPT4 Procedure/Service")
        self._verify_code_results("CPT4")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cvx_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("CVX Immunization")
        self._verify_code_results("CVX")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_icd10_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("ICD10 Diagnosis")
        self._verify_code_results("ICD10")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_snomed_diag_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("SNOMED Diagnosis")
        self._verify_code_results("SNOMED Diagnosis")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_snomed_clinical_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("SNOMED Clinical Term")
        self._verify_code_results("SNOMED Clinical Term")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_snomed_proc_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("SNOMED Procedure")
        self._verify_code_results("SNOMED Procedure")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_loinc_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("LOINC")
        self._verify_code_results("LOINC")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_nci_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("NCI CONCEPT ID")
        self._verify_code_results("NCI CONCEPT ID")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_cqm_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("CQM Valueset")
        self._verify_code_results("CQM Valueset")

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_oid_code_data_presence(self, config):
        success = login(self.browser, config.username, config.password, config.url, config.server_name)
        assert success, f"Login failed for server {config.url}"
        wait_for_page_load(self.browser)

        self._navigate_to_codes_page()
        self._search_code_type("OID Valueset")
        self._verify_code_results("OID Valueset")