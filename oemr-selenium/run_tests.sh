#!/bin/bash

# Define the root directory for the scripts
ROOT_DIR="/home/ksunchu/oemr_selenium/openemr/oemr-selenium"

echo "Cron job started at $(date)" >> "$ROOT_DIR/logfile.log"

# Report directory
REPORT_DIR="$ROOT_DIR/reports"
REPORT_FILE="$REPORT_DIR/report.html"

# Ensure the reports directory exists
mkdir -p $REPORT_DIR

# Remove the previous combined report if it exists
rm -f $REPORT_FILE

# Change to the directory where the test files are located
cd $ROOT_DIR

# Define your test files
TEST_FILES="login_tests.py logout.py vitals.py patient_search.py cdr_rule.py"

# Run pytest to execute all specified tests and generate a single HTML report
# HEADLESS=true is set if you're running tests in headless mode
HEADLESS=true python3 -m pytest $TEST_FILES --html=$REPORT_FILE --self-contained-html

# Check the exit status of pytest
if [ $? -ne 0 ]; then
    echo "Tests failed, processing report..."
    # Send the report
    echo "Sending report"
    python3 $ROOT_DIR/send_mail.py
else
    echo "All tests passed, no need to send report."
fi

echo "Tests completed. Report generated at $REPORT_FILE."
