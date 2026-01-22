#!/bin/bash

# Parallel Selenium Test Runner for OpenEMR
# Uses pytest-xdist for parallel test execution across multiple instances

# Get the directory where this script is located
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
REPORT_DIR="$ROOT_DIR/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/report_${TIMESTAMP}.html"
LATEST_REPORT="$REPORT_DIR/report.html"

# Number of parallel workers (default: 10 to avoid Chrome crashes on servers)
# If Chrome keeps crashing, try WORKERS=1 or WORKERS=2
WORKERS=${WORKERS:-10}

# Distribution mode for pytest-xdist
# loadscope: groups tests by their parametrize scope (keeps same server tests together)
# loadfile: distributes by test file
# load: distributes individual tests (maximum parallelism)
DIST_MODE=${DIST_MODE:-loadscope}

echo "=============================================="
echo "OpenEMR Selenium Test Runner"
echo "=============================================="
echo "Started at: $(date)"
echo "Workers: $WORKERS"
echo "Distribution mode: $DIST_MODE"
echo "Report: $REPORT_FILE"
echo "=============================================="

# Ensure the reports directory exists
mkdir -p "$REPORT_DIR"
mkdir -p "$REPORT_DIR/screenshots"

# Change to the test directory
cd "$ROOT_DIR"

# Activate virtual environment if it exists
if [ -d "$ROOT_DIR/venv" ]; then
    source "$ROOT_DIR/venv/bin/activate"
fi

# Install/upgrade dependencies if requirements.txt exists
if [ -f "$ROOT_DIR/requirements.txt" ]; then
    echo "Checking dependencies..."
    pip install -q -r "$ROOT_DIR/requirements.txt"
fi

# Run pytest with parallel execution
echo ""
echo "Running tests in parallel..."
echo ""

HEADLESS=true python3 -m pytest \
    -n "$WORKERS" \
    --dist "$DIST_MODE" \
    --html="$REPORT_FILE" \
    --self-contained-html \
    -v \
    --tb=short \
    "$@"

EXIT_CODE=$?

# Create symlink to latest report
ln -sf "$REPORT_FILE" "$LATEST_REPORT"

echo ""
echo "=============================================="
echo "Test Run Complete"
echo "=============================================="
echo "Finished at: $(date)"
echo "Exit code: $EXIT_CODE"
echo "Report: $REPORT_FILE"
echo "Latest report link: $LATEST_REPORT"

# Send email report on failure
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "Tests failed! Sending report..."
    if [ -f "$ROOT_DIR/send_mail.py" ]; then
        python3 "$ROOT_DIR/send_mail.py" "$REPORT_FILE"
    fi
else
    echo ""
    echo "All tests passed!"
fi

echo "=============================================="

exit $EXIT_CODE
