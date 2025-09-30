import os
import sys
import json
import requests

diff_file = sys.argv[1]

# Load diff JSON
with open(diff_file) as f:
    pr_diff = json.load(f)

# Your custom prompt template
PROMPT_TEMPLATE = """
You are an expert code reviewer.
For the following code snippet, provide concise, constructive comments.
Code:
{code}
"""

# Gemini API endpoint
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Prepare review comments per file
review_comments = []

for file_path, changes in pr_diff.items():
    for change in changes:
        code_snippet = change["code"]
        prompt = PROMPT_TEMPLATE.format(code=code_snippet)
        
        headers = {
            "Authorization": f"Bearer {os.environ['GEMINI_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "max_output_tokens": 150
        }
        
        resp = requests.post(GEMINI_URL, headers=headers, json=payload)
        resp_json = resp.json()
        ai_comment = resp_json.get("output_text", "No response from Gemini.")
        
        review_comments.append({
            "path": file_path,
            "line": change["line"],
            "body": ai_comment
        })

# Post to GitHub Pull Request Reviews API
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = os.environ["PR_NUMBER"]
COMMIT_SHA = os.environ["GITHUB_SHA"]

API_URL = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/reviews"

data = {
    "commit_id": COMMIT_SHA,
    "body": "Automated AI review",
    "event": "COMMENT",
    "comments": review_comments
}

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

resp = requests.post(API_URL, headers=headers, json=data)
print(resp.status_code, resp.text)
