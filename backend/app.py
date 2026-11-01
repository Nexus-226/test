import random

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest

# 配置 Flask 去 frontend 文件夹找静态文件
app = Flask(__name__, static_folder='../frontend', static_url_path='')

@app.errorhandler(500)
def internal_error(_error):
    return jsonify({
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "服务端发生错误"
        }
    }), 500

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
                "message": "请求体必须是合法 JSON",
                "details": [{"field": "body", "reason": "Content-Type 必须是 application/json"}]
            }
        }), 400

    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({
            "error": {
                "code": "INVALID_JSON",
                "message": "请求体必须是合法 JSON",
                "details": [{"field": "body", "reason": "无法解析 JSON 请求体"}]
            }
        }), 400

    def validation_error(field, reason):
        return jsonify({
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数不符合约定",
                "details": [{"field": field, "reason": reason}]
            }
        }), 422

    if not isinstance(data, dict):
        return validation_error("body", "必须是 JSON 对象")

    candidates = data.get('candidates')
    count = data.get('count', 1)

    if not isinstance(candidates, list):
        return validation_error("candidates", "必须是数组")
    if not 1 <= len(candidates) <= 100:
        return validation_error("candidates", "候选人数必须为 1～100")

    normalized_candidates = []
    seen_ids = set()
    for index, candidate in enumerate(candidates):
        field = f"candidates[{index}]"
        if not isinstance(candidate, dict):
            return validation_error(field, "必须是对象")

        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str):
            return validation_error(f"{field}.id", "必须是字符串")
        candidate_id = candidate_id.strip()
        if not 1 <= len(candidate_id) <= 64:
            return validation_error(f"{field}.id", "去除首尾空白后长度必须为 1～64")
        if candidate_id in seen_ids:
            return validation_error(f"{field}.id", "候选人 ID 不能重复")
        seen_ids.add(candidate_id)

        name = candidate.get("name")
        if not isinstance(name, str):
            return validation_error(f"{field}.name", "必须是字符串")
        name = name.strip()
        if not 1 <= len(name) <= 50:
            return validation_error(f"{field}.name", "去除首尾空白后长度必须为 1～50")

        normalized_candidates.append({"id": candidate_id, "name": name})

    if not isinstance(count, int) or isinstance(count, bool):
        return validation_error("count", "必须是整数")
    if not 1 <= count <= len(normalized_candidates):
        return validation_error("count", "必须在 1 到候选人数之间")

    winners = random.sample(normalized_candidates, count)

    return jsonify({
        "picked": winners,
        "candidate_count": len(normalized_candidates)
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)