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


def dateToRegularExpression(date):
    date = re.sub('[^0-9]', '', date.text)
    if len(date) == 3:
        date = '0' + date
    return date


def urlToRegularExpression(url):
    return 'https://www.ptt.cc' + url


def dictAddKeyValueByOne(inputDict, key):
    if inputDict.get(key) is not None:
        inputDict[key] = inputDict[key] + 1
    else:
        inputDict[key] = 1
    return inputDict


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
        fullTitle_list = soup.find_all('div', {'class': 'title'})
        
        for j in range(len(fullTitle_list)):
            if i == 3656 and j < 8:
                continue
            elif i == 3944 and j == len(fullTitle_list) - 5:
                break
            
            date = date_list[j]
            date = dateToRegularExpression(date)
            
            title = fullTitle_list[j].findChildren('a', recursive=False)[0].text
            if str(title).startswith("[公告]") or str(title).startswith("Fw: [公告]"):
                continue
            
            url = fullTitle_list[j].findChildren('a', recursive=False)[0]['href']
            url = urlToRegularExpression(url)
            
            rtcle = {
                'date': date,
                'title': title,
                'url': url
            }
            
            json.dump(rtcle, allArticlesJsonFile, ensure_ascii=False)
            allArticlesJsonFile.write('\n')
            
            nrec = nrec_list[j].findChildren('span', recursive=False)
            if len(nrec) != 0:
                if nrec[0].text == '爆':
                    json.dump(rtcle, popularArticlesJsonFile, ensure_ascii=False)
                    popularArticlesJsonFile.write('\n')


def push(startDate, endDate):
    allArticlesJsonFile = open('articles.jsonl', 'r', encoding='utf8')
    rtcles = []
    push = {}
    boo = {}
    push['total'] = 0
    boo['total'] = 0
    
    for Article in allArticlesJsonFile:
        rtcles.append(json.loads(Article))
    
    for rtcle in rtcles:
        if int(rtcle['date']) >= int(startDate) and int(rtcle['date']) <= int(endDate):
            url = rtcle['url']
            result = rs.get(url)
            content = result.text
            
            soup = BeautifulSoup(content, 'html.parser')
            tweet_list = soup.find_all('div', {'class': 'push'})
            
            for tweet in tweet_list:
                tweetTag = tweet.findChildren('span', recursive=False)[0].text.strip()
                tweetUserID = tweet.findChildren('span', recursive=False)[1].text
                
                if tweetTag == '推':
                    push['total'] = push['total'] + 1
                    push = dictAddKeyValueByOne(push, tweetUserID)
                elif tweetTag == '噓':
                    boo['total'] = boo['total'] + 1
                    boo = dictAddKeyValueByOne(boo, tweetUserID)
    print(push)
    print(boo)


if __name__ == "__main__":
    if sys.argv[1] == 'crawl':
        crawl()
    elif sys.argv[1] == 'push':
        push(sys.argv[2], sys.argv[3])
