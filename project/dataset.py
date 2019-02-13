import json
import time
import requests


# GitHub throttles unauthenticated searches to 10 per minute, so just
# wait 6 seconds between each request.
# TODO: add authentication to requests so this is faster


def get_next_url(response_headers):
    link_string = response_headers.get('Link')
    links = link_string.split(",")

    next_links = [link for link in links if 'rel="next"' in link]
    if next_links:
        [next_link] = next_links
        next_url = next_link.split(";")[0].strip(" <> ")

        return next_url

    return False


BASE_URL = "https://api.github.com"
SEARCH_URL = BASE_URL + "/search/repositories"

topics = [
    "react",
    "javascript",
    "python",
    "r",
    "shellcode",
    "payload",
]


# Find the most popular repo's for each of the above topics
repos = []

for topic in topics:
    print(SEARCH_URL)
    response = requests.get(
        SEARCH_URL,
        params={
            "q": "topic:" + topic,
            "sort": "stars",
        },
        headers=headers,
    )
    time.sleep(6)
    repos += response.json().get("items")

    # Fetch all the searh results, not just the first page
    next_url = get_next_url(response.headers)
    while(next_url):
        print(next_url)
        response = requests.get(
            next_url,
            headers=headers,
        )
        time.sleep(6)

        repos += response.json().get("items")

        next_url = get_next_url(response.headers)

# Save this repo list for later
with open('../data/repo-list.json', 'w') as repo_list_file:
    json.dump(repos, repo_list_file)

# Load repo list back in
with open('../data/repo-list.json', 'r') as repo_list_file:
    repos = json.load(repo_list_file)

# Filter to include small repos only
megabyte = 1000000
repos = [repo for repo in repos if repo.get("size", 0) < megabyte]

# To download the repo as a whole, use the html url the api gives:
r = requests.get(repos[0]['html_url'] + '/archive/master.zip')

# We've picked topics that roughly map to programming languages, but
# there will still be a mix in each repo. For example, Python projects
# may include make files, or small bits of frontend javascript. Here,
# we navigate through each repo and pull out files which match a
# programming language we want to model. The files in each repo are
# then concatentated to form a document with a mixture of known
# programming languages. Each of these composite files becomes a
# labelled document in our model (consisting of a mixture of
# topics/languages).

language_file_names = {
    'Javascript': ['.*\.js'],
    'Markdown': ['.*\.md'],
    'Python': ['.*\.py'],
    'R': ['.*\.R'],
    'C/C++': ['.*\.c', '.*\.h', '.*\.cpp'],
    'Bash': ['\.sh'],
    'Make': ['makefile'],
}

for repo in repos:
