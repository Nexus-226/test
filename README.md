# test

随机点名器：三人 Git / PR 协作练习。

我们要做一个小网页：输入几个人的名字，点击按钮，随机选出一个或几个人。练习的重点是三个人各做一部分，再通过 PR 把成果放到一起。

> 项目使用 Flask 同时提供网页和 API。前端、后端和测试 PR 全部合并后，可按照本文“安装与启动”一节完成本地运行和验收。

## 先认识这几个地方

| 位置 | 放什么 | 主要负责人 |
| --- | --- | --- |
| `frontend/` | 用户看到的页面和按钮交互 | A |
| `backend/` | 接收名单、随机抽取、返回结果的服务 | B |
| `tests/` | 检查功能是否正确的测试 | C |
| [docs/API.md](docs/API.md) | 前端发什么、后端回什么的共同约定 | 三人一起确认 |
| [AGENTS.md](AGENTS.md) | 给编程助手看的协作规则 | 三人共同遵守 |

PR 可以理解成“请队友检查并接收我的修改”。分支是每个人自己的工作版本，`main` 是大家共享的版本。

## 技术栈要求

本项目统一使用下面这套技术栈。三个人按同一套约定开发，练习过程中不更换框架。

| 部分 | 必须使用 | 要求 |
| --- | --- | --- |
| 前端 | 原生 HTML + CSS + JavaScript | 不使用 React、Vue、Node.js、npm 或前端构建工具 |
| 后端 | Python 3.11 或更高版本 + Flask 3.x | 实现 `POST /api/pick`，并负责提供前端页面 |
| 测试 | pytest + Flask 测试客户端 | 测试接口校验、状态码和返回内容 |
| 数据存储 | 不使用数据库 | 名单随请求传入，不保存抽取历史 |

### 运行方式

Flask 必须同时提供页面和 API：

- 访问 `/` 时返回 `frontend/index.html`。
- 前端通过相对路径 `/api/pick` 请求接口。
- 页面和接口使用同一个本地地址，不额外配置跨域。
- 后端入口放在 `backend/app.py`。
- Python 依赖写入仓库根目录的 `requirements.txt`，至少包含 Flask 和 pytest。
- 业务代码分别放在 `frontend/` 和 `backend/`，测试放在 `tests/`。

项目支持下面的基本操作：

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m flask --app backend.app run --debug
python -m pytest
```

启动 Flask 后，终端会显示本地访问地址。三个人都通过这个地址打开页面，不单独启动前端服务。

## 开始前：三个人都要做

1. 仓库负责人给另外两个人添加协作者权限，对方接受邀请。下面的操作按三人都有仓库写入权限来写。
2. 先在 GitHub 合并本次文档 PR，大家再获取代码，确保都能看到这份说明和 `AGENTS.md`。
3. 每个人在自己的电脑上打开终端，第一次下载仓库：

```bash
git clone https://github.com/Nexus-226/test.git
cd test
```

已经下载过的人，在仓库目录中执行：

```bash
git status
git switch main
git pull --ff-only origin main
```

如果 `git status` 显示有未提交的修改，先保存或提交自己的工作，再切换分支；不要直接删除修改。

4. 一起读 [API 约定](docs/API.md) 和上方的“技术栈要求”，确认三个人都安装了 Python 3.11 或更高版本，并按统一的运行方式开发。
5. A、B、C 各建自己的分支，然后开始各自的任务。分支名见下面各人的步骤。

## A：负责页面

1. 创建自己的分支：

```bash
git switch -c feat/picker-ui
```

2. 主要修改 `frontend/`，做出输入名单、选择抽取人数、点击抽取、展示结果这几个操作。
3. 每个人需要一个唯一的 ID；名字可以相同。按 `docs/API.md` 组织请求，不要只发送名字数组。
4. 后端还没做好时，可以先用符合 API 约定的假数据做页面。真正联调时再接上 `POST /api/pick`。
5. 自己检查：空名单有没有提示、等待结果时按钮状态是否合理、请求出错时用户能不能看懂。
6. 按下方“提交 PR”操作提交页面，让 C 审查。告诉 B 和 C 页面怎么启动，以及要连接的后端地址。

给编程助手的任务可以这样说：

> 阅读 AGENTS.md 和 docs/API.md。我负责前端，请在 frontend/ 中实现随机点名页面，遵守接口约定。完成后说明启动方式和验证结果，先不要提交或推送。

## B：负责抽取接口

1. 创建自己的分支：

```bash
git switch -c feat/pick-api
```

2. 主要修改 `backend/`，实现 `POST /api/pick`。
3. 按 `docs/API.md` 检查输入，再返回抽取结果。同一次抽取不能重复选到同一个 ID。
4. 自己检查：正常名单能返回结果，空名单、重复 ID 和不合理的抽取人数会返回约定的错误。
5. 按下方“提交 PR”操作提交接口，让 A 审查。告诉 A 和 C 后端怎么启动、监听哪个地址。
6. 配置 Flask 同时提供 `frontend/index.html` 和 API，确保前端可以通过相对路径 `/api/pick` 请求接口。

给编程助手的任务可以这样说：

> 阅读 AGENTS.md 和 docs/API.md。我负责后端，请在 backend/ 中实现 POST /api/pick，包含参数校验和约定的错误响应。完成后说明启动方式和验证结果，先不要提交或推送。

## C：负责测试和最后拼起来

1. 创建自己的分支：

```bash
git switch -c test/pick-contract
```

2. 先读 API 文档，列出要检查的情况：正常抽取、只提供一个候选人、空名单、重复 ID、数量超出名单人数、格式错误。
3. 在 `tests/` 中编写适合已选技术栈的测试。后端还没做好时，先准备测试用例和预期结果。
4. 抽取结果是随机的，检查“选了几人、是不是名单里的人、有没有重复”，不要要求每次都选中同一个名字。
5. 按下方“提交 PR”操作提交测试，让 B 审查。把测试运行方法补到本文件。
6. A、B 的 PR 合并后，同步最新代码，启动前后端，完成一次从输入名单到显示结果的操作。有问题就告诉对应成员，让对方修复后再提 PR。

给编程助手的任务可以这样说：

> 阅读 AGENTS.md 和 docs/API.md。我负责测试和联调，请根据接口约定在 tests/ 中补充测试，并整理可复现的检查步骤。完成后报告结果和问题，先不要提交或推送。

## 做完自己的部分：提交 PR

下面用 A 举例。B 把 `frontend/` 换成 `backend/`，分支换成 `feat/pick-api`；C 换成 `tests/` 和 `test/pick-contract`。

```bash
git status
git diff
git add frontend/
git diff --cached
git commit -m "feat: add picker UI"
git push -u origin feat/picker-ui
```

如果还改了运行说明等文件，检查后单独添加，例如 `git add README.md`。提交信息也改成自己实际完成的内容。

打开 GitHub 仓库，进入 **Pull requests → New pull request**，目标分支选 `main`，来源分支选自己的分支。写清楚：

- 我完成了什么。
- 队友怎样启动和检查。
- 我已经验证了什么，还有什么问题。

让队友查看改动并按步骤试一下。通过后，由有权限的成员点击 **Merge pull request** 合并。一次只合并一个 PR，合并后再检查下一个。

## 别人的 PR 合并后：同步代码

当前工作已经提交、工作区没有未提交修改时，在自己的功能分支执行：

```bash
git fetch origin
git merge origin/main
```

这样会把大家共享版本的新内容带入自己的分支。若提示冲突，先看清两个人分别改了什么，和队友确认后保留需要的内容，重新验证，再提交并推送。

自己的 PR 已合并、准备开始新任务时，回到 `main` 更新，再为新任务创建一个新分支。

## 最后一起验收

- 三个人都完成一次“分支 → 提交 → PR → 队友检查 → 合并”。
- 按本文件的说明，另一位成员能够安装并启动项目。
- 输入几个人，点击抽取，页面能显示结果。
- 输入不合理的数据，页面能给出提示。
- C 的测试可以运行，并说明了结果。

可以按约 30 分钟安排：前 5 分钟统一接口和工具，中间 15 分钟各自开发，最后 10 分钟审查 PR、合并和联调。先完成最小可用流程。

## 安装与启动

需要 Python 3.11 或更高版本。以下命令都在仓库根目录执行，不需要单独启动前端，也不需要 Node.js 或 npm。

### 1. 获取完整代码

前端、后端和测试 PR 全部合并后，切换并更新默认分支：

```bash
git switch main
git pull --ff-only origin main
```

确认仓库中至少存在 `frontend/index.html`、`backend/app.py`、`requirements.txt` 和 `tests/`。

### 2. 创建环境并安装依赖

Windows PowerShell：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS 或 Linux：

```bash
python3 --version
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

命令直接使用虚拟环境中的 Python，因此无需手动激活虚拟环境。

### 3. 启动网页和 API

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m flask --app backend.app run --debug
```

macOS 或 Linux：

```bash
./.venv/bin/python -m flask --app backend.app run --debug
```

看到 `Running on http://127.0.0.1:5000` 后，保持终端窗口运行，并在浏览器打开：

```text
http://127.0.0.1:5000/
```

页面通过同源相对路径 `POST /api/pick` 调用后端。正常联调时不要直接打开 `frontend/index.html`，也不要把 `USE_MOCK` 改为 `true`。在终端按 `Ctrl+C` 可停止服务。

### 4. 运行测试

测试使用 Flask 测试客户端，不需要先启动开发服务器。

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS 或 Linux：

```bash
./.venv/bin/python -m pytest
```

### 5. 手动验收

1. 输入多个人名，抽取 1 人，确认结果来自名单。
2. 抽取多人，确认人数正确且同一次结果没有重复 ID。
3. 检查空名单、抽取人数为 0、人数超过名单人数等错误提示。
4. 先触发错误，再改为合法输入并成功抽取，确认旧错误提示消失；反向操作时旧结果也应消失。

### 常见问题

- `No module named flask`：通常是安装依赖和启动服务时使用了不同的 Python；请直接使用上方 `.venv` 中的 Python 命令。
- `ERR_CONNECTION_REFUSED`：Flask 没有运行，或运行它的终端已经关闭。重新启动服务并保持终端开启。
- 首页显示 `Not Found`：确认当前分支包含 `frontend/index.html`，并从仓库根目录启动 Flask。
- 页面仍显示旧样式或旧脚本：先按 `Ctrl+F5` 强制刷新浏览器。
- 页面布局异常：使用浏览器无痕窗口复测；若无痕窗口正常，通常是浏览器扩展注入样式造成的冲突。
- 5000 端口被占用：启动时追加其他端口，例如 `--port 5001`，并打开对应地址。
