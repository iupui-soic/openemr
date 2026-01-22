"""
Pytest configuration for parallel Selenium test execution.

This module provides shared fixtures and configuration for running
Selenium tests in parallel using pytest-xdist.
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "server(name): mark test to run on specific server"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection for better parallel distribution.

    Groups tests by their server/URL parameter to keep related tests
    together when using --dist loadscope.
    """
    # Sort items by their parametrized server URL if available
    # This helps pytest-xdist group tests more efficiently
    def get_server_key(item):
        # Extract server URL from test parameters for grouping
        if hasattr(item, 'callspec') and hasattr(item.callspec, 'params'):
            params = item.callspec.params
            if 'config' in params:
                return params['config'].url
            if 'url' in params:
                return params['url']
        return item.nodeid

    items.sort(key=get_server_key)


@pytest.fixture(scope="function")
def browser():
    """
    Shared browser fixture for all test classes.

    This fixture creates a Chrome WebDriver instance with appropriate
    options for headless execution and parallel test runs.

    Yields:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    options = Options()

    # Headless mode for CI/parallel execution
    if os.environ.get('HEADLESS', 'false').lower() == 'true':
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # Additional options for stability in parallel execution
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    # Unique user data dir per worker to avoid conflicts
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    if worker_id != 'main':
        options.add_argument(f"--user-data-dir=/tmp/chrome-{worker_id}")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)

    yield driver

    # Cleanup
    try:
        driver.close()
        driver.quit()
    except Exception:
        pass  # Browser may already be closed


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    Capture screenshot on test failure for debugging.

    When a test fails, this hook captures a screenshot and attaches
    it to the HTML report if pytest-html is being used.
    """
    if call.when == "call" and call.excinfo is not None:
        # Test failed - try to capture screenshot
        browser = item.funcargs.get('browser') or getattr(item.instance, 'browser', None)
        if browser:
            try:
                # Create screenshots directory if needed
                screenshots_dir = os.path.join(os.path.dirname(__file__), 'reports', 'screenshots')
                os.makedirs(screenshots_dir, exist_ok=True)

                # Generate unique filename
                worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
                screenshot_name = f"{item.name}_{worker_id}.png".replace("[", "_").replace("]", "_")
                screenshot_path = os.path.join(screenshots_dir, screenshot_name)

                browser.save_screenshot(screenshot_path)
            except Exception:
                pass  # Don't fail the test further if screenshot fails