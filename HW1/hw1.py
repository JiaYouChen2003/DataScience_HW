from bs4 import BeautifulSoup
import json
import re
import requests
import sys

payload = {
    'from': '/bbs/Beauty/index.html',
    'yes': 'yes'
}
rs = requests.session()
rs.post('https://www.ptt.cc/ask/over18', data=payload)


def crawl():
    allArticlesJsonFile = open('articles.jsonl', 'w', encoding='utf8')
    popularArticlesJsonFile = open('popular_articles.jsonl', 'w', encoding='utf8')
    
    for i in range(3656, 3945):
        url = 'https://www.ptt.cc/bbs/Beauty/index' + str(i) + '.html'
        result = rs.get(url)
        content = result.text
        
        soup = BeautifulSoup(content, 'html.parser')
        nrec_list = soup.find_all('div', {'class': 'nrec'})
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
            
            if len(nrec_list[j].findChildren('span', recursive=False)) != 0:
                if nrec_list[j].findChildren('span', recursive=False)[0].text == '爆':
                    json.dump(rtcle, popularArticlesJsonFile, ensure_ascii=False)
                    popularArticlesJsonFile.write('\n')
            
            json.dump(rtcle, allArticlesJsonFile, ensure_ascii=False)
            allArticlesJsonFile.write('\n')


def push(startDate, endDate):
    allArticlesJsonFile = open('articles.jsonl', 'r', encoding='utf8')
    rtcles = []
    
    for Article in allArticlesJsonFile:
        rtcles.append(json.loads(Article))
    
    for rtcle in rtcles:
        if int(rtcle['date']) >= int(startDate) and int(rtcle['date']) <= int(endDate):
            print(rtcle)


if __name__ == "__main__":
    if sys.argv[1] == 'crawl':
        crawl()
    elif sys.argv[1] == 'push':
        push(sys.argv[2], sys.argv[3])
