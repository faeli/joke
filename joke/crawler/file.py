#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
处理文件
"""

import os,sys
import hashlib
import requests


class DownloadFile(object):
    def __init__(self, config):
        if 'res' in config:
            self.dir = config['res']
        else:
            self.dir = 'joke/res'
    
    def load(self, url, file_name=None):
        r = requests.get(url)
        _,ext = os.path.splitext(os.path.basename(url))
        md5obj = hashlib.md5()
        md5obj.update(r.content)
        md5 = str(md5obj.hexdigest())[8:-8]
        if not file_name:
            file_name = md5[8:16]
        file_name = "".join([file_name , ext])
        file_path = os.sep.join([self.dir,md5[:4],md5[4:8]]) 
        out_file = os.sep.join([file_path,file_name])
        # print(md5)
        # print(out_file)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        try:
            tmp_file = open(out_file,'wb')
            tmp_file.write(r.content)
            tmp_file.close()
        except IOError as e:
            print(e)
        return out_file

class DownloadImage(DownloadFile):
    def __init__(self, config):
        super(DownloadImage, self).__init__(config)
        if 'res' in config:
            self.dir = config['res']
        else:
            self.dir = 'joke/res/images'