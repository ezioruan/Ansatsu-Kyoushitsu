#!/usr/bin/env python
# coding=utf-8
"""
Filename:       ansatsu_kyoushitsu.py
Last modified:  2016-03-03 21:27

Description:

"""
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import shutil
import requests
from bs4 import BeautifulSoup
import gevent
from gevent import monkey
monkey.patch_socket()

here = os.path.abspath(os.path.dirname(__file__))
pic_dir = os.path.join(here, 'ansatsu_kyoushitsu')
if not os.path.exists(pic_dir):
    os.mkdir(pic_dir)


base_url = 'http://manhua.fzdm.com/141/'


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
}


def get_chapters():
    soup = BeautifulSoup(requests.get(base_url).text)
    for li in soup.findAll('li', 'pure-u-1-2 pure-u-lg-1-4'):
        chapter = li.a.get('href').split('/')[0]
        #if chapter.isdigit() and int(chapter) < 170:
        #    # 看过了
        #    continue
        url = '%s%s' % (base_url, li.a.get('href'))
        gevent.spawn(download_chapters, li.a.get('title'), url).join()


def download_chapters(title, url):
    print 'download_chapters %s:%s' % (title, url)
    chapter_dir = os.path.join(pic_dir, title)
    if not os.path.exists(chapter_dir):
        os.mkdir(chapter_dir)
    soup = BeautifulSoup(requests.get(url).text)
    for navigation in soup.findAll('div', 'navigation'):
        for a in navigation.findAll('a'):
            sub = a.text
            if sub == u'第1页':
                sub = 1
            elif sub == u'下一页':
                continue
            file_name = os.path.join(chapter_dir, '%s.jpg' % sub)
            chapter_sub_url = '%s%s' % (url, a.get('href'))
            gevent.spawn(save_pic, file_name, chapter_sub_url).join()


def save_pic(file_name, url):
    print 'save_pic', file_name, url
    if os.path.exists(file_name):
        return
    soup = BeautifulSoup(requests.get(url).text)
    img = soup.find(id='mhpic')
    img_url = img.get('src')
    print 'img_url', img_url
    resp = requests.get(img_url, headers=headers, stream=True)
    if resp.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
    else:
        print 'error', resp


def main():
    get_chapters()


if __name__ == "__main__":
    main()
