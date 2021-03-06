#!/usr/bin/python
# -*- coding= utf-8 -*-

import requests
import re
import time
import random
import sys

from lib.upload_lib import *
from lib.single import *
import logging as log

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=log.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

basedir = os.path.dirname(__file__)

log.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s',
                level = log.DEBUG, filename = os.path.join(basedir,  upload_log_file))

stderr_logger = log.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, log.ERROR)
sys.stderr = sl

name = "pornhub"

def get_videos():
    data = os.walk(os.path.join(basedir,  videos_folder, name))
    for root,  dirs,  files in data:
        return files
        
def get_user():
    with open(os.path.join(basedir,  upload_accounts_folder,  'pornhub.txt'),  'r') as files:
        users = files.read().split('\n')
        
    users_list = []
    for user in users:
        if len(user) > 1:
            users_list.append(user)
            
    if len(users_list) > 0:
        return users_list
    else:
        return None

def get_proxy():
    try:
        with open(os.path.join(basedir,  upload_accounts_folder,  'proxy.txt'),  'r') as files:
            proxies = files.read().split('\n')
    except:
        return None

    proxies_list = []
    for proxy in proxies:
        if len(proxy) > 1:
            proxies_list.append(proxy)
            
    if len(proxies_list) > 0:
        return proxies_list
    else:
        return None
        
def create_session(login, password, proxy):
    s = requests.Session()

    p_data = proxy.split(':')

    proxy = 'http://%s:%s@%s:%s/' % (p_data[2], p_data[3], p_data[0], p_data[1])
    s.proxies = {'http':  proxy,
                    'https': proxy}
    
    log.info("{}: try to login into account {}:{}".format(name,  login,  password))

    try:
        resp = s.get('http://www.pornhub.com/')
    except:
        log.info("{}: proxy {} dead".format(name,  proxy))
        return False

    redict = re.findall('name="redirect" value="(.+?)"', resp.text)[0]
    login_key = re.findall('id="login_key" value="(.+?)"', resp.text)[0]
    login_hash = re.findall('id="login_hash" value="(.+?)"', resp.text)[0]

    data = {
        'from': 'pc_login_modal_:index',
        'from': 'pc_login_modal_:index',
        'login_hash': login_hash,
        'login_hash': login_hash,
        'login_key': login_key,
        'login_key': login_key,
        'password': '',
        'password': password,
        'redirect': redict ,
        'redirect': redict ,
        'remember_me': '1',
        'remember_me': '1',
        'username': '',
        'username': login
        }

    url = 'http://www.pornhub.com/front/login_json'

    resp = s.post(url, data)
    log.debug("{}: {}".format(name, resp.text))

    if resp.json()['success'] == 1:
        log.info("{}: login success".format(name))
        return s
    else:
        return 'Bad acc'

    
def get_upload_param():
    url = 'http://www.pornhub.com/upload/get_upload_file_params'

    data = {}
    resp = s.post(url, data)
    log.debug("{}: {}".format(name, resp.text))

    if 'error' in resp.text:
        delete_user_from_file(users,  user)
        log.error("{}: Wrong account. {}".format(name, user))
        exit()
    
    url = eval(resp.text)['fileparams'][0]['uploadFileUrl'].replace('\\', '')
    formHash = eval(resp.text)['fileparams'][0]['formHash']
    viewkey = eval(resp.text)['fileparams'][0]['viewkey']
    
    log.info("{}: get upload page {}".format(name,  url))

    return url, formHash, viewkey


def get_file_data(filename):
    with open(os.path.join(basedir,  videos_folder, name,  filename), 'rb') as files:
        filedata = files.read()

    return filedata
    
def upload_video(filename):
    log.info("{}: try to upload {}".format(name, filename ))
    url, formHash, viewkey = get_upload_param()
    
    all_data = get_file_data(filename)
    all_length = len(all_data)
    finish_step = -1

    while True:
        filedata, start_step, finish_step = get_next_data(finish_step, 11534335,
                                                          all_data, all_length)
        
        s.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
        s.headers['Content-Range'] = 'bytes %s-%s/%s' % (start_step, finish_step, all_length)
        s.headers['Content-Type'] = 'multipart/form-data; boundary=---------------------------30531190830488'
        s.headers['Host'] = 'www.pornhub.com'
        s.headers['Referer'] = 'http://www.pornhub.com/upload/videodata'
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:43.0) Gecko/20100101 Firefox/43.0'
        s.headers['X-Requested-With'] = 'XMLHttpRequest'

        data = '''-----------------------------30531190830488
Content-Disposition: form-data; name="viewkey"

{}
-----------------------------30531190830488
Content-Disposition: form-data; name="formHash"

{}
-----------------------------30531190830488
Content-Disposition: form-data; name="source"

5
-----------------------------30531190830488
Content-Disposition: form-data; name="Filedata"; filename="{}"
Content-Type: video/mp4

'''.format(viewkey, formHash, filename)

        data += filedata
        data += '\n-----------------------------30531190830488--'

        resp = s.post(url, data)
        log.debug("{}: {}".format(name, resp.text))

        if finish_step >= all_length - 1:
            break

    save_videodata(filename, viewkey, formHash)


def get_next_data(prev_step, size, data, all_length):
    start_step = prev_step + 1
    finish_step = start_step + size
    if finish_step >= all_length:
        finish_step = all_length - 1

    filedata = data[start_step:finish_step]
    return filedata, start_step, finish_step

def save_videodata(filename, viewkey, formHash):
    s.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    s.headers.pop('Content-Range')
    s.headers.pop('Content-Disposition')
    
    title = make_title(filename)
    category_ = str(make_category(title, pornhub_category )).replace('\'',  '\"')
    tags_ = ' '.join(make_tags(title, tags))
    description_ = make_description(description)
    log.info("{}: title: {}".format(name, title))
    log.info("{}: category: {}".format(name, category_))
    log.info("{}: tags: {}".format(name, tags_))
    log.info("{}: description: {}".format(name, description_))
    
    
    data = {
        'title': title,
        'platformId': '1',
        'viewkey': viewkey,
        'formHash': formHash,
        'categories': category_,
        'tags': tags_,
        'privacy': 'community',
        'source': '5',
        'pornstars': '',
        'language': 'english',
        'production': 'professional',
        'projectionType': '',
        'vrView': '',
        'vrType': '',
        'timestamp': time.time(),
        'isPremiumVideo': '0'
        }

    url = 'http://www.pornhub.com/uploading/save_videodata'

    resp = s.post(url, data)
    log.debug("{}: {}".format(name, resp.text))
    if resp.json()['success'] == 'true':
        log.info("{}: upload success".format(name))
    
    
def delete_user_from_file(all_users,  current_user):
    all_users.remove(current_user)
    with open(os.path.join(basedir,  upload_accounts_folder,  'pornhub.txt'),  'w') as files:
        files.write('\n'.join(all_users))

def delete_proxy_from_file(all_proxies,  current_proxy):
    all_proxies.remove(current_proxy)
    with open(os.path.join(basedir,  upload_accounts_folder,  'proxy.txt'),  'w') as files:
        files.write('\n'.join(all_proxies))
        
def delete_video_from_folder(filename):
    os.remove(os.path.join(basedir,  videos_folder, name,  filename))
    

def main():
    videos = get_videos()
    if len(videos) <5:
        log.error("{}: no video for uploading, upload skipped".format(name))
        exit()

    global users
    global user
        
    users= get_user()
    if not users:
        log.error("{}: no accounts to login, upload skipped".format(name))
        exit()
    
    user = users[0]
    log.debug("{}: {}".format(name, user))

    proxies = get_proxy()
    if not proxies:
        log.error("{}: no proxy, upload skipped".format(name))
        exit()

    proxy = random.choice(proxies)
    
    login = user.split(':')[0]
    password  = user.split(':')[1]
    
    global s
    s = create_session(login,  password, proxy)
    
    if not s:
        delete_proxy_from_file(proxies, proxy)
        exit()
    elif s == 'Bad acc':
        delete_user_from_file(users,  user)
        log.error("{}: Wrong account. {}".format(name, user))
        exit()
        
    for _ in range(upload_packet):
        video = videos.pop(0)
        log.debug("{}: upload video {}".format(name, video))

        upload_video(video)
        delete_video_from_folder(video)
        time.sleep(upload_packet_timeout)
        
    delete_user_from_file(users,  user)


if __name__ == "__main__":
    soo_lonely = SingleInstance() 
    main()
 # защита от запуска второй копии скрипта
    

 #Берем аккаунт из lib.data.accounts.pornhub.txt
 #смотрим есть ли ролики в upload/pornhub
 #если роликов нет - просто завершаем скрипт

 #если роликов 5 и больше - запускаем заливку.
 #в каждый аккаунт грузим пять роликов.
 #title, tags, description - формируются в upload_lib.py
 #после заливки аккаунт удаляется из pornhub.txt
 
 #**заливка осуществляется через прокси.
 #я на впс подниму прокси.
 #*** скрипт будет работать по крону - поэтому basedir не забыть )




