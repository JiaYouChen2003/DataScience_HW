from bs4 import BeautifulSoup
import json
import re
import requests

payload = {
    'from': '/bbs/Beauty/index.html',
    'yes': 'yes'
}
rs = requests.session()
rs.post('https://www.ptt.cc/ask/over18', data=payload)

jsonFile = open('articles.jsonl', 'w', encoding='utf8')

for i in range(3656, 3945):
    url = 'https://www.ptt.cc/bbs/Beauty/index' + str(i) + '.html'
    result = rs.get(url)
    content = result.text
    
    soup = BeautifulSoup(content, 'html.parser')
    date_list = soup.find_all('div', {'class': 'date'})
    full_title_list = soup.find_all('div', {'class': 'title'})
    
    for j in range(len(full_title_list)):
        if i == 3656 and j < 8:
            continue
        elif i == 3944 and j == len(full_title_list) - 5:
            break
        
        date = date_list[j]
        date = re.sub('[^0-9]', '', date.text)
        if len(date) == 3:
            date = '0' + date
        
        title = full_title_list[j].findChildren('a', recursive=False)[0].text
        if str(title).startswith("[公告]") or str(title).startswith("Fw: [公告]"):
            continue
        
        url = 'https://www.ptt.cc' + \
            full_title_list[j].findChildren('a', recursive=False)[0]['href']
        
        rtcle = {
            'date': date,
            'title': title,
            'url': url
        }
        
        json.dump(rtcle, jsonFile, ensure_ascii=False)
        jsonFile.write('\n')
