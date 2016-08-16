#!/usr/bin/python
# -*- coding= utf-8 -*-

import requests
import re
import time

from lib.upload_lib import *
from lib.single import *
import logging as log

basedir = os.path.dirname(__file__)

log.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = log.DEBUG, filename = os.path.join(basedir,  upload_log_file))

name = "pornhub"

#
#log.info("{name}: check if fields exist".format())
#
#log.info("{name}: check if fields exists".format())
#
#
#log.info("{name}: data to report file {login}:{password}:http://www.pornhub.com/view_video.php?viewkey=ph57aa13005297a{public_url}".format())
#
#log.error("{name}: no field 'field-name -название поля, которого нет' , script stopped".format())
#log.error("{name}: exception. ".format())

def get_videos():
    data = os.walk(os.path.join(basedir,  videos_folder))
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
        
def create_session(login, password):
    s = requests.Session()
    
    log.info("{}: try to login into account {}:{}".format(name,  login,  password))

    resp = s.get('http://www.pornhub.com/')

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
    print(resp.text)
    if resp.json()['success'] == 1:
        log.info("{}: login success".format(name))

    return s
    
def get_upload_param():
    url = 'http://www.pornhub.com/upload/get_upload_file_params'

    data = {}
    resp = s.post(url, data)
    print(resp.text)
    url = eval(resp.text)['fileparams'][0]['uploadFileUrl'].replace('\\', '')
    formHash = eval(resp.text)['fileparams'][0]['formHash']
    viewkey = eval(resp.text)['fileparams'][0]['viewkey']
    
    log.info("{}: get upload page {}".format(name,  url))

    return url, formHash, viewkey


def get_file_data(filename):
    with open(os.path.join(basedir,  videos_folder,  filename), 'rb') as files:
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
        print(resp.text)

        if finish_step >= all_length - 1:
            print('break')
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
    tags_ = make_tags(title, tags)
    description_ = make_description(description)
    
    
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
    print(data)

    url = 'http://www.pornhub.com/uploading/save_videodata'

    resp = s.post(url, data)
    print(resp.text)
    if resp.json()['success'] == 'true':
        log.info("{}: upload success".format(name))
    
    
def delete_user_from_file(all_users,  current_user):
    all_users.remove(current_user)
    with open(os.path.join(basedir,  upload_accounts_folder,  'pornhub.txt'),  'w') as files:
        files.write('\n'.join(all_users))
        
def delete_video_from_folder(filename):
    os.remove(os.path.join(basedir,  videos_folder,  filename))
    

def main():
    videos = get_videos()
    if len(videos) <5:
        log.error("{}: no video for uploading, upload skipped".format(name))
        exit()
        
    users= get_user()
    if not users:
        log.error("{}: no accounts to login, upload skipped".format(name))
        exit()
    
    user = users[0]
    
    print(user)
    login = user.split(':')[0]
    password  = user.split(':')[1]
    global s
    s = create_session(login,  password)
    for _ in range(upload_packet):
        video = videos.pop(0)
        print('upload video',  video)
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




