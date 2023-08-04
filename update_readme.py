import os
import requests
import time

GITLAB_API = "https://gitlab.com/api/v4/users/{username}/projects"
MAX_RETRIES = 5
RATE_LIMIT_PAUSE = 60

def get_projects(username):
    retries = 0
    while retries < MAX_RETRIES:
        response = requests.get(GITLAB_API.format(username=username))
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Rate limit exceeded
            print(f"Rate limit exceeded. Pausing for {RATE_LIMIT_PAUSE} seconds.")
            time.sleep(RATE_LIMIT_PAUSE)
            retries += 1
        else:
            response.raise_for_status()
    raise Exception("Failed to fetch the projects after multiple retries")

def make_project_list(projects):
    project_list = "## My GitLab Projects\n\n"
    for project in projects:
        desc = project['description'] if project['description'] else "No description provided."
        project_list += f"- [{project['name']}]({project['web_url']}) - {desc}\n"
    return project_list

def main():
    projects = get_projects("adentahir")

    with open("README.md", "r") as f:
        readme_contents = f.read()

    project_list = make_project_list(projects)

    if "## My GitLab Projects" in readme_contents:
        # If we've already added the GitLab projects section before,
        # replace it with the updated one
        start_index = readme_contents.find("## My GitLab Projects")
        end_index = readme_contents.find("##", start_index + 1)
        if end_index == -1:  # no other headers found, append to the end
            end_index = len(readme_contents)
        readme_contents = readme_contents[:start_index] + project_list + readme_contents[end_index:]
    else:
        # If this is the first run, append the GitLab projects section at the end
        readme_contents += "\n" + project_list

    with open("README.md", "w") as f:
        f.write(readme_contents)

if __name__ == "__main__":
    main()
