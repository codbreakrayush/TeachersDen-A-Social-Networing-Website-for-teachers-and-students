from os import stat
import time
from logging import error
from django.shortcuts import render,redirect
import pyrebase
from requests.sessions import session
from django.http import HttpResponse
from oauth2client.client import Error
from datetime import datetime
from datetime import datetime,timezone
import pytz
import json

with open("config.json","r") as c:
    params=json.load(c)["params"]


class NotFilledDetailsError(Error):
    pass

firebaseConfig = {
    "apiKey": params['apiKey'],
    "authDomain": params['authDomain'],
    "databaseURL":params["databaseURL"],
    "projectId": params["projectId"],
    "storageBucket": params["storageBucket"],
    "messagingSenderId": params["messagingSenderId"],
    "appId": params["appId"],
    "measurementId": params["measurementId"]
}

firebase=pyrebase.initialize_app(firebaseConfig)
authe=firebase.auth()
db=firebase.database()

def home(request):
    param={"login":False}
    if request.session.get('uid'):
        uname=request.session.get('name')
        param={"login":True,"uname":uname}
        activities=db.child("unames").child(uname).child("activities").shallow().get().val()
        ac=[]
        if activities!=None:
            for a in activities:
                pname=db.child("unames").child(uname).child("activities").child(a).child("commenter").get().val()
                ts=db.child("unames").child(uname).child("activities").child(a).child("ts").get().val()
                if ts==None:
                    ts="1"
                ac.append([pname,ts])
            param["activities"]=ac
        else:
            param["activities"]="1"
        timestamps=db.child("unames").child(uname).child("timeline").shallow().get().val()
        com="0"
        tz=pytz.timezone('Asia/Kolkata')
        time_now=datetime.now(timezone.utc).astimezone(tz)
        millis=int(time.mktime(time_now.timetuple()))
        oname=request.POST.get("oname")
        comment=request.POST.get("comment")
        if oname or comment!="":
            com=request.POST.get("com")
            ts=request.POST.get("time")
            Followers=db.child("unames").child(oname).child("Followers").shallow().get().val()
            if Followers!=None:
                for f in Followers:
                    if db.child("unames").child(f).child("timeline").child(ts).child("comments").child(oname).get().val()!=None:
                        db.child("unames").child(f).child("timeline").child(ts).child("comments").child(millis).set({"cname":uname,"comment":comment})
            db.child("unames").child(oname).child("Myposts").child(ts).child("comments").child(millis).set({"cname":uname,"comment":comment})
            db.child("unames").child(oname).child("activities").child(millis).set({"commenter":uname,"ts":ts})
        elif comment=="":
            com="1"
        if timestamps==None:
            pass
        else:
            i=0
            times=[]
            data=[]
            for t in timestamps:
                times.append(t)
            print(times)
            for t in sorted(times,reverse=True):
                if i==2:
                    break
                l=[]
                usname=db.child('unames').child(uname).child("timeline").child(t).child("uname").get().val()
                name=db.child('unames').child(uname).child("timeline").child(t).child("name").get().val()
                url=db.child("unames").child(uname).child("timeline").child(t).child("url").get().val()
                desc=db.child("unames").child(uname).child("timeline").child(t).child("desc").get().val()
                tcommenters=db.child("unames").child(uname).child("timeline").child(t).child("comments").shallow().get().val()
                comments=[]
                for c in tcommenters:
                    comments.append([db.child("unames").child(uname).child("timeline").child(t).child("comments").child(c).child("cname").get().val(),db.child("unames").child(uname).child("timeline").child(t).child("comments").child(c).child("comment").get().val()])
                nt=int(millis)-int(t)
                if nt//60!=0:
                    nt=nt//60
                    if nt//60!=0:
                        nt=nt//60
                        if nt//24!=0:
                            nt=nt//24
                            if nt//365!=0:
                                nt=nt//365
                                nt=str(nt)+" years ago"
                            else:
                                nt=str(nt)+" days ago"
                        else:
                            nt=str(nt)+" hours ago"
                    else:
                        nt=str(nt)+" minutes ago"
                else:
                    nt=str(nt)+" seconds ago"
                l.append(usname)
                l.append(name)
                l.append(url)
                l.append(desc)
                l.append(nt)
                l.append(t)
                l.append(comments)
                data.append(l)
                # if com!="1":
                #     db.child('unames').child(uname).child("timeline").child(t).child("uname").remove()
                #     db.child('unames').child(uname).child("timeline").child(t).child("name").remove()
                #     db.child("unames").child(uname).child("timeline").child(t).child("url").remove()
                #     db.child("unames").child(uname).child("timeline").child(t).child("desc").remove()
                #     db.child("unames").child(uname).child("timeline").child(t).child("time").remove()
                i+=1
            param['data']=data
    return render(request,'index.html',param)

def posts(request,pname):
    param={"login":False}
    if request.session.get('uid'):
        uname=request.session.get('name')
        param={"login":True,"uname":uname,"activities":"1"}
        # activities=db.child("unames").child(uname).child("activities").shallow().get().val()
        # ac=[]
        # if activities!=None:
        #     for a in activities:
        #         pname=db.child("unames").child(uname).child("activities").child(a).child("commenter").get().val()
        #         ts=db.child("unames").child(uname).child("activities").child(a).child("ts").get().val()
        #         if ts==None:
        #             ts="1"
        #         ac.append([pname,ts])
        #     param["activities"]=ac
        timestamps=db.child("unames").child(pname).child("Myposts").shallow().get().val()
        print(timestamps,".,./,.,/")
        tz=pytz.timezone('Asia/Kolkata')
        time_now=datetime.now(timezone.utc).astimezone(tz)
        millis=int(time.mktime(time_now.timetuple()))
        oname=request.POST.get("oname")
        comment=request.POST.get("comment")
        if oname or comment!="":
            print(comment)
            ts=request.POST.get("time")
            Followers=db.child("unames").child(oname).child("Followers").shallow().get().val()
            if Followers!=None:
                for f in Followers:
                    if db.child("unames").child(f).child("timeline").child(ts).child("comments").child(oname).get().val()!=None:
                        db.child("unames").child(f).child("timeline").child(ts).child("comments").child(millis).set({"cname":uname,"comment":comment})
            db.child("unames").child(oname).child("Myposts").child(ts).child("comments").child(millis).set({"cname":uname,"comment":comment})
            db.child("unames").child(oname).child("activities").child(millis).set({"commenter":uname,"ts":ts})
        data=[]
        if timestamps==None:
            pass
        else:
            times=[]
            for t in timestamps:
                times.append(t)
            for t in sorted(times,reverse=True):
                l=[]
                usname=db.child('unames').child(pname).child("Myposts").child(t).child("uname").get().val()
                name=db.child('unames').child(pname).child("Myposts").child(t).child("name").get().val()
                url=db.child("unames").child(pname).child("Myposts").child(t).child("url").get().val()
                desc=db.child("unames").child(pname).child("Myposts").child(t).child("desc").get().val()
                tcommenters=db.child("unames").child(pname).child("Myposts").child(t).child("comments").shallow().get().val()
                comments=[]
                for c in tcommenters:
                    comments.append([db.child("unames").child(pname).child("Myposts").child(t).child("comments").child(c).child("cname").get().val(),db.child("unames").child(pname).child("Myposts").child(t).child("comments").child(c).child("comment").get().val()])
                nt=int(millis)-int(t)
                if nt//60!=0:
                    nt=nt//60
                    if nt//60!=0:
                        nt=nt//60
                        if nt//24!=0:
                            nt=nt//24
                            if nt//365!=0:
                                nt=nt//365
                                nt=str(nt)+" years ago"
                            else:
                                nt=str(nt)+" days ago"
                        else:
                            nt=str(nt)+" hours ago"
                    else:
                        nt=str(nt)+" minutes ago"
                else:
                    nt=str(nt)+" seconds ago"
                l.append(usname)
                l.append(name)
                l.append(url)
                l.append(desc)
                l.append(nt)
                l.append(t)
                l.append(comments)
                data.append(l)
            param['data']=data
    return render(request,"posts.html",param)

def singlepost(request,ts):
    param={"login":False}
    if request.session.get('uid'):
        uname=request.session.get('name')
        param={"login":True,"uname":uname}
        tz=pytz.timezone('Asia/Kolkata')
        time_now=datetime.now(timezone.utc).astimezone(tz)
        millis=int(time.mktime(time_now.timetuple()))
        comment=request.POST.get("comment")
        if comment!="":
            t=request.POST.get("time")
            Followers=db.child("unames").child(uname).child("Followers").shallow().get().val()
            if Followers!=None:
                for f in Followers:
                    if db.child("unames").child(f).child("timeline").child(t).child("comments").child(uname).get().val()!=None:
                        db.child("unames").child(f).child("timeline").child(t).child("comments").child(millis).set({"cname":uname,"comment":comment})
            db.child("unames").child(uname).child("Myposts").child(t).child("comments").child(millis).set({"cname":uname,"comment":comment})
        name=db.child('unames').child(uname).child("Myposts").child(ts).child("name").get().val()
        url=db.child("unames").child(uname).child("Myposts").child(ts).child("url").get().val()
        desc=db.child("unames").child(uname).child("Myposts").child(ts).child("desc").get().val()
        tcommenters=db.child("unames").child(uname).child("Myposts").child(ts).child("comments").shallow().get().val()
        comments=[]
        for c in tcommenters:
            comments.append([db.child("unames").child(uname).child("Myposts").child(ts).child("comments").child(c).child("cname").get().val(),db.child("unames").child(uname).child("Myposts").child(ts).child("comments").child(c).child("comment").get().val()])
        nt=int(millis)-int(ts)
        if nt//60!=0:
            nt=nt//60
            if nt//60!=0:
                nt=nt//60
                if nt//24!=0:
                    nt=nt//24
                    if nt//365!=0:
                        nt=nt//365
                        nt=str(nt)+" years ago"
                    else:
                        nt=str(nt)+" days ago"
                else:
                    nt=str(nt)+" hours ago"
            else:
                nt=str(nt)+" minutes ago"
        else:
            nt=str(nt)+" seconds ago"
        param['name']=name
        param['url']=url
        param['desc']=desc
        param['nt']=nt
        param['ts']=ts
        param['comments']=comments
    else:
        return redirect("/LogIn")
    return render(request,"post.html",param)

def Search(request):
    name=request.GET.get("name")
    skill=request.GET.get("skill")
    city=request.GET.get("city")
    state=request.GET.get("state")
    country=request.GET.get("country")

    uname=request.session.get('name')
    results=db.child("unames").shallow().get().val()
    result=[]
    rs={}
    if results!=None:
        for r in results:
            l=[]
            if r!="None" and r!=uname:
                if db.child("unames").child(r).child("profile").child("account-type").get().val()!="Teacher":
                    continue
                if name!="":
                    if name.lower() not in r.lower():
                        continue
                if skill!="":
                    skills=db.child("unames").child(r).child("skills").shallow().get().val()
                    if (skills!=None and skill.lower() not in [skil.lower() for skil in skills]) or skills==None:
                            continue
                if city!="":
                    ucity=db.child("unames").child(r).child("profile").child("city").get().val()
                    if (ucity!=None and city.lower()!=ucity.lower()) or ucity==None:
                        continue
                if state!="":
                    ustate=db.child("unames").child(r).child("profile").child("state").get().val()
                    if (ustate!=None and state.lower()!=ustate.lower()) or ustate==None:
                        continue
                if country!="":
                    ucountry=db.child("unames").child(r).child("profile").child("country").get().val()
                    if (ucountry!=None and country.lower()!=ucountry.lower()) or ucountry==None:
                        continue
                uscore=db.child("unames").child(r).child("myscore").child("total").get().val()
                rs[r]=float(uscore)
    rss=sorted(rs,key=rs.get)
    i=0
    for r in rss:
        l=[]
        if i==12:
            break
        name=db.child("unames").child(r).child("profile").child("name").get().val()
        bio=db.child("unames").child(r).child("profile").child("bio").get().val()
        atype=db.child("unames").child(r).child("profile").child("account-type").get().val()
        img_url=db.child("unames").child(r).child("dp").child("url").get().val()
        if img_url==None:
            img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
        l.append(r)
        l.append(name)
        l.append(bio)
        l.append(atype)
        l.append(img_url)
        l.append(rs[r])
        result.append(l)
        i+=1
    if len(result)==0:
        data={"results":"0"}
    else:
        data={"results":result}
    return render(request,'explore.html',data)

def image(request):
    data={}
    try:
        uname=request.session.get('name')
        img_url=db.child('unames').child(uname).child("dp").child("url").get().val()
        if img_url==None:
            img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
        data={"img":img_url}
    except:
        return redirect("/LogOut")
    return render(request,"image.html",data)

def postimage(request):
    uname=request.session.get('name')
    url=request.POST.get("url")
    img_url=db.child('unames').child(uname).child("dp").child("url").get().val()
    if img_url!=None:
        db.child('unames').child(uname).child("dp").update({"url":url})
    else:
        db.child('unames').child(uname).child("dp").set({"url":url})
    return redirect('/Profile')

def Profile(request):
    try:
        uname=request.session.get('name')
        idToken=request.session['uid']
        user=authe.get_account_info(idToken)
        uid=user["users"][0]["localId"]

        # About Section
        name=db.child('users').child(uid).child("details").child("name").get().val()
        city=db.child('unames').child(uname).child("profile").child("city").get().val()
        state=db.child('unames').child(uname).child("profile").child("state").get().val()
        country=db.child('unames').child(uname).child("profile").child("country").get().val()
        paddress=db.child('unames').child(uname).child("profile").child("paddress").get().val()
        phone=db.child('unames').child(uname).child("profile").child("phone-number").get().val()
        pphone=db.child('unames').child(uname).child("profile").child("pphone-number").get().val()
        email=db.child('unames').child(uname).child("profile").child("email").get().val()
        bio=db.child('unames').child(uname).child("profile").child("bio").get().val()
        profile=db.child('unames').child(uname).child("profile").child("account-type").get().val()
        name=name.split()
        fname=name[0]
        name.remove(fname)
        lname=" ".join(name)
        address=""
        if city!=None:
            address+=city+" . "
        if state!=None:
            address+=state+" . "
        if country!=None:
            address+=country+" . "
        data={"fname":fname,"lname":lname,"uname":uname,"address":address,"paddress":paddress,"phone":phone,"pphone":pphone,"email":email,"bio":bio,"profile":profile}

        # Image Section
        img_url=db.child('unames').child(uname).child("dp").child("url").get().val()
        if img_url==None:
            img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
        data["img"]=img_url
        #Experience Section
        experiences=db.child("unames").child(uname).child("experiences").shallow().get().val()
        if experiences!=None:
            experiencesl=[]
            for e in experiences:
                l=[e]
                l.append(db.child("unames").child(uname).child("experiences").child(e).child("place").get().val())
                l.append(db.child("unames").child(uname).child("experiences").child(e).child("desc").get().val())
                experiencesl.append(l)
            data["experiences"]=experiencesl

        #Skills Section
        skills=db.child("unames").child(uname).child("skills").shallow().get().val()
        if skills!=None:
            skillsl=[]
            for sk in skills:
                skillsl.append(sk)
            data["skills"]=skillsl

        #Interests Section
        interests=db.child("unames").child(uname).child("interests").shallow().get().val()
        if interests!=None:
            interestsl=[]
            for sk in interests:
                interestsl.append(sk)
            data["interests"]=interestsl

        #Awards Section
        awards=db.child("unames").child(uname).child("awards").shallow().get().val()
        if awards!=None:
            awardsl=[]
            for a in awards:
                l=[a]  
                l.append(db.child("unames").child(uname).child("awards").child(a).child("award_desc").get().val())
                l.append(db.child("unames").child(uname).child("awards").child(a).child("award_link").get().val())
                awardsl.append(l)
            data["awards"]=awardsl
    except:
        return redirect("/LogOut")
    return render(request,'Profile.html',data)
def editabout(request):
    return render(request,"SignUp.html",{"work":"editabout"})
def postabout(request):
    idToken=request.session['uid']
    user=authe.get_account_info(idToken)
    uid=user["users"][0]["localId"]
    uname=request.session.get('name')
    name=db.child('users').child(uid).child("details").child("name").get().val()
    district=request.POST.get('city')
    state=request.POST.get('state')
    country=request.POST.get('country')
    paddress=request.POST.get('pAddress')
    phone=request.POST.get('phone')
    pphone=request.POST.get('pphone')
    email=request.POST.get('email')
    bio=request.POST.get('bio')
    atype=request.POST.get('atype')
    data={"city":district,"state":state,"country":country,"paddress":paddress,"pphone-number":pphone,"bio":bio}
    if db.child("unames").child(uname).child("profile").child("city").get().val()==None:
        db.child("unames").child(uname).child("profile").update(data)
    else:
        if district!="":
            db.child("unames").child(uname).child("profile").update({"city":district})
        if state!="":
            db.child("unames").child(uname).child("profile").update({"state":state})
        if country!="":
            db.child("unames").child(uname).child("profile").update({"country":country})
        if paddress!=None:
            db.child("unames").child(uname).child("profile").update({"paddress":paddress})
        if phone!="":
            db.child("unames").child(uname).child("profile").update({"phone-number":phone})
            db.child("users").child(uid).child("details").update({"phone-number":phone})
        if pphone!=None:
            db.child("unames").child(uname).child("profile").update({"pphone-number":pphone})
        if email!="":
            db.child("unames").child(uname).child("profile").update({"email":email})
            db.child("users").child(uid).child("details").update({"email":email})
        if atype!=None:
            db.child("unames").child(uname).child("profile").update({"account-type":atype})
            db.child("users").child(uid).child("details").update({"account-type":atype})
        if bio!="":
            db.child("unames").child(uname).child("profile").update({"bio":bio})
    return redirect("/Profile")
def editexp(request):
    return render(request,"SignUp.html",{"work":"editexp"})
def postexp(request):
    exp=request.POST.get('exp')
    eplace=request.POST.get('eplace')
    edesc=request.POST.get('edesc')
    uname=request.session.get('name')
    db.child("unames").child(uname).child("experiences").child(exp).set({"place":eplace,"desc":edesc})
    return redirect("/Profile")
def editedu(request):
    return render(request,"SignUp.html",{"work":"editedu"})
def postedu(request):
    return 
def editskills(request):
    return render(request,"SignUp.html",{"work":"editskills"})
def postskills(request):
    skill=request.POST.get('skill')
    uname=request.session.get('name')
    # if db.child("unames").child(uname).child("skills").get().val()!=None:
    #     skills=db.child("unames").child(uname).child("skills").shallow().get().val()
    #     skillsl=[]
    #     for sk in skills:
    #         skillsl.append(sk)
    #     value=1
    #     for sk in skillsl:
    #         if int(db.child("unames").child(uname).child("skills").child(sk).child("val").get().val())>value:
    #             value=1+(db.child("unames").child(uname).child("skills").child(sk).child("val").get().val())
    #     db.child("unames").child(uname).child("skills").child(skill).set({"val":value})
    # else:
    db.child("unames").child(uname).child("skills").child(skill).set({"val":0})
    return redirect("/Profile")

def score(request,pname):
    uname=request.session.get("name")
    nta=int(float(db.child("unames").child(pname).child("myscore").child("ta").get().val())*(100/(5*0.3)))
    nts=int(float(db.child("unames").child(pname).child("myscore").child("ts").get().val())*(100/(5*0.2)))
    ncs=int(float(db.child("unames").child(pname).child("myscore").child("cs").get().val())*(100/(5*0.2)))
    nma=int(float(db.child("unames").child(pname).child("myscore").child("ma").get().val())*(100/(5*0.1)))
    nh=int(float(db.child("unames").child(pname).child("myscore").child("h").get().val())*(100/(5*0.1)))
    ni=int(float(db.child("unames").child(pname).child("myscore").child("i").get().val())*(100/(5*0.1)))
    count=int(db.child("unames").child(pname).child("myscore").child("count").get().val())
    total=float(db.child("unames").child(pname).child("myscore").child("total").get().val())
    img_url=db.child('unames').child(pname).child("dp").child("url").get().val()
    if img_url==None:
        img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
    scor=db.child("unames").child(uname).child("scores").child(pname).child("score").get().val()
    if scor==None:
        scor="0"
    if uname==pname:
        scor="2"
    data={"nta":nta,"nts":nts,"ncs":ncs,"nma":nma,"nh":nh,"ni":ni,"count":count,"total":total,"uname":pname,"score":scor,"img":img_url,"usname":uname}
    return render(request,"score.html",data)
def addscore(request,pname):
    if not request.session.get('uid'):
        return redirect('/LogIn')
    return render(request,"addscore.html",{"uname":pname})

def postscore(request):
    if not request.session.get('uid'):
        return redirect('/LogIn')
    uname=request.session.get('name')
    f=request.POST.get("teaching_ability")
    s=request.POST.get("teaching_style")
    t=request.POST.get("communication_skills")
    f=request.POST.get("motivation_ability")
    fi=request.POST.get("heplful")
    si=request.POST.get("Inspire")
    pname=request.POST.get("uname")
    
    ta=float(f)*0.3
    ts=float(s)*0.2
    cs=float(t)*0.2
    ma=float(f)*0.1
    h=float(fi)*0.1
    i=float(si)*0.1
    nta=float(db.child("unames").child(pname).child("myscore").child("ta").get().val())
    nts=float(db.child("unames").child(pname).child("myscore").child("ts").get().val())
    ncs=float(db.child("unames").child(pname).child("myscore").child("cs").get().val())
    nma=float(db.child("unames").child(pname).child("myscore").child("ma").get().val())
    nh=float(db.child("unames").child(pname).child("myscore").child("h").get().val())
    ni=float(db.child("unames").child(pname).child("myscore").child("i").get().val())
    count=int(db.child("unames").child(pname).child("myscore").child("count").get().val())
    nta=round((nta*count+ta)/(count+1),1)
    nts=round((nts*count+ts)/(count+1),1)
    ncs=round((ncs*count+cs)/(count+1),1)
    nma=round((nma*count+ma)/(count+1),1)
    nh=round((nh*count+h)/(count+1),1)
    ni=round((ni*count+i)/(count+1),1)
    total=nta+nts+ncs+nma+nh+ni
    total=round(total,1)
    count+=1
    db.child("unames").child(pname).child("myscore").update({"ta":nta,"ts":nts,"cs":ncs,"ma":nma,"h":nh,"i":ni,"total":total,"count":count})
    db.child("unames").child(uname).child("scores").child(pname).set({"ta":ta,"ts":ts,"cs":cs,"ma":ma,"h":h,"i":i,"score":1})
    url="/score/{}".format(pname)
    return redirect(url)

def editinterest(request):
    return render(request,"SignUp.html",{"work":"editinterest"})
def postinterest(request):
    interest=request.POST.get('interest')
    uname=request.session.get('name')
    db.child("unames").child(uname).child("interests").child(interest).set({"val":0})
    return redirect('/Profile/') 
def editawards(request):
    return render(request,"SignUp.html",{"work":"editawards"})
def postawards(request):
    award=request.POST.get('award')
    award_desc=request.POST.get('adesc')
    award_link=request.POST.get('alink')
    uname=request.session.get('name')
    db.child("unames").child(uname).child("awards").child(award).set({"award_desc":award_desc,"award_link":award_link})
    return redirect('/Profile')

def logIn(request):
    return render(request,'LogIn.html' )

def PostSignIn(request):
    email = request.POST.get('email')
    passw=request.POST.get('pass')
    if request.session.get('uid'):
        message="User is already logged in, Please log out before logging in again!!"
        return render(request, "index.html", {"message": message})
    else:
        try:
            user=authe.sign_in_with_email_and_password(email,passw)
        except:
            message = "Invalid Credentials!!Please Check your Data"
            return render(request, "LogIn.html", {"message": message})
        session_id=user['idToken']
        request.session['uid'] = str(session_id)
        uname=""
        for i in email:
            if i=="@":
                break
            uname+=i
        request.session['name'] = uname
        request.session['email'] = email
    return redirect("/")

def logOut(request):
    try:
        del request.session['uid']
    except:
        pass
    return redirect("/LogIn")

def signUp(request):
    return render(request,"SignUp.html",{"work":"createanaccount"})

def PostSignUp(request):
    name=request.POST.get('name')
    phone=request.POST.get('phone')
    birthday=request.POST.get('birthday')
    gender=request.POST.get('gender')
    email=request.POST.get('email')
    passw=request.POST.get('pass')
    atype=request.POST.get('type')
    uname=""
    for i in email:
        if i=="@":
            break
        uname+=i
    try:
        if name=="" or phone=="" or birthday=="" or gender==None or email=="" or atype==None :
            raise NotFilledDetailsError
        
        user=authe.create_user_with_email_and_password(email,passw)
        uid=user['localId']
        print(uid)
        data={"name":name,"phone-number":phone,"birth-date":birthday,"gender":gender,"email":email,"account-type":atype}
        db.child("users").child(uid).child("details").set(data)
        db.child("unames").child(uname).set({"email":email})
        db.child("unames").child(uname).child("profile").set({"name":name,"email":email,"phone-number":phone,"account-type":atype})
        if atype=="Teacher":
            db.child("unames").child(uname).child("myscore").set({"ta":"0.0","ts":"0.0","cs":"0.0","ma":"0.0","h":"0.0","i":"0.0","total":"0.0","count":0})
    except(NotFilledDetailsError):
        message="Please fill all details before signing up"
        return render(request,"SignUp.html",{"message":message})
    except:
        message="This email already exists. So try again with different email"
        return render(request,"SignUp.html",{"message":message})
    data={"name":name,"phone-number":phone,"birth-date":birthday,"gender":gender,"email":email,"account-type":atype}
    print(data)

    return redirect("/LogIn")

def cookie_session(request):
    request.session.set_test_cookie()
    return HttpResponse("<h1>dataflair</h1>")

def cookie_delete(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return HttpResponse("Cookie Created")
    return HttpResponse("Not accept Cookies")

def follower(request,pname):
    uname=request.session.get('name')
    Followers=db.child("unames").child(pname).child("Followers").shallow().get().val()
    cFollowings=db.child("unames").child(uname).child("Followings").shallow().get().val()
    pimg_url=db.child('unames').child(pname).child("dp").child("url").get().val()
    if pimg_url==None:
        pimg_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
    data={"pimg":pimg_url,"pname":pname,"uname":uname}
    if Followers!=None:
        Followersl=[]
        for f in Followers:
            if f!="None":
                l=[]
                l.append(f)
                img_url=db.child('unames').child(f).child("dp").child("url").get().val()
                if img_url==None:
                    img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
                l.append(img_url)
                if cFollowings!=None:
                    if f in cFollowings:
                        l.append("1")
                    else:
                        l.append("0")
                else:
                    l.append("0")
                Followersl.append(l)
        data["Followers"]=Followersl
        
    Followings=db.child("unames").child(pname).child("Followings").shallow().get().val()
    if Followings!=None:
        Followingsl=[]
        for f in Followings:
            if f!="None":
                l=[]
                l.append(f)
                img_url=db.child('unames').child(f).child("dp").child("url").get().val()
                if img_url==None:
                    img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
                l.append(img_url)
                if cFollowings!=None:
                    if f in cFollowings:
                        l.append("1")
                    else:
                        l.append("0")
                else:
                    l.append("0")
                Followingsl.append(l)
        data["Followings"]=Followingsl
    return render(request,"follow.html",data)

def follow(request):
    uname=request.session.get('name')
    pname=request.POST.get("follow")
    tz=pytz.timezone('Asia/Kolkata')
    time_now=datetime.now(timezone.utc).astimezone(tz)
    millis=int(time.mktime(time_now.timetuple()))
    db.child("unames").child(uname).child("Followings").child(pname).set({"status":"active"})
    db.child("unames").child(pname).child("Followers").child(uname).set({"status":"active"})
    db.child("unames").child(pname).child("activities").child(millis).set({"commenter":uname})
    return redirect("/")

def unfollow(request):
    pname=request.POST.get("unfollow")
    uname=request.session.get('name')
    try:
        db.child("unames").child(uname).child("Followings").child(pname).child("status").remove()
        db.child("unames").child(pname).child("Followers").child(uname).child("status").remove()
    except:
        pass
    return redirect("/follow")

def aprofile(request,pname):
    uname=request.session.get('name')
    # About Section
    name=db.child('unames').child(pname).child("profile").child("name").get().val()
    city=db.child('unames').child(uname).child("profile").child("city").get().val()
    state=db.child('unames').child(uname).child("profile").child("state").get().val()
    country=db.child('unames').child(uname).child("profile").child("country").get().val()
    paddress=db.child('unames').child(pname).child("profile").child("paddress").get().val()
    phone=db.child('unames').child(pname).child("profile").child("phone-number").get().val()
    pphone=db.child('unames').child(pname).child("profile").child("pphone-number").get().val()
    email=db.child('unames').child(pname).child("profile").child("email").get().val()
    bio=db.child('unames').child(pname).child("profile").child("bio").get().val()
    profile=db.child('unames').child(pname).child("profile").child("account-type").get().val()
    name=name.split()
    fname=name[0]
    name.remove(fname)
    lname=" ".join(name)
    address=""
    if city!=None:
        address+=city+" . "
    if state!=None:
        address+=state+" . "
    if country!=None:
        address+=country+" . "
    data={"fname":fname,"lname":lname,"uname":pname,"address":address,"paddress":paddress,"phone":phone,"pphone":pphone,"email":email,"bio":bio,"profile":profile}

    img_url=db.child('unames').child(pname).child("dp").child("url").get().val()
    if img_url==None:
        img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
    data["img"]=img_url

    follow=db.child("unames").child(uname).child("Followings").shallow().get().val()
    if follow!=None:
        if pname in follow:
            data["follow"]=1
    #Experience Section
    experiences=db.child("unames").child(pname).child("experiences").shallow().get().val()
    if experiences!=None:
        experiencesl=[]
        for e in experiences:
            l=[e]
            l.append(db.child("unames").child(pname).child("experiences").child(e).child("place").get().val())
            l.append(db.child("unames").child(pname).child("experiences").child(e).child("desc").get().val())
            experiencesl.append(l)
        data["experiences"]=experiencesl

    #Skills Section
    skills=db.child("unames").child(pname).child("skills").shallow().get().val()
    if skills!=None:
        skillsl=[]
        for sk in skills:
            skillsl.append(sk)
        data["skills"]=skillsl

    #Interests Section
    interests=db.child("unames").child(pname).child("interests").shallow().get().val()
    if interests!=None:
        interestsl=[]
        for sk in interests:
            interestsl.append(sk)
        data["interests"]=interestsl

    #Awards Section
    awards=db.child("unames").child(pname).child("awards").shallow().get().val()
    if awards!=None:
        awardsl=[]
        for a in awards:
            l=[a]  
            l.append(db.child("unames").child(pname).child("awards").child(a).child("award_desc").get().val())
            l.append(db.child("unames").child(pname).child("awards").child(a).child("award_link").get().val())
            awardsl.append(l)
        data["awards"]=awardsl
    # except:
    #     return redirect("/LogOut")   
        
    return render(request,"aprofile.html",data)

def addpost(request):
    img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMYdcANR0zcV7kEjGVHd7X6CajSpi7eMT6XpqvKN-WiC2nmgNYIudZhkxQlsCxBNVtXB8&usqp=CAU"
    return render(request,"addpost.html",{"img":img_url})

def postpost(request):
    uname=request.session.get('name')
    url=request.POST.get("url")
    desc=request.POST.get("desc")
    name=db.child('unames').child(uname).child("profile").child("name").get().val()
    if url==None:
        return redirect('/addpost')
    if desc==None:
        desc=""
    tz=pytz.timezone('Asia/Kolkata')
    time_now=datetime.now(timezone.utc).astimezone(tz)
    millis=int(time.mktime(time_now.timetuple()))
    data={"url":url,"desc":desc,"time":millis,"uname":uname,"name":name}
    Followers=db.child("unames").child(uname).child("Followers").shallow().get().val()
    for f in Followers:
        db.child("unames").child(f).child("timeline").child(millis).set(data)
        db.child("unames").child(f).child("timeline").child(millis).child("comments").child(millis).set({"cname":uname,"comment":desc})
    db.child("unames").child(uname).child("Myposts").child(millis).set(data)
    db.child("unames").child(uname).child("Myposts").child(millis).child("comments").child(millis).set({"cname":uname,"comment":desc})
    return redirect("/Profile")

def about(request):
    return render(request,"about.html")