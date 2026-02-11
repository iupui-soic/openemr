import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from dataclasses import dataclass
from typing import List

# Common timeout for all wait operations
DEFAULT_TIMEOUT = 30


def get_chrome_options():
    """
    Get Chrome options configured for reliable headless execution on servers.

    Returns:
        Options: Configured Chrome options
    """
    options = Options()

    if os.environ.get('HEADLESS', 'false').lower() == 'true':
        options.add_argument("--headless=new")  # Use new headless mode (more stable)

    # Critical for running on Linux servers (especially as root)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")

    # Stability options
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # Memory optimization for parallel execution
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    # Additional stability for resource-constrained servers
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-prompt-on-repost")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-component-update")

    # Memory limits - critical for parallel execution
    options.add_argument("--js-flags=--max-old-space-size=512")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-ipc-flooding-protection")

    # Unique user data dir per worker to avoid conflicts in parallel execution
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    if worker_id != 'main':
        options.add_argument(f"--user-data-dir=/tmp/chrome-{worker_id}-{os.getpid()}")
        # Use unique debugging port to avoid conflicts
        options.add_argument("--remote-debugging-port=0")

    return options


def create_browser(retries=3, retry_delay=2):
    """
    Create a configured Chrome WebDriver instance with retry logic.

    Args:
        retries: Number of times to retry browser creation on failure
        retry_delay: Seconds to wait between retries

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver
    """
    from selenium.common.exceptions import SessionNotCreatedException, WebDriverException

    options = get_chrome_options()
    last_exception = None

    for attempt in range(retries):
        try:
            browser = webdriver.Chrome(options=options)
            browser.maximize_window()
            browser.implicitly_wait(10)
            return browser
        except (SessionNotCreatedException, WebDriverException) as e:
            last_exception = e
            if attempt < retries - 1:
                print(f"Browser creation failed (attempt {attempt + 1}/{retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                # Increase delay for subsequent retries
                retry_delay *= 1.5
            else:
                print(f"Browser creation failed after {retries} attempts")

    raise last_exception

@dataclass
class ServerConfig:
    server_name: str
    url: str
    username: str
    password: str

    def __repr__(self):
        return f"ServerConfig(server={self.url})"

def read_configurations_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    configurations = []
    for server_name, user_data in data["SERVERS"].items():
        url = user_data['url']
        users = user_data['users']
        for user in users:
            config = ServerConfig(
                server_name=server_name,
                url=url,
                username=user['username'],
                password=user['password']
            )
            configurations.append(config)
    return configurations

def sanitize_test_name(config: ServerConfig):
    return f"server-{config.url}"

def read_urls_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    servers_data = data.get("SERVERS", {})
    urls = [server_data['url'] for server_data in servers_data.values()]
    return urls

def get_expected_url_after_login(server_name, file_path='secret.json'):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    servers = data.get("SERVERS", {})
    return servers.get(server_name, {}).get('expected_url_after_login', '')

def login(browser, username, password, login_url, server_name, file_path='secret.json'):
    expected_url_after_login = get_expected_url_after_login(server_name, file_path)
    browser.get(login_url)
    wait = WebDriverWait(browser, DEFAULT_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.ID, 'authUser'))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.ID, "clearPass"))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).submit()
    tabs_to_close = browser.find_elements(By.CSS_SELECTOR, 'span[class="fa fa-fw fa-xs fa-times"]')
    for tab_close in tabs_to_close:
        tab_close.click()
    return expected_url_after_login in browser.current_url

def read_admin_configurations_from_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    first_user_configurations = []
    for server_name, user_data in data["SERVERS"].items():
        url_value = user_data['url']
        if user_data['users']:
            first_user = user_data['users'][0]
            username = first_user['username']
            password = first_user['password']
            first_user_configurations.append((server_name, url_value, username, password))
    return first_user_configurations

def wait_for_page_load(driver, timeout=DEFAULT_TIMEOUT):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return typeof jQuery == "undefined" || jQuery.active == 0')
    )

def wait_for_element(browser, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for element to be present and return it."""
    return WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def wait_for_clickable(browser, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for element to be clickable and return it."""
    return WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((by, value))
    )

def wait_and_click(browser, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for element to be clickable and click it."""
    element = wait_for_clickable(browser, by, value, timeout)
    element.click()
    return element

def wait_and_send_keys(browser, by, value, keys, timeout=DEFAULT_TIMEOUT):
    """Wait for element to be present and send keys to it."""
    element = wait_for_element(browser, by, value, timeout)
    element.send_keys(keys)
    return element

def wait_for_visible(browser, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for element to be visible and return it."""
    return WebDriverWait(browser, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def wait_for_frame(browser, frame_locator, timeout=DEFAULT_TIMEOUT):
    """Wait for frame to be available and switch to it."""
    return WebDriverWait(browser, timeout).until(
        EC.frame_to_be_available_and_switch_to_it(frame_locator)
    )

def get_element_text_with_retry(browser, by, value, timeout=DEFAULT_TIMEOUT, retries=3):
    """Get element text with retry logic to handle stale element references."""
    for attempt in range(retries):
        try:
            element = WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element.text.strip()
        except StaleElementReferenceException:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
            raise
    return ""


def js_click(browser, element):
    """Click element using JavaScript - more reliable than Selenium click for menus."""
    browser.execute_script("arguments[0].click();", element)

#change1 OpenEMR buttons (including global search) listen to mousedown, not click
def js_mousedown(browser, element):
    """
    REQUIRED for OpenEMR:
    Triggers KnockoutJS event bindings (data-bind: mousedown)
    """
    browser.execute_script(
        """
        const evt = new MouseEvent('mousedown', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        arguments[0].dispatchEvent(evt);
        """,
        element,
    )



def wait_and_js_click(browser, by, value, timeout=DEFAULT_TIMEOUT):
    """Wait for element and click using JavaScript."""
    element = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((by, value))
    )
    js_click(browser, element)
    return element

#chabge2 Used for buttons that visually exist but don’t respond to .click().

def wait_and_js_mousedown(browser, by, value, timeout=DEFAULT_TIMEOUT):
    element = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((by, value))
    )
    browser.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", element
    )
    js_mousedown(browser, element)
    return element



def click_with_retry(browser, by, value, timeout=DEFAULT_TIMEOUT, retries=3):
    """Click element with retry logic for flaky interactions."""
    from selenium.common.exceptions import (
        ElementClickInterceptedException,
        ElementNotInteractableException,
    )

    last_exception = None
    for attempt in range(retries):
        try:
            element = WebDriverWait(browser, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return element
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException) as e:
            last_exception = e
            time.sleep(0.5)
            # Try JavaScript click as fallback
            try:
                element = browser.find_element(by, value)
                #js_click(browser, element)
                js_mousedown(browser, element)#change3 Fallback clicks were still failing because click() ≠ mousedown

                return element
            except Exception:
                continue
    raise last_exception


def navigate_to_menu(browser, menu_path, timeout=DEFAULT_TIMEOUT):
    """
    Navigate through OpenEMR menu using text-based locators.

    Args:
        browser: WebDriver instance
        menu_path: List of menu labels, e.g. ["Admin", "Clinic", "Facilities"]
        timeout: Wait timeout in seconds
    """
    wait_for_page_load(browser)

    for i, menu_text in enumerate(menu_path):
        is_last = (i == len(menu_path) - 1)

        # Try multiple selector strategies
        selectors = [
            # Primary: menuLabel class with text
            f"//div[contains(@class, 'menuLabel') and contains(normalize-space(), '{menu_text}')]",
            # Dropdown toggle
            f"//div[contains(@class, 'dropdown-toggle') and contains(normalize-space(), '{menu_text}')]",
            # Any div with the text in menu area
            f"//*[@id='mainMenu']//div[contains(normalize-space(), '{menu_text}')]",
            # Link text
            f"//a[contains(normalize-space(), '{menu_text}')]",
        ]

        clicked = False
        for selector in selectors:
            try:
                element = WebDriverWait(browser, timeout / 2).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )

                # Scroll element into view
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)

                # Use JavaScript click for reliability
                #js_click(browser, element)
                js_mousedown(browser, element)#change3 Menu items are also bound via KnockoutJS mousedown.

                clicked = True

                # Wait a bit for menu to expand (except for last item)
                if not is_last:
                    time.sleep(0.3)
                break
            except Exception:
                continue

        if not clicked:
            raise Exception(f"Could not find menu item: {menu_text}")

    wait_for_page_load(browser)
#change5

def switch_to_frame_with_retry(browser, frame_name, timeout=DEFAULT_TIMEOUT, retries=3):
    """
    Switch to iframe if it exists.
    OR continue in main DOM if iframe was removed (new OpenEMR versions).
    """

    for _ in range(retries):
        try:
            browser.switch_to.default_content()
        except Exception:
            pass

        try:
            WebDriverWait(browser, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, frame_name))
            )
            return True
        except TimeoutException:
            pass

        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            name = iframe.get_attribute("name") or ""
            fid = iframe.get_attribute("id") or ""
            src = iframe.get_attribute("src") or ""

            if frame_name in name or frame_name in fid or frame_name in src:
                browser.switch_to.frame(iframe)
                return True

        time.sleep(0.5)

    # iframe genuinely does not exist → VALID
    browser.switch_to.default_content()
    return False
