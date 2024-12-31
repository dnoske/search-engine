"""Offers functionality for searching an index."""

from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from whoosh.highlight import UppercaseFormatter
from typing import List, Any, Tuple


def extended_search(words: str, ix: Any) -> List[Tuple[str, str]]:
    """Search in passed index.

    Args:
        words (str): words to search for
        ix (Any): whoosh index

    Returns:
        List[Tuple[str, str]]: hits, list of (link, title) tuples

    """
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(words)
        results = searcher.search(query)
        results.formatter = UppercaseFormatter()
        results.fragmenter.maxchars = 300
        results.fragmenter.surround = 50
        hits = []
        for hit in results:
            hits.append((hit["link"], hit["title"], hit.highlights("content", top=1)))
        return hits


if __name__ == "__main__":
    ix = open_dir("indexdir")
    print(extended_search("platypus", ix))
