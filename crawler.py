import requests
from bs4 import BeautifulSoup

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
    
def search(words, index):
    """returns all links incuding the words from list words using an index returned by crawl()"""
    links = index[words[0].lower()]
    for i in range (1, len(words)):
        links = links.intersection(index[words[i].lower()])
    return links

if __name__ == "__main__":
    index = crawl('https://vm009.rz.uos.de/crawl/', 'index.html')
    #print(index)
    print(search(["platypus"], index))
    print()
    index2 = crawl('https://iwop.eu/', '')
    print(search(["niemann", "sascha"], index2))