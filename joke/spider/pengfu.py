#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from lxml import html
import requests

class Pengfu(object):
    def __init__(self, options=None, index=None):
        self._init(options, index)
    
    # init config
    def _init(self, options, index):
        """
        https://www.pengfu.com/index_{page}.html     def
        https://www.pengfu.com/zuijurenqi_1_{page}.html 热门 HOT
        https://www.pengfu.com/cysk_0_0_1_{page}.html 神回复 SHF
        https://www.pengfu.com/qutu_{page}.html 趣图         IMG
        https://www.pengfu.com/xiaohua_{page}.html 段子      TALK
        """
        self.index = -1
        if not options:
            uri_list = {
                'HOT': {
                    'uri': 'https://www.pengfu.com/zuijurenqi_1_{page}.html',
                    'page': 24
                },
                'SHF': {
                    'uri': 'https://www.pengfu.com/cysk_0_0_1_{page}.html',
                    'page': 15
                },
                'IMG': {
                    'uri': 'https://www.pengfu.com/qutu_{page}.html',
                    'page': 25
                },
                'TALK': {
                    'uri': 'https://www.pengfu.com/xiaohua_{page}.html',
                    'page': 50
                },
                'DEF': {
                    'uri': 'https://www.pengfu.com/index_{page}.html',
                    'page': 50
                }
            }
            options = {
                'uri': uri_list
            }
        
        if index:
            self.index = index
        if 'index' in options:
            self.index = options['index']
        if 'uri' in options:
            self.uri = options['uri']
            
    def jokes(self, uri, topic):
        # print(topic+" : "+uri)
        ret = []
        page = requests.get(uri)
        tree = html.fromstring(page.content)
        jokes = tree.xpath('//div[@class="list-item bg1 b1 boxshadow"]')
        # print(jokes)
        for item in jokes:
            joke = {}
            
            # //*[@id="1698759"]
            joke['origin_id'] = 'PF_' + item.get('id')
            joke['origin'] = 'https://www.pengfu.com'
            joke['origin_name'] = "捧腹网"
            joke['joke_topic'] = topic
            author = item.xpath('dl/dt')[0]
            
            joke['author_id'] = 'PF_' + author.get('id')
            author_img = author.xpath('a/img')[0]
            joke['author_avatar'] = author_img.get('src')
            joke['author_name'] = author_img.get('alt')
            title = item.xpath('dl/dd/h1/a')[0]
            joke['title'] = title.text
            joke['origin_uri'] = title.get('href')
            
            joke['content'] = item.xpath('dl/dd/div[@class="content-img clearfix pt10 relative"]/text()')[0].strip('\r\n\t')
            img = item.xpath('dl/dd/div[@class="content-img clearfix pt10 relative"]/img')
            if len(img) > 0:
                img = img[0]
                joke['jpg'] = img.get('jpgsrc') or img.get('src')
                joke['gif'] = img.get('gifsrc')
            # comment
            comments = item.xpath('div[@class="dl-shenhf"]/dl/dd/div[@class="shenhf-con"]/text()')
            if len(comments) > 0:
                comment = {}
                comment['content'] = comments[0].strip()
                author = item.xpath('div[@class="dl-shenhf"]/dl/dt/a/img')[0]
                
                comment['author_name'] = author.get('alt')
                comment['author_avatar'] = author.get('src')
                comment['author_id'] , _ = os.path.splitext(os.path.basename(comment['author_avatar']))
                comment['author_id'] = 'PF_' + comment['author_id']
                joke['comments'] = [comment]
            
            # tags
            tags = item.xpath('div[@class="action clearfix"]/div[@class="fr"]/a/text()')
            if len(tags) > 0:
                joke['tags'] = tags
            #print(joke)
            ret.append(joke)
        return ret

    # sync to db
    def sync(self,save=None, options=None, index=None):
        self._init(options, index)
        
        keys = list(self.uri.keys())
        keys_count = len(keys)
        
        def run_one(index):
            if index > keys_count:
                print("Done.")
                return
            key = keys[index-1]
            value = self.uri[key]
            uri = value['uri']
            if self.index > 0:
                url = uri.format(page=self.index)
                jokes = self.jokes(url, key)
                if save:
                    save(jokes)
            elif 'page' in value and value['page']>0: 
                page = value['page']
                def run_page(uri,page,index):
                    if index > page:
                        return
                    url = uri.format(page=index)
                    jokes = self.jokes(url,key)
                    if save:
                        save(jokes)
                    run_page(uri,page,index+1)
                run_page(uri,page,1)
            run_one(index+1)
        run_one(1)