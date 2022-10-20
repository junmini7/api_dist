import os
import urllib.request
import six
import time
import pickle
client_id,client_secret=pickle.load(open('papago_api_key.pickle','rb'))
key=0

def translate(text,toLang,fromLang):

    global key
    encText = urllib.parse.quote(text)
    data = "source=%s&target=%s&text="%(fromLang,toLang) + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    response=None
    while response==None:
        request.add_header("X-Naver-Client-Id",client_id[key])
        request.add_header("X-Naver-Client-Secret",client_secret[key])
        try:
            response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        except:
            print('key has changed from %d to %d'%(key,key+1))
            key+=1
            if key==len(client_id):
                assert False
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read().decode('utf-8')
        result=response_body.split('"translatedText":"')[1].split('"')[0]
        return result
