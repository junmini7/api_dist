
# def view2(id):

#     headers = {
#         'Connection': 'keep-alive',
#         'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
#         'Accept-Language': 'ko-KR',
#         'sec-ch-ua-mobile': '?0',
#         'Authorization': 'OAuth bcls7ass304l0hqcrjy6yiyf22dh1n',
#         'Content-Type': 'text/plain;charset=UTF-8',
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
#         'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
#         'X-Device-Id': '29adxSa1Gcyd1TUk60O4gicOD8RhmChw',
#         'Accept': '*/*',
#         'Origin': 'https://www.twitch.tv',
#         'Sec-Fetch-Site': 'same-site',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Dest': 'empty',
#         'Referer': 'https://www.twitch.tv/',
#     }
#     data = '[{"operationName":"ChatViewers","variables":{"channelLogin":"%s"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"e0761ef5444ee3acccee5cfc5b834cbfd7dc220133aa5fbefe1b66120f506250"}}}]' % id
#
#     response = requests.post('https://gql.twitch.tv/gql', headers=headers, data=data)
#     data = json.loads(response.text)
#     peoples = data[0]['data']['channel']['chatters']
#     broadcasters = [i['login'] for i in peoples['broadcasters']]
#     staff = [i['login'] for i in peoples['staff']]
#     moderators = [i['login'] for i in peoples['moderators']]
#     vips = [i['login'] for i in peoples['vips']]
#     viewers = [i['login'] for i in peoples['viewers']]
#     count = int(peoples['count'])

# 	# print(staff,moderators,vips,(viewers))
#     return {'broadcasters': broadcasters, 'staff': staff, 'moderators': moderators, 'vips': vips, 'viewers': viewers,
#             'count': count}
