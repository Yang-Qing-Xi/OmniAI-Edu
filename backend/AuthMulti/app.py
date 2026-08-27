from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import hashlib
import random
import re

app = Flask(__name__)
CORS(app)

# MongoDB连接
client = MongoClient('mongodb://localhost:27017/')
db = client['omni_edu']

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

# 验证码存储
sms_codes = {}
email_codes = {}

@app.route('/api/auth/send-code', methods=['POST'])
def send_code():
    """发送验证码（手机或邮箱）"""
    data = request.json
    account = data.get('account', '').strip()
    
    if not account:
        return jsonify({'code': 400, 'message': '请输入手机号或邮箱'})
    
    code = generate_code()
    
    if re.match(r'^1[3-9]\d{9}$', account):
        sms_codes[account] = {'code': code, 'time': datetime.now()}
        print(f"[模拟] 向手机 {account} 发送验证码: {code}")
    elif re.match(r'^[\w.-]+@[\w.-]+\.\w+$', account):
        email_codes[account] = {'code': code, 'time': datetime.now()}
        print(f"[模拟] 向邮箱 {account} 发送验证码: {code}")
    else:
        return jsonify({'code': 400, 'message': '手机号或邮箱格式不正确'})
    
    return jsonify({'code': 200, 'message': '验证码已发送', 'debug_code': code})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """注册"""
    data = request.json
    method = data.get('method', 'password')
    
    if method == 'password':
        username = data.get('username', '').strip()
        password = data.get('password', '')
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        
        if not username or not password:
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'})
        if len(password) < 6:
            return jsonify({'code': 400, 'message': '密码至少6位'})
        
        existing = db.users.find_one({'$or': [
            {'username': username},
            {'phone': phone} if phone else {},
            {'email': email} if email else {}
        ]})
        if existing:
            return jsonify({'code': 409, 'message': '用户名/手机号/邮箱已被注册'})
        
        user = {
            'username': username,
            'password': hash_password(password),
            'phone': phone,
            'email': email,
            'bind_wechat': '',
            'bind_qq': '',
            'created_at': datetime.now(),
            'avatar': ''
        }
        result = db.users.insert_one(user)
        user['_id'] = str(result.inserted_id)
        del user['password']
        
        return jsonify({'code': 200, 'message': '注册成功', 'data': user})
    
    elif method == 'code':
        account = data.get('account', '').strip()
        code = data.get('code', '').strip()
        password = data.get('password', '')
        
        valid = False
        if account in sms_codes:
            c = sms_codes[account]
            if c['code'] == code and (datetime.now() - c['time']) < timedelta(minutes=5):
                valid = True
        elif account in email_codes:
            c = email_codes[account]
            if c['code'] == code and (datetime.now() - c['time']) < timedelta(minutes=5):
                valid = True
        
        if not valid:
            return jsonify({'code': 403, 'message': '验证码错误或已过期'})
        
        is_phone = re.match(r'^1[3-9]\d{9}$', account)
        query_field = 'phone' if is_phone else 'email'
        existing = db.users.find_one({query_field: account})
        if existing:
            return jsonify({'code': 409, 'message': '该账号已被注册'})
        
        user = {
            'username': f'用户{account[-4:]}',
            'password': hash_password(password) if password else '',
            'phone': account if is_phone else '',
            'email': account if not is_phone else '',
            'bind_wechat': '',
            'bind_qq': '',
            'created_at': datetime.now(),
            'avatar': ''
        }
        result = db.users.insert_one(user)
        user['_id'] = str(result.inserted_id)
        del user['password']
        
        sms_codes.pop(account, None)
        email_codes.pop(account, None)
        
        return jsonify({'code': 200, 'message': '注册成功', 'data': user})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """登录"""
    data = request.json
    method = data.get('method', 'password')
    
    if method == 'password':
        account = data.get('account', '').strip()
        password = data.get('password', '')
        
        if not account or not password:
            return jsonify({'code': 400, 'message': '请输入账号和密码'})
        
        user = db.users.find_one({'$or': [
            {'username': account},
            {'phone': account},
            {'email': account}
        ]})
        
        if not user or user.get('password') != hash_password(password):
            return jsonify({'code': 401, 'message': '账号或密码错误'})
        
        user['_id'] = str(user['_id'])
        del user['password']
        return jsonify({'code': 200, 'message': '登录成功', 'data': user})
    
    elif method == 'code':
        account = data.get('account', '').strip()
        code = data.get('code', '').strip()
        
        valid = False
        if account in sms_codes:
            c = sms_codes[account]
            if c['code'] == code and (datetime.now() - c['time']) < timedelta(minutes=5):
                valid = True
        elif account in email_codes:
            c = email_codes[account]
            if c['code'] == code and (datetime.now() - c['time']) < timedelta(minutes=5):
                valid = True
        
        if not valid:
            return jsonify({'code': 403, 'message': '验证码错误或已过期'})
        
        is_phone = re.match(r'^1[3-9]\d{9}$', account)
        query_field = 'phone' if is_phone else 'email'
        user = db.users.find_one({query_field: account})
        
        if not user:
            return jsonify({'code': 404, 'message': '该账号未注册，请先注册'})
        
        sms_codes.pop(account, None)
        email_codes.pop(account, None)
        
        user['_id'] = str(user['_id'])
        del user['password']
        return jsonify({'code': 200, 'message': '登录成功', 'data': user})
    
    elif method == 'wechat':
        openid = data.get('openid', '')
        if not openid:
            return jsonify({'code': 400, 'message': '微信授权失败'})
        
        user = db.users.find_one({'bind_wechat': openid})
        if not user:
            user = {
                'username': f'微信用户{openid[-4:]}',
                'password': '',
                'phone': '',
                'email': '',
                'bind_wechat': openid,
                'bind_qq': '',
                'created_at': datetime.now(),
                'avatar': ''
            }
            result = db.users.insert_one(user)
            user['_id'] = str(result.inserted_id)
        else:
            user['_id'] = str(user['_id'])
            del user['password']
        
        return jsonify({'code': 200, 'message': '微信登录成功', 'data': user})
    
    elif method == 'qq':
        qq_openid = data.get('qq_openid', '')
        if not qq_openid:
            return jsonify({'code': 400, 'message': 'QQ授权失败'})
        
        user = db.users.find_one({'bind_qq': qq_openid})
        if not user:
            user = {
                'username': f'QQ用户{qq_openid[-4:]}',
                'password': '',
                'phone': '',
                'email': '',
                'bind_wechat': '',
                'bind_qq': qq_openid,
                'created_at': datetime.now(),
                'avatar': ''
            }
            result = db.users.insert_one(user)
            user['_id'] = str(result.inserted_id)
        else:
            user['_id'] = str(user['_id'])
            del user['password']
        
        return jsonify({'code': 200, 'message': 'QQ登录成功', 'data': user})

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    data = request.json
    account = data.get('account', '').strip()
    code = data.get('code', '').strip()
    new_password = data.get('new_password', '')
    
    if not account or not code or not new_password:
        return jsonify({'code': 400, 'message': '参数不完整'})
    if len(new_password) < 6:
        return jsonify({'code': 400, 'message': '密码至少6位'})
    
    valid = False
    if account in sms_codes:
        c = sms_codes[account]
        if c['code'] == code and (datetime.now() - c['time']) < timedelta(minutes=5):
            valid = True
    elif account in email_codes:
        c = email_codes[account]
        if c['code'] == code and (datetime.now() - c['time']) < timedelta(minutes=5):
            valid = True
    
    if not valid:
        return jsonify({'code': 403, 'message': '验证码错误或已过期'})
    
    is_phone = re.match(r'^1[3-9]\d{9}$', account)
    query_field = 'phone' if is_phone else 'email'
    
    result = db.users.update_one(
        {query_field: account},
        {'$set': {'password': hash_password(new_password)}}
    )
    
    if result.modified_count == 0:
        return jsonify({'code': 404, 'message': '账号不存在'})
    
    sms_codes.pop(account, None)
    email_codes.pop(account, None)
    
    return jsonify({'code': 200, 'message': '密码重置成功'})

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5021)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=False)