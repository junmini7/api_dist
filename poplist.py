import requests
import json
import pickle
import pandas as pd
from datetime import datetime as dt
n=39000
def update():
    data=pd.DataFrame.from_dict(requests.get(f'https://api.everywak.kr/bestwakki/WakkiPopularArticles?&page=1&perPage={n}').json()['message']['result']['popularArticleList'])
    data = data.astype({'writeDateTimestamp':'int','updatedTimeStamp':'int'})
    data['date'] = data['writeDateTimestamp'].apply(lambda x:dt.fromtimestamp(x))
    data['updatedate'] = data['updatedTimeStamp'].apply(lambda x:dt.fromtimestamp(x))
    data['link']='<a href="https://cafe.naver.com/steamindiegame/'+data["articleId"]+'" target="_blank">'+data["subject"]+'</a>'
    pickle.dump(data,open('pop.pandas','wb'))   
def recall():
    data=pickle.load(open('pop.pandas','rb'))
    return data
update()
data=recall()
#print(data['nickname'].value_counts())
nickname='도밍이'

userdata=data.loc[data['nickname'] == nickname][['subject','date','link']].reset_index(drop=True)

print(userdata.to_html())
#print(data[1:1001:999][['subject','date','updatedate']])
