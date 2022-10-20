import pickle
import subprocess


def merge(a):
    b=pickle.load(open(a,'rb'))
    c=pickle.load(open("./"+a.split(".")[0]+"_from_server"+"."+a.split(".")[1],'rb'))
    print(len(b),len(c))
    for i in c:
        if i in b:
            try:
                if c[i]['last_updated']>b[i]['last_updated']:
                    b[i]=c[i]
            except:
                b[i]=c[i]
                #print('last_updated' in c[i].keys(),'last_updated' in b[i].keys())
                #print(c[i]['followers'],b[i]['followers'],a)
        else:
            b[i]=c[i]
    print(len(b))
    pickle.dump(b,open("./"+a.split(".")[0]+"_merged"+"."+a.split(".")[1],'wb'))
queue=['streamers_data.pickle','hakko_streamers_data.pickle']
for i in queue:
    subprocess.run(["scp","root@woowakgood.live:api/"+i,"./"+i.split(".")[0]+"_from_server"+"."+i.split(".")[1]])
    merge(i)
