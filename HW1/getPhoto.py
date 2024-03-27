import json
import os
import requests
import sys
import threading
import time

import hw1


def isImageURL(urlText):
    urlText = str(urlText)
    if urlText.startswith('http://') or urlText.startswith('https://'):
        urlText = urlText.lower()
        if urlText.endswith('.jpg') or urlText.endswith('.jpeg') or urlText.endswith('.png'):
            return True
    return False


def downloadImages(url, folderName, rtcleCount):
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    soup = hw1.getSoupByURL(url)
    imgUrls = soup.find_all('img')
    
    for imgCount, imgUrl in enumerate(imgUrls):
        imgUrl = imgUrl.get('src')
        try:
            imgFilenum = str(100 * rtcleCount + imgCount)
            imgResponse = requests.get(imgUrl)
            if len(imgResponse.content) > 100:
                imgFile = open(os.path.join(folderName, imgFilenum + '.png'), 'wb')
                imgFile.write(imgResponse.content)
                print(f"{imgFilenum}: {imgUrl}")
            else:
                print('empty image')
        except:
            print('error')
            time.sleep(2)


def crawl():
    ijRange = hw1.findStartAndEndPoint()
    i_min, j_min, i_max, j_max = ijRange
    
    popularPhotoArticlesJsonFile = open('popular_photo_articles.jsonl', 'a', encoding='utf8')
    notPopularPhotoArticlesJsonFile = open('not_popular_photo_articles.jsonl', 'a', encoding='utf8')
    
    for i in range(i_min - 10, i_max + 10):
        url = 'https://www.ptt.cc/bbs/Beauty/index' + str(i) + '.html'
        soup = hw1.getSoupByURL(url)
        
        nrec_list = soup.find_all('div', {'class': 'nrec'})
        date_list = soup.find_all('div', {'class': 'date'})
        fullTitle_list = soup.find_all('div', {'class': 'title'})
        
        for j in range(len(fullTitle_list)):
            if not hw1.isIn2023(i, j, ijRange):
                continue
            
            date = date_list[j]
            date = hw1.dateToRegularExpression(date)
            
            title = fullTitle_list[j].findChildren('a', recursive=False)[0].text
            if str(title).startswith('[公告]') or str(title).startswith('Fw: [公告]'):
                continue
            
            url = fullTitle_list[j].findChildren('a', recursive=False)[0]['href']
            url = hw1.urlToRegularExpression(url)
            
            rtcle = {
                'date': date,
                'title': title,
                'url': url
            }
            
            nrec = nrec_list[j].findChildren('span', recursive=False)
            if len(nrec) != 0:
                if nrec[0].text == '爆':
                    json.dump(rtcle, popularPhotoArticlesJsonFile, ensure_ascii=False)
                    popularPhotoArticlesJsonFile.write('\n')
                    continue
                elif not nrec[0].text.startswith('X'):
                    if int(nrec[0].text) > 35:
                        json.dump(rtcle, popularPhotoArticlesJsonFile, ensure_ascii=False)
                        popularPhotoArticlesJsonFile.write('\n')
                        continue
            
            json.dump(rtcle, notPopularPhotoArticlesJsonFile, ensure_ascii=False)
            notPopularPhotoArticlesJsonFile.write('\n')


def downloadPopularPhotos(popularPhotoArticles, destinationFolder, initialNum):
    for num, article in enumerate(popularPhotoArticles, start=1):
        url = article['url']
        downloadImages(url, destinationFolder, num + initialNum)


def downloadNotPopularPhotos(notPopularPhotoArticles, destinationFolder, initialNum):
    for num, article in enumerate(notPopularPhotoArticles, start=1):
        url = article['url']
        downloadImages(url, destinationFolder, num + initialNum)


def downloadPhoto():
    with open('popular_photo_articles.jsonl', 'r', encoding='utf8') as popularPhotoArticlesJsonFile:
        popularPhotoArticles = [json.loads(line) for line in popularPhotoArticlesJsonFile]
    
    with open('not_popular_photo_articles.jsonl', 'r', encoding='utf8') as notPopularPhotoArticlesJsonFile:
        notPopularPhotoArticles = [json.loads(line) for line in notPopularPhotoArticlesJsonFile]
    
    numCores = os.cpu_count()
    rtclesPerThread = len(popularPhotoArticles) // numCores
    ranges = [(i * rtclesPerThread, (i + 1) * rtclesPerThread) for i in range(numCores - 1)]
    ranges.append(((numCores - 1) * rtclesPerThread, len(popularPhotoArticles)))
    
    popularThreads = []
    for _, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=downloadPopularPhotos, args=(popularPhotoArticles[start:end], './assets/popular/', start))
        popularThreads.append(thread)
        thread.start()
    
    for thread in popularThreads:
        thread.join()
    
    rtclesPerThread = len(notPopularPhotoArticles) // numCores
    ranges = [(i * rtclesPerThread, (i + 1) * rtclesPerThread) for i in range(numCores - 1)]
    ranges.append(((numCores - 1) * rtclesPerThread, len(notPopularPhotoArticles)))
    
    notPopularThreads = []
    for _, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=downloadNotPopularPhotos, args=(notPopularPhotoArticles[start:end], './assets/notPopular/', start))
        notPopularThreads.append(thread)
        thread.start()
    
    for thread in notPopularThreads:
        thread.join()


if __name__ == '__main__':
    if sys.argv[1] == 'crawl':
        crawl()
    elif sys.argv[1] == 'download':
        downloadPhoto()
