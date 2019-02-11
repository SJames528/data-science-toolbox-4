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

all_repos = []

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
    repos = response.json().get("items")

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

    # Filter to include small repos only
    megabyte = 1000000
    small_repos = [repo for repo in repos if repo.get("size", 0) < megabyte]

    # Search results are ordered by number of stars each repo has, so fetch
    # a maximum of 1000 repos.
    top_repos = small_repos[0:1000]

    all_repos += top_repos
