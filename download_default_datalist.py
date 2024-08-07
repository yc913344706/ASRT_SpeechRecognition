#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2016-2099 Ailemon.net
#
# This file is part of ASRT Speech Recognition Tool.
#
# ASRT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ASRT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ASRT.  If not, see <https://www.gnu.org/licenses/>.
# ============================================================================

"""
@author: nl8590687
用于下载ASRT语音识别系统声学模型训练默认用的数据集列表程序
"""

import os
import logging
import json
import requests
import zipfile
import sys

logging.basicConfig(
    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    level=logging.INFO)

URL_DATALIST_INDEX = "https://d.ailemon.net/asrt_assets/datalist/index.json"

DATASET_DOWNLOAD_DIR = "/data/speech_data"

params = sys.argv[1:]

if len(params) == 0:
    print(f'[WARN] No download directory specified, use default directory [{DATASET_DOWNLOAD_DIR}]')
    user_confirm = input('Are you sure to download datalist to there? (y/n/input_new_dir) > ')
    if user_confirm.lower() == 'y':
        pass
    elif user_confirm.lower() == 'n':
        sys.exit(0)
    else:
        DATASET_DOWNLOAD_DIR = user_confirm

if not os.path.exists(DATASET_DOWNLOAD_DIR):
    logging.error('%s%s', 'Can not find the directory ', DATASET_DOWNLOAD_DIR)
    sys.exit(1)

# default downlaod to ${PWD}/datalist/
DEFAULT_DATALIST_PATH = os.path.join(DATASET_DOWNLOAD_DIR, 'datalist/')
if not os.path.exists(DEFAULT_DATALIST_PATH):
    os.makedirs(DEFAULT_DATALIST_PATH)


def download_datalist():
    # get json from url
    rsp_index = requests.get(URL_DATALIST_INDEX)
    rsp_index.encoding = 'utf-8'
    if rsp_index.ok:
        logging.info('Has connected to ailemon\'s download server...')
    else:
        logging.error('%s%s', 'Can not connected to ailemon\'s download server.',
                    'please check your network connection.')

    index_json = json.loads(rsp_index.text)
    if index_json['status_code'] != 200:
        raise Exception(index_json['status_message'])

    body = index_json['body']
    logging.info('start to download datalist from ailemon\'s download server...')

    for i in range(len(body['datalist'])):
        print(i, body['datalist'][i]['name'])
    print(len(body['datalist']), 'all datalist')

    # select whichone to download
    num = input('Please choose which you select: (default all) > ')
    if len(num) == 0:
        num = len(body['datalist'])
    else:
        num = int(num)
    
    # real download
    if num == len(body['datalist']):
        for i in range(len(body['datalist'])):
            deal_download(body['datalist'][i], body['url_prefix'], DEFAULT_DATALIST_PATH)
    else:
        deal_download(body['datalist'][num], body['url_prefix'], DEFAULT_DATALIST_PATH)

    logging.info('%s%s%s', 'Datalist files download complete. ',
                'Please remember to download these datasets from ',
                body['dataset_download_page_url'])


def deal_download(datalist_item, url_prefix_str, datalist_path):
    """
    to deal datalist file download
    """
    logging.info('%s%s', 'start to download datalist ', datalist_item['name'])
    save_path = datalist_path
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        logging.info('%s`%s`', 'Created directory ', save_path)

    zipfilename = datalist_item['zipfile']
    tmp_url = url_prefix_str + zipfilename
    save_filename = os.path.join(save_path, zipfilename)
    rsp = requests.get(tmp_url)
    with open(save_filename, "wb") as file_pointer:
        file_pointer.write(rsp.content)
    if rsp.ok:
        logging.info('%s `%s` %s', 'Download', zipfilename, 'complete')
    else:
        logging.error('%s%s%s%s%s', 'Can not download ', zipfilename,
                      ' from ailemon\'s download server. ',
                      'http status ok is ', str(rsp.ok))

    f = zipfile.ZipFile(save_filename, 'r')  # 压缩文件位置
    f.extractall(save_path)
    f.close()
    logging.info('%s `%s` %s', 'unzip', zipfilename, 'complete')


if __name__ == "__main__":
    download_datalist()
