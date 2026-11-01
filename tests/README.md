# 测试与联调步骤

本目录的测试以 `docs/API.md` 为准，使用 pytest 和 Flask 测试客户端。测试不固定随机抽中的姓名，而是检查抽取数量、候选人来源和单次结果不重复。

## 自动测试

先确保后端成员的实现已经出现在当前分支，并且存在 `backend/app.py` 和根目录的 `requirements.txt`。在仓库根目录运行：

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest -v
```

测试覆盖：

- 指定抽取人数和默认抽取 1 人。
- 同名、不同 ID 的候选人可以同时存在。
- 未定义的额外字段会被忽略。
- 候选人缺失、类型错误、空数组和超过 100 人。
- ID 或姓名缺失、空白、超长，以及重复 ID。
- `count` 为 0、超过候选人数或使用错误类型。
- 非法 JSON 返回 `400 INVALID_JSON`。
- 校验问题返回 `422 VALIDATION_ERROR`，所有响应均为 JSON。

## 手动接口检查

启动服务：

```bash
python -m flask --app backend.app run --debug
```

终端默认会显示类似 `http://127.0.0.1:5000` 的地址。另开一个 PowerShell 窗口，在仓库根目录执行下面的命令。

正常抽取应返回 `200`，`picked` 中有 1 人，`candidate_count` 为 2：

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/pick -H "Content-Type: application/json" --data-raw '{"candidates":[{"id":"student-001","name":"Ada"},{"id":"student-002","name":"Grace"}],"count":1}'
```

空名单应返回 `422` 和 `VALIDATION_ERROR`：

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/pick -H "Content-Type: application/json" --data-raw '{"candidates":[]}'
```

非法 JSON 应返回 `400` 和 `INVALID_JSON`：

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/pick -H "Content-Type: application/json" --data-raw '{'
```

## 浏览器联调

1. 保持 Flask 正在运行，打开终端显示的本地地址。
2. 输入至少 3 个虚构姓名，选择抽取 2 人并点击抽取。
3. 确认页面显示 2 名名单中的候选人，同一次结果没有重复。
4. 清空名单后再次抽取，确认页面显示能看懂的错误提示。
5. 打开浏览器开发者工具的 Network 面板，确认页面请求的是相对路径 `/api/pick`，成功请求为 `200`，输入错误为 `422`。
6. 刷新页面并再次抽取，确认应用不依赖上一次请求保存的服务端状态。
