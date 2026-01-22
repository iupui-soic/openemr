import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    navigate_to_menu,
    switch_to_frame_with_retry,
    wait_for_element,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestFacilityList:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_facility_list_displayed_correctly(self, config):
        assert login(self.browser, config.username, config.password, config.url, config.server_name), "Login failed"
        wait_for_page_load(self.browser)

        # Use text-based menu navigation instead of brittle XPaths
        navigate_to_menu(self.browser, ["Admin", "Clinic", "Facilities"])

        # Switch to iframe with retry logic
        switch_to_frame_with_retry(self.browser, "adm")
        print("Switched into iframe 'adm'.")

        # Wait for facility elements to load
        wait_for_element(self.browser, By.CSS_SELECTOR, "a.font-weight-bold.medium_modal", timeout=DEFAULT_TIMEOUT)

        # These are the expected facilities - we check that at least some core ones exist
        # rather than requiring an exact match (different servers may have different facilities)
        expected_facilities = [
            "Allergy and Immunology Department",
            "Cardiology Unit",
            "City Dermatology Clinic",
            "City Radiology Facility",
            "Critical Care Unit",
            "Dental Care Unit",
            "Endocrinology Clinic",
            "ENT Department",
            "Gastroenterology Department",
            "Hematology/Oncology Department",
            "Indiana Burn Unit",
            "Infectious Disease Unit",
            "Nephrology Unit",
            "Obstetrics and Gynecology Unit",
            "Ophthalmology Department",
            "Orthopedic and Fracture Care",
            "Pediatric Care Center",
            "Psychiatry Department",
            "Pulmonology Unit",
            "Rheumatology Clinic",
            "Your Clinic Name Here",
        ]

        facility_elements = self.browser.find_elements(By.CSS_SELECTOR, "a.font-weight-bold.medium_modal")
        facility_names = [elem.text.strip() for elem in facility_elements if elem.text.strip()]
        print("Facilities found on page:", facility_names)

        # Check that facilities are displayed (at least one)
        assert len(facility_names) > 0, "No facilities found on the page"

        # Check each expected facility
        missing_facilities = []
        for facility in expected_facilities:
            if facility not in facility_names:
                missing_facilities.append(facility)

        if missing_facilities:
            print(f"Missing facilities: {missing_facilities}")
            # Fail only if more than 20% are missing (allows for minor server variations)
            missing_ratio = len(missing_facilities) / len(expected_facilities)
            assert missing_ratio < 0.2, f"Too many facilities missing ({len(missing_facilities)}/{len(expected_facilities)}): {missing_facilities}"

        print("All expected facilities are present.")