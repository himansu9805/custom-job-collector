import os

# LinkedIn configuration
USER_EMAIL = os.environ.get("USER_EMAIL", "")
USER_PASSWORD = os.environ.get("USER_PASSWORD", "")

# Email configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = os.environ.get("SMTP_PORT", "")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "")
