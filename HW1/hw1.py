from bs4 import BeautifulSoup
import requests

payload = {
    'from': '/bbs/Beauty/index.html',
    'yes': 'yes'
}
rs = requests.session()
rs.post("https://www.ptt.cc/ask/over18", data=payload)

for i in range(3656, 3945):
    url = "https://www.ptt.cc/bbs/Beauty/index" + str(i) + ".html"
    result = rs.get(url)
    content = result.text

    soup = BeautifulSoup(content, 'html.parser')
    print(soup.find_all("div", {"class": "title"}))
    print(soup.find_all("div", {"class": "date"}))
