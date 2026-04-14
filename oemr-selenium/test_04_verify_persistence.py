"""
Test: Verify custom user settings persisted after save.
Uses querySelectorAll + tab.current to target the right form_N element.
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
    base_url = get_base_url(login_url)
    browser.get(f"{base_url}/super/edit_globals.php?mode=user")
    wait_for_page_load(browser)
    time.sleep(1)

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


def js_get_value_in_current_tab(browser, field_id):
    return browser.execute_script("""
        var els = document.querySelectorAll('[id="' + arguments[0] + '"]');
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            if (tab && tab.classList.contains('current')) return els[i].value;
        }
        for (var i = 0; i < els.length; i++) {
            var tab = els[i].closest('.tab');
            if (tab && getComputedStyle(tab).display !== 'none') return els[i].value;
        }
        if (els.length > 0) return els[els.length - 1].value;
        return null;
    """, field_id)


class TestVerifyPersistedSettings:

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
    def test_groq_api_token_persisted(self, config):
        field = FIELDS[0]
        actual = js_get_value_in_current_tab(self.browser, field["input_id"])
        assert actual == field["value"], (
            f"{field['label']}: expected '{field['value']}', got '{actual}'"
        )

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_modal_api_token_persisted(self, config):
        field = FIELDS[1]
        actual = js_get_value_in_current_tab(self.browser, field["input_id"])
        assert actual == field["value"], (
            f"{field['label']}: expected '{field['value']}', got '{actual}'"
        )

    @pytest.mark.parametrize(
        "config",
        get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_modal_api_secret_persisted(self, config):
        field = FIELDS[2]
        actual = js_get_value_in_current_tab(self.browser, field["input_id"])
        assert actual == field["value"], (
            f"{field['label']}: expected '{field['value']}', got '{actual}'"
        )
