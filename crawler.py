import requests
from bs4 import BeautifulSoup
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

def whoosh_crawl(prefix, home):
    """will search for all links that can be accessed by the page defined by home of type html with the same prefix and creates an index on you local device using whoosh""" 
    start_url = prefix + home
    agenda = [start_url]
    visited = {start_url}
    script_dir = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(script_dir + os.sep + "indexdir"):
        os.mkdir(script_dir + os.sep + "indexdir")
    ix = create_in(script_dir + os.sep + "indexdir", Schema(link=TEXT(stored=True, phrase=False), title=TEXT(stored=True, phrase=False), content=TEXT(phrase=False)))
    writer = ix.writer()
    while agenda:
        url = agenda.pop()
        r = requests.get(url)
        type = r.headers["Content-Type"]
        if ("text/html" in type or "application/xhtml+xml" in type) and r.status_code != 404 and r.status_code != 414:
            if r.status_code != 200:
                print(r.status_code)
                print(f"Something went wrong for {url}")
                print()
            print("Process ", url)
            print()
            soup = BeautifulSoup(r.content, 'html.parser')
            title = soup.find('title').get_text()
            text = soup.body.get_text()
            writer.add_document(link=url, title=title, content=text)
            
            links = soup.find_all('a', href=True)
            for l in links:
                link = l["href"]
                global_link = False
                if link.startswith(('http://', 'https://', 'mailto:')):
                    global_link = True
                if global_link and link[0:len(prefix)] == prefix and not link in visited:
                    visited.add(link)
                    agenda.append(link)
                elif not global_link:
                    if link and link[0] == "/":
                        link = link[1:]
                    if not prefix+link in visited:
                        visited.add(prefix+link)
                        agenda.append(prefix+link)

    writer.commit()
    return ix


def crawl(prefix, home):
    """will search for all links that can be accessed by the page defined by home of type html with the same prefix and return an in-memory index""" 
    start_url = prefix + home
    agenda = [start_url]
    visited = {start_url}
    indexing = {}

    while agenda:
        url = agenda.pop()
        r = requests.get(url)
        type = r.headers["Content-Type"]
        if ("text/html" in type or "application/xhtml+xml" in type) and r.status_code != 404 and r.status_code != 414:
            if r.status_code != 200:
                print(r.status_code)
                print(f"Something went wrong for {url}")
                print()
            print("Process ", url)
            print()
            soup = BeautifulSoup(r.content, 'html.parser')
            print(soup)
            print()
            for s in soup:
                w = ""
                for char in s.get_text():
                    if char.isalpha():
                        w = w + char.lower()
                    elif not w in indexing and w != "":
                        indexing[w] = {url}
                        w = ""
                    elif w != "":
                        indexing[w].add(url)
                        w = ""
            
            links = soup.find_all('a', href=True)
            for l in links:
                link = l["href"]
                global_link = False
                if link.startswith(('http://', 'https://', 'mailto:')):
                    global_link = True
                if global_link and link[0:len(prefix)] == prefix and not link in visited:
                    visited.add(link)
                    agenda.append(link)
                elif not global_link:
                    if link and link[0] == "/":
                        link = link[1:]
                    if not prefix+link in visited:
                        visited.add(prefix+link)
                        agenda.append(prefix+link)
    return indexing

def whoosh_search(words, ix):
    query_string = " AND ".join(words)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_string)
        results = searcher.search(query)
        for r in results:
            print(f"Found words {query_string} on page {r['link']} with title {r['title']}")
    
def search(words, index):
    """returns all links incuding the words from list words using an index returned by crawl()"""
    links = index[words[0].lower()]
    for i in range (1, len(words)):
        links = links.intersection(index[words[i].lower()])
    return links

if __name__ == "__main__":
    index = whoosh_crawl('https://vm009.rz.uos.de/crawl/', 'index.html')
    whoosh_search(["platypus"], index)
    #whoosh_crawl('https://iwop.eu/', '')
    #whoosh_search(["niemann", "sascha"], index))