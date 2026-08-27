from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# MongoDB连接
client = MongoClient('mongodb://localhost:27017/')
db = client['omni_edu']

@app.route('/api/discussions', methods=['GET'])
def get_discussions():
    """获取所有帖子（分页）"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    skip = (page - 1) * limit
    
    try:
        posts = list(db.discussions.find(
            {'parent_id': None},
            sort=[('created_at', -1)],
            skip=skip,
            limit=limit
        ))
        
        total = db.discussions.count_documents({'parent_id': None})
        
        for post in posts:
            post['reply_count'] = db.discussions.count_documents({'parent_id': str(post['_id'])})
            post['_id'] = str(post['_id'])
            if 'created_at' in post and isinstance(post['created_at'], datetime):
                post['created_at'] = post['created_at'].isoformat()
        
        return jsonify({
            'code': 200,
            'data': {
                'posts': posts,
                'total': total,
                'page': page,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/discussions', methods=['POST'])
def create_post():
    """发帖"""
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username', '匿名用户')
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'})
    
    try:
        post = {
            'user_id': user_id,
            'username': username,
            'title': title,
            'content': content,
            'parent_id': None,
            'created_at': datetime.now(),
            'likes': 0,
            'views': 0
        }
        result = db.discussions.insert_one(post)
        post['_id'] = str(result.inserted_id)
        post['created_at'] = post['created_at'].isoformat()
        
        return jsonify({'code': 200, 'message': '发布成功', 'data': post})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/discussions/<post_id>', methods=['GET'])
def get_post_detail(post_id):
    """获取帖子详情及回复"""
    try:
        post = db.discussions.find_one({'_id': ObjectId(post_id)})
        if not post:
            return jsonify({'code': 404, 'message': '帖子不存在'})
        
        db.discussions.update_one({'_id': ObjectId(post_id)}, {'$inc': {'views': 1}})
        
        replies = list(db.discussions.find(
            {'parent_id': post_id},
            sort=[('created_at', 1)]
        ))
        
        post['_id'] = str(post['_id'])
        if 'created_at' in post and isinstance(post['created_at'], datetime):
            post['created_at'] = post['created_at'].isoformat()
        
        for reply in replies:
            reply['_id'] = str(reply['_id'])
            if 'created_at' in reply and isinstance(reply['created_at'], datetime):
                reply['created_at'] = reply['created_at'].isoformat()
        
        post['replies'] = replies
        
        return jsonify({'code': 200, 'data': post})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/discussions/<post_id>/reply', methods=['POST'])
def add_reply(post_id):
    """回复帖子"""
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username', '匿名用户')
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'code': 400, 'message': '回复内容不能为空'})
    
    try:
        parent = db.discussions.find_one({'_id': ObjectId(post_id)})
        if not parent:
            return jsonify({'code': 404, 'message': '原帖不存在'})
        
        reply = {
            'user_id': user_id,
            'username': username,
            'title': '',
            'content': content,
            'parent_id': post_id,
            'created_at': datetime.now(),
            'likes': 0,
            'views': 0
        }
        result = db.discussions.insert_one(reply)
        reply['_id'] = str(result.inserted_id)
        reply['created_at'] = reply['created_at'].isoformat()
        
        return jsonify({'code': 200, 'message': '回复成功', 'data': reply})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/discussions/<post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞"""
    try:
        result = db.discussions.update_one(
            {'_id': ObjectId(post_id)},
            {'$inc': {'likes': 1}}
        )
        if result.modified_count == 0:
            return jsonify({'code': 404, 'message': '帖子不存在'})

        post = db.discussions.find_one({'_id': ObjectId(post_id)})
        return jsonify({'code': 200, 'likes': post.get('likes', 0)})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/discussions/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """删除帖子（仅作者本人可删，连同回复一起删除）"""
    data = request.json or {}
    user_id = data.get('user_id')
    try:
        post = db.discussions.find_one({'_id': ObjectId(post_id)})
        if not post:
            return jsonify({'code': 404, 'message': '帖子不存在'})
        if not user_id or str(post.get('user_id') or '') != str(user_id):
            return jsonify({'code': 403, 'message': '只能删除自己的帖子'})
        db.discussions.delete_many({'$or': [{'_id': ObjectId(post_id)}, {'parent_id': post_id}]})
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5020)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=False)