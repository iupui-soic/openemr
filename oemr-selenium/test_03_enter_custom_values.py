"""
Test: Enter sample values into custom user settings fields.

Key insight: The User Settings page has MULTIPLE elements with the same
ID (form_1, form_2, form_3) — one per tab panel. getElementById returns
the FIRST one (usually Appearance tab), not the Custom tab's version.

Solution: Use querySelectorAll to find ALL matching elements, then pick
the one inside the active/visible tab container.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from helpers import (
    create_browser,
    login,
    read_configurations_from_file,
    sanitize_test_name,
    wait_for_page_load,
    js_click,
    DEFAULT_TIMEOUT,
)


FIELDS = [
    {"input_id": "form_1", "label": "GROQ API Token",   "value": "gsk_test_abc123def456ghi789"},
    {"input_id": "form_2", "label": "MODAL API Token",  "value": "mk_test_xyz987uvw654rst321"},
    {"input_id": "form_3", "label": "MODAL API Secret", "value": "ms_test_secret_000111222333"},
]


def get_configs():
    return read_configurations_from_file('secret.json')


def get_base_url(login_url):
    idx = login_url.find('/interface/')
    if idx != -1:
        return login_url[:idx + len('/interface')]
    return login_url.rsplit('/login/', 1)[0]


def go_to_user_settings_custom(browser, login_url):
    """Navigate to User Settings and activate the Custom tab."""
    base_url = get_base_url(login_url)
    browser.get(f"{base_url}/super/edit_globals.php?mode=user")
    wait_for_page_load(browser)
    time.sleep(1)

    # Click the Custom tab
    try:
        custom_link = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//ul[@id='oe-nav-ul']//a[normalize-space(text())='Custom']")
            )
        )
        browser.execute_script("arguments[0].scrollIntoView({block:'center'});", custom_link)
        time.sleep(0.3)
        try:
            custom_link.click()
        except Exception:
            js_click(browser, custom_link)
    except TimeoutException:
        browser.execute_script("""
            var links = document.querySelectorAll('#oe-nav-ul a');
            for (var i = 0; i < links.length; i++) {
                if (links[i].textContent.trim() === 'Custom') {
                    links[i].click();
                    break;
                }
            }
        """)
    time.sleep(1)

    # Debug: count how many form_1 exist and which tab they're in
    debug = browser.execute_script("""
        var els = document.querySelectorAll('[id="form_1"]');
        var info = [];
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            var tabClass = tab ? tab.className : 'no-tab-parent';
            var display = tab ? getComputedStyle(tab).display : 'unknown';
            info.push('idx=' + i + ' tab=' + tabClass + ' display=' + display + ' val=' + els[i].value.substring(0,20));
        }
        return info.join(' | ');
    """)
    print(f"[DEBUG] All form_1 elements: {debug}")


def js_set_value_in_current_tab(browser, field_id, value):
    """Set value on the form field inside the currently visible tab."""
    result = browser.execute_script("""
        var els = document.querySelectorAll('[id="' + arguments[0] + '"]');
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            if (tab && tab.classList.contains('current')) {
                els[i].value = arguments[1];
                els[i].dispatchEvent(new Event('input', {bubbles: true}));
                els[i].dispatchEvent(new Event('change', {bubbles: true}));
                return 'set_in_current';
            }
        }
        // Fallback: try element inside a visible tab (display != none)
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            if (tab && getComputedStyle(tab).display !== 'none') {
                els[i].value = arguments[1];
                els[i].dispatchEvent(new Event('input', {bubbles: true}));
                els[i].dispatchEvent(new Event('change', {bubbles: true}));
                return 'set_in_visible';
            }
        }
        // Last resort: set on last element (Custom is the last tab)
        if (els.length > 0) {
            var last = els[els.length - 1];
            last.value = arguments[1];
            last.dispatchEvent(new Event('input', {bubbles: true}));
            last.dispatchEvent(new Event('change', {bubbles: true}));
            return 'set_on_last';
        }
        return 'not_found';
    """, field_id, value)
    print(f"[DEBUG] js_set_value({field_id}): {result}")
    return result


def js_get_value_in_current_tab(browser, field_id):
    """Read value from the form field inside the currently visible tab."""
    return browser.execute_script("""
        var els = document.querySelectorAll('[id="' + arguments[0] + '"]');
        // Try current tab first
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            if (tab && tab.classList.contains('current')) {
                return els[i].value;
            }
        }
        // Try visible tab
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            if (tab && getComputedStyle(tab).display !== 'none') {
                return els[i].value;
            }
        }
        // Last resort: last element
        if (els.length > 0) {
            return els[els.length - 1].value;
        }
        return null;
    """, field_id)


def js_click_save_in_current_tab(browser):
    """Click the Save button inside the visible tab area."""
    browser.execute_script("""
        // Find Save buttons, click the visible one
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.indexOf('Save') !== -1 &&
                buttons[i].offsetParent !== null) {
                buttons[i].click();
                return;
            }
        }
        // Fallback: click any Save button
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.indexOf('Save') !== -1) {
                buttons[i].click();
                return;
            }
        }
    """)


class TestEnterCustomSettings:

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

        go_to_user_settings_custom(self.browser, self.login_url)

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
    def test_fill_groq_api_token(self, config):
        """Enter a value into the GROQ API Token field."""
        field = FIELDS[0]
        js_set_value_in_current_tab(self.browser, field["input_id"], field["value"])
        actual = js_get_value_in_current_tab(self.browser, field["input_id"])
        assert actual == field["value"], (
            f"Expected '{field['value']}', got '{actual}'"
        )

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_fill_modal_api_token(self, config):
        """Enter a value into the MODAL API Token field."""
        field = FIELDS[1]
        js_set_value_in_current_tab(self.browser, field["input_id"], field["value"])
        actual = js_get_value_in_current_tab(self.browser, field["input_id"])
        assert actual == field["value"], (
            f"Expected '{field['value']}', got '{actual}'"
        )

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_fill_modal_api_secret(self, config):
        """Enter a value into the MODAL API Secret field."""
        field = FIELDS[2]
        js_set_value_in_current_tab(self.browser, field["input_id"], field["value"])
        actual = js_get_value_in_current_tab(self.browser, field["input_id"])
        assert actual == field["value"], (
            f"Expected '{field['value']}', got '{actual}'"
        )

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_save_settings(self, config):
        """Fill all fields and save settings without error."""
        for field in FIELDS:
            js_set_value_in_current_tab(self.browser, field["input_id"], field["value"])

        js_click_save_in_current_tab(self.browser)
        wait_for_page_load(self.browser)
        time.sleep(2)

        body = self.browser.find_element(By.TAG_NAME, "body").text.lower()
        assert "error" not in body, f"Error detected after saving: {body[:300]}"
