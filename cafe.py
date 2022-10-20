import requests
import json
headers = {
    'authority': 'lm06.cafe.naver.com',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    'accept': '*/*',
    'origin': 'https://cafe.naver.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://cafe.naver.com/steamindiegame?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D27842958%2526articleid%3D3475694%2526commentFocus%3Dtrue',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

params = (
    ('r', 'linkedMember'),
    ('cafeKey', '27842958'),
    ('ncmc4', '43739bbeabea8936658bccdbd624412380d62fca9cd72df30bc8f27fc4e700bd7cba46b1afe4196643ae8256f12230c63f3f242fd4f59aa7ac67e71dedfb5997d8ffccd7c1d8dbcef8f7d2f5c3dad5c8cad0eae5c4e3d09fec'),
)

def list():
    return json.loads(requests.get('https://lm06.cafe.naver.com/addAndList.nhn', headers=headers, params=params).text)['l']
