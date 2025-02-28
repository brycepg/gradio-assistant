from datetime import datetime, timezone
import json

import argparse


def main():
    parser = argparse.ArgumentParser(description="Filter GitHub data")
    parser.add_argument("input", type=str, help="Input file")
    parser.add_argument("output", type=str, help="Output file")
    args = parser.parse_args()

    issue_seq = []
    with open(args.input, 'r', encoding="utf-8") as fh:
        issue_seq.extend(json.load(fh))

    filtered_issue_seq = []
    reference_2024 = datetime(2024, 9, 1, tzinfo=timezone.utc)
    for issue in issue_seq:
        if not issue["body"]:
            continue
        if not issue["comments"]:
            continue
        comment_users = []
        for comment in issue["comments"]:
            comment_users.append(comment["user"]["login"])
        if len(set(comment_users)) == 1 and comment_users[0] == "gradio-pr-bot":
            continue
        updated_at = issue["created_at"]
        dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if dt < reference_2024:
            continue
        filtered_issue_seq.append(issue)

    url_result_seq = []
    for filtered_issue in filtered_issue_seq:
        title = filtered_issue["title"]
        body = filtered_issue["body"]
        comments = filtered_issue["comments"]
        comments_body = "\n\n".join([x["body"] for x in comments])
        url_result_seq.append(
            {
                "content": "# " + title + "\n\n" + body + "\n\n" + comments_body,
                "url": filtered_issue["html_url"],
            }
        )
    with open(args.output, 'w', encoding="utf-8") as fh:
        json.dump(url_result_seq, fh, indent=2)

if __name__ == "__main__":
    main()
