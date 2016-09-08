#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random

from data.tags import *
from data.category import *
from data.description import *

#########  SETTINGS ##########
videos_folder = 'upload'
upload_accounts_folder = 'lib/accounts/'
upload_report_file = 'log/report.txt'
upload_log_file = 'log/upload.log'
# how many videos upload per one account per one session
upload_packet = 5
# timeout sec between upload videos in upload_packet
# upload first video - upload_packet_timeout - upload second video ...
upload_packet_timeout = 10
# timeout sec for uploading one video into one account
upload_timeout = 3600


def make_title(filename):
    title = filename.split('.')[0]
    title = re.sub('[\d_-]', ' ', title)
    return title.strip()
    
    # функция получает filename и возвращает чистое название
    # например, получили 23_Hot_teen_girl.mp4
    # вернули Hot teen girl
    # без цифр _ и расширения mp4

  # Например title = make_title(filename)

def make_category(title, site_category):
    category = []
    for cat in site_category:
        if cat[0][0] in title:
            category.append(cat[1][0])

        if len(category) == 3:
            return category

    for _ in range(3):
        cat_id = random.choice(site_category)[1][0]  
        category.append(cat_id)

        if len(category) == 3:
            return category

    # функция получает чистый титл + название списка категорий для данного сайта из category.py
    # берем из списка категорий первое значение и ищем в title совпадение
    # Ищем сверху вниз по списку
    # Результат функции - возврат 3-х категорий (три номера категорий)
    # вернули 3 категории, если нашли 3
    # вернули 3 категории, если нашли только 2 совпадения + 1 категорию выбрали случайно
    # вернули 3 категории, если нашли только 1 совпадение + 2 категории выбрали случайно
    # вернули 3 тега, если не нашли совпадений + 3 категории выбрали случайно




def make_tags(title, site_tags):
    tags = []
    for tag in site_tags:
        if tag in title:
            tags.append(tag)

        if len(tags) == 3:
            return tags

    for _ in range(3):
        tag = random.choice(site_tags)
        tags.append(tag)

        if len(tags) == 3:
            return tags
    # функция получает чистый титл и возвращает 3 тега
    # берем список tags
    # берем первое значение из списка tags - смотрим его в титле
    # и так по порядку сверху вниз пока не найдем 3 тега.
    # результат функции:
    # вернули 3 тега, если нашли 3
    # вернули 3 тега, если нашли только 2 совпадения + 1 тег выбрали случайно
    # вернули 3 тега, если нашли только 1 совпадение + 2 тега выбрали случайно
    # вернули 3 тега, если не нашли совпадений + 3 тега выбрали случайно


def make_description(pronhub_description):
    description = []
    for _ in range(2):
        desc = random.choice(pronhub_description)
        description.append(desc)

    return description
    # функция выбирает 2 случайные значения из списка description





