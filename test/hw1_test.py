import json
import pytest

from HW1 import hw1


@pytest.mark.hw1
def test_nothing():
    assert True


@pytest.mark.hw1
@pytest.mark.longExecuteTime
def test_crawl():
    hw1.crawl()
    
    allArticlesJsonFile = open('articles.jsonl', 'r', encoding='utf8')
    popularArticlesJsonFile = open('popular_articles.jsonl', 'r', encoding='utf8')
    rtcles = []
    popularRtcles = []
    
    for Article in allArticlesJsonFile:
        rtcles.append(json.loads(Article))
    assert len(rtcles) == 5684
    
    for popularArticles in popularArticlesJsonFile:
        popularRtcles.append(json.loads(popularArticles))
    assert len(popularRtcles) == 165


@pytest.mark.hw1
def test_push():
    hw1.push('0304', '0305')
    
    pushAndBooJsonFile = open('push_0304_0305.json', 'r', encoding='utf8')
    pushAndBoo = json.load(pushAndBooJsonFile)
    assert pushAndBoo['push']['total'] == 789
    assert pushAndBoo['boo']['total'] == 120
    
    pushTop10UserIDs = ['qqwwweee', 'HsiangMing', 'spermjuice', 'amare1015', 'FoRTuNaTeR', 'sikadear', 'johnwu', 'Krishna', 'yggyygy', 'wafiea708']
    for i, pushTop10UserID in enumerate(pushAndBoo['push']['top10']):
        assert pushTop10UserID['user_id'] == pushTop10UserIDs[i]
    
    booTop10UserIDs = ['chiz2', 'angelsi', 'adolf111', 'ShockHo222', 'JustinTurner', 'talesb72232', 'noname78531', 'madeathmao', 'hide7isgod', 'ddIvan']
    for i, booTop10UserID in enumerate(pushAndBoo['boo']['top10']):
        assert booTop10UserID['user_id'] == booTop10UserIDs[i]


@pytest.mark.hw1
def test_popular():
    hw1.popular('0304', '0331')
    
    popularArticleNumAndImageURLsJsonFile = open('popular_0304_0331.json', 'r', encoding='utf8')
    popularArticleNum = json.load(popularArticleNumAndImageURLsJsonFile)
    assert popularArticleNum['number_of_popular_articles'] == 10
    assert len(popularArticleNum['image_urls']) == 170


@pytest.mark.hw1
def test_keyword():
    hw1.keyword('0304', '0305', '神人')
    
    keywordArticleImageURLsJsonFile = open('keyword_0304_0305_神人.json', 'r', encoding='utf8')
    keywordArticleImageURLs = json.load(keywordArticleImageURLsJsonFile)
    assert len(keywordArticleImageURLs['image_urls']) == 14
