import subprocess
import sys
import os
from datetime import datetime

# List of email addresses to send to
recipients = ['abc@mail.com','xyz@mail.com']
recipient_string = ",".join(recipients)

# Path to the HTML file you want to attach
# Can be passed as command-line argument or uses default
default_report_path = os.path.join(os.path.dirname(__file__), 'reports', 'report.html')
html_file_path = sys.argv[1] if len(sys.argv) > 1 else default_report_path

current_time = datetime.now()

# Subject and body of the email
subject = "Test Automation Report - {}".format(current_time)
body = "You are receiving this automated mail because one or more automated tests have failed. Please see the attached test execution report."

from_address = "from_address@mail.com"

# Command to send email using mutt
command = f'echo "{body}" | mutt -e "set from={from_address}" -s "{subject}" -a "{html_file_path}" -- {recipient_string}'

# Execute the command
subprocess.run(command, shell=True, check=True)

print("Email sent!")
