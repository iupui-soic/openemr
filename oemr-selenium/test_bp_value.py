import pytest
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from helpers import (
    read_configurations_from_file,
    sanitize_test_name,
    login,
    wait_for_page_load,
    wait_for_element,
    wait_for_clickable,
    wait_and_js_click,
    wait_and_js_mousedown,
    switch_to_frame_with_retry,
    js_click,
    create_browser,
    DEFAULT_TIMEOUT,
)


class TestBPValues:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.browser = create_browser()
        yield
        try:
            self.browser.quit()
        except Exception:
            pass

    @pytest.mark.parametrize("config", read_configurations_from_file("secret.json"), ids=sanitize_test_name)
    def test_bp_systolic_and_diastolic_present(self, config):
        """Test that Blood Pressure values are present on the patient dashboard."""
        assert login(self.browser, config.username, config.password, config.url, config.server_name), "Login failed"
        wait_for_page_load(self.browser)

        # Search for patient with test data (Charles Abbott)
        search_box = wait_for_element(self.browser, By.ID, "anySearchBox")
        search_box.clear()
        search_box.send_keys("Abbott")
        wait_and_js_mousedown(self.browser, By.ID, "search_globals")
        wait_for_page_load(self.browser)

        # Click first patient in search results
        switch_to_frame_with_retry(self.browser, "fin")

        first_patient = wait_for_clickable(self.browser, By.CSS_SELECTOR, "tr td a")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", first_patient)
        js_click(self.browser, first_patient)

        self.browser.switch_to.default_content()
        wait_for_page_load(self.browser)

        # Wait for patient dashboard to load - try multiple frame strategies
        time.sleep(1)  # Brief wait for frame to appear after patient selection

        # Switch to patient dashboard frame - try different frame names
        frame_switched = False
        for frame_name in ["pat", "patdata", "RTop"]:
            try:
                switch_to_frame_with_retry(self.browser, frame_name, timeout=10, retries=1)
                frame_switched = True
                break
            except Exception:
                self.browser.switch_to.default_content()
                continue

        if not frame_switched:
            # Fallback: try to find any iframe and switch to it
            try:
                iframes = self.browser.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        self.browser.switch_to.frame(iframe)
                        # Check if this frame has vitals content
                        body_text = self.browser.find_element(By.TAG_NAME, "body").text
                        if "Blood Pressure" in body_text or "Vitals" in body_text:
                            frame_switched = True
                            break
                        self.browser.switch_to.default_content()
                    except Exception:
                        self.browser.switch_to.default_content()
                        continue
            except Exception:
                pass

        assert frame_switched, "Could not switch to patient dashboard frame"

        # Get page text and look for Blood Pressure
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        print(f"[DEBUG] Looking for Blood Pressure in patient dashboard...")

        # Look for BP pattern like "Blood Pressure: 118/78" or "Blood Pressure:118/78"
        bp_pattern = r'Blood Pressure[:\s]*(\d+)[/](\d+)'
        bp_match = re.search(bp_pattern, page_text)

        if bp_match:
            systolic = bp_match.group(1)
            diastolic = bp_match.group(2)
            print(f"[PASS] Blood Pressure found: {systolic}/{diastolic}")
            assert systolic != "", "Systolic BP value is missing"
            assert diastolic != "", "Diastolic BP value is missing"
            assert int(systolic) > 0, "Systolic BP should be a positive number"
            assert int(diastolic) > 0, "Diastolic BP should be a positive number"
        else:
            # Fallback: look for vitals section
            try:
                vitals_section = self.browser.find_element(By.XPATH, "//*[contains(text(), 'Vitals')]")
                vitals_text = vitals_section.find_element(By.XPATH, "./ancestor::div[1]").text
                print(f"[DEBUG] Vitals section text: {vitals_text}")

                bp_match = re.search(bp_pattern, vitals_text)
                if bp_match:
                    systolic = bp_match.group(1)
                    diastolic = bp_match.group(2)
                    print(f"[PASS] Blood Pressure found in vitals section: {systolic}/{diastolic}")
                    assert True
                else:
                    pytest.fail(f"Blood Pressure values not found in vitals section")
            except Exception as e:
                pytest.fail(f"Could not find Blood Pressure data: {e}")