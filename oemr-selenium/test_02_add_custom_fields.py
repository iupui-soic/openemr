"""
Test: Verify/add custom API token fields in Custom User Settings layout.

The layout editor truncates label display, so we check input values
instead of body text to verify field existence.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers import (
    create_browser,
    login,
    read_configurations_from_file,
    sanitize_test_name,
    wait_for_page_load,
    DEFAULT_TIMEOUT,
)


FIELDS = [
    {"label": "GROQ API Token",   "field_id": "groq_api_token",   "data_type": "Textbox"},
    {"label": "MODAL API Token",  "field_id": "modal_api_token",  "data_type": "Textbox"},
    {"label": "MODAL API secret", "field_id": "modal_api_secret", "data_type": "Textbox"},
]


def get_configs():
    return read_configurations_from_file('secret.json')


def get_base_url(login_url):
    idx = login_url.find('/interface/')
    if idx != -1:
        return login_url[:idx + len('/interface')]
    return login_url.rsplit('/login/', 1)[0]


def go_to_custom_user_layout(browser, login_url):
    """Navigate to Layout Editor with Custom User Settings loaded."""
    base_url = get_base_url(login_url)
    browser.get(f"{base_url}/super/edit_layout.php")
    wait_for_page_load(browser)

    browser.execute_script("""
        var sel = document.getElementById('layout_id');
        for (var i = 0; i < sel.options.length; i++) {
            if (sel.options[i].text === 'Custom User Settings') {
                sel.selectedIndex = i;
                break;
            }
        }
        document.getElementById('theform').submit();
    """)
    time.sleep(3)
    wait_for_page_load(browser)


def field_exists_in_layout(browser, label):
    """Check if a field label exists by searching input values in the layout table."""
    # Labels are stored in input fields, check their values
    return browser.execute_script("""
        var inputs = document.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].value === arguments[0]) return true;
        }
        return false;
    """, label)


def add_one_field(browser, field):
    """Click Add Field, fill the new row, save."""
    browser.execute_script("""
        var btn = document.querySelector('button.addfield');
        if (btn) btn.click();
    """)
    time.sleep(1)

    browser.execute_script("""
        var inputs = document.querySelectorAll("input[name*='gnewid'][name*='label']");
        if (inputs.length > 0) inputs[inputs.length - 1].value = arguments[0];
    """, field["label"])

    browser.execute_script("""
        var inputs = document.querySelectorAll("input[name*='gnewid'][name*='field_id']");
        if (inputs.length > 0) inputs[inputs.length - 1].value = arguments[0];
    """, field["field_id"])

    browser.execute_script("""
        var selects = document.querySelectorAll("select[name*='gnewid'][name*='data_type']");
        if (selects.length > 0) {
            var last = selects[selects.length - 1];
            for (var i = 0; i < last.options.length; i++) {
                if (last.options[i].text === arguments[0]) {
                    last.selectedIndex = i; break;
                }
            }
        }
    """, field["data_type"])

    browser.execute_script("""
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.indexOf('Save Changes') !== -1) {
                buttons[i].click(); return;
            }
        }
    """)
    wait_for_page_load(browser)
    time.sleep(2)


class TestAddCustomFields:

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
        "config", get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_add_groq_api_token(self, config):
        go_to_custom_user_layout(self.browser, self.login_url)
        if field_exists_in_layout(self.browser, FIELDS[0]["label"]):
            print(f"[INFO] '{FIELDS[0]['label']}' already exists.")
        else:
            add_one_field(self.browser, FIELDS[0])
        assert field_exists_in_layout(self.browser, FIELDS[0]["label"])

    @pytest.mark.parametrize(
        "config", get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_add_modal_api_token(self, config):
        go_to_custom_user_layout(self.browser, self.login_url)
        if field_exists_in_layout(self.browser, FIELDS[1]["label"]):
            print(f"[INFO] '{FIELDS[1]['label']}' already exists.")
        else:
            add_one_field(self.browser, FIELDS[1])
        assert field_exists_in_layout(self.browser, FIELDS[1]["label"])

    @pytest.mark.parametrize(
        "config", get_configs(),
        ids=[sanitize_test_name(c) for c in get_configs()],
    )
    def test_add_modal_api_secret(self, config):
        go_to_custom_user_layout(self.browser, self.login_url)
        if field_exists_in_layout(self.browser, FIELDS[2]["label"]):
            print(f"[INFO] '{FIELDS[2]['label']}' already exists.")
        else:
            add_one_field(self.browser, FIELDS[2])
        assert field_exists_in_layout(self.browser, FIELDS[2]["label"])
