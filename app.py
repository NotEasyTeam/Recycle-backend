from functools import wraps
import hashlib
import json
from re import S
#from bson import ObjectId
import jwt
from datetime import datetime, timedelta
from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import certifi

client = MongoClient('mongodb+srv://test:sparta@cluster0.1idhr.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.dbsparta

SECRET_KEY = 'recycle'

app = Flask(__name__)
cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost', 27017)
db = client.tencycle

@app.route('/')
def home():
    return jsonify({'msg' : 'success'})

@app.route("/signup", methods=["POST"])
def sign_up():
    
    data = json.loads(request.data)
    print(data)
    
    password_hash = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    
    doc = {
        'username' : data.get('username'),
        'userid' : data.get('userid'),
        'password' : password_hash,
        'userpoint' : '0'
    }
    
    db.users.insert_one(doc)
    
    return jsonify({'msg':'success'})


@app.route("/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    print(data)
    
    userid = data.get("userid")
    password = data.get("password")
    
     # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    result = db.users.find_one({
        'userid': userid, 
        'password': hashed_pw
    })
    
    if result:
       
        
        payload = {
            'id': str(result["_id"]),
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')
        
    
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route("/upload", methods=["POST"])
def image_predict():
    img=request.files['file'] # 이미지 파일
    user_id=request.form['id_give'] # 사용자 ID
    now_time=datetime.now() # 현재 시각
    ext_tail=img_name.split(".")[-1] # 확장자 추출
    file_name=f"{current_time.strftime('%Y%m%d%H%M%S')}.{ext_tail}" # '날짜.확장자' 를 파일명으로 지정
    save_location=f"/static/image/{file_name}" # 저장할 장소
    img.save(save_location) # 이미지 저장

    # 예측
    pred=load_model.predict(save_location)

    # DB로 결과와 함께 전달
    doc={
        'user_id': user_id,
        'image': img,
        'category': pred,
        'date': now_time
    }
    db.recycles.insert_one(doc)

    return jsonify({'msg': '예측 완료!'})


@app.route("/main", methods=["GET"])
def get_image():
    user_id=request.form['id_give'] # 사용자 ID
    result=db.recycles.find_one({'user_id': user_id}) # 가장 최근꺼 결과 가져오기

    return jsonify({'img': img})




if __name__ =='__main__':
    app.run('0.0.0.0', port=5500, debug=True)