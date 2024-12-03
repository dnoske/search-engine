import requests
from bs4 import BeautifulSoup

prefix = 'https://vm009.rz.uos.de/crawl/'

start_url = prefix+'index.html'

agenda = [start_url]
visited = {start_url}

while agenda:
    url = agenda.pop()
    r = requests.get(url)
    type = r.headers["Content-Type"]
    if "text/html" in type or "application/xhtml+xml" in type:
        print("Process ", url)
        soup = BeautifulSoup(r.content, 'html.parser')
        #print(soup)
        links = soup.find_all('a')
        for l in links:
            link = l["href"]
            global_link = False
            if link[0:4] == "http":
                global_link = True
            if global_link and link[0:len(prefix)] == prefix and not l["href"] in visited:
                visited.add(l["href"])
                agenda.append(l["href"])
            elif not global_link and not prefix+l["href"] in visited:
                visited.add(prefix+l["href"])
                agenda.append(prefix+l["href"])