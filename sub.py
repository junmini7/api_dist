import pickle
import pandas as pd
subj=pickle.load(open('subj','rb'))
stu=pickle.load(open('23grade','rb'))
def trade(subject,bef,aft):
    befname=subject+'-'+str(bef)
    aftname=subject+'-'+str(aft)
    mytime=subj[befname]
    allowlist=[]
    for item in subj:
        if len(set(subj[item])&set(mytime))==0:
            allowlist.append(item)
    re=[]
    likestu=stu.loc[stu[aftname] == 1]
    for i in likestu.index:
        if set(list(likestu.columns[(likestu==1.0).loc[i]])).issubset(set(allowlist)):
            re.append(i)
    return re
def whotakesubj(subject):
    bun=1
    re=[]
    while True:
        try: 
            re+=whotake(subject,bun)
            bun+=1
        except: break
    return re
def whotake(subject,bun):
    name=subject+'-'+str(bun)
    likestu=stu.loc[stu[name] == 1]
    return(list(likestu.index))
