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
            print("Process ", url)
            soup = BeautifulSoup(r.content, 'html.parser')
            #print(soup)
            #print()
            links = soup.find_all('a', href=True)
            for l in links:
                link = l["href"]
                global_link = False
                if link.startswith(('http://', 'https://', 'mailto:')):
                    global_link = True
                if global_link and link[0:len(prefix)] == prefix and not l["href"] in visited:
                    visited.add(link)
                    agenda.append(link)
                elif not global_link:
                    if link[0] == "/":
                        link = link[1:]
                    if not prefix+link in visited:
                        visited.add(prefix+link)
                        agenda.append(prefix+link)

if __name__ == "__main__":
    crawl('https://vm009.rz.uos.de/crawl/', 'index.html')
    #crawl('https://de.wikipedia.org/', 'wiki/Wikipedia:Hauptseite')
    #crawl('https://www.uni-osnabrueck.de/', 'startseite/')