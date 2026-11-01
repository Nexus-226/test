from flask import Flask, request, jsonify
import random
import json

app = Flask(__name__)

@app.route('/api/pick', methods=['POST'])
def pick():
    # 5. 非法 JSON 处理 (返回 400 + INVALID_JSON)
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
    # 2. count 为可选，默认值为 1
    count = data.get('count', 1)

    # 3. 参数校验统一返回 422 VALIDATION_ERROR
    def error_response(message, details=""):
        return jsonify({
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
                "details": details
            }
        }), 422

    # 6. 字符串类型的 count 处理
    if not isinstance(count, int) or isinstance(count, bool):
        return error_response("count must be an integer", f"Got type: {type(count).__name__}")

    if not candidates or not isinstance(candidates, list):
        return error_response("candidates must be a non-empty array", "Missing or invalid candidates")

    if len(candidates) == 0:
        return error_response("candidates list cannot be empty")

    # 检查重复 ID (兼容对象和字符串)
    ids = []
    for c in candidates:
        if isinstance(c, dict) and 'id' in c:
            ids.append(str(c['id']))
        else:
            ids.append(str(c))

    if len(ids) != len(set(ids)):
        return error_response("Duplicate IDs found in candidates")

    if count <= 0 or count > len(candidates):
        return error_response(f"count must be between 1 and {len(candidates)}", f"Got count: {count}")

    # 随机抽取
    winners = random.sample(candidates, count)

    # 1. 成功响应返回 picked + candidate_count
    return jsonify({
        "picked": winners,
        "candidate_count": len(candidates)
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)