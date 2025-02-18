"""Implements functionality that crawls websites and creates an index."""

import requests
from bs4 import BeautifulSoup
import os
from whoosh.index import create_in
from whoosh.fields import *
from urllib.parse import urlparse, urlunparse
from typing import List, Set, Any


def clean_url(url: str) -> str:
    """Remove query arguments and fragments.

    Args:
        url (str): url to be cleaned

    Returns:
        str: cleaned url

    """
    parsed_url = urlparse(url)
    url_cleaned = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            "",
            "",
        )
    )
    return url_cleaned


def is_html(t: str) -> bool:
    """Check whether the passed content-type belongs to html.

    Args:
        t (str): content-type form http header

    Returns:
        bool: True if html

    """
    return "text/html" in t or "application/xhtml+xml" in t


def add_link_if_not_already_visited(
    link: str, prefix: str, agenda: List[str], visited: Set[str]
) -> None:
    """Add link to agenda if it was not already visited.

    Args:
        link (str): link to add
        prefix (str): prefix url
        agenda (List[str]): list of urls to visit
        visited (Set[str]): set of visited urls

    """
    link = clean_url(link)
    parsed_link = urlparse(link)

    # if scheme is mailto or something
    if (
        parsed_link.scheme != "https"
        and parsed_link.scheme != "http"
        and parsed_link.scheme != ""
    ):
        return

    # handle absolute links
    if parsed_link.scheme == "https" or parsed_link.scheme == "http":
        if link[: len(prefix)] == prefix and not link in visited:
            visited.add(link)
            agenda.append(link)
        return

    # get path and get rid of leading or trailing '/'
    link_path = parsed_link.path
    while link_path and link_path[0] == "/":
        link_path = link_path[1:]
    while link_path and link_path[-1] == "/":
        link_path = link_path[:-1]

    link_to_add = prefix + link_path
    if not link_to_add in visited:
        visited.add(link_to_add)
        agenda.append(link_to_add)


def visit_page(url: str, writer: Any, **kwargs) -> None:
    """Add url to index and add all its contained links to agenda.

    Args:
        url (str): url to add to index
        writer (Any): whoosh writer
        **kwargs: Arbitrary keyword arguments.
            prefix (str): prefix url
            agenda (List[str]): list of urls to visit
            visited (Set[str]): set of already visited urls

    """
    response = requests.get(url)

    if not is_html(response.headers["Content-Type"]):
        return
    if response.status_code != 200:
        print(f"{response.status_code}: Something went wrong for {url}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find("title").get_text()
    text = soup.body.get_text()
    writer.add_document(link=url, title=title, content=text)

    links = soup.find_all("a", href=True)
    for l in links:
        link = l["href"]
        add_link_if_not_already_visited(link, **kwargs)


def crawl(prefix: str, home: str, ix: Any = None) -> Any:
    """Will search for all links that can be accessed by the page defined by home of type html with the same prefix and creates an index on you local device using whoosh.

    Args:
        prefix (str): prefix of the url
        home (str): home page
        ix (Any, optional): whoosh index. Defaults to None.

    Returns:
        Any: whoosh index

    """
    start_url = prefix + home
    agenda = [start_url]
    visited = {start_url}
    os.makedirs("indexdir", exist_ok=True)
    if not ix:
        ix = create_in(
            "indexdir",
            Schema(
                link=TEXT(stored=True, phrase=False),
                title=TEXT(stored=True, phrase=False),
                content=TEXT(phrase=False, stored=True),
            ),
        )
    writer = ix.writer()
    while agenda:
        url = agenda.pop()
        visit_page(url, writer, agenda=agenda, visited=visited, prefix=prefix)

    writer.commit()
    return ix


if __name__ == "__main__":
    index = crawl("https://vm009.rz.uos.de/crawl/", "index.html")
