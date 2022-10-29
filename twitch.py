import requests
import copy
import json
import time
import pickle
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date
import tqdm
from bs4 import BeautifulSoup as bs
import difflib
from collections import defaultdict
from iso639 import languages
import random
import itertools
# from flask import render_template
import jinja2
import re
import settings
env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
gui_template = env.get_template("gui_templete.html")
streamer_info_template = env.get_template("streamer_info_template.html")
api_url='https://woowakgood.live:8007'

def load(filename):
    temp = pickle.load(open(filename, 'rb'))
    print(f'{filename} loaded')
    return temp


def dump(object, filename):
    pickle.dump(object, open(filename, 'wb'))


def isvalidlogin(login):
    return bool(re.match("^[A-Za-z0-9_-]*$",login))


def isvalidlogins(logins):
    for i in logins:
        if not isvalidlogin(i):
            return False
    return True
def dttoko(ti: dt):
    datedifference = (date.today() - ti.date()).days
    if datedifference < 3:
        datename = ['오늘', '어제', '엊그저께'][datedifference]
    elif datedifference < 10:
        datename = '%d일전' % datedifference
    else:
        datename = str(ti.date())
    ex = '오전'
    ho = ti.hour
    if ti.hour > 12:
        ex = '오후'
        ho = ti.hour - 12
    return '%s %s %d시 %d분' % (datename, ex, ho, ti.minute)


def tdtoko(ti: td):
    ms, s, d = ti.microseconds, ti.seconds, ti.days

    if d > 365.25:
        return f'{int(d / 365.25)}년'
    if d > 365 / 12:
        return f'{int(d / (365 / 12))}달'
    if d > 0:
        return f'{d}일'
    if s > 3600:
        return f'{int(s / 3600)}시간'
    if s > 60:
        return f'{int(s / 60)}분'
    if s > 0:
        return f'{s}초'
    if ms > 1000:
        return f'{int(ms / 1000)}ms'
    return f'{ms}us'


def twitch_parse(t):
    return dt.strptime(t, '%Y-%m-%dT%H:%M:%SZ') + td(hours=9)


def timedelta_to_ko(time_delta):
    return '%d 시간 %d 분 %d 초' % (time_delta.seconds // 3600, (time_delta.seconds // 60) % 60, (time_delta.seconds % 60))


def json_print(data):
    print(json.dumps(data, indent=4, sort_keys=True))


def follow_stream(userheaders, login='skuuk1zky'):
    id = login_to_id(login)
    url = 'https://api.twitch.tv/helix/streams/followed?user_id=' + id
    response = requests.get(url, headers=userheaders).json()
    return response


def twitch_api(url):
    return requests.get(url, headers=random.choice(global_header))


def langcode_to_langname(
        lang):  # {'', 'sv', 'fr', 'uk', 'it', 'zh-hk', 'zh', 'en', 'tl', 'da', 'sk', 'hu', 'ro', 'el', 'ru', 'id',
    # 'no', 'ko', 'pl', 'th', 'de', 'cs', 'ar', 'pt', 'ja', 'es', 'fi', 'tr', 'other'}
    try:
        return languages.get(alpha2=lang).name
    except:
        return 'other'


def langcode_to_country(langcode):
    langname = langcode_to_langname(langcode)
    langtocountry = {'Modern Greek (1453-)': '그리스', 'Tagalog': '타갈로그어권 (필리핀 등지)', 'Swedish': '스웨덴어권',
                     'Spanish': '스페인어권 (남미, 스페인 등지)', 'Chinese': '중국', 'French': '프랑스', 'Polish': '폴란드',
                     'Danish': '덴마크', 'Hungarian': '헝가리', 'Romanian': '루마니아', 'Russian': '러시아', 'Norwegian': '노르웨이',
                     'Japanese': '일본어',
                     'Italian': '이탈리아', 'German': '독일', 'Korean': '한국', 'Ukrainian': '우크라이나', 'English': '영어권',
                     'Indonesian': '인도네시아', 'Arabic': '아랍어권',
                     'other': '기타 국가', 'Turkish': '튀르키예 (터키)'}
    if langname in langtocountry:
        return langtocountry[langname]
    return langname


def header_update():
    for i, client_info in enumerate(client_infos):
        response = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={client_info['id']}&client_secret={client_info['secret']}&grant_type=client_credentials")
        access_token = json.loads(response.text)['access_token']
        global_header[i]['client-id'] = client_info['id']
        global_header[i]['Authorization'] = 'Bearer ' + access_token
    print(len(client_infos), ' header updated')


def streams_info(login):
    url = 'https://api.twitch.tv/helix/streams?user_login=' + login
    try:
        req = twitch_api(url)
        print('get streams info')
        json_data = req.json()
        if len(json_data['data']) == 1:
            on_info = json_data['data'][0]
            on_info['started_at'] = twitch_parse(on_info['started_at'])
            on_info['uptime'] = dt.now() - on_info['started_at']
            return on_info
        else:
            return False
    except Exception as e:
        try:
            print(req.text)
        except:
            print('get failed')
        print("Error checking user: ", e, login)
        return False


def total_view(login, refresh=False):
    return login_to_something(login, 'view_count')


def login_to_image(login, refresh=False):
    return login_to_something(login, 'profile_image_url')


def login_to_something(login, information, refresh=False):
    # ['id', 'login', 'display_name', 'type', 'broadcaster_type', 'description', 'profile_image_url', 'offline_image_url', 'view_count', 'created_at']

    if not isinstance(login, list):
        if not refresh:
            if login in streamers_data and information in streamers_data[login]:
                res = streamers_data[login][information]
                print(f'used data of {login} which was updated at {streamers_data[login]["last_updated"]}')
                return res

        try:
            return streamer_info(login)[information]
        except:
            return 'banned'
    else:
        if not refresh:
            try:
                return {i: streamers_data[i][information] for i in login}
            except:
                pass
        return {i['login']: i[information] for i in streamer_info(login)}


time_to_sleep = 1


def channel_info(broadcaster_id: list):
    assert broadcaster_id
    assert type(broadcaster_id) == list
    url = f'https://api.twitch.tv/helix/channels?broadcaster_id={"&broadcaster_id=".join(broadcaster_id)}'
    print('get channel info')
    return twitch_api(url).json()['data']


def login_info(login_list: list):
    assert login_list
    assert type(login_list) == list
    url = 'https://api.twitch.tv/helix/users?login=' + '&login='.join(login_list)
    print('get login info')
    res=twitch_api(url).json()
    return res['data']




def id_info(id_list: list):
    assert id_list
    assert type(id_list) == list
    url = 'https://api.twitch.tv/helix/users?id=' + '&id='.join(id_list)
    print('get id info')
    return twitch_api(url).json()['data']


def streamer_info_api(login_list):
    print(len(login_list))
    print(login_list)
    if '' in login_list:
        login_list.remove('')
    if not login_list:
        return []
    if not isvalidlogins(login_list):
        return []
    req = login_info(login_list)
    if not req:
        return []
    channel_infos = channel_info([i['id'] for i in req])
    lang_infos_dict = {i['broadcaster_login']: i['broadcaster_language'] for i in channel_infos}
    assert len(req) == len(channel_infos)
    for inf in req:
        inf['lang'] = lang_infos_dict[inf['login']]
    return req

def streamer_info_from_data(login_queue,follower_requirements=0):
    if isinstance(login_queue, list):
        islist = True
    else:
        islist = False
        login_queue = [login_queue]

    req = []
    for i in login_queue:
        if i in streamers_data and 'lang' in streamers_data[i] and 'ranking' in streamers_data[i] and streamers_data[i]['followers']>=follower_requirements:  # check for valid data
            req.append(streamers_data[i])
    if islist:
        return req
    else:
        try:
            return req[0]
        except:
            return {'error': 'no such streamers'}
def streamer_info(login_queue, provide_detailed_information_instead_of_data=False, give_chance_to_banned=False,
                  update_follow=True):  # id로 하면 이 모든 짓을 안해도 되는데
    print(update_follow)

    if isinstance(login_queue, list):
        islist = True
    else:
        islist = False
        login_queue = [login_queue]


    logins_data.update(login_queue)
    req = streamer_info_api(login_queue)
    temp_failed = list(set(login_queue) - set([i['login'] for i in req]))
    if temp_failed:
        print('failed',temp_failed)
    banned = []
    updated = []
    added = []
    crawled = []
    failed = []
    # we guess there would not be the streamer that changes name just after banned
    if temp_failed:  # we always check for already banned account whereas we don't check for small streamers, because it would be harder to grow bigger than being freed.
        banned = [streamer_login for streamer_login in temp_failed if
                  streamer_login in streamers_data and streamers_data[streamer_login][
                      'banned'] and not give_chance_to_banned]  # 원래 밴되어 있던 것들은 그대로 밴됨 #list(set(failed)&set(streamers_data.keys()))
        print(banned)
        for originally_banned_streamers in banned:
            assert streamers_data[originally_banned_streamers]['banned']
            #         if not 'banned_histroy' in streamers_data[i].keys():
            #             streamers_data[i]['banned_history'] = []
            #         streamers_data[i]['banned_history'].append(dt.now())
            #         streamers_data[i]['last_updated'] = dt.now()

        newly_banned_or_changed_streamers_old_logins = [streamer_login for streamer_login in temp_failed if
                                                        streamer_login in streamers_data and (not
                                                                                              streamers_data[
                                                                                                  streamer_login][
                                                                                                  'banned'] or give_chance_to_banned)]  # 밴 안되어 있고 원래 있는 것들은 새롭게 밴 되거나 닉 바뀐것 (닉바꼈으면 원래꺼 없애야 되고 이전 닉 기록)
        failed = [streamer_login for streamer_login in temp_failed if
                  not streamer_login in streamers_data]  # 애초에 원래 없었으면 그냥 없는 아이디나 하꼬 중에 밴당한것 인것, 하꼬는 처리 안함
        assert len(banned) + len(newly_banned_or_changed_streamers_old_logins) + len(failed) == len(temp_failed)

        if newly_banned_or_changed_streamers_old_logins:
            # 새롭게 밴 혹은 닉 바뀐 거 처리 부분
            newly_banned_or_changed_streamers_ids = [streamers_data[i]['id'] for i in
                                                     newly_banned_or_changed_streamers_old_logins]
            newly_banned_or_changed_streamers_datas = id_info(newly_banned_or_changed_streamers_ids)
            print(newly_banned_or_changed_streamers_datas)
            changed_streamers_id = [i['id'] for i in newly_banned_or_changed_streamers_datas]
            changed_streamers_new_logins = [i['login'] for i in newly_banned_or_changed_streamers_datas]
            new_id_to_login = {i['id']: i['login'] for i in newly_banned_or_changed_streamers_datas}
            newly_banned_streamers_ids = list(
                set(newly_banned_or_changed_streamers_ids) - set(changed_streamers_id))
            assert len(changed_streamers_id) + len(newly_banned_streamers_ids) == len(
                newly_banned_or_changed_streamers_ids)

            old_id_to_login = {i['id']: i['login'] for i in streamers_data.values()}
            newly_banned_streamers_logins = [old_id_to_login[i] for i in newly_banned_streamers_ids]
            banned += newly_banned_streamers_logins
            changed_streamers_old_logins = list(set(newly_banned_or_changed_streamers_old_logins) - set(
                newly_banned_streamers_logins))  # newly banned는 login은 안바뀌고, 그래서 old 에서 빼면 나옴
            # 기존에 있던 모든 이미 바껴버린 아이디가 들어오게 되있음
            assert len(changed_streamers_old_logins) + len(newly_banned_streamers_logins) == len(
                newly_banned_or_changed_streamers_old_logins)
            assert len(changed_streamers_new_logins) <= len(changed_streamers_old_logins)
            # banned += list(set(newly_banned_or_changed_streamers_old_logins) - set(changed_streamers_new_logins)) 이러면 예전 로그인이 빠지는게 아니라서 안됨
            # strmr data 뒤져서 id는 이거고 로그인은 새거는 아니고 헌거에 속하는 거 찾아도 될듯
            assert bool(changed_streamers_old_logins) == bool(changed_streamers_new_logins)
            if changed_streamers_new_logins:
                for changed_streamer_old_login in changed_streamers_old_logins:
                    assert streamers_data[changed_streamer_old_login]['id'] in changed_streamers_id
                    changed_streamer_new_login = new_id_to_login[streamers_data[changed_streamer_old_login]['id']]
                    print(changed_streamer_old_login, changed_streamer_new_login)

                    if 'past_login' in streamers_data[changed_streamer_old_login]:
                        streamers_data[changed_streamer_new_login]['past_login'] = \
                            streamers_data[changed_streamer_old_login]['past_login'] + [changed_streamer_old_login]
                    else:
                        streamers_data[changed_streamer_new_login]['past_login'] = [changed_streamer_old_login]
                    streamers_data[changed_streamer_new_login].update(streamers_data[changed_streamer_old_login])
                    del streamers_data[changed_streamer_old_login]
                streamer_info(changed_streamers_new_logins)

        for banned_streamer in banned:
            streamers_data[banned_streamer]['banned'] = True
            if not 'banned_histroy' in streamers_data[banned_streamer]:
                streamers_data[banned_streamer]['banned_history'] = []
            streamers_data[banned_streamer]['banned_history'].append(dt.now())
            streamers_data[banned_streamer]['last_updated'] = dt.now()
        ranking_refresh()

        # 오래된거.update() #banned history, login history 등등?

        # past logins
        # select correct past login

    for j, inf in enumerate(req):
        temp_login = inf['login']
        inf['banned'] = False
        inf['created_at'] = twitch_parse(inf['created_at'])
        if not update_follow:
            crawled.append(temp_login)
            streamers_data[temp_login].update(inf)
            print(
                f"just crawled {inf['display_name']}({temp_login}) who speaks in {inf['lang']}")
        else:
            inf['followers'] = followed_api(inf['id'], 100)['total']
            inf['last_updated'] = dt.now()
            streamers_data[temp_login].update(inf)
            ranking_refresh()
            inf.update(streamers_data[temp_login])
            if not temp_login in streamers_data:
                added.append(temp_login)
            else:
                updated.append(temp_login)
            time.sleep(time_to_sleep)
            print(
                f"{'updated' * (temp_login in updated) + 'added' * (temp_login in added)}"
                f" {inf['display_name']}({temp_login}) who have {inf['followers']} followers at the time of {dt.now()} and speaks in {inf['lang']}")


    # streamers_data = {k: v for k, v in sorted(streamers_data.items(), key=lambda item: item[1]['followers'], reverse=True)}
    # what I found : list object is global variable by default, but once you newly assign a object to it, it moves from global namespace to local namespace
    # but still it is possible to change component of mutable objects like list

    if provide_detailed_information_instead_of_data:
        return {'data': req, 'failed': failed, 'banned': banned, 'updated': updated, 'added': added,
                'crawled': crawled}
    return req


def login_to_name(login, refresh=False):
    return login_to_something(login, 'display_name', refresh)


def login_to_ranking(login):
    return login_to_something(login, 'ranking')


def login_last_updated(login):
    return login_to_something(login, 'last_updated')


def login_to_id(login, refresh=False):
    return login_to_something(login, 'id', refresh)


# def id_info(id):
#     if isinstance(id, list):
#         url = 'https://api.twitch.tv/helix/users?id=' + '&id='.join(id)
#         req = twitch_api(url).json()
#         print('get id info')
#         return req
#     else:
#         url = 'https://api.twitch.tv/helix/users?id=' + id
#         req = twitch_api(url).json()
#         print('get id info')
#         return req


def id_to_login(id):
    if isinstance(id, list):
        url = 'https://api.twitch.tv/helix/users?id=' + '&id='.join(id)
        req = twitch_api(url).json()
        print('get id info')
        return [t['login'] for t in req['data']]
    else:
        url = 'https://api.twitch.tv/helix/users?id=' + id
        req = twitch_api(url).json()
        print('get id info')
        return req['data'][0]['login']


def is_following(from_login, to_login):
    return bool(is_following_api(from_login, to_login)['total'])


def is_following_api(from_login, to_login):
    from_id = login_to_id(from_login)
    toid = login_to_id(to_login)
    url = f'https://api.twitch.tv/helix/users/follows?from_id={from_id}&to_id={toid}&first=100'
    req = twitch_api(url).json()
    print('get follow from and to ')
    return req


def both_follow(login):
    ft = followed(login, -1)
    ff = following(login, -1)
    res = []
    for i in ft['data']:
        for j in ff['data']:
            if i['login'] == j['login']:
                res.append({'login': i['login'], 'name': i['name'], 'whenfollow': j['when'], 'whenfollowed': i['when']})
    return res


def following(login, end, also_update_logins=False):
    update_following_data = False
    if end == -1:
        update_following_data = True
        end = float("inf")
    id = login_to_id(login, also_update_logins)
    if not id:
        return 'banned'
    if end <= 100:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=' + id + '&first=' + str(end)
        req = twitch_api(url).json()
        print('get following info')
    else:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=' + id + '&first=100'
        req = twitch_api(url).json()
        print('get following info', end='')
        if len(req['pagination']) > 0:
            cursor = req['pagination']['cursor']
        else:
            cursor = False
        total = req['total']
        end = min(int(total), end)
        data = copy.deepcopy(req['data'])
        while cursor and len(data) <= end:
            url = 'https://api.twitch.tv/helix/users/follows?from_id=' + id + '&first=100&after=' + cursor
            req = twitch_api(url).json()
            print('.', end='')
            data = data + req['data']
            if len(req['pagination']) > 0:
                cursor = req['pagination']['cursor']
            else:
                cursor = False
        data = data[:end]
        req = {"total": total, "data": data}
    temp_follow = [
        {'id': j['to_id'], 'login': j['to_login'], 'name': j['to_name'], 'when': twitch_parse(j['followed_at']),
         'last_updated': dt.now()} for j
        in
        req['data']]
    if update_following_data:
        following_data[login] = temp_follow
        followed_update()
    logins_data.update([i['login'] for i in temp_follow])
    return temp_follow


def followed(login, end):
    id = login_to_id(login)
    res = followed_api(id, end)
    temp = {"total": res['total'], 'data': [
        {'id': j['from_id'], 'login': j['from_login'], 'name': j['from_name'], 'when': twitch_parse(j['followed_at'])}
        for j in res['data']]}
    return temp


def followed_api(id, end):
    if end == -1:
        end = float("inf")
    if end <= 100:
        url = 'https://api.twitch.tv/helix/users/follows?to_id=' + id + '&first=' + str(end)
        req = twitch_api(url).json()
        print('get followed info')
        return req
    else:
        url = 'https://api.twitch.tv/helix/users/follows?to_id=' + id + '&first=100'
        req = twitch_api(url).json()
        print('get followed info', end='')
        if len(req['pagination']) > 0:
            cursor = req['pagination']['cursor']
        else:
            cursor = False
        total = req['total']
        end = min(int(total), end)
        data = copy.deepcopy(req['data'])
        while cursor and len(data) <= end:
            url = 'https://api.twitch.tv/helix/users/follows?to_id=' + id + '&first=100&after=' + cursor
            req = twitch_api(url).json()
            print('.', end='')
            data = data + req['data']
            if len(req['pagination']) > 0:
                cursor = req['pagination']['cursor']
            else:
                cursor = False
        data = data[:end]
        req = {"total": total, "data": data}
        return req


def every_view(login, broadcasters=False):
    watchers = view(login)
    peoples = watchers['viewers'] + watchers['moderators'] + watchers['vips'] + watchers[
        'broadcasters'] * broadcasters + watchers['staff']
    return peoples


now_working_on_view = []


def view(login):

    while login in now_working_on_view:  # or time.time()<now+100:
        time.sleep(0.25)
    if login in temp_view and (time.time() - temp_view[login]['time']) < 60:
        print(f'used view of {login} from {temp_view[login]["time"]}')
        with open('viewlog.txt', 'a') as f:
            f.write(dt.now().strftime("%Y/%m/%d %H:%M:%S"))
        return temp_view[login]['view']
    now_working_on_view.append(login)
    print(now_working_on_view)
    print('view info')
    response = requests.get('https://tmi.twitch.tv/group/user/%s/chatters' % login)

    data = json.loads(response.text)
    viewers = data['chatters']['viewers']
    broadcasters = data['chatters']['broadcaster']

    vips = data['chatters']['vips']

    moderators = data['chatters']['moderators']
    staff = data['chatters']['staff']
    count = int(data['chatter_count'])
    temp_view[login] = {'view': {'broadcasters': broadcasters, 'staff': staff, 'moderators': moderators, 'vips': vips,
                                 'viewers': viewers, 'count': count}, 'time': time.time()}
    now_working_on_view.remove(login)
    print(f'view finished {login}')
    print(now_working_on_view)
    return {'broadcasters': broadcasters, 'staff': staff, 'moderators': moderators, 'vips': vips, 'viewers': viewers,
            'count': count}


def temp_view_clear(time_interval=60):
    for login in temp_view:
        if time.time() - temp_view[login]['time'] >= time_interval:
            del temp_view[login]



def viewer_intersection(streamers):
    intersect = set.intersection(*[set(every_view(streamer, True)) for streamer in streamers])
    return list(intersect)


def hakko_streamers_logins(follower_requirements):
    return [i for i in streamers_data if
            'followers' in streamers_data[i] and streamers_data[i]['followers'] < follower_requirements]


def streamers_data_update(logins_queue, skip_already_done=False, give_chance_to_hakko=False,
                          give_one_more_chance_to_banned=False, update_follow=True, follower_requirements=3000):
    if type(logins_queue) is str:
        logins_queue = [logins_queue]

    total_failed, total_updated, total_added, total_banned, total_crawled = [], [], [], [], []
    index = 0
    #already_done_login = set(streamers_data.keys())
    already_done_login=set({i for i in streamers_data if 'followers' in streamers_data[i]})
    skipped = []
    if skip_already_done:
        skipped = list(already_done_login & set(logins_queue))
        logins_queue = list(set(logins_queue) - already_done_login)
    skipped_hakko = []
    update_data = []
    if not give_chance_to_hakko:
        hakko_list=hakko_streamers_logins(follower_requirements)
        skipped_hakko = list(set(hakko_list) & set(logins_queue))
        logins_queue = list(set(logins_queue) - set(hakko_list))
    pbar = tqdm.tqdm(total=len(logins_queue))
    while index < len(logins_queue):
        queue = logins_queue[index:index + 100]
        results = streamer_info(queue, True, give_one_more_chance_to_banned, update_follow)
        update_data += results['data']
        total_failed += results['failed']
        total_banned += results['banned']
        total_added += results['added']
        total_updated += results['updated']
        total_crawled += results['crawled']
        pbar.update(100)
        index += 100
        time.sleep(time_to_sleep)
    res = {'updated': total_updated, 'added': total_added, 'failed': total_failed,
           'banned': total_banned, 'skipped_hakko': skipped_hakko, 'skipped': skipped,
           'crawled': total_crawled, 'data': update_data}
    pbar.close()
    return res


def logins_data_crawl():
    hdr = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) '
                      'Version/9.0 Mobile/13F69 Safari/601.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    print('crawling login data')
    logins_queue = set()
    for page_num in tqdm.tqdm(range(1, 29)):
        response = requests.get(f"https://twitchtracker.com/channels/most-followers/korean?page={page_num}",
                                headers=hdr,
                                allow_redirects=False).text
        soup = bs(response, 'html.parser')

        for ind in range(100):
            try:
                streamer_login = soup.select_one('#channels > tbody > tr:nth-child(%d) > td:nth-child(3) > a' % ind)[
                                     'href'][1:]
                if not streamer_login in logins_queue:
                    logins_queue.add(streamer_login)
            except:
                pass
    for i in tqdm.tqdm(range(1, 6)):
        response = requests.get(f"https://www.twitchmetrics.net/channels/popularity?lang=ko&page={i}", headers=hdr,
                                allow_redirects=False).text
        soup = bs(response, 'html.parser')
        count = 0
        j = 0
        while True:
            j += 1
            try:
                streamer_login = soup.select_one(
                    f'body > div.container.mt-5 > div.row > div.col-12.col-md-10 > ul > li:nth-child({j}) > div > '
                    f'div.col-lg-8.col-6 > div > div.col-11 > div > div.col-9.col-lg-10 > div.d-flex.mb-2.flex-wrap > '
                    f'a')[
                    'href']
                streamer_login = streamer_login[streamer_login.index('-') + 1:]
                if not streamer_login in logins_queue:
                    logins_queue.add(streamer_login)
                count += 1
            except:
                if count >= 50:
                    break
    original_logins = len(logins_data)
    logins_data.update(logins_queue)
    return logins_queue, len(logins_data) - original_logins


def streamer_data_update_with_logins_data(not_update_originals=True,update_follow=False):
    return streamers_data_update(list(logins_data), not_update_originals, False,update_follow=update_follow)


def streamers_data_refresh_by_itself(rank=1000, lang='ko', update_follow=False):
    return streamers_data_update(list(ranking_in_lang(lang).keys())[:rank], False, False,update_follow=update_follow)


def streamers_data_refresh_by_popular_streamers_follow(rank=100, lang='ko', skip_already_done=True, update_follow=True):
    list_of_popular_streamers = list(ranking_in_lang(lang).keys())[:rank]
    list_to_refresh = list(set.union(
        *[{i['login'] for i in streamer_following(streamer, False)} for streamer in list_of_popular_streamers]) - set(
        ['']))
    return streamers_data_update(list_to_refresh, skip_already_done, False, update_follow=update_follow)


def list_multiplier(a, b):
    return list_merger([[[j] + [i] for i in b] for j in a])


def list_merger(listoflists):
    return list(itertools.chain.from_iterable(listoflists))


def streamers_data_refresh_by_itself_if_not_lang():
    st = list(streamers_data.keys())
    do = []
    for i in st:
        if not 'lang' in streamers_data[i]:
            do.append(i)
    return streamers_data_update(do, False, False)


def streamer_search(query):
    if query in streamers_data:
        return True, streamers_data[query]
    if query.lower() in streamers_data:
        return True, streamers_data[query.lower()]
    name_to_login = {i['display_name'].lower(): i for i in streamers_data.values()}
    if query.lower() in name_to_login:
        return True, name_to_login[query.lower()]
    if isvalidlogin(query):
        print('try to add in streamer search')
        streamer_result = streamer_info(query)
        if streamer_result:
            streamer_data=streamer_result[0]
            assert 'followers' in streamer_data
            assert 'ranking' in streamer_data
            return True, streamer_data

    search_data = list(set(streamers_data.keys())| {i['display_name'].lower() for i in streamers_data.values()})
    return False, difflib.get_close_matches(query, search_data)


def streamer_search_client(query):
    streamer_data = streamer_search(query)
    if not streamer_data[0]:
        temp = f"<meta charset='utf-8'>'{query}'에 해당하는 스트리머가 없습니다. 아이디 또는 닉네임 둘 다로 검색 가능하니 다시 한번 해보세요. " \
               f"<br>만약 실제로 있는 스트리머의 아이디(이름은 추가 불가)라면 이 <a href='{api_url}/twitch/addlogin/?logins={query}&give_chance_to_hakko=true&skip_already_done=false'>링크</a>를 눌러 추가해보세요.<br>"
        if len(streamer_data[1]) == 1:
            temp += f"<a href='/twitch/streamer_watching_streamer/?query={streamer_data[1][0]}'>{streamer_data[1][0]}</a>가 찾고 계신 스트리머 인가요? 만약 그렇다면 링크를 누르세요."
        elif len(streamer_data[1]) > 1:
            temp += f"혹시 {', '.join([f'''<a href='/twitch/streamer_watching_streamer/?query={streamer}'>{streamer}</a>''' for streamer in streamer_data[1]])} 중에 찾고 계신 스트리머가 있나요? "
        return False, temp
    elif streamer_data[1]['banned']:
        temp = f"스트리머 {streamer_data[1]['display_name']}({streamer_data[1]['login']})는 {streamer_data[1]['last_updated']} 기준으로 정지된 것을 확인했습니다. <br>현재는 정지가 해제되었을 수 있으니, 만약 이 스트리머의 상태를 업데이트하고 싶다면 <a href='{api_url}/twitch/addlogin/?logins={streamer_data[1]['login']}&skip_already_done=false'>{streamer_data[1]['login']}</a>으로 접속해서 상태를 갱신하세요."
        return False, temp
    elif not 'followers' in streamer_data[1]:
        print('no followers on streamer search client')
        streamer_data = streamer_info(streamer_data[1]['login'])[0]
        assert 'followers' in streamer_data
        assert 'ranking' in streamer_data
        return True, streamer_data
    else:
        streamer_data = streamer_data[1]
        return True, streamer_data


def streamer_introduce(streamer_data):
    return f"{langcode_to_country(streamer_data['lang'])} 내 트위치 팔로워 <a href='{api_url}/twitch/addlogin/?logins={streamer_data['login']}&skip_already_done=false&give_chance_to_hakko=true'>{streamer_data['ranking'][streamer_data['lang']]}위({streamer_data['followers']}명, {tdtoko(dt.now() - streamer_data['last_updated'])}전 확인)</a> 인 {streamer_data['display_name']} ({streamer_data['login']})"


def currently_banned():
    return {k: v for k, v in streamers_data.items() if v['banned']}


def streamer_following_update():
    logins = list(streamers_data.keys())
    for login in tqdm.tqdm(logins):
        print(login)
        data = following(login, -1, False)
        try:
            print(data['total'])
        except:
            print(data)


def streamer_following(login, refresh=False):
    if not refresh:
        if login in following_data:
            streamer_followings = following_data[login]
            print(f'used following data of {login}')
            return streamer_followings

    return following(login, -1, False)


# def update_logins(login_list):
#     login_list = list(set(login_list) - set(['']))
#     print(f"updated {len(set(login_list) - set(logins_data))} streamers to logins_data.pickle")
#     t=time.time()
#     for i in login_list:
#         if not i in logins_data:
#             logins_data.append(i)
#     print(time.time()-t)
#     pickle.dump(logins_data, open('logins_data.pickle', 'wb'))


def followed_update():
    followed_by_streamers_dict = defaultdict(list)
    for i in following_data:
        for j in following_data[i]:
            if not j['login'] == '':
                followed_by_streamers_dict[j['login']].append(
                    {'login': i, 'when': j['when'], 'last_updated': j['last_updated']})
    logins_data.update(followed_by_streamers_dict.keys())
     #problem of this is that it cannot change the followed data at origin if we initiate function from origin
    settings.followed_data = followed_by_streamers_dict
    print('updated followed_data')
    return followed_by_streamers_dict


def save_datas():
    dump(streamers_data, 'streamers_data.pickle')
    dump(settings.followed_data, 'followed_data.pickle')
    dump(following_data, 'following_data.pickle')
    dump(logins_data, 'logins_data.pickle')


def ranking_in_lang(lang="ko"):
    return {k: v for k, v in sorted(
        [i for i in streamers_data.items() if not i[1]['banned'] and i[1]['lang'] == lang and 'ranking' in i[1]],
        key=lambda item: item[1]['ranking'][lang])}


def ranking_refresh():
    langs = set([streamers_data[i]['lang'] for i in streamers_data if not streamers_data[i]['banned']])
    for lang in langs:
        for i, k in enumerate(sorted([j for j in streamers_data.keys() if not streamers_data[j]['banned'] and streamers_data[j]['lang'] == lang and 'followers' in streamers_data[j]],
                                     key=lambda i: streamers_data[i]['followers'], reverse=True)):
            streamers_data[k]['ranking'] = {lang: i + 1}
    print('ranking refreshed')


def follow_icon(known_following, streamer_followed_data, login):
    if login in streamer_followed_data:
        return "fa-solid fa-heart"
    if login in known_following:
        return "fa-regular fa-heart"
    return "fa-solid fa-question"


def follow_about_heart(known_following, streamer_followed_data, login):
    if login in streamer_followed_data:
        return f"<a href='/twitch/following?query={login}'>{streamer_followed_data[login]['when'].date()}</a>"
    if login in known_following:
        return f"<a href='/twitch/following?query={login}'>새로고침</a>" #refresh 추가
    return f"<a href='/twitch/following?query={login}'>확인하기</a>"


def gui_maker(title, variable, url, buttonname, page_url, submit=False):
    return gui_template.render(title=title, variable=variable, page_url=page_url, url=url, buttonname=buttonname,
                               submit=submit,
                               condition=' || '.join([f'$("#{i[0]}").val() == ""' for i in variable]),input_size=12,input_size_2=int(12/len(variable)))


def streamer_info_maker(v, now, known_following, followed_streamers_data_dict,original_streamer):
    return streamer_info_template.render(login=v['login'], image_url=v['profile_image_url'], name=v['display_name'],
                                         follower=v['followers'], country=langcode_to_country(v['lang']),
                                         rank=v['ranking'][v['lang']], time=tdtoko(now - v['last_updated']),
                                         icon=follow_icon(known_following, followed_streamers_data_dict, v['login']),
                                         following=follow_about_heart(known_following, followed_streamers_data_dict,
                                                                      v['login']),api_url=api_url,login_disp=v['login']!=v['display_name'].lower(),is_manager=('role' in v and original_streamer in v['role']))

def just_crawl_logins(logins_queue):
    streamers_data_update(logins_queue, False, False, False, False)
a = {}
client_infos = load('client_infos.pickle')
global_header = [{} for i in range(len(client_infos))]
header_update()
settings.init()
following_data = load('following_data.pickle')
logins_data = load('logins_data.pickle')
if not isvalidlogins(logins_data):
    logins_data={i for i in logins_data if isvalidlogin(i)}
    print('logins data get fixed')
streamers_data = load('streamers_data.pickle')
#hakko_streamers_data = load('hakko_streamers_data.pickle')
temp_view = {}
# if len(set(streamers_data.keys())&set(hakko_streamers_data.keys()))==0:
#     print('update from hakko')
#     streamers_data_update(list(hakko_streamers_data.keys()), False, False, False, False)
# for i in hakko_streamers_data:
#     if i in streamers_data:
#         if not 'followers' in streamers_data[i]:
#             assert not 'last_updated' in streamers_data[i]
#             streamers_data[i]['followers']=hakko_streamers_data[i]['followers']
#             if 'last_updated' in hakko_streamers_data[i]:
#                 streamers_data[i]['last_updated'] = hakko_streamers_data[i]['last_updated']
#             else:
#                 streamers_data[i]['last_updated']=dt.now()
#     else:
#         print(i)
# assert type(streamers_data) == defaultdict

ranking_refresh()
for i in streamers_data:
    if not streamers_data[i]['banned']:
        assert 'lang' in streamers_data[i]
    if 'followers' in streamers_data[i]:
        assert 'ranking' in streamers_data[i]
        assert 'last_updated' in streamers_data[i]
    if 'last_updated' in streamers_data[i]:
        assert 'followers' in streamers_data[i]

# streamers_data={k: v for k, v in pickle.load(open('streamers_data.pickle', 'rb')).items() if v['followers'] >= follower_requirements}
# assert every thing has lang
print(f" {len(streamers_data)} streamers")
# all_streamers_data = {**streamers_data, **hakko_streamers_data}
# streamers_data = {k: v for k, v in all_streamers_data.items() if v['followers'] >= follower_requirements}
# hakko_streamers_data = {k: v for k, v in all_streamers_data.items() if v['followers'] < follower_requirements}
# print(f"final big strmrs : {len(streamers_data)}, final hakkos : {len(hakko_streamers_data)}")



refresh_token_dict = load('refresh_token_dict')

followed_update()
save_datas()
print('loading finished')
if __name__ == '__main__':
    streamer_info('baalzebb')
    save_datas()
