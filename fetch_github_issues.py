import os
import requests
import json
import time
from datetime import datetime
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError, ChunkedEncodingError
from http.client import RemoteDisconnected
from dotenv import load_dotenv

load_dotenv()

def check_rate_limit(response):
    """Check remaining rate limit and wait if necessary."""
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_timestamp = int(response.headers.get('X-RateLimit-Reset', 0))

    if remaining == 0:
        reset_time = datetime.fromtimestamp(reset_timestamp)
        sleep_duration = (reset_time - datetime.now()).total_seconds()
        if sleep_duration > 0:
            print(f"Rate limit reached. Sleeping for {sleep_duration:.2f} seconds until {reset_time}")
            time.sleep(sleep_duration + 1)  # Add 1 second buffer
            return True
    return False

def make_request(url, params=None, headers=None, max_retries=17, initial_backoff=1):
    """Make a request with rate limit handling and exponential backoff retry."""
    retry_count = 0
    backoff = initial_backoff

    while retry_count <= max_retries:
        try:
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
                if check_rate_limit(response):
                    continue

            if response.status_code == 200:
                return response

            response.raise_for_status()

        except (ConnectionError, ChunkedEncodingError, ProtocolError, RemoteDisconnected) as e:
            retry_count += 1
            if retry_count > max_retries:
                raise Exception(f"Max retries ({max_retries}) exceeded. Last error: {str(e)}")

            sleep_time = backoff * (2 ** (retry_count - 1))  # Exponential backoff
            print(f"Connection error occurred: {str(e)}")
            print(f"Retrying in {sleep_time} seconds... (Attempt {retry_count} of {max_retries})")
            time.sleep(sleep_time)
            continue

def save_progress(issues, current_page):
    """Save current progress to a backup file with rotation."""
    backup_files = ['issues_backup_1.json', 'issues_backup_2.json']
    progress_data = {
        'last_page': current_page,
        'issues': issues,
        'timestamp': datetime.now().isoformat()
    }

    # Write to temporary file first
    temp_file = 'issues_backup_temp.json'
    try:
        with open(temp_file, 'w') as f:
            json.dump(progress_data, f)

        # Rotate backup files
        if os.path.exists(backup_files[1]):
            os.replace(backup_files[1], backup_files[0])
        os.replace(temp_file, backup_files[1])

    except Exception as e:
        print(f"Warning: Failed to save backup: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

def load_progress():
    """Load progress from backup files, trying the most recent first."""
    backup_files = ['issues_backup_2.json', 'issues_backup_1.json']

    for backup_file in backup_files:
        try:
            with open(backup_file, 'r') as f:
                progress_data = json.load(f)
                print(f"Loaded backup from {backup_file} (saved at {progress_data.get('timestamp', 'unknown time')})")
                return progress_data['issues'], progress_data['last_page']
        except json.JSONDecodeError as e:
            print(f"Warning: Backup file {backup_file} is corrupted: {e}")
            continue
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Warning: Error reading {backup_file}: {e}")
            continue

    print("No valid backup found, starting from beginning")
    return [], 1

def fetch_all_issues_with_comments(owner, repo, token=None, start_page=1):
    issues = []
    page = start_page

    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    if token:
        headers['Authorization'] = f'token {token}'

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {
            'state': 'all',
            'per_page': 100,
            'page': page
        }

        try:
            response = make_request(url, params=params, headers=headers)
            issues_page = response.json()

            if not issues_page:
                break

            page_issues = []  # Temporary storage for current page
            for issue in issues_page:
                try:
                    # Fetch comments for each issue
                    comments_url = issue['comments_url']
                    comments_response = make_request(comments_url, headers=headers)
                    issue['comments'] = comments_response.json()
                    page_issues.append(issue)

                except Exception as e:
                    print(f"Error fetching comments for issue #{issue.get('number', 'unknown')}: {e}")
                    issue['comments'] = []  # Set empty comments and continue
                    page_issues.append(issue)

            # Add all issues from the page at once
            issues.extend(page_issues)
            save_progress(issues, page)

            print(f"Processed page {page} ({len(issues)} issues so far)")
            page += 1

        except Exception as e:
            print(f"Error processing page {page}: {e}")
            # Save progress before re-raising the exception
            save_progress(issues, page)
            raise

    return issues

def clean_backups():
    """Clean up backup files."""
    backup_files = ['issues_backup_1.json', 'issues_backup_2.json', 'issues_backup_temp.json']
    for file in backup_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"Warning: Failed to remove backup file {file}: {e}")

def main():
    # Configuration
    owner = 'gradio-app'
    repo = 'gradio'
    token = os.environ["GITHUB_TOKEN"]

    try:
        # Load previous progress if any
        existing_issues, start_page = load_progress()
        if existing_issues:
            print(f"Resuming from page {start_page} with {len(existing_issues)} issues already collected")

        print(f"Fetching issues for {owner}/{repo}")
        issues = fetch_all_issues_with_comments(owner, repo, token, start_page)

        # If resuming, combine with existing issues
        if existing_issues:
            issues = existing_issues + issues

        output_file = 'issues_with_comments.json'
        # Write to temporary file first
        temp_file = 'issues_with_comments_temp.json'
        with open(temp_file, 'w') as f:
            json.dump(issues, f, indent=2)
        # Then rename to final filename
        os.replace(temp_file, output_file)

        print(f"Successfully saved {len(issues)} issues to {output_file}")

        # Clean up backup files only after successful completion
        clean_backups()

    except Exception as e:
        print(f"Script failed: {e}")
        print("You can resume from the last saved progress by running the script again.")
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Progress has been saved.")
        print("You can resume from the last saved progress by running the script again.")

if __name__ == "__main__":
    main()
