import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
DBT_CLOUD_API_TOKEN = os.getenv('DBT_CLOUD_API_TOKEN')
DBT_CLOUD_ACCOUNT_ID = os.getenv('DBT_CLOUD_ACCOUNT_ID')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # Default to 587 if not set
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')

# Get users from dbt Cloud API
def get_users():
    url = f'https://cloud.getdbt.com/api/v2/accounts/{DBT_CLOUD_ACCOUNT_ID}/users/'
    headers = {
        'Authorization': f'Token {DBT_CLOUD_API_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']

# Check for inactive users
def check_inactive_users(users):
    inactive_users = []
    threshold_date = datetime.now(timezone.utc) - timedelta(days=30)
    for user in users:
        last_login = parser.parse(user['last_login'])
        if last_login < threshold_date:
            inactive_users.append(user)
    return inactive_users

# Send Slack notification
def send_slack_notification(inactive_users):
    if not inactive_users:
        return

    message = "Inactive users:\n"
    for user in inactive_users:
        message += f"- {user['email']} (Last login: {user['last_login']})\n"

    payload = {
        'text': message
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()

# Send Teams notification
def send_teams_notification(inactive_users):
    if not inactive_users:
        return

    message = "Inactive users:\n"
    for user in inactive_users:
        message += f"- {user['email']} (Last login: {user['last_login']})\n"

    payload = {
        'text': message
    }

    response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
    response.raise_for_status()

# Send email notification
def send_email_notification(inactive_users):
    if not inactive_users:
        return

    message = "Inactive users:\n"
    for user in inactive_users:
        message += f"- {user['email']} (Last login: {user['last_login']})\n"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = 'Inactive Users Notification'
    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO.split(','), msg.as_string())

# Main function
def main():
    users = get_users()
    inactive_users = check_inactive_users(users)
    if inactive_users:
        # toggle / delete these if you don't need all
        send_slack_notification(inactive_users)
        send_teams_notification(inactive_users)
        send_email_notification(inactive_users)
    else:
        print('No inactive users found.')

if __name__ == '__main__':
    main()