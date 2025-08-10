
import requests
import json

username = "mbastola"
headers = {"Accept": "application/vnd.github.v3+json"}
projects = []

repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
repos_res = requests.get(repos_url, headers=headers)

if repos_res.status_code != 200:
    raise Exception(f"Failed to fetch repos: {repos_res.status_code}")

repos = repos_res.json()

for repo in repos:
    repo_name = repo["name"]
    default_branch = repo["default_branch"]
    contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
    contents_res = requests.get(contents_url, headers=headers)

    if contents_res.status_code != 200:
        continue

    contents = contents_res.json()
    for item in contents:
        if item["type"] == "dir":
            folder_name = item["name"]
            ignore_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/{folder_name}/site/.ignore"
            if requests.get(ignore_url).status_code == 200:
                continue  # Skip if .ignore exists

            tags_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/{folder_name}/site/tags.txt"
            tags_res = requests.get(tags_url)
            tags = []
            if tags_res.status_code == 200:
                tags = [tag.strip() for tag in tags_res.text.split(",") if tag.strip()]

            readme_url_val = None
            readme_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/{folder_name}/README.md"
            # Use a HEAD request to efficiently check for the README's existence
            readme_res = requests.head(readme_url)
            if readme_res.status_code == 200:
                readme_url_val = readme_url

            commit_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?path={folder_name}&per_page=1"
            commit_res = requests.get(commit_url, headers=headers)
            commit_json = commit_res.json()
            commit_date = repo["updated_at"]
            if isinstance(commit_json, list) and len(commit_json) > 0:
                commit_date = commit_json[0]["commit"]["author"]["date"]

            projects.append({
                "repo": repo_name,
                "folder": folder_name,
                "url": item["html_url"],
                "img": f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/{folder_name}/image/main.jpg",
                "updated": commit_date,
                "tags": tags,
                "readme_url": readme_url_val
            })

projects.sort(key=lambda x: x["updated"], reverse=True)

with open("projects.json", "w") as f:
    json.dump(projects, f, indent=2)

print("site/projects.json created with", len(projects), "items and tags included.")
