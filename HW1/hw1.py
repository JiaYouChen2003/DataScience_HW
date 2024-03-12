from bs4 import BeautifulSoup
import json
import os
import re
import requests
import threading
import sys

payload = {
    'from': '/bbs/Beauty/index.html',
    'yes': 'yes'
}
rs = requests.session()
rs.post('https://www.ptt.cc/ask/over18', data=payload)


def getSoupByURL(url):
    result = rs.get(url)
    content = result.text
    soup = BeautifulSoup(content, 'html.parser')
    return soup


def findStartAndEndPoint():
    i_min = 0
    j_min = 0
    i_max = 0
    j_max = 0
    for i in range(3600, 3945):
        url = 'https://www.ptt.cc/bbs/Beauty/index' + str(i) + '.html'
        soup = getSoupByURL(url)
        fullTitle_list = soup.find_all('div', {'class': 'title'})
        for j in range(len(fullTitle_list)):
            title = fullTitle_list[j].findChildren('a', recursive=False)[0].text
            if str(title).startswith('[正妹] 孟潔MJ'):
                i_min = i
                j_min = j + 1
            if str(title).startswith('[正妹] 趙露思跨年晚會'):
                i_max = i
                j_max = j + 2
    return [i_min, j_min, i_max, j_max]


def isIn2023(i, j, ijRange):
    i_min, j_min, i_max, j_max = ijRange
    if i < i_min or (i == i_min and j < j_min) or (i == i_max and j >= j_max) or i > i_max:
        return False
    return True


def dateToRegularExpression(date):
    date = re.sub('[^0-9]', '', date.text)
    if len(date) == 3:
        date = '0' + date
    return date


def urlToRegularExpression(url):
    return 'https://www.ptt.cc' + url


def rtcleIsBetweenDates(rtcle, startDate, endDate):
    return int(rtcle['date']) >= int(startDate) and int(rtcle['date']) <= int(endDate)


def addDictKeyValueByOne(inputDict, key):
    outputDict = inputDict
    if inputDict.get(key) is not None:
        outputDict[key] = inputDict[key] + 1
    else:
        outputDict[key] = 1
    return outputDict


def sortAndItemizedDictByValueThenLexicographical(inputDict):
    itemizedDict = sorted(inputDict.items(), reverse=True)
    sortedItemizedDict = sorted(itemizedDict, key=lambda item: item[1], reverse=True)
    return sortedItemizedDict


def dumpPushAndBoo(push, boo, pushAndBooJsonFile):
    pushTop10UserID = []
    booTop10UserID = []
    
    for i in range(1, min(11, len(push) - 1)):
        pushTop10UserID.append({'user_id': push[i][0], 'count': push[i][1]})
        booTop10UserID.append({'user_id': boo[i][0], 'count': boo[i][1]})
    
    pushAndBoo = {
        'push': {
            'total': push[0][1],
            'top10': pushTop10UserID
        },
        'boo': {
            'total': boo[0][1],
            'top10': booTop10UserID
        }
    }
    
    json.dump(pushAndBoo, pushAndBooJsonFile, ensure_ascii=False, indent=4)


def isImageURL(urlText):
    urlText = str(urlText)
    if urlText.startswith('http://') or urlText.startswith('https://'):
        urlText = urlText.lower()
        if urlText.endswith('.jpg') or urlText.endswith('.jpeg') or urlText.endswith('.png') or urlText.endswith('.gif'):
            return True
    return False


def dumpPopularRtcleNumAndImageURLs(popularRtcleNum, popularRtcleImageURLs, popularArticleNumAndImageURLsJsonFile):
    popularRtcleNumAndImageURLs = {
        "number_of_popular_articles": popularRtcleNum,
        "image_urls": popularRtcleImageURLs
    }
    
    json.dump(popularRtcleNumAndImageURLs, popularArticleNumAndImageURLsJsonFile, ensure_ascii=False, indent=4)


def dumpKeywordRtcleImageURLs(keywordRtcleImageURLs, keywordArticleImageURLsJsonFile):
    keywordRtcleImageURLs = {
        "image_urls": keywordRtcleImageURLs
    }
    
    json.dump(keywordRtcleImageURLs, keywordArticleImageURLsJsonFile, ensure_ascii=False, indent=4)


def crawl():
    ijRange = findStartAndEndPoint()
    i_min, j_min, i_max, j_max = ijRange
    
    allArticlesJsonFile = open('articles.jsonl', 'a', encoding='utf8')
    popularArticlesJsonFile = open('popular_articles.jsonl', 'a', encoding='utf8')
    
    for i in range(i_min - 10, i_max + 10):
        url = 'https://www.ptt.cc/bbs/Beauty/index' + str(i) + '.html'
        soup = getSoupByURL(url)
        
        nrec_list = soup.find_all('div', {'class': 'nrec'})
        date_list = soup.find_all('div', {'class': 'date'})
        fullTitle_list = soup.find_all('div', {'class': 'title'})
        
        for j in range(len(fullTitle_list)):
            if not isIn2023(i, j, ijRange):
                continue
            
            date = date_list[j]
            date = dateToRegularExpression(date)
            
            title = fullTitle_list[j].findChildren('a', recursive=False)[0].text
            if str(title).startswith('[公告]') or str(title).startswith('Fw: [公告]'):
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


def processArticles(rtcles, start, end, push, boo, startDate, endDate):
    for rtcle in rtcles[start:end]:
        if rtcleIsBetweenDates(rtcle, startDate, endDate):
            url = rtcle['url']
            soup = getSoupByURL(url)
            
            tweet_list = soup.find_all('div', {'class': 'push'})
            
            for tweet in tweet_list:
                tweetTag = tweet.findChildren('span', recursive=False)[0].text.strip()
                tweetUserID = tweet.findChildren('span', recursive=False)[1].text
                
                if tweetTag == '推':
                    push['total'] = push['total'] + 1
                    push = addDictKeyValueByOne(push, tweetUserID)
                elif tweetTag == '噓':
                    boo['total'] = boo['total'] + 1
                    boo = addDictKeyValueByOne(boo, tweetUserID)


def push(startDate, endDate):
    allArticlesJsonFile = open('articles.jsonl', 'r', encoding='utf8')
    pushAndBooJsonFile = open('push_' + startDate + '_' + endDate + '.json', 'a', encoding='utf8')
    rtcles = [json.loads(Article) for Article in allArticlesJsonFile]
    
    push = {}
    boo = {}
    push['total'] = 0
    boo['total'] = 0
    
    numCores = os.cpu_count()
    articlesPerThread = len(rtcles) // numCores
    ranges = [(i * articlesPerThread, (i + 1) * articlesPerThread) for i in range(numCores - 1)]
    ranges.append(((numCores - 1) * articlesPerThread, len(rtcles)))
    
    threads = []
    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=processArticles, args=(rtcles, start, end, push, boo, startDate, endDate))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
        
    push = sortAndItemizedDictByValueThenLexicographical(push)
    boo = sortAndItemizedDictByValueThenLexicographical(boo)
    
    dumpPushAndBoo(push, boo, pushAndBooJsonFile)


def popular(startDate, endDate):
    popularArticlesJsonFile = open('popular_articles.jsonl', 'r', encoding='utf8')
    popularRtcles = []
    popularArticleNumAndImageURLsJsonFile = open('popular_' + startDate + '_' + endDate + '.json', 'a', encoding='utf8')
    popularRtcleNum = 0
    popularRtcleImageURLs = []
    
    popularRtcles = [json.loads(popularArticle) for popularArticle in popularArticlesJsonFile]
    
    for popularRtcle in popularRtcles:
        if rtcleIsBetweenDates(popularRtcle, startDate, endDate):
            popularRtcleNum = popularRtcleNum + 1
            
            url = popularRtcle['url']
            soup = getSoupByURL(url)
            
            urlText_list = soup.find_all('a')
            
            for urlText in urlText_list:
                urlText = urlText.text
                if isImageURL(urlText):
                    popularRtcleImageURLs.append(urlText)
    dumpPopularRtcleNumAndImageURLs(popularRtcleNum, popularRtcleImageURLs, popularArticleNumAndImageURLsJsonFile)


def processKeyword(rtcles, start, end, keyword, result_list, startDate, endDate):
    keyword_rtcle_image_urls = []
    
    for rtcle in rtcles[start:end]:
        if rtcleIsBetweenDates(rtcle, startDate, endDate):
            url = rtcle['url']
            soup = getSoupByURL(url)
            
            mainContent = soup.find('div', {'id': 'main-content'})
            
            line_list = mainContent.text.split('\n')
            allLine = ''
            for line in line_list:
                line = str(line).strip()
                if line.startswith('※ 發信站'):
                    if allLine.find(keyword) != -1:
                        urlText_list = soup.find_all('a')
                        
                        for urlText in urlText_list:
                            urlText = urlText.text
                            if isImageURL(urlText):
                                keyword_rtcle_image_urls.append(urlText)
                    break
                
                allLine = allLine + line
    result_list.extend(keyword_rtcle_image_urls)


def keyword(startDate, endDate, keyword):
    allArticlesJsonFile = open('articles.jsonl', 'r', encoding='utf8')
    keywordArticleImageURLsJsonFile = open('keyword_' + startDate + '_' + endDate + '_' + keyword + '.json', 'a', encoding='utf8')
    
    rtcles = [json.loads(Article) for Article in allArticlesJsonFile]
    
    numCores = os.cpu_count()
    rtclesPerThread = len(rtcles) // numCores
    ranges = [(i * rtclesPerThread, (i + 1) * rtclesPerThread) for i in range(numCores - 1)]
    ranges.append(((numCores - 1) * rtclesPerThread, len(rtcles)))
    
    threads = []
    result_list = []
    
    for _, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=processKeyword, args=(rtcles, start, end, keyword, result_list, startDate, endDate))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    dumpKeywordRtcleImageURLs(result_list, keywordArticleImageURLsJsonFile)


if __name__ == '__main__':
    if sys.argv[1] == 'crawl':
        crawl()
    elif sys.argv[1] == 'push':
        push(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'popular':
        popular(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'keyword':
        keyword(sys.argv[2], sys.argv[3], sys.argv[4])
