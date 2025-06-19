## Using the Testing Environment with Pytest and Selenium

1. Create `secret.json` with the following contents:

```json
{
  "expected_url_after_login": "EXPECTED_LOGIN_SUCCESS_URL",
  "SERVERS": {
    "SERVER1": {
      "url": "SERVER_URL",
      "users": [
        {
          "username": "USERNAME",
          "password": "PASSWORD"
        },
        {
          "username": "USERNAME1",
          "password": "PASSWORD1"
        }
      ]
    }
  }
}
```

2. **If you are using IntelliJ:**
   - Open the project from the `oemr-selenium` folder.

3. **Install necessary packages:**
   - Install `py`: `pip install py`
   - Install `selenium`: `pip install selenium`
   - Install ` webdriver-manager`: `pip install webdriver-manager`
   - [Ubuntu only] Download `chrome stable package`: `wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb`
   - [Ubuntu only] Install `google-chrome`: `dpkg -i google-chrome-stable_current_amd64.deb`

4. **If using another IDE/Environment:**
   - Activate the virtual environment (venv).
   - Install Pytest: `pip install pytest`
   - Install `py`: `pip install py`

5. **To generate reports on Windows, run:**
   - `python -m pytest .\file_name.py --html=reports/report.html`

6. **To generate reports Ubuntu, run:**
   - ` HEADLESS=true python -m pytest .\file_name.py --html=reports/report.html`
