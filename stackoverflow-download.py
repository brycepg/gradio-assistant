"""Download question and answers from stackoverflow"""
import requests
import json
import argparse
from time import sleep

def fetch_stackoverflow_posts(tag, page=1):
    base_url = "https://api.stackexchange.com/2.3/questions"

    params = {
        'page': page,
        'pagesize': 100,
        'order': 'desc',
        'sort': 'activity',
        'tagged': tag,
        'site': 'stackoverflow',
        'filter': '!-*jbN-o8P3E5', # Custom filter to include bodies, answers and comments
        'answers': 'true'  # Only questions with answers
    }

    response = requests.get(base_url, params=params)
    return response.json()

def fetch_comments(post_id, post_type):
    """Fetch comments for a post (question or answer)"""
    base_url = f"https://api.stackexchange.com/2.3/{post_type}s/{post_id}/comments"

    params = {
        'order': 'desc',
        'sort': 'creation',
        'site': 'stackoverflow',
        'filter': '!-*jbN-o8P3E5'
    }

    response = requests.get(base_url, params=params)
    return response.json().get('items', [])

def fetch_answers_with_comments(question_id):
    """Fetch answers and their comments for a question"""
    base_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"

    params = {
        'order': 'desc',
        'sort': 'votes',
        'site': 'stackoverflow',
        'filter': '!-*jbN-o8P3E5'
    }

    response = requests.get(base_url, params=params)
    answers = response.json().get('items', [])

    # Fetch comments for each answer
    for answer in answers:
        sleep(0.5)  # Respect rate limits
        answer['comments'] = fetch_comments(answer['answer_id'], 'answer')

    return answers

def main():
    parser = argparse.ArgumentParser(description='Download Stack Overflow posts by tag')
    parser.add_argument('--tag', type=str, required=True, help='Tag to search for')
    parser.add_argument('--output', type=str, default='stackoverflow_posts.json',
                        help='Output JSON file name')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of questions to download')
    args = parser.parse_args()

    all_posts = []
    page = 1
    has_more = True

    print(f"Downloading posts with tag: {args.tag}")

    while has_more:
        try:
            data = fetch_stackoverflow_posts(args.tag, page)

            if not data.get('items'):
                break

            for question in data['items']:
                # Fetch question comments
                sleep(0.5)  # Respect rate limits
                question['comments'] = fetch_comments(question['question_id'], 'question')

                # Fetch answers and their comments
                sleep(0.5)  # Respect rate limits
                question['answers'] = fetch_answers_with_comments(question['question_id'])

                all_posts.append(question)
                print(f"Processed question {question['question_id']} with {len(question['answers'])} answers")

                if args.limit and len(all_posts) >= args.limit:
                    has_more = False
                    break

            # if has_more:
            #     has_more = data['has_more']
            #     page += 1
            #     print(f"Moving to page {page}, total posts: {len(all_posts)}")
            #     sleep(60*10)  # Respect API rate limits between pages
            break

        except Exception as e:
            print(f"Error occurred: {e}")
            break

    print(f"total posts: {len(all_posts)}")

    # Save to JSON file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)

    print(f"Successfully saved {len(all_posts)} posts to {args.output}")

if __name__ == "__main__":
    main()
