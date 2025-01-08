import os
import requests
from datetime import datetime, timedelta

DBT_CLOUD_API_TOKEN = os.getenv('DBT_CLOUD_API_TOKEN')
DBT_CLOUD_ACCOUNT_ID = os.getenv('DBT_CLOUD_ACCOUNT_ID')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

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
    threshold_date = datetime.now() - timedelta(days=30)
    for user in users:
        last_login = datetime.strptime(user['last_login'], '%Y-%m-%dT%H:%M:%S.%fZ')
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

# Main function
def main():
    users = get_users()
    inactive_users = check_inactive_users(users)
    if inactive_users:
        send_slack_notification(inactive_users)
    else:
        print('No inactive users found.')

if __name__ == '__main__':
    main()