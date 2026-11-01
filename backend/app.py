from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/api/pick', methods=['POST'])
def pick():
    data = request.get_json()
    
    if not data or 'candidates' not in data or 'count' not in data:
        return jsonify({"error": "参数错误，需要提供 candidates 和 count"}), 400

    candidates = data['candidates']
    count = data['count']

    if not candidates or len(candidates) == 0:
        return jsonify({"error": "名单不能为空"}), 400

    ids = []
    for c in candidates:
        if isinstance(c, dict) and 'id' in c:
            ids.append(c['id'])
        else:
            ids.append(str(c))

    if len(ids) != len(set(ids)):
        return jsonify({"error": "名单中有重复的 ID"}), 400

    if count <= 0 or count > len(candidates):
        return jsonify({"error": "抽取人数超出名单范围或小于等于 0"}), 400

    winners = random.sample(candidates, count)

    return jsonify({
        "winners": winners
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)