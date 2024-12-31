"""Offers functionality for searching an index."""

from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from typing import List, Any, Tuple


def extended_search(words: str, ix: Any) -> List[Tuple[str, str]]:
    """Search in passed index.

    Args:
        words (str): words to search for
        ix (Any): whoosh index

    Returns:
        List[Tuple[str, str]]: hits, list of (link, title) tuples

    """
    w = words.split()
    query_string = " AND ".join(w)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_string)
        results = searcher.search(query)
        hits = []
        for r in results:
            hits.append((r["link"], r["title"]))
        return hits


def search(words: str, index: dict) -> List[str]:
    """Return all links incuding the words from list words using an index returned by crawl().

    Args:
        words (str): words to search for
        index (dict): indexing dict

    Returns:
        List[str]: urls

    """
    links = index[words[0].lower()]
    for i in range(1, len(words)):
        links = links.intersection(index[words[i].lower()])
    return links


if __name__ == "__main__":
    ix = open_dir("indexdir")
    print(extended_search("platypus", ix))
