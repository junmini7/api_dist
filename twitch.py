import requests
import copy
import json
import time
import pickle
from datetime import datetime as dt
from datetime import timedelta as td
import tqdm
from bs4 import BeautifulSoup as bs
import difflib
from collections import defaultdict
from iso639 import languages
import random

follower_requirements = 3000
streamers_data = pickle.load(open('streamers_data.pickle', 'rb'))
# streamers_data={k: v for k, v in pickle.load(open('streamers_data.pickle', 'rb')).items() if v['followers'] >= follower_requirements}
hakko_streamers_data = pickle.load(open('hakko_streamers_data.pickle', 'rb'))
print(len(streamers_data), len(hakko_streamers_data))
assert len(set(hakko_streamers_data.keys()) & set(streamers_data.keys())) == 0
all_streamers_data = {**streamers_data, **hakko_streamers_data}
streamers_data = {k: v for k, v in all_streamers_data.items() if v['followers'] >= follower_requirements}
hakko_streamers_data = {k: v for k, v in all_streamers_data.items() if v['followers'] < follower_requirements}
print(len(streamers_data), len(hakko_streamers_data))


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


# 'fr', 'pt', 'other', 'es', 'zh-hk', 'th', 'da', 'uk', 'cs', 'zh', 'en', 'tr', 'ar', 'sv', 'it', 'ko', 'id', 'ru', 'de', 'pl', 'ja', 'no', 'fi'}

client_infos = pickle.load(open('client_infos.pickle', 'rb'))


def twitch_api(url):
    return requests.get(url, headers=random.choice(global_header))


def langcode_to_langname(lang):
    return languages.get(alpha2=lang).name


def langcode_to_country(langcode):
    langname = langcode_to_langname(langcode[:2])
    langtocountry = {'Korean': '한국', 'Japanese': '일본', 'English': '영어권'}
    if langname in langtocountry:
        return langtocountry[langname]
    return langname


def header_update():
    print('header updated')
    for i, client_info in enumerate(client_infos):
        response = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={client_info['id']}&client_secret={client_info['secret']}&grant_type=client_credentials")
        access_token = json.loads(response.text)['access_token']
        global_header[i]['client-id'] = client_info['id']
        global_header[i]['Authorization'] = 'Bearer ' + access_token


global_header = [{} for i in range(len(client_infos))]

header_update()
print(global_header)
refresh_token_dict = pickle.load(open('refresh_token_dict', 'rb'))


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


def channel_info(broadcaster_id):
    url = f'https://api.twitch.tv/helix/channels?broadcaster_id={broadcaster_id}'
    print('get channel info')
    return twitch_api(url).json()


def total_view(login, refresh=False):
    return login_to_something(login, 'view_count')


def login_to_image(login, refresh=False):
    return login_to_something(login, 'profile_image_url')


def channel_id_to_lang(id):
    return channel_info(id)['data'][0]['broadcaster_language']


def login_to_something(login, information,
                       refresh=False):  # ['id', 'login', 'display_name', 'type', 'broadcaster_type', 'description', 'profile_image_url', 'offline_image_url', 'view_count', 'created_at']

    if not isinstance(login, list):
        if not refresh:
            try:
                res = streamers_data[login][information]
                print(f'used data of {login} which was updated at {streamers_data[login]["last_updated"]}')
                return res
            except:
                pass
        try:
            return login_info(login, True, True)[information]
        except:
            return 'banned'
    else:
        if not refresh:
            try:
                return {i: streamers_data[i][information] for i in login}
            except:
                pass
        return {i['login']: i[information] for i in login_info(login, True, True)}

time_to_sleep=[0.2]
def login_info(login, update_follow=False, give_chance_to_hakko=False, provide_detailed_information=False,
               refresh=True):
    if isinstance(login, list):
        islist = True
    else:
        islist = False
        login = [login]
    if not refresh:
        req=[]
        for i in login:
            try:
                if 'lang' in streamers_data[i].keys():
                    req.append(streamers_data[i])
            except:
                pass
        #req = [streamers_data[i] for i in login if not i in hakko_streamers_data and not streamers_data[i]['banned']]
        if islist:
            return req
        else:
            try:
                return req[0]
            except:
                return {'error':'no such streamers'}
    else:
        update_logins(login)
        print(len(login))
        print(login)
        url = 'https://api.twitch.tv/helix/users?login=' + '&login='.join(login)
        req = twitch_api(url).json()['data']
        print('get login info')
        failed = list(set(login) - set([i['login'] for i in req]))
        banned = []
        updated = []
        added = []
        new_hakko = []
        still_hakko = []
        streamers_to_hakko = []
        hakko_to_streamers = []
        if failed:
            print('banned or unavailable accounts : ', failed)
            for i in failed:
                if i in streamers_data:
                    print('banned : ', i)
                    banned.append(i)
                    streamers_data[i]['banned'] = True
                    if not 'banned_histroy' in streamers_data[i].keys():
                        streamers_data[i]['banned_history'] = []
                    streamers_data[i]['banned_history'].append(dt.now())
                    streamers_data[i]['last_updated'] = dt.now()
            failed = list(set(failed) - set(banned))
            save_datas()
        for j, inf in enumerate(req):
            temp_login = inf['login']

            # print('inspecting', temp_login, 'in login_informaton')
            if (not temp_login in streamers_data) or update_follow or streamers_data[temp_login][
                'banned']:
                inf['followers'] = followed_api(inf['id'], 100)['total']
                inf['last_updated'] = dt.now()
                inf['banned'] = False
                if inf['followers'] < follower_requirements:
                    if temp_login in streamers_data:
                        del streamers_data[temp_login]
                        streamers_to_hakko.append(temp_login)
                    elif temp_login in hakko_to_streamers:
                        still_hakko.append(temp_login)
                    else:
                        new_hakko.append(temp_login)
                    hakko_streamers_data[temp_login] = inf
                    pickle.dump(hakko_streamers_data, open('hakko_streamers_data.pickle', 'wb'))
                    print(temp_login, 'saved to hakko_streamers_data')
                else:
                    if temp_login in hakko_streamers_data:
                        del hakko_streamers_data[temp_login]
                        hakko_to_streamers.append(temp_login)
                    elif temp_login in streamers_data:
                        updated.append(temp_login)
                    else:
                        added.append(temp_login)
                    inf['lang'] = channel_id_to_lang(inf['id'])

                    streamers_data[temp_login] = inf
                    ranking_refresh()
                    print(
                        f"{'updated' * (temp_login in updated) + 'added' * (temp_login in added) + 'new hakko' * (temp_login in new_hakko)} \
                        {inf['display_name']}({temp_login}) who have {inf['followers']} followers at the time of {dt.now()} \
                        and speaks in {inf['lang']}")
            save_datas()
            print(temp_login, 'saved to streamers_data')

            time.sleep(time_to_sleep[0])

        # streamers_data = {k: v for k, v in sorted(streamers_data.items(), key=lambda item: item[1]['followers'], reverse=True)}
        # what I found : list object is global variable by default, but once you newly assign a object to it, it moves from global namespace to local namespace
        # but still it is possible to change component of mutable objects like list

        if provide_detailed_information:
            return {'data': req, 'failed': failed, 'banned': banned, 'updated': updated, 'added': added,
                    'new_hakko': new_hakko,
                    'still_hakko': still_hakko,
                    'streamers_to_hakko': streamers_to_hakko,
                    'hakko_to_streamers': hakko_to_streamers}
        if islist:
            return req
        else:
            return req[0]
    # else:
    #     update_logins([login])
    #     url = 'https://api.twitch.tv/helix/users?login=' + login
    #     req = twitch_api(url).json()
    #     try:
    #         inf = req['data'][0]
    #         result_message = 'nothing'
    #         if not login in streamers_data or update_follow or streamers_data[login]['banned']:
    #             inf['followers'] = followed_api(inf['id'], 100, headers)['total']
    #             inf['last_updated'] = dt.now()
    #             inf['banned'] = False
    #             if not login in streamers_data:
    #                 result_message = 'added'
    #             else:
    #                 result_message = 'updated'
    #             print('updated' * (login in streamers_data) + 'added' * (not login in streamers_data),
    #                   login,
    #                   inf['followers'])
    #             streamers_data[login] = inf
    #             for i, k in enumerate(sorted([j for j in streamers_data.keys() if not streamers_data[j]['banned']],
    #                                          key=lambda i: streamers_data[i]['followers'], reverse=True)):
    #                 streamers_data[k]['ranking'] = {'ko': i + 1}
    #             pickle.dump(streamers_data, open('streamers_data.pickle', 'wb'))
    #             print(login, 'saved to streamer_data')
    #
    #     except:
    #         print('banned or unavailable accounts : ', login)
    #         result_message = 'failed'
    #         if login in streamers_data:
    #             result_message += ' banned'
    #             streamers_data[login]['banned'] = True
    #             streamers_data[login]['last_updated'] = dt.now()
    #         inf = {}
    #     if provide_detailed_information:
    #         return {'data': inf, 'detailed_message': result_message}
    #     else:
    #         return inf


def login_to_name(login, refresh=False):
    return login_to_something(login, 'display_name', refresh)


def login_to_ranking(login):
    return login_to_something(login, 'ranking')


def login_last_updated(login):
    return login_to_something(login, 'last_updated')


def login_to_id(login, refresh=False):
    return login_to_something(login, 'id', refresh)


def id_info(id):
    if isinstance(id, list):
        url = 'https://api.twitch.tv/helix/users?id=' + '&id='.join(id)
        req = twitch_api(url).json()
        print('get id info')
        return req
    else:
        url = 'https://api.twitch.tv/helix/users?id=' + id
        req = twitch_api(url).json()
        print('get id info')
        return req


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


def following(login, end, also_update_logins=True):
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
    temp_follow = [{'id': j['to_id'], 'login': j['to_login'], 'name': j['to_name'], 'when': twitch_parse(j['followed_at']),'last_updated':dt.now()} for j
        in
        req['data']]
    if update_following_data:
        follow = pickle.load(open('following_data.pickle', 'rb'))
        follow[login] = temp_follow
        pickle.dump(follow, open('following_data.pickle', 'wb'))
        followed_update()
        del follow
        print(login, 'saved to following_data')
    update_logins([i['login'] for i in temp_follow])
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


temp_view = {}


def every_view(login, broadcasters=False):
    watchers = view(login)
    peoples = watchers['viewers'] + watchers['moderators'] + watchers['vips'] + watchers[
        'broadcasters'] * broadcasters + watchers['staff']
    return peoples


def view(login):
    if login in temp_view and (time.time() - temp_view[login]['time']) < 60:
        with open('viewlog.txt', 'a') as f:
            f.write(dt.now().strftime("%Y/%m/%d %H:%M:%S"))
        return temp_view[login]['view']

    response = requests.get('https://tmi.twitch.tv/group/user/%s/chatters' % login)
    print('view info')
    data = json.loads(response.text)
    viewers = data['chatters']['viewers']
    broadcasters = data['chatters']['broadcaster']
    vips = data['chatters']['vips']
    moderators = data['chatters']['moderators']
    staff = data['chatters']['staff']
    count = int(data['chatter_count'])
    temp_view[login] = {'view': {'broadcasters': broadcasters, 'staff': staff, 'moderators': moderators, 'vips': vips,
                                 'viewers': viewers, 'count': count}, 'time': time.time()}
    return {'broadcasters': broadcasters, 'staff': staff, 'moderators': moderators, 'vips': vips, 'viewers': viewers,
            'count': count}


def temp_view_clear(time_interval=60):
    for login in temp_view:
        if time.time() - temp_view[login]['time'] >= time_interval:
            del temp_view[login]


def streamer_watching(login):
    peoples = every_view(login)
    return {k: v for k, v in streamers_data.items() if k in peoples}


def watcher_num(login):
    return len(every_view(login))


def viewer_intersection(streamers):
    intersect = set.intersection(*[set(every_view(streamer, True)) for streamer in streamers])
    return list(intersect)


def streamers_data_update(logins_data, skip_already_done=False, give_chance_to_hakko=False):
    if type(logins_data) is str:
        logins_data = [logins_data]
    total_failed, total_updated, total_added, total_banned, total_new_hakko, total_still_hakko, total_streamers_to_hakko, total_hakko_to_streamers = [], [], [], [], [], [], [], []
    index = 0
    already_done_login = set(streamers_data.keys())
    skipped = []
    if skip_already_done:
        skipped = list(already_done_login & set(logins_data))
        logins_data = list(set(logins_data) - already_done_login)
    skipped_hakko = []
    if not give_chance_to_hakko:
        skipped_hakko = list(set(hakko_streamers_data.keys()) & set(logins_data))
        logins_data = list(set(logins_data) - set(hakko_streamers_data.keys()))
    pbar = tqdm.tqdm(total=len(logins_data))
    while index < len(logins_data):
        queue = logins_data[index:index + 100]
        try:
            results = login_info(queue, True, give_chance_to_hakko, True)
        except:
            return False
        print(results)
        total_failed += results['failed']
        total_banned += results['banned']
        total_added += results['added']
        total_updated += results['updated']
        total_new_hakko += results['new_hakko']
        total_still_hakko += results['still_hakko']
        total_hakko_to_streamers += results['hakko_to_streamers']
        total_streamers_to_hakko += results['streamers_to_hakko']
        pbar.update(100)
        index += 100
    res = {'updated': total_updated, 'added': total_added, 'failed': total_failed,
           'banned': total_banned, 'skipped_hakko': skipped_hakko, 'new_hakko': total_new_hakko,
           'still_hakko': total_still_hakko, 'skipped': skipped,
           'hakko_to_streamers': total_hakko_to_streamers, 'streamers_to_hakko': total_streamers_to_hakko}
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
    logins_data = set()
    for page_num in tqdm.tqdm(range(1, 29)):
        response = requests.get(f"https://twitchtracker.com/channels/most-followers/korean?page={page_num}",
                                headers=hdr,
                                allow_redirects=False).text
        soup = bs(response, 'html.parser')

        for ind in range(100):
            try:
                streamer_login = soup.select_one('#channels > tbody > tr:nth-child(%d) > td:nth-child(3) > a' % ind)[
                                     'href'][1:]
                if not streamer_login in logins_data:
                    logins_data.add(streamer_login)
                    print(f'{streamer_login} newly added')
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
                    f'body > div.container.mt-5 > div.row > div.col-12.col-md-10 > ul > li:nth-child({j}) > div > div.col-lg-8.col-6 > div > div.col-11 > div > div.col-9.col-lg-10 > div.d-flex.mb-2.flex-wrap > a')[
                    'href']
                streamer_login = streamer_login[streamer_login.index('-') + 1:]
                if not streamer_login in logins_data:
                    logins_data.add(streamer_login)
                    print(f'{streamer_login} newly added')
                count += 1
            except:
                if count >= 50:
                    break
    update_logins(list(logins_data))
    return logins_data


def streamer_data_update_with_logins_data(not_update_originals=True):
    return streamers_data_update(pickle.load(open('logins_data.pickle', 'rb')), not_update_originals, False)


def streamers_data_refresh_by_itself():
    return streamers_data_update(list(streamers_data.keys()), False, False)


def streamers_data_refresh_by_itself_if_not_lang():
    st = list(streamers_data.keys())
    do = []
    for i in st:
        if not 'lang' in streamers_data[i].keys():
            do.append(i)
    return streamers_data_update(do, False, False)

def streamer_search(query):
    try:
        return True, streamers_data[query]
    except:
        try:
            return True, {i['display_name'].lower(): i for i in streamers_data.values()}[query.lower()]
        except:
            search_data = list(streamers_data.keys()) + [i['display_name'].lower() for i in streamers_data.values()]
            return False, difflib.get_close_matches(query, search_data)


def streamer_search_client(query):
    streamer_data = streamer_search(query)
    if not streamer_data[0]:
        temp = f"<meta charset='utf-8'>팔로워 {follower_requirements}명 이상인 스트리머 중 '{query}'에 해당하는 스트리머가 없습니다. 아이디 또는 닉네임 둘 다로 검색 가능하니 다시 한번 해보세요. " \
               f"<br>만약 실제로 있는 스트리머의 아이디(이름은 추가 불가)라면 이 <a href='/twitch/addlogin/?logins={query}&give_chance_to_hakko=true&skip_already_done=false'>링크</a>를 눌러 추가해보세요.<br>"
        if len(streamer_data[1]) == 1:
            temp += f"<a href='/twitch/populariswatching/{streamer_data[1][0]}'>{streamer_data[1][0]}</a>가 찾고 계신 스트리머 인가요? 만약 그렇다면 링크를 누르세요."
        elif len(streamer_data[1]) > 1:
            temp += f"혹시 {', '.join([f'''<a href='/twitch/populariswatching/{streamer}'>{streamer}</a>''' for streamer in streamer_data[1]])} 중에 찾고 계신 스트리머가 있나요? "
        return False, temp
    elif streamer_data[1]['banned']:
        temp = f"스트리머 {streamer_data[1]['display_name']}({streamer_data[1]['login']})는 {streamer_data[1]['last_updated']} 기준으로 정지된 것을 확인했습니다. <br>현재는 정지가 해제되었을 수 있으니, 만약 이 스트리머의 상태를 업데이트하고 싶다면 <a href='/twitch/addlogin/?logins={streamer_data[1]['login']}&skip_already_done=false'>{streamer_data[1]['login']}</a>으로 접속해서 상태를 갱신하세요."
    else:
        streamer_data = streamer_data[1]
        return True, streamer_data


def streamer_introduce(streamer_data):
    return f"{langcode_to_country(streamer_data['lang'])} 내 트위치 팔로워 {streamer_data['ranking'][streamer_data['lang']]}위({streamer_data['followers']}명) 인 {streamer_data['display_name']} ({streamer_data['login']})"


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


def streamer_following_load():
    return pickle.load(open('following_data.pickle', 'rb'))


def streamer_following(login, refresh=False):
    if not refresh:
        try:
            with open('following_data.pickle', 'rb') as f:
                followingdata=pickle.load(f)[login]
                print(f'used following data of {login} which was updated at {followingdata[0]["last_updated"]}')
                return followingdata

        except:
            pass
    return following(login, -1, True)


def update_logins(login_list):
    logins_data = pickle.load(open('logins_data.pickle', 'rb'))
    login_list = set(login_list) - set([''])
    print(f"updated {len(set(login_list) - set(logins_data))} streamers to logins_data.pickle")
    logins_data = list(set(logins_data) | set(login_list))
    pickle.dump(logins_data, open('logins_data.pickle', 'wb'))


def followed_update():
    follow = streamer_following_load()
    followed_by_streamers_dict = defaultdict(list)
    for i in follow:
        for j in follow[i]:
            if not j['login'] == '':
                followed_by_streamers_dict[j['login']].append(
                    {'login': i, 'when': j['when'], 'last_updated': j['last_updated']})
    pickle.dump(followed_by_streamers_dict, open('followed_data.pickle', 'wb'))
    print('saved to followed_data')
    update_logins(list(followed_by_streamers_dict.keys()))
    return followed_by_streamers_dict


def followed_by_streamers_load():
    return pickle.load(open('followed_data.pickle', 'rb'))


def followed_by_streamers(login):
    with open('followed_data.pickle', 'rb') as f:
        return pickle.load(f)[login]


def save_datas():
    pickle.dump(streamers_data, open('streamers_data.pickle', 'wb'))
    pickle.dump(hakko_streamers_data, open('hakko_streamers_data.pickle', 'wb'))


def ranking_in_lang(lang="ko"):
    return {k: v for k, v in sorted([i for i in streamers_data.items() if not i[1]['banned'] and i[1]['lang'] == lang],
                                    key=lambda item: item[1]['ranking'][lang])}
def ranking_refresh():
    langs = set([streamers_data[i]['lang'] for i in streamers_data if not streamers_data[i]['banned']])
    for lang in langs:
        for i, k in enumerate(sorted([j for j in streamers_data.keys() if
                                      not streamers_data[j]['banned'] and streamers_data[j][
                                          'lang'] == lang],
                                     key=lambda i: streamers_data[i]['followers'], reverse=True)):
            streamers_data[k]['ranking'] = {lang: i + 1}
    print('ranking refreshed')

def gui_maker(title, variable, url, buttonname, submit=False):
    inp = """<div class="col-12 col-md-4">
          <div class="row px-3">
            <label for="%s" class="col-12">%s</label>
            <input type="string" class="col-12 py-2" value="%s" id="%s">
          </div>
        </div>"""
    alert = '$("#%s").val() == ""'
    templates = open('gui_templete.html', 'r').read()
    alerts = ' || '.join([alert % (i[0]) for i in variable])
    inps = ''.join([inp % (i[0], i[1], i[2], i[0]) for i in variable])
    return templates % (title, title, title, inps, buttonname, alerts, url, 'submit()' * submit)

ranking_refresh()
followed_update()

if __name__ == '__main__':
    print(login_info('freeter1999'))
