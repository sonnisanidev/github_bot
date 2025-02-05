from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Get token from environment variable
access_token = os.environ.get("GITHUB_TOKEN")
if not access_token:
    raise ValueError("GITHUB_TOKEN is not set in the environment variables or .env file!")

headers = {"Authorization": f"Token {access_token}"}

@app.route('/debug-token')
def debug_token():
    return jsonify({"token": access_token[:5] + '...'})  # Show first 5 chars for safety


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

@app.route('/repos', methods=['GET', 'OPTIONS'])
def repos_endpoint():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        return response

    repo_data = get_all_repos()
    response = make_response(jsonify({
        "count": len(repo_data),
        "repositories": repo_data
    }))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/')
def home():
    return """
    <h1>GitHub Repo Bot</h1>
    <p>Access repository data at <a href="/repos">/repos</a></p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
