import json
import requests

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
    'cookie': 'NNB=KI5OERVAX7PWA; nx_ssl=2; ncvid=#vid#_175.209.144.17c7jH; nid_inf=-1745616849; NID_AUT=99OTeBh1SirWaj5dYlIk5+qT8ECTI5mgsbtOWRgB8hPYx894cScOEeBlKuliiki8; NID_JKL=xDG9T6ve0j3vqWlut4CSLoxxJGlwOaS+V6szwbrXhz4=; _ga=GA1.2.1651240237.1625911211; _ga_7VKFYR6RV1=GS1.1.1625923010.2.0.1625923010.60; NID_SES=AAABhu3/PhRJI1Q1yJlx+cqlFj5sbX9FZ0G/T/Kp8pXu1GiznJfp4Pa1k8DA+NluVuUNc5WhEEJuyljjsbtt+0YXWwr2qswcvKCE06sMaLmox7fsGrUZ6YH07AJOcpikH1lcsD2hsWchMnZDJ7nhouVqpMZSSpSKr67NusMd6Pu1WJL5PbjaH8LLLn0TYQ0RMKvChBLQO8+qW6+yzyPqSNCdFF6+sMyEXESHba/NDQWqQ8Fh0nJD7NTBDnmOI4MIFYvTtlwzJhNimUrdSlTQk3MTvC1hc7cdrhG3vtHUEhGCTNPQMnJ8cOag5GgXaBy+W91OUjmWJWFk0s2Ab9tS9e+ejHjG69qdc2i5NiW0pn7lZ5V+wnG2iKmT8dd3b7+cVLcfdrbHif+MTKYwoxWgLm9N/LkUeBCkrD+R2MVHlK/PlZ1DnTMFJPg0F6RBJxOe7AvHGsGTy8nsE828gYsK64FEVV6cM2vMdRUlclXiSzPrS1V+LPLGpwWEkIa1BgX+4nBTAFJMpol/qNzYY4tQV5YxKu4=; ncu=93b9456f78355decd82341744eaf8ef5550389651664b533a84258e1f1; nci4=cfff1732276605bae90740575ab1cca4005ea4411e47aa758f4772813633f60f01903df338430a3c4acc7edf1ea8dcb41e401576cf34c6e8a60bbb71a7fdb5ead082f08e8319fce9f09ef0d3717c44675540455148404d6352755066555b58785f6d3c4d40674677534b4b6f4e7f333c3017370a4536391a3d125c2e2100271432242b0e291c516c6c6d69686660171e391d327e117e7a78146974196a717c; ncmc4=7f4fa78297d6b50a59b7f0e7ea187d1fbcea13f6a0eb11cf37f4ce43f8db3c8140867a8d794bd4de8e22569127a502ca5a7c5637d3cc859cac55fd07e1e07ca5c2e5c0f1b9bad5; ncvc2=e7cd311b0c412998ac5735003adbfa812177916d3d668b50a76f5f9d3907fa36ff1cc306c3f90c',
}

params = (
    ('r', 'linkedMember'),
    ('cafeKey', '27842958'),
    ('ncmc4', '43739bbeabea8936658bccdbd624412380d62fca9cd72df30bc8f27fc4e700bd7cba46b1afe4196643ae8256f12230c63f3f242fd4f59aa7ac67e71dedfb5997d8ffccd7c1d8dbcef8f7d2f5c3dad5c8cad0eae5c4e3d09fec'),
)

def idsandnicks():
    a=json.loads(requests.get('https://lm06.cafe.naver.com/addAndList.nhn', headers=headers, params=params).text)
    return [i['m'] for i in a['l']],[i['n'] for i in a['l']]
def giveall():
    a=json.loads(requests.get('https://lm06.cafe.naver.com/addAndList.nhn', headers=headers, params=params).text)
    return [[i['m'],i['n']] for i in a['l']]
