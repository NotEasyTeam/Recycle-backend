from functools import wraps
import hashlib
import json
from re import S
from bson import ObjectId
import jwt
from datetime import datetime, timedelta
from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

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









if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)