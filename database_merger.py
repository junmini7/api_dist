import pickle
# import subprocess



b=pickle.load(open('streamers_data.pickle','rb'))
c=pickle.load(open("streamers_data_from_local.pickle",'rb'))
print(len(b),len(c))
for i in c:
    if i in b:
        # if (not 'followers' in b[i] and 'followers' in c[i]) or ('followers' in b[i] and 'followers' in c[i] and c[i]['last_updated']>b[i]['last_updated']):
        #     b[i]['followers']=c[i]['followers']
        if not 'last_updated' in b[i] and 'followers' in b[i]:
            b[i]['last_updated']=c[i]['last_updated']
            #print('last_updated' in c[i].keys(),'last_updated' in b[i].keys())
            #print(c[i]['followers'],b[i]['followers'],a)
    else:
        b[i]=c[i]
print(len(b))

pickle.dump(b,open("streamers_data.pickle",'wb'))
# queue=['streamers_data.pickle','hakko_streamers_data.pickle']
# for i in queue:
#     subprocess.run(["scp","root@woowakgood.live:api/"+i,"./"+i.split(".")[0]+"_from_server"+"."+i.split(".")[1]])
#
