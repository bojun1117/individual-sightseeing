from bson.objectid import ObjectId
from flask import *
import pymongo

app = Flask(__name__)
app.secret_key = "eric1117"

@app.route("/")     #首頁
def index():  
    return render_template("home.html")

@app.route("/member")   #會員首頁
def member():
    if "nickname" in session:
        return render_template("member.html",member_name=session['nickname'])
    else:
        redirect("/")

@app.route("/login")        #登入
def login():
    return render_template("login.html")

@app.route("/sign", methods=["POST"])         #取得登入資訊
def sign():
    client = pymongo.MongoClient("mongodb+srv://host:eric1117@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.members
    ID = request.form["ID"]
    password = request.form["password"]
    data = collection.find_one({
        "$and":[
            {"ID":ID},
            {"password":password}
        ]
    })
    if data == None:
        flash("帳號或密碼錯誤","info")
        return redirect("/")
    else:
        flash("登入成功","info")
        member = data.get("nickname")
        session["nickname"] = member
        return redirect("/member")

@app.route("/signout")      #登出
def signout():
    del session['nickname']
    return redirect("/")

@app.route("/register")     #註冊
def register():
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])        #取得註冊資訊
def create_account():
    client = pymongo.MongoClient("mongodb+srv://host:eric1117@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.members
    nickname = request.form["nickname"]
    ID = request.form["ID"]
    password = request.form["password"]
    data = collection.find_one({
        "ID":ID
    })
    if data != None:
        flash("失敗!學號已使用","info")
        return redirect("/")
    else:
        collection.insert_one({
            "nickname":nickname,
            "ID":ID,
            "password":password,
            "collect":[]
        })
        flash("註冊成功!","info")
        return redirect("/")

@app.route("/visitor_show")     #訪客顯示結果
def visitor_show():
    client = pymongo.MongoClient("mongodb+srv://visitor:123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.attractions
    location = request.args.get("location")
    data = collection.find({
        "locate":location
    })
    all_place = list()
    for place in data:
        place["_id"] = str(place["_id"])
        all_place.append(place)
    l = location+"地區"
    return render_template("visitor_show.html",location=l,places=all_place)

@app.route("/member_show")      #會員顯示結果
def member_show():
    if "nickname" in session:
        client = pymongo.MongoClient("mongodb+srv://member:abc_123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
        db = client.travel
        collection1 = db.attractions
        collection2 = db.members
        location = request.args.get("location")
        session['location'] = location
        data = collection1.find({
            "locate":location
        })
        member_collection = collection2.find_one({
            "nickname":session["nickname"]
        })
        member_collect = member_collection.get("collect")
        member_collectSet = set(member_collect)
        all_place = list()
        for place in data:
            place["_id"] = str(place["_id"])
            all_place.append(place)
        l = location+"地區"
        return render_template("member_show.html",member_name=session['nickname'],location=l,places=all_place,collects=member_collectSet)
    else:
        redirect("/")

@app.route("/append")   #添加景點
def append():
    return render_template("append.html")

@app.route("/getdata", methods=["POST"])      #取得添加景點資訊
def getdata():
    client = pymongo.MongoClient("mongodb+srv://member:abc_123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.attractions
    locate = request.form['locate']
    country = request.form['country']
    name = request.form['place']
    score = request.form['score']
    tag = request.form['tag']
    picture = request.form['picture']
    comment = request.form['comment']
    data = collection.find_one({
        "name":name
    })
    if data == None:
        collection.insert_one({
            "locate":locate,
            "country":country,
            "name":name,
            "score":score,
            "tag":[tag],
            "comment":[comment],
            "picture":picture
        })
    else:
        num = len(data['comment'])
        new_score = round((float(data['score'])*num+float(score))/(num+1),1)
        collection.update_one({
            "name":name
        },{
            "$addToSet":{
                "tag":tag,
                "comment":comment
            }
        })
        collection.update_one({
            "name":name
        },{
            "$set":{
                "score":new_score
            }
        })
    return redirect("/member")

@app.route("/addfavor", methods=["POST"])       #加入會員收藏
def addfavor():
    client = pymongo.MongoClient("mongodb+srv://member:abc_123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.members
    data = request.form['attraction']
    collection.update_one({
        "nickname":session["nickname"]
    },{
        "$addToSet":{
            "collect":data
        }
    })
    return redirect("/member_show?location="+session['location'])

@app.route("/removefavor", methods=["POST"])       #移除會員收藏
def removefavor():
    client = pymongo.MongoClient("mongodb+srv://member:abc_123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.members
    data = request.form['attraction']
    collection.update_one({
        "nickname":session["nickname"]
    },{
        "$pull":{
            "collect":data
        }
    })
    return redirect("/member_show?location="+session['location'])

@app.route("/delfavor", methods=["POST"])     #favor介面移除收藏
def delfavor():
    client = pymongo.MongoClient("mongodb+srv://member:abc_123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
    db = client.travel
    collection = db.members
    data = request.form['attraction']
    collection.update_one({
        "nickname":session["nickname"]
    },{
        "$pull":{
            "collect":data
        }
    })
    return redirect("/favor")

@app.route("/favor")    #會員景點收藏界面
def favor():
    if "nickname" in session:
        client = pymongo.MongoClient("mongodb+srv://member:abc_123@travelcluster.s7nmq.mongodb.net/travel?retryWrites=true&w=majority")
        db = client.travel
        collection1 = db.attractions
        collection2 = db.members
        data = collection2.find_one({
            "nickname":session["nickname"]
        })
        all_place = list()
        for placeid in data['collect']:
            item = collection1.find_one(ObjectId(placeid))
            all_place.append(item)
        return render_template("favor.html",member_name=session['nickname'],places=all_place)
    else:
        return redirect("/")

app.run(port=3000)