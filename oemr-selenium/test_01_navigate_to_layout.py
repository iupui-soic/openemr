"""
Test: Navigate to Layout Editor and select Custom User Settings.

Verifies:
    - Layout Editor page loads
    - "Custom User Settings" layout can be selected from the dropdown
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from helpers import (
    create_browser,
    login,
    read_configurations_from_file,
    sanitize_test_name,
    wait_for_page_load,
    js_mousedown,
    DEFAULT_TIMEOUT,
)


def get_configs():
    return read_configurations_from_file('secret.json')


def get_base_url(login_url):
    """Extract base URL from login URL.
    e.g. 'https://host/interface/login/login.php?site=default'
      -> 'https://host/interface'
    """
    idx = login_url.find('/interface/')
    if idx != -1:
        return login_url[:idx + len('/interface')]
    # fallback: strip login path
    return login_url.rsplit('/login/', 1)[0]


def navigate_to_layouts(browser, login_url):
    """
    Navigate to the Layout Editor page.

    OpenEMR's KnockoutJS menu system loads content into internal tabs.
    When you click Admin -> Forms -> Layouts, it loads edit_layout.php
    inside the tab system. We use two strategies:

    Strategy 1: Use JS to trigger the menu click and then find the
                content in the iframe that OpenEMR creates.
    Strategy 2: If that fails, navigate directly to the URL.
    """
    wait_for_page_load(browser)

    # Strategy 1: Trigger the Layouts menu item via JS mousedown,
    # then look for the content in the OpenEMR tab iframe.
    clicked = browser.execute_script("""
        var sections = document.querySelectorAll('.menuSection');
        for (var i = 0; i < sections.length; i++) {
            var topLabel = sections[i].querySelector(':scope > .menuLabel');
            if (topLabel && topLabel.textContent.trim() === 'Admin') {
                var allLabels = sections[i].querySelectorAll('.menuLabel');
                for (var j = 0; j < allLabels.length; j++) {
                    if (allLabels[j].textContent.trim() === 'Layouts') {
                        var evt = new MouseEvent('mousedown', {
                            bubbles: true, cancelable: true, view: window
                        });
                        allLabels[j].dispatchEvent(evt);
                        return 'clicked';
                    }
                }
            }
        }
        return 'not_found';
    """)
    print(f"[DEBUG] Menu JS click result: {clicked}")

    if clicked == 'clicked':
        time.sleep(3)

        # OpenEMR loads content inside iframes within #framesDisplay
        # (same pattern as test.py: '#framesDisplay > div > iframe')
        iframes = browser.find_elements(By.CSS_SELECTOR, '#framesDisplay iframe')
        print(f"[DEBUG] framesDisplay iframes: {len(iframes)}")

        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute('src') or ''
            print(f"[DEBUG]   iframe[{i}] src='{src[:100]}'")
            if 'edit_layout' in src or 'layout' in src.lower():
                browser.switch_to.frame(iframe)
                try:
                    return WebDriverWait(browser, 10).until(
                        EC.visibility_of_element_located((By.ID, "layout_id"))
                    )
                except TimeoutException:
                    browser.switch_to.default_content()

        # Try the last iframe (newest tab)
        if iframes:
            browser.switch_to.default_content()
            browser.switch_to.frame(iframes[-1])
            try:
                return WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located((By.ID, "layout_id"))
                )
            except TimeoutException:
                browser.switch_to.default_content()

    # Strategy 2: Direct URL navigation
    print("[DEBUG] Menu click did not open Layouts. Trying direct URL.")
    base_url = get_base_url(login_url)
    layout_url = f"{base_url}/super/edit_layout.php"
    print(f"[DEBUG] Navigating to: {layout_url}")
    browser.get(layout_url)
    wait_for_page_load(browser)

    try:
        return WebDriverWait(browser, DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located((By.ID, "layout_id"))
        )
    except TimeoutException:
        pass

    # Final debug dump
    print(f"[DEBUG] Final URL: {browser.current_url}")
    print(f"[DEBUG] Page title: {browser.title}")
    print(f"[DEBUG] Body (first 300): {browser.find_element(By.TAG_NAME, 'body').text[:300]}")
    pytest.fail("Could not load Layout Editor page via menu or direct URL.")


class TestNavigateToCustomLayout:

    @pytest.fixture(autouse=True)
    def browser_setup_and_teardown(self, config):
        self.browser = create_browser()
        assert login(
            self.browser,
            config.username,
            config.password,
            config.url,
            config.server_name,
        ), f"Login failed for {config.url}"
        self.login_url = config.url

        yield

        try:
            self.browser.close()
            self.browser.quit()
        except Exception:
            pass

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_open_layouts_page(self, config):
        """Layout Editor page loads with layout dropdown visible."""
        dropdown = navigate_to_layouts(self.browser, self.login_url)
        assert dropdown.is_displayed(), "Layout dropdown not found on Layouts page"

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_select_custom_user_settings(self, config):
        """'Custom User Settings' can be selected from the layout dropdown."""
        dropdown = navigate_to_layouts(self.browser, self.login_url)
        select = Select(dropdown)

        option_texts = [opt.text for opt in select.options]
        print(f"[DEBUG] Layout options: {option_texts}")

        matching = [t for t in option_texts if "Custom User" in t or "USR" in t]
        assert matching, (
            f"No 'Custom User Settings' option found. Available: {option_texts}"
        )

        select.select_by_visible_text(matching[0])
        wait_for_page_load(self.browser)

        body_text = self.browser.find_element(By.TAG_NAME, "body").text
        assert len(body_text) > 50, (
            "Layout editor did not load after selecting Custom User Settings"
        )
