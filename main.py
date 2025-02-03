from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get token from environment variable
access_token = os.environ.getenv("GITHUB_TOKEN")
if not access_token:
    raise ValueError("GITHUB_TOKEN is not set in the environment variables or .env file!")

headers = {"Authorization": f"token {access_token}"}

def get_all_repos():
    repos = []
    page = 1
    while True:
        response = requests.get(
            "https://api.github.com/user/repos",
            params={"per_page": 100, "page": page},
            headers=headers
        )
        
        if response.status_code != 200:
            return {"error": f"GitHub API error: {response.status_code}"}
            
        page_repos = response.json()
        if not page_repos:
            break
            
        repos.extend([{
            "name": repo["full_name"],
            "url": repo["html_url"],
            "description": repo["description"],
            "stars": repo["stargazers_count"]
        } for repo in page_repos])
        
        page += 1
        
    return repos

@app.route('/repos', methods=['GET'])
def repos_endpoint():
    repo_data = get_all_repos()
    return jsonify({
        "count": len(repo_data),
        "repositories": repo_data
    })

@app.route('/')
def home():
    return """
    <h1>GitHub Repo Bot</h1>
    <p>Access repository data at <a href="/repos">/repos</a></p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
