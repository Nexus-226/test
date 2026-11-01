from flask import Flask, request, jsonify, send_from_directory
import random
import os

# 配置 Flask 去 frontend 文件夹找静态文件
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# 解决第 2 点：添加根路由，返回前端页面
@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except FileNotFoundError:
        return "前端页面 index.html 还没做好，请稍后再试。", 404

@app.route('/api/pick', methods=['POST'])
def pick():
    if not request.is_json:
        return jsonify({
            "error": {
                "code": "INVALID_JSON",
                "message": "Request must be JSON",
                "details": "Content-Type must be application/json"
            }
        }), 400
    
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "error": {
                "code": "INVALID_JSON",
                "message": "Malformed JSON",
                "details": "Could not parse JSON body"
            }
        }), 400

    candidates = data.get('candidates')
    count = data.get('count', 1)

    def error_response(message, details=""):
        return jsonify({
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
                "details": details
            }
        }), 422

    if not isinstance(count, int) or isinstance(count, bool):
        return error_response("count must be an integer", f"Got type: {type(count).__name__}")

    if not candidates or not isinstance(candidates, list):
        return error_response("candidates must be a non-empty array", "Missing or invalid candidates")

    if len(candidates) == 0:
        return error_response("candidates list cannot be empty")

    # 解决第 3 点：严格的字段类型和长度校验
    ids = []
    for i, c in enumerate(candidates):
        if not isinstance(c, dict):
            return error_response(f"candidate at index {i} must be an object", "Not a JSON object")
        
        # 校验 id
        if 'id' not in c or not isinstance(c['id'], str):
            return error_response(f"candidate at index {i} missing string 'id'")
        
        clean_id = c['id'].strip()
        if not (1 <= len(clean_id) <= 64):
            return error_response(f"candidate id at index {i} length must be 1-64")
        
        # 校验 name
        if 'name' not in c or not isinstance(c['name'], str):
            return error_response(f"candidate at index {i} missing string 'name'")
            
        if not (1 <= len(c['name']) <= 50):
            return error_response(f"candidate name at index {i} length must be 1-50")

        ids.append(clean_id)

    # 检查重复
    if len(ids) != len(set(ids)):
        return error_response("Duplicate IDs found in candidates")

    if count <= 0 or count > len(candidates):
        return error_response(f"count must be between 1 and {len(candidates)}", f"Got count: {count}")

    winners = random.sample(candidates, count)

    return jsonify({
        "picked": winners,
        "candidate_count": len(candidates)
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)