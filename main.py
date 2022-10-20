from datetime import date
from datetime import timedelta as td
from datetime import datetime as dt
import itertools
from typing import Optional
from twitch import *
from navercafe import *
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from typing import List, Optional
from fastapi import Header, Query, Request
from translate import *
import random
import json
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from youtube import *
from fastapi.responses import HTMLResponse
import subprocess
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
# import io
# from starlette.responses import StreamingResponse
import os
from datetime import datetime as dt
import requests
import pickle
import pandas as pd
import difflib
import psutil
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

data = pickle.load(open('pop.pandas', 'rb'))
app = FastAPI()


# app.add_middleware(HTTPSRedirectMiddleware)


class TranReq(BaseModel):
    fromLang: Optional[str] = None
    text: str
    toLang: str


class Contact(BaseModel):
    advice: str
    email: str


class chat(BaseModel):
    content: str


origins = ["*"]
waiting_2 = 100
LastVisit = '아직 방문안함'
CafeNow = False
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def timeparse(t):
    return dt.strptime(t, '%Y-%m-%dT%H:%M:%SZ') + td(hours=9)


def ends_with_jong(kstr):
    k = kstr[-1]
    if "가" <= k <= "힣":
        return (ord(k) - ord("가")) % 28 > 0
    else:
        return


def yi(kstr):
    josa = "이" if ends_with_jong(kstr) else "가"
    return f"{kstr}{josa}"


def eul(kstr):
    josa = "을" if ends_with_jong(kstr) else "를"
    return f"{kstr}{josa}"


def onlyyi(kstr):
    return "이" if ends_with_jong(kstr) else "가"


def onlyeul(kstr):
    return "을" if ends_with_jong(kstr) else "를"


def dttoko(ti):
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


firstvisit = dttoko(dt.now())
rww = pickle.load(open('random_word', 'rb'))
wordlengthdict = {7: 23950, 9: 29081, 10: 22281, 11: 16134, 8: 29684, 4: 3995, 12: 11399, 5: 8885, 6: 15720, 3: 1003,
                  14: 5056, 15: 3157, 13: 7743, 2: 99}
from bs4 import BeautifulSoup as bs

cafenum = 0
twview = 0
ytnum = 0
ytview = 0
follower = 0
subscriber = 0


@app.get("/wakinfo/")
async def wakinfo():
    global cafenum, twview, follower, subscriber, ytview, ytnum
    return {'cafenum': cafenum, 'follower': follower, 'twview': twview, 'subscriber': subscriber, 'ytview': ytview,
            'ytnum': ytnum}


@app.get("/navercafe/membernum")
async def membern():
    global cafenum
    return cafenum


@app.get("/favicon.ico")
async def favicon():
    return FileResponse('./favicon.ico', media_type='application/octet-stream', filename='favicon.ico')


@app.get("/word")
async def randword(count: Optional[int] = 50, minLength: Optional[int] = 1, maxLength: Optional[int] = 100):
    ret = []
    if minLength > maxLength or minLength > 15 or maxLength < 2:
        return False
    if sum([wordlengthdict[u] for u in range(max(2, minLength), min(maxLength + 1, 16))]) < count:
        return False
    for co in range(count):
        while True:
            a = random.choice(rww)
            if len(a) >= minLength and len(a) <= maxLength:
                ret.append(a)
                break
    return ret


# @app.get("/word/all")
# async def allword():
#    return rww
@app.get("/twitch/followcount/{login}")
async def folcount(login: str):
    return login_to_something(login, 'followers', True)


import youtube_dl

ydl = youtube_dl.YoutubeDL(
    {'outtmpl': '%(id)s.%(ext)s', 'format': ' bestaudio/best', 'extractaudio': True, 'listformats': False})


@app.get("/watch", response_class=HTMLResponse)
async def mp3download(v: str):
    inf = ydl.extract_info(v, download=False)
    dic = {i['format_id']: i['url'] for i in inf['formats']}
    if '140' in dic.keys():
        return RedirectResponse(dic['140'])
    else:
        return RedirectResponse(dic[str(max([int(j) for j in list(set(dic.keys()) & {'249', '250', '251'})]))])


@app.get("/youtube/mp3old/{videoId}")
async def mp3download(videoId: str):
    filelist = os.listdir('./mp3')
    for file in filelist:
        if os.path.basename(file).endswith(videoId):
            return FileResponse('./mp3/' + file, media_type='application/octet-stream', filename=file)
    subprocess.run(['youtube-dl', '--extract-audio', '--audio-format', 'mp3', '--output',
                    './mp3/%(uploader)s%(title)s%(id)s.%(ext)s', videoId])
    filelist = os.listdir('./mp3')
    for file in filelist:
        if os.path.basename(file).endswith(videoId):
            return FileResponse('./mp3/' + file, media_type='application/octet-stream', filename=file)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<meta charset='utf-8'> 본 API는 Twitch, YouTube, Naver cafe 등의 플랫폼에서 다양한 데이터를 수집하고 분석합니다. <br>" \
           "관련 모든 문의는 <a href='mailto:junmini7@snu.ac.kr'>junmini7@snu.ac.kr</a>로 주세요. 하루 내로 확인하겠습니다.<br>" \
           "This API collects and analyzes various data from Twitch, YouTube, Naver cafe etc. <br>" \
           "For inquiries, please mail to <a href='mailto:junmini7@snu.ac.kr'>junmini7@snu.ac.kr</a>. I'll check it out in a day."


@app.get("/youtube/searchid/{query}")
async def youtubesearchid(query: str):
    return searchid(query)


@app.get("/youtube/vidfromplaylist/{playlistid}")
async def vidfromplaylist(playlistid: str, end: Optional[int] = 50):
    return videofromplaylist(playlistid, end)


@app.get("/youtube/vidfromchannelbylist/{channelid}")
async def vidfromchannelbylist(channelid: str, end: Optional[int] = 50):
    return videofromplaylist(playlistfromid(channelid), end)


@app.get("/youtube/vidfromchannel/{channelid}")
async def vidfromchannel(channelid: str, end: Optional[int] = 50):
    return videofromid(channelid, end)


@app.get("/youtube/vidfromchanneldetail/{channelid}")
async def vidfromchanneldetail(channelid: str, end: Optional[int] = 50):
    return videodetailfromid(channelid, end)


@app.get("/youtube/statistics/")
async def stat(id: Optional[str] = '', username: Optional[str] = ''):
    if id == '' and username == '':
        return False
    if id == '':
        return statisticsfromusername(username)
    else:
        return statisticsfromid(id)


# @app.get("/papago/quote")
# async def translatedQuote():
#     return quote()


@app.get("/twitch/stream/{broadcaster_id}")
async def stream(broadcaster_login: str):
    return streams_info(broadcaster_login)


@app.get("/twitch/viewer/{broadcaster_id}")
async def viewer(broadcaster_id: str):
    return view(broadcaster_id)


@app.get("/twitch/addlogingui/", response_class=HTMLResponse)
async def add_login_gui():
    return gui_maker('데이터베이스에 스트리머 추가하기', [['login', '스트리머의 아이디 (이름은 불가)', '']],
                     "'/twitch/addlogin/?logins='+$('#login').val()+'&skip_already_done=false'", '추가하기 (엔터)')


@app.get("/twitch/addlogin/", response_class=HTMLResponse)
def add_logins(request: Request, logins: List[str] = Query(None), skip_already_done: Optional[bool] = True,
               give_chance_to_hakko: Optional[bool] = False):
    about_skipped = f"%s에 해당하는 스트리머는 {follower_requirements}명 이상의 팔로워를 보유하고 있어 이미 데이터 배이스 상에 존재하며, 옵션이 따라 건너뛰었습니다."
    about_update = f"%s에 해당하는 스트리머는 {follower_requirements}명 이상의 팔로워를 보유하고 있어 이미 데이터 베이스 상에 존재하며, 따라서 이를 업데이트 하였습니다."
    about_added = f"%s에 해당하는 스트리머는 {follower_requirements}명 이상의 팔로워를 보유하고 있기 때문에 데이터베이스에 새롭게 추가되었습니다."
    about_failed = "%s에 해당하는 스트리머는 조회에 실패하였습니다. 트위치로부터 영구 혹은 임시 정지를 받거나 잘못된 아이디가 아닌지 확인해보세요."
    about_banned = "%s에 해당하는 스트리머는 정지를 받거나, 기존에 정지 상태인 것이 확인되었습니다."
    about_skipped_hakko = f"%s에 해당하는 스트리머는 {follower_requirements}명 미만의 팔로워를 보유하고 있는것이 이전에 확인되었고, 새로 업데이트하는 변수가 false로 설정되어 있기 때문에 스킵되었습니다."
    about_new_hakko = f"%s에 해당하는 스트리머는 {follower_requirements}명 미만의 팔로워를 보유하고 있기 때문에 데이터 베이스 상에 추가는 되었지만, 앞으로의 통계에 활용되지는 않습니다. {follower_requirements}명의 이상의 팔로워를 가지게 된다면 다시 시도해주세요."
    about_still_hakko = f"%s에 해당하는 스트리머는 여전히 {follower_requirements}명 미만의 팔로워를 보유하고 있음이 확인되었습니다. {follower_requirements}명의 이상의 팔로워를 가지게 된다면 다시 시도해주세요."
    about_hakko_to_streamers = f"%s에 해당하는 스트리머는 최근 {follower_requirements}명 이상의 팔로워 기록을 갱신하였기 때문에 기존의 보관용 데이터베이스에서 통계용 데이터베이스로 이동되었습니다. 축하드립니다."
    about_streamer_to_hakko = f"%s에 해당하는 스트리머는 최근 {follower_requirements}명 미만의 팔로워로 떨어졌기 때문에 기존의 통계용 데이터베이스에서 보관용 데이터베이스로 이동되었습니다."
    description = {'updated': about_update, 'added': about_added, 'failed': about_failed,
                   'banned': about_banned, 'skipped_hakko': about_skipped_hakko, 'new_hakko': about_new_hakko,
                   'still_hakko': about_still_hakko, 'skipped': about_skipped,
                   'hakko_to_streamers': about_hakko_to_streamers, 'streamers_to_hakko': about_streamer_to_hakko}
    result = streamers_data_update(logins, skip_already_done, give_chance_to_hakko)
    if result == False:
        return f"<meta charset='utf-8'>{logins}는 트위치에 없는 아이디입니다."
    explanation = "<meta charset='utf-8'> 데이터베이스 추가/업데이트 작업이 완료되었습니다."
    for i in description:
        if result[i]:
            explanation += '<br>' + description[i] % (', '.join(result[i]))

    return explanation


@app.get("/loading.gif")
async def loadinggif():
    return RedirectResponse(
        'https://woowakgood.live/loading-2.gif')  # FileResponse('loading.gif', media_type='application/octet-stream', filename='loading.gif')


@app.get("/twitch/refreshdata")
async def refresh_data(request: Request, password: str, by: str):
    if password == 'pw1234':
        if by == 'itself':
            streamers_data_refresh_by_itself()
        elif by == 'loginsdata':
            streamer_data_update_with_logins_data()
        else:
            return {'error': 'option incorrect'}
    else:
        return {'error': 'password incorrect'}


@app.get("/twitch/populariswatchingtextapi/{broadcaster_login}")
async def popular_is_watching_api(request: Request, broadcaster_login: str):
    ip = str(request.client.host)
    result = streamer_watching(broadcaster_login)
    with open('log.txt', 'a') as f:
        f.write(
            f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} polulariswatching {broadcaster_login} from {ip} {" ".join(map(str, result))}\n')
    return result


@app.get("/twitch/populariswatching/", response_class=HTMLResponse)
async def popular_is_watching_introduce(request: Request):
    return gui_maker("방송보는 스트리머", [['query', '스트리머 이름 또는 아이디', '']],
                     "'/twitch/populariswatchingapi/'+$('#query').val()", '방송보는 스트리머 확인 (엔터)')

@app.get("/twitch/populariswatching/{query}", response_class=HTMLResponse)
async def popular_is_watching(request: Request, query: str):
    return gui_maker("방송보는 스트리머", [['query', '스트리머 이름 또는 아이디', query]],
                     "'/twitch/populariswatchingapi/'+$('#query').val()", '방송보는 스트리머 확인 (엔터)', True)

def follow_icon(known_following,followed_data,login):
    if login in followed_data:
        return "fa-solid fa-heart"
    if login in known_following:
        return "fa-regular fa-heart"
    return "fa-solid fa-question"
def follow_about_heart(known_following,followed_data,login):
    if login in followed_data:
        return followed_data[login]['when'].date()
    if login in known_following:
        return f"<a href='/twitch/following/{login}'>새로고침</a>"
    return f"<a href='/twitch/following/{login}'>확인하기</a>"
@app.get("/twitch/populariswatchingapi/{query}", response_class=HTMLResponse)
def popular_is_watching_gui(request: Request, query: str):
    result = streamer_search_client(query)
    if not result[0]:
        return result[1]
    else:
        streamer_data = result[1]
    ip = str(request.client.host)
    result_dict = streamer_watching(streamer_data['login'])
    with open('log.txt', 'a') as f:
        f.write(
            f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} polulariswatching {streamer_data["login"]} from {ip} {" ".join(map(str, result_dict))}\n')

    temp = f"<meta charset='utf-8'>{streamer_introduce(streamer_data)}{onlyeul(streamer_data['display_name'])} 시청 중인 {watcher_num(streamer_data['login'])}명의 로그인 시청자 중 팔로워 수 {follower_requirements}명 이상의 스트리머 (팔로워 순)"
    followed_data={i['login']:i for i in followed_by_streamers(streamer_data['login'])}


    known_following=list(streamer_following_load().keys())
    streamer_info_template = open('streamer_info_template.html','r').read()
    if not result_dict:
        temp += '가 없습니다.'
    else:

        temp += '<br><br><div class="row">' + ''.join([streamer_info_template % (
            v['login'], v['profile_image_url'], v['display_name'], k, v['followers'], langcode_to_country(v['lang']),
            v['ranking'][v['lang']],follow_icon(known_following,followed_data,k),follow_about_heart(known_following,followed_data,k)) for k, v in sorted(result_dict.items(), key=lambda x: x[1]['followers'], reverse=True) if k != 'commanderroot'])+'</div>'
    temp += f"<br>팔로워 정보 최종 업데이트 일시 : {streamer_data['last_updated']}<br>시청 정보 최종 업데이트 일시 : {dt.now()}<br>" \
            f"<a href='/twitch/addlogin/?{'&'.join(['logins=' + k for k in list(result_dict.keys()) + [streamer_data['login']] if k != 'commanderroot'])}&skip_already_done=false&give_chance_to_hakko=true'>여기 등장하는 {len(list(result_dict.keys()) + [streamer_data['login']])}명의 스트리머들의 랭킹 및 팔로워 수 정보 업데이트하기</a>" \
            "<br>주의 - 스트리머 순위는 국내 스트리머 약 2000명에서 시작해 그들이 팔로우 하는 다른 스트리머들을 계속 탐색하는 식으로 얻어냈기에 해외 스트리머의 경우에는 순위가 무의미합니다." \
            f"<br>여기에는 없지만 알고 있는 스트리머가 있다면 <a href='/twitch/addlogingui/'>이곳</a>을 눌러 추가해주세요." \
            f"<br><a href='/twitch/following/{streamer_data['login']}'>{streamer_data['display_name']}({streamer_data['login']}){onlyyi(streamer_data['display_name'])} 팔로우하는 유명 스트리머 목록 보기</a> ({recom('following', streamer_data['login'])})" \
            f"<br><a href='/twitch/followedbypopular/{streamer_data['login']}'>{streamer_data['display_name']}({streamer_data['login']}){onlyeul(streamer_data['display_name'])} 팔로우하는 유명 스트리머 목록 보기</a> ({recom('followedbypopular', streamer_data['login'])})" \
            f"<br><a href='/twitch/ranking'>(한국에서) 가장 정확한 트위치 팔로워 랭킹 목록</a>" \
            f"<br>정지당한 스트리머들은 표시되지 않습니다. <a href='/twitch/banned'>여기서 그 목록을 확인하세요</a>"

    # temp+="<br>made by <a href='http://github.com/junmini7'>junmini7</a> from <a href='http://ece.snu.ac.kr'>SNU ECE</a>"

    return temp


order_dict = {'follow': ['팔로워 많은', '팔로워 적은'], 'time': ['오래된', '최근']}
by_options = ['time', 'follow']
reverse_options = [False, True]


def list_multiplier(a, b):
    return list(itertools.chain.from_iterable([[[j] + [i] for i in b] for j in a]))


def recom(fromorto, broadcaster_login):
    return ', '.join(
        [f"<a href='/twitch/{fromorto}/{broadcaster_login}?by={i}&reverse={j}'>{order_dict[i][j]} 순</a>" for i, j in
         list_multiplier(by_options, reverse_options)])


@app.get("/twitch/following/{query}", response_class=HTMLResponse)
def following_by_popular(request: Request, query: str, by: Optional[str] = 'time',
                               reverse: Optional[bool] = False):
    # result = streamer_search_client(query)
    # if not result[0]:
    #     return result[1]
    # else:
    #     streamer_data = result[1]

    broadcaster_login = query  # streamer_data['login']
    lists = streamer_following(broadcaster_login)
    print([i['login'] for i in lists])
    result = login_info([i['login'] for i in lists], False, False, False, False)
    recom('following', broadcaster_login)
    list_dict = {i['login']: i for i in lists}
    order_ment = order_dict[by][reverse]
    if by == 'follow':
        sort_by = lambda x: x['followers']
        reverse = 1 - reverse
    elif by == 'time':
        sort_by = lambda x: list_dict[x['login']]['when']
    reco = recom('following', broadcaster_login)
    return f'<meta charset="utf-8">{broadcaster_login}가 팔로우하는 {follower_requirements}명 이상의 팔로워를 가진 유명 스트리머들 ({order_ment} 순) {reco}<br>' + '<br>'.join(
        [
            f"<a href='/twitch/populariswatching/{v['login']}'><img src='{v['profile_image_url']}' width='100' height='100'></a> {v['display_name']} ({v['login']}), 팔로워 {v['followers']}명, {langcode_to_country(v['lang'])} {v['ranking'][v['lang']]}위, {broadcaster_login}가 {list_dict[v['login']]['when']}에 팔로우, last update on {list_dict[v['login']]['last_updated']}"
            for v in sorted(result, key=sort_by, reverse=reverse)])


@app.get("/twitch/followedbypopular/{query}", response_class=HTMLResponse)
async def followed_by_popular(request: Request, query: str, by: Optional[str] = 'time',
                              reverse: Optional[bool] = False):
    result = streamer_search_client(query)
    if not result[0]:
        return result[1]
    else:
        streamer_data = result[1]
    broadcaster_login = streamer_data['login']
    lists = followed_by_streamers(broadcaster_login)
    print(lists)
    # print([i['login'] for i in lists])
    result = login_info([i['login'] for i in lists], False, False, False, False)
    list_dict = {i['login']: i for i in lists}
    order_ment = order_dict[by][reverse]
    reco = recom('followedbypopular', broadcaster_login)
    if by == 'follow':
        sort_by = lambda x: x['followers']
        reverse = 1 - reverse
    elif by == 'time':
        sort_by = lambda x: list_dict[x['login']]['when']

    return f'<meta charset="utf-8">{streamer_introduce(streamer_data)}{onlyeul(streamer_data["display_name"])} 팔로우하는 {follower_requirements}명 이상의 팔로워를 가진 유명 스트리머들 ({order_ment} 순) {reco}<br>' + '<br>'.join(
        [
            f"<a href='/twitch/populariswatching/{v['login']}'><img src='{v['profile_image_url']}' width='100' height='100'></a> {v['display_name']} ({v['login']}), 팔로워 {v['followers']}명, {langcode_to_country(v['lang'])} {v['ranking'][v['lang']]}위, {streamer_data['display_name']}({streamer_data['login']})을 {list_dict[v['login']]['when']}에 팔로우, last update on {list_dict[v['login']]['last_updated']}"
            for v in sorted(result, key=sort_by, reverse=reverse)])


@app.get("/twitch/ranking/", response_class=HTMLResponse)
async def ranking(request: Request, lang: Optional[str] = 'ko'):
    ranking_dicts = ranking_in_lang(lang)
    return f'<meta charset="utf-8">{langcode_to_country(lang)} 내 팔로워 랭킹<br>' + '트위치에서 정지당한 스트리머는 본 목록에 뜨지 않으므로 다음을 참조하세요. <a href="/twitch/banned">정지당한 스트리머 목록</a><br>여기에는 없지만 알고 있는 스트리머가 있다면 <a href="/twitch/addlogingui/">이곳</a>을 눌러 추가해주세요.<br>' + '<br>'.join(
        [
            f"<a href='/twitch/populariswatching/{v['login']}'><img src='{v['profile_image_url']}' width='100' height='100'></a> {v['display_name']} ({v['login']}), 팔로워 {v['followers']}명, {langcode_to_country(v['lang'])} {v['ranking'][v['lang']]}위 (last update on {v['last_updated']})"
            for v in ranking_dicts.values()])


@app.get("/twitch/banned/", response_class=HTMLResponse)
async def banned_ui(request: Request, lang: Optional[str] = 'ko'):
    banned_dict = currently_banned()
    return f'<meta charset="utf-8">현재 트위치에서 정지당한 스트리머들 목록<br>' + '<br>'.join(
        [
            f"<a href='/twitch/populariswatching/{v['login']}'><img src='{v['profile_image_url']}' width='100' height='100'></a> {v['display_name']} ({v['login']}), 팔로워 {v['followers']}명,  {v['ranking']}위 ({v['last_updated']}에 여전히 밴먹은것 확인)"
            for v in
            banned_dict.values()]) + f"<br><a href='/twitch/addlogin/?{'&'.join(['logins=' + k for k in list(banned_dict.keys())])}&skip_already_done=false'>여기 등장하는 {len(banned_dict)}명의 정지당한 스트리머들 새로고침하기"


@app.get("/twitch/viewerintersection")
async def viewerintersection(request: Request, streamers: List[str] = Query(None)):
    ip = str(request.client.host)
    intersect = viewer_intersection(streamers)
    with open('log.txt', 'a') as f:
        f.write(
            f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} viewerintersection {" ".join(streamers)} from {ip} {" ".join(map(str, intersect))}\n')
    return intersect


@app.get("/twitch/multipleiswatching")
async def multipleiswatching(request: Request, streamer: str, ids: List[str] = Query(None)):
    ip = str(request.client.host)
    watchers = view(streamer)
    peop = watchers['viewers'] + watchers['moderators'] + watchers['vips'] + watchers['broadcasters'] + watchers[
        'staff']
    result = list(set(peop) & set(ids))
    with open('log.txt', 'a') as f:
        f.write(
            f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} multiple {" ".join(ids)} iswatching {streamer} from {ip} {" ".join(map(str, result))}\n')

    return result


@app.get("/twitch/iswatchingmultiple")
async def iswatchingmultiple(request: Request, id: str, streamers: List[str] = Query(None)):
    ip = str(request.client.host)
    res = []
    for streamer in streamers:
        watchers = view(streamer)
        peop = watchers['viewers'] + watchers['moderators'] + watchers['vips'] + watchers['broadcasters'] + watchers[
            'staff']
        if id in peop:
            res.append(streamer)
    with open('log.txt', 'a') as f:
        f.write(
            f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} {id} iswatching {" ".join(streamers)} multiple from {ip} {" ".join(map(str, res))}\n')
    return res


@app.get("/twitch/iswatchingfollowing")
async def iswatchingfollowing(request: Request, id):
    ip = str(request.client.host)
    followlist = following(id, -1)
    res = []
    for streamer in followlist:
        watchers = view(streamer['login'])
        peop = watchers['viewers'] + watchers['moderators'] + watchers['vips'] + watchers['broadcasters'] + watchers[
            'staff']
        if id in peop:
            res.append([streamer['name'], streamer['login']])
    with open('log.txt', 'a') as f:
        f.write(
            f'{dt.now().strftime("%Y/%m/%d %H:%M:%S")} {id} iswatchingfollowing from {ip} {" ".join(map(str, res))}\n')

    return res


@app.get("/twitch/login/")
async def multipleloginapi(logins: List[str] = Query(None)):
    return login_info(logins)


@app.get("/twitch/logintoid/")
async def multiplelogintoidapi(logins: List[str] = Query(None)):
    return login_to_id(logins)


@app.get("/twitch/idtologin/")
async def multipleidtologinapi(ids: List[str] = Query(None)):
    return id_to_login(ids)


@app.get("/twitch/id/")
async def multipleidapi(ids: List[str] = Query(None)):
    return id_info(ids)


@app.get("/twitch/login/{login}")
async def loginapi(login: str):
    return login_info(login)


@app.get("/twitch/totalview/{login}")
async def totalviewapi(login: str):
    return total_view(login)


@app.get("/twitch/namefromlogin/{login}")
async def namefromlogin(login: str):
    return login_to_name(login)


@app.get("/twitch/logintoid/{login}")
async def logintoidapi(login: str):
    return login_to_id(login)


@app.get("/twitch/idtologin/{id}")
async def idtologinapi(id: str):
    return id_to_login(id)


@app.get("/twitch/id/{id}")
async def idapi(id: str):
    return id_info(id)


@app.get("/twitch/followfrom/{login}")
async def follow_from_api(login: str, end: Optional[int] = 100):
    return following(login, end)


@app.get("/twitch/followto/{login}")
async def following_to_api(login: str, end: Optional[int] = 100):
    return followed(login, end)


@app.get('/twitch/isfollowing/{fromlogin}/{tologin}')
async def is_following(fromlogin: str, tologin: str):
    return is_following(fromlogin, tologin)


@app.get('/twitch/whenfollowed/{fromlogin}/{tologin}')
async def whenfollowed(fromlogin: str, tologin: str):
    t = is_following_api(fromlogin, tologin)
    try:
        return twitch_parse(t['data'][0]['followed_at'])
    except:
        return False


@app.post("/userexp/")
async def userexperience(request: Request, a: Contact):
    open('../advice.txt', 'a').write(
        a.advice + '\n' + str(dt.now()) + '\n' + str(request.client) + ' ' + a.email + '\n')
    return '성공적으로 훈수를 하였습니다!'


chattemp = """
<div class="chat-message clearfix">
                <div class="chat-message-content clearfix">
                  <span class="chat-time">%s</span>
                  <h5>%s</h5>
                  <p>%s
                  </p>
                </div>
                <!-- end chat-message-content -->
              </div>
              <!-- end chat-message -->
              <hr />"""
blocklist = ['39.118.207.214']
try:
    ipdict = pickle.load(open('../ipdict', 'rb'))
except:
    ipdict = {}
try:
    chats = open('../chat.txt', 'r').read()
except:
    chats = ""
randomwordlist = pickle.load(open('random', 'rb'))


@app.get('/searchpop/{query}', response_class=HTMLResponse)
async def search_pop(query: str):
    userdata = data[data['subject'].str.contains(query) | data['nickname'].str.contains(query)][
        ['link', 'date']].reset_index(drop=True)
    return userdata.to_html().replace('&lt;', '<').replace('&gt;', '>')


@app.get('/searchpopindetail/{query}', response_class=HTMLResponse)
async def search_pop_in_detail(query: str, by: Optional[str] = 'subject'):
    userdata = data[data[by].str.contains(query)][['link', 'date']].reset_index(drop=True)
    return userdata.to_html().replace('&lt;', '<').replace('&gt;', '>')


@app.get('/mypop/{nickname}', response_class=HTMLResponse)
async def my_pop(nickname: str):
    userdata = data.loc[data['nickname'] == nickname][['link', 'date']].reset_index(drop=True)
    return userdata.to_html().replace('&lt;', '<').replace('&gt;', '>')


@app.get('/youtube/thumb/', response_class=HTMLResponse)
async def thumb(v: str):
    return f'<img src="{f"https://img.youtube.com/vi/{v}/maxresdefault.jpg"}"></img>'  # RedirectResponse(f'https://img.youtube.com/vi/{v}/maxresdefault.jpg')


@app.get("/youtube/channel/{channelname}", response_class=HTMLResponse)
async def youtube_thumb(channelname: str, end: Optional[int] = 50):
    inf = searchid(channelname)
    id = inf[0]
    name = inf[1]
    vidinf = videodetailfromplaylist(playlistfromid(id), end)
    res = f"<meta charset='utf-8'><script src='https://code.jquery.com/jquery-3.6.0.js'></script><iframe id='ytplayer' type='text/html' width='1280' height='720' src='https://www.youtube.com/embed/{vidinf[0]['id']}' frameborder='0' allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture' allowfullscreen style='position: fixed;right:0px'></iframe><b>%s</b>" % name
    for i in vidinf:
        res += f"""<br><p>{i['title']} uploaded at : {i['time']}</p><br><img src='https://img.youtube.com/vi/{i['id']}/maxresdefault.jpg' width='400' onclick="$('#ytplayer').attr('src','https://www.youtube.com/embed/{i['id']}?autoplay=1')"><br>"""
    return res


# @app.get("/channelthumb/{channelid}", response_class=HTMLResponse)
# async def channelthumb(channelid:str):
@app.post("/chat/", response_class=HTMLResponse)
async def chatting(request: Request, c: chat):
    global chats, ipdict
    ip = str(request.client.host)
    if ip in blocklist:
        return "<font color='red'>도배 멈춰!</font>"
    no = dt.now()
    if not ip in ipdict.keys():
        ipdict[ip] = randomwordlist[len(ipdict)]
        pickle.dump(ipdict, open('../ipdict', 'wb'))
    o = chattemp % ("%s:%s" % (no.hour, no.minute), ipdict[ip], c.content.replace("<", "&lt;").replace(">", "&gt;"))
    chats = o + chats
    open('../chat.txt', 'w').write(chats)
    return chats


@app.get('/chatdata/', response_class=HTMLResponse)
async def chatdata():
    global chats
    return chats


@app.get("/twitch/iswatching/{broadcaster_id}/{viewer_id}")
async def isWatching(broadcaster_id: str, viewer_id: str):
    a = view(broadcaster_id)
    result = False
    keyss = list(a.keys())
    keyss.remove('count')
    for key in keyss:
        if viewer_id in a[key]:
            result = key
    return result


@app.get("/navercafe/cafeid/{id}")
async def cafe_id(id: str):
    return id in ids()


@app.get("/navercafe/cafenick/{nick}")
async def cafe_nick(nick: str):
    return nick in nicks()


@app.get("/navercafe/")
async def cafe():
    return idsandnicks()


@app.get('/papago/')
async def papago(text: str, toLang: str, fromLang: Optional[str] = None):
    return translate(text, toLang, fromLang)


@app.on_event("startup")
@repeat_every(seconds=1000)
def getnewheader() -> None:
    header_update()


@app.get("/videoinfo/{videoId}")
async def videoinf(videoId: str, about: Optional[str] = None):
    if not about:
        return videoinfo(videoId)
    elif about == 'view':
        return int(videoinfo(videoId)['items'][0]['statistics']['viewCount'])
    elif about == 'like':
        return int(videoinfo(videoId)['items'][0]['statistics']['likeCount'])
    elif about == 'comment':
        return int(videoinfo(videoId)['items'][0]['statistics']['commentCount'])
    elif about == 'title':
        return videoinfo(videoId)['items'][0]['snippet']['title']
    elif about == 'when':
        return timeparse(videoinfo(videoId)['items'][0]['snippet']['publishedAt']).strftime("%Y.%m.%d, %H:%M:%S")
    elif about == 'channel':
        return str(videoinfo(videoId)['items'][0]['snippet']['channelTitle'])
    elif about == 'channelid':
        return videoinfo(videoId)['items'][0]['snippet']['channelId']


@app.on_event("startup")
@repeat_every(seconds=200)
def getwakinfo() -> None:
    global cafenum, twview, follower
    res = bs(requests.get('https://cafe.naver.com/steamindiegame').text, 'html.parser')
    res = res.select('div div ul li a em')[1].text.replace('비공개', '')
    cafenum = int(res)
    y = login_info('woowakgood')
    twview = int(y['data'][0]['view_count'])
    follower = login_to_something('woowakgood', 'followers', True)


@app.on_event("startup")
@repeat_every(seconds=10)
def temp_view_clear_daemon() -> None:
    temp_view_clear()
    print('temp_view_cleared', sys.getsizeof(temp_view), len(temp_view), temp_view.keys(),
          print(psutil.Process(os.getpid()).memory_info().rss))


@app.on_event("startup")
@repeat_every(seconds=100)
def getwakytinfo() -> None:
    global subscriber, ytview, ytnum
    y = statisticsfromusername('woowakgood')
    subscriber = int(y["subscriberCount"])
    ytview = int(y["viewCount"])
    ytnum = int(y["videoCount"])


@app.on_event("startup")
@repeat_every(seconds=10)
def getwakcafeinfo() -> None:
    global CafeNow, LastVisit, waiting_2, firstvisit
    realnow = 'ecvhao' in ids()
    if realnow:
        waiting_2 = 0
        if CafeNow == False:
            CafeNow = True
            firstvisit = dttoko(dt.now())
        open('../wakvisit.txt', 'a').write(str(dt.now()) + ' ' + dttoko(dt.now()))
        LastVisit = dttoko(dt.now())
    else:
        waiting_2 += 1
        if waiting_2 > 20:
            CafeNow = False


@app.get("/wakcafe/")
async def wakc():
    global CafeNow, LastVisit, firstvisit
    return CafeNow, LastVisit, firstvisit
