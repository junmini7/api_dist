import requests
import time
cookies1 = {
    'NNB': 'YGTVWLXYRNOWE',
    '_ga_7VKFYR6RV1': 'GS1.1.1652633704.2.1.1652633906.60',
    'nid_inf': '1006648836',
    'NID_AUT': '1IcMsRFYFgKtsGRMF+enqnbbdUEvcE5zVVuThbCSdb/cYvfF/qys4DsNDeu3FUb/',
    'NID_SES': 'AAABjZl+X7GvwzH+lXeRUkJtDTjT/sQqHIoak2yw35ZSraL9oSqDmgJUWK2Dc0tGKEnKxdbuMQ1nRaYap6FKuKroQ+jPZ4NEFTa7DuCnO+6yhHK9Es1c+9u4/oteImIqajKs4oTmHZ7QdD1qAi1nkkQk61i6pt1WnvGoWzas8Dsd+K9J3v4hxFsZ6HKFAMIFiIyE5mXsm6c1Aid8oY/njd+9ANSFtRRRoF96zQHBYtAt+eXoIvIEAgMwCZRMiTbhSSu81UzSL5OJ0HD/8BJ6zuVSFYuvz3jObDDK5AyDx2KD6gWNwuzrw4wWtJ6LaHUNqBF5gp4PpstUdnC61DCcK27HVDrUQESzEBtZDyGpgifFAVLXX3yNi+48huZCqtKB53WKw4i3lcXyX97dkPdbCe1QSIS41MqQV4nna4eNVAeFGeDNwegMnucuG0QXQeEwLyKsVrCQWiC24RLD1IpRFfJYKYiNSCiXcF72P14MWG0jc2LyK3WZR0vxH9+FDkdVS8nSkOweXxurHal4CDFov9/rdFw=',
    'NID_JKL': 'L+UmSMu/uKlFfwXpiZYN1KPo5i+ecCbgJQhwclN/0Rw=',
    '_ga': 'GA1.1.1604685670.1650392147',
    'ncu': '8cb55971632854f5d7344a6e4490e4bb3d5ffa7f0477f99e',
    'nci4': 'cfff1732276605bae90740575ab1cca4005ea4411e47aa758f4772813633f60f01903df338430a3c4acc7edf1ea8dcb41e401576cf34c6e8a60bbb71a7fdb5ead082f08e8319fce9f09ef0d3717c44675540455148404d6352755066555b58785f6d3c4d40674677534b4b6f4e7f333c3017370a4536391a3d125c2e2100271432242b0e291c516c6c6d69686660171e391d327e117e7a78146974196a717c',
    'ncmc4': '7141a98c99d8bb0457b9fee9e41f691bbae916e7a1fc1edc35e6e931aeab788140ae52b3475cd4f6a61c7fee56f302f40d0d1605d3e4ada2a042fd2fc9de55d9b0ef',
    '_ga_YTT2922408': 'GS1.1.1657112237.1.1.1657113666.0',
    'ncvc2': 'e0d9351d0f443899bb5826022890f4882779816831689d5dbc665e89371df339f134',
}
cookies2 = {
    'NNB': 'TNMSKRIHUQ6GE',
    'ncvid': '#vid#_147.47.128.169aDrC',
    'ncu': 'b59f63495e137b97cb2562757881f83b',
    'NID_AUT': 'UfOY5PF7ljAD5GkDBZ2X34QAqv5OghIU2+kaiBdXJxv5n3nI+rQcyMyW4gw6pTdN',
    'NID_JKL': 'xEsc07ykVRw/DSq99R0zeq6phZsM6yvGLu4FnPxA2Pc=',
    '_ga_8P4PY65YZ2': 'GS1.1.1650249603.1.1.1650249717.0',
    'ASID': '932f80a9000001808766413100000053',
    'nx_ssl': '2',
    'page_uid': 'hqKUasprvxZssiZGfBKssssssDN-499599',
    '_ga_7VKFYR6RV1': 'GS1.1.1655467251.14.0.1655467251.60',
    'nci4': 'cfff1732276605bae90740575ab1cca4005ea4411e47aa758f4772813633f60f01903df338430a3c4acc7edf1ea8dcb41e401576cf34c6e8a60bbb71a7fdb5ead082f08e8319fce9f09ef0d3717c44675540455148404d6352755066555b58785f6d3c4d40674677534b4b6f4e7f333c3017370a4536391a3d125c2e2100271432242b0e291c516c6c6d69686660171e391d327e117e7a78146974196a717c',
    'ncmc4': '8bbb5376632241fead4304131eec89eb481ee702092ac53ee4101dc57277b24ba35a8e6f8d815f7604e8b54dd347c400d1d1dcfd3010717e6a9f74a912',
    'BMR': 's=1657103900428&r=https%3A%2F%2Fm.blog.naver.com%2Fmonopizza%2F222369124909&r2=https%3A%2F%2Fwww.google.com%2F',
    '_ga': 'GA1.1.1889016392.1648141338',
    '_ga_YTT2922408': 'GS1.1.1657112216.1.0.1657113061.0',
    'NID_SES': 'AAABo0qvgpVdzvToHtc6afwGqqrJ+/XghDyUmgT6snJ1d16gsJNOIwa33nCXs4Ug9Z9W/L+tOZd332f8R1pV4fxOc4gvhRg5DyZt/wGXMVqNgSf9EgqyKdPHaHRep2yzSsKTfAGtokslD1iZbJmWVeKIANgD/xtxpG7G8y+i2G00lHKVT0jdDgwY8sPideOBo14KBDTdJeVzC2Lq4mTQNzhM+bQg/l7sPrN9oO1fBAUbrOMv+0yLpAVMgUiM9nYMvY/0F42IrLnql8v9ptPwo8OAbEOkQGdKNdKkvJZGvT2YfVk/kaf8xTbDLU9n1UCYG1lfyPWWG9aZWOBNJPphwMB670BXKjO9JPK8NxtfpXZc/I9DgeuG+TeemnuHSYJwWGKSIMgyipqiAzTUGDLKPAAHaDnZsOykCZCkOrgEtiNM8xKlNE6b2t+tLc6ogjfsrxOE8cDjxb2Tx6WmeSeKYKWypY76A9AKZAkA+UfEIaMR7G6oTE9ywOhJwXvdMHTnTbuldVqZc9Gf2h/o8APT7s5DWBI/JLP0iFHTxFE1xt4QF4JQajRhUDY2fc0KHjcUDHfTww==',
    'ncvc2': '93b9456f78355db1817f1b2514f485f05d1bf8074c1dfd27d21b26f685',
}
cookies3 = {
    'NNB': 'YGTVWLXYRNOWE',
    '_ga_7VKFYR6RV1': 'GS1.1.1652633704.2.1.1652633906.60',
    '_ga': 'GA1.1.1604685670.1650392147',
    '_ga_YTT2922408': 'GS1.1.1657112237.1.1.1657113666.0',
    'nid_inf': '-442708717',
    'NID_AUT': 'dMCn+OM9Mz8pLlK2AUOBp/nmAsm5Sw6syB1+wi/pRrCzmtRWKsBbe9ZaIX20OxvK',
    'NID_JKL': 'IE0gHhm7O8dlL2BMXcc2FQPNDZbg3/W57AkCxzzcRzc=',
    'NID_SES': 'AAABfPwnSkcqmYDe3abC8RsUEqrF0gmZmbVsRKtoaZCtzd1SAYpC4Xhz3P6YYxlVu2Q2gb7h39DpMPMzhDJ0raj9z5jBvtuYxj0BMDnHwUrm0HL5o+TNRdUS9rOONO5pX6Ojm3XULakUwdR2au2Y6gODjCyhwGj1AjK3D7yCn5p1J1PjzZMKc9o6xnyucwzYEuTLctqhxy1PPns6dopRJxrNTCPjHvdTtdonP637mUstREJXHrPQPWWb7E9WDUSLFHk0SLtAzjgO6Zjo+grwWdcLQBsryN0dh33wh/OaVjb99DaVzs/aan+i4CaxLx+3F2CaZtHDRDKNrdRgla5ngFGNCS3gO+F4RX++Aofp/TjEWWUx684AUuRwalVqlXmxz1JO3kXU7tCCHQs6QO0XwtqtM6T7rmlNEmasv79+0rHK5V8R3GTkSs7OOS9YDriPyXhBvwkcYlUok2XsrAH2w8DMMHjJZIlxWvTA5X6V+2v3Smb2MdtxpBSnwv2JNcULU/9nYw==',
    'ncu': '93b9456f78355decd82341744eaf8ef5550389651664b533a84258e1f1',
    'nci4': 'cfff1732276605bae90740575ab1cca4005ea4411e47aa758f4772813633f60f01903df338430a3c4acc7edf1ea8dcb41e401576cf34c6e8a60bbb71a7fdb5ead082f08e8319fce9f09ef0d3717c44675540455148404d6352755066555b58785f6d3c4d40674677534b4b6f4e7f333c3017370a4536391a3d125c2e2100271432242b0e291c516c6c6d69686660171e391d327e117e7a78146974196a717c',
    'ncmc4': '7f4fa78297d6b50a59b7f0e7ea187d1fbcea13f6a0eb11cf37f4ce43f8db3c8140867a8d794bd4de8e22569127a502ca5a7c5637d3cc859cac55fd07e1e07ca5c2e5c0f1beb8d8',
    'ncvc2': '3a03efc7d59ee2436182fcd8f24a2e52fda35bb2ebb2478766bc8453edc729e32bba6e8f6d61e4d7ba2572ab14b32dce12301c0abb80efc2e83390438fb808c4a0b5abb7aeaaa8aea8a4aaa149',
}
headers = {
    'authority': 'lm06.cafe.naver.com',
    'accept': '*/*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://cafe.naver.com',
    'referer': 'https://cafe.naver.com/steamindiegame',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}
params1 = {
    'r': 'linkedMember',
    'cafeKey': '27842958',
    'ncmc4': '497991b4a1e0833c6f81c6d1dc27512382d12edf99c426e40dded1099693403fde69b902fd864b360dade1589144b4268ddf8001e5fab3aa8256e834e0e85dbbf4c5e1f9f0d7f2c3d6c6dddccef4e4c7e3ddc4d4cbcadde5d4f3d6e0acc7',
}
params2 = {
    'r': 'linkedMember',
    'cafeKey': '27842958',
    'ncmc4': '6757bf9a8fcead1241afe8fff2006507a4f20beee5c629d208fc0adc6925d01556b844a55177f7c3b53d5787199b2af5331b1621fbd8a697a574eb39dfc84399e1f8fbeed0dffadde2ad42',
}
params3 = {
    'r': 'linkedMember',
    'cafeKey': '27842958',
    'ncmc4': '5f6f87a2b7f6952a7997d0c7ca385d3f9cca33d680cb31ef17d4ee63d8fb1ca160a65aada6e6053f5f8a901509a304da3509333ad0fdab8c987bed16cff06d8bd2c9dbc2c5d0eae5ccebd8c3d4cfd1c0fbfbdef9ce81fd',
}
cookies=[cookies1,cookies2,cookies3]
params=[params1,params2,params3]
def intersect(a,b):
	c=b[:]
	for i in a:
		if not i in b:
			c.append(i)
	return c
def idsandnicks(time_gap=0):
	res=[]
	for i in range(len(params)):
		temp_list=(requests.get('https://lm06.cafe.naver.com/addAndList.nhn', params=params[i], cookies=cookies[i], headers=headers).json()['l'])
		ids_nicks=[[j['m'],j['n']] for j in temp_list]
		res=intersect(res,ids_nicks)
		time.sleep(time_gap)
	return res

def ids(time_gap=0):
	return [i[0] for i in idsandnicks(time_gap)]
def nicks(time_gap=0):
        return [i[1] for i in idsandnicks(time_gap)]
if __name__=='__main__':
	a=[]
	for i in range(3):
		a=intersect(a,idsandnicks())
		time.sleep(1)
	print(len(a))
