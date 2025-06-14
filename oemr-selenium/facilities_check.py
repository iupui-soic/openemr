import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_utils import *

class TestFacilityList:
    @pytest.fixture(autouse=True)
    def setup_browser(self): yield from browser_setup_and_teardown(self)


    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_facility_list_displayed_correctly(self, config):
        assert login(self.browser, config.username, config.password, config.url, config.server_name), "Login failed"
        wait_for_page_load(self.browser)

        admin_menu = WebDriverWait(self.browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dropdown-toggle') and normalize-space()='Admin']"))
        )
        admin_menu.click()

        clinic_menu = WebDriverWait(self.browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dropdown-toggle') and normalize-space()='Clinic']"))
        )
        clinic_menu.click()

        facilities_menu = WebDriverWait(self.browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'menuLabel') and normalize-space()='Facilities']"))
        )
        facilities_menu.click()

        wait_for_page_load(self.browser)

        WebDriverWait(self.browser, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "adm"))
        )
        print("Switched into iframe 'adm'.")

        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.font-weight-bold.medium_modal"))
        )

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
        facility_names = [elem.text.strip() for elem in facility_elements]
        print("Facilities found on page:", facility_names)

        for facility in expected_facilities:
            assert facility in facility_names, f"Facility '{facility}' not found on the page."

        print("All expected facilities are present.")
