// 默认请求真实后端 POST /api/pick。
// 仅本地开发、后端未启动时，可临时改为 true 用假数据调试。
const USE_MOCK = false;

const namesEl = document.getElementById('names');
const countEl = document.getElementById('count');
const pickBtn = document.getElementById('pick-btn');
const resultEl = document.getElementById('result');
const errorEl = document.getElementById('error');

pickBtn.addEventListener('click', onPick);

async function onPick() {
  hideResult();
  hideError();

  // 1. 读取并校验名单
  const names = parseNames(namesEl.value);
  if (names.length === 0) {
    showError('请先输入至少一个名字。');
    return;
  }

  // 2. 校验抽取人数
  const count = parseCount(countEl.value, names.length);
  if (count.error) {
    showError(count.error);
    return;
  }

  // 3. 构造符合契约的请求体：候选人是含唯一 id 的对象数组，不是纯名字数组
  const candidates = names.map((name, i) => ({
    id: `candidate-${i + 1}`,
    name,
  }));

  // 4. 请求期间锁定按钮
  setLoading(true);
  try {
    const data = await pick({ candidates, count: count.value });
    renderResult(data.picked, data.candidate_count);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

// 把多行文本解析成去重空格后的名字列表
function parseNames(text) {
  return text
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
}

// 解析并校验抽取人数：空值默认 1
function parseCount(raw, max) {
  const trimmed = String(raw).trim();
  if (trimmed === '') {
    return { value: 1 };
  }
  const n = Number(trimmed);
  if (!Number.isInteger(n)) {
    return { error: '抽取人数必须是整数。' };
  }
  if (n < 1) {
    return { error: '抽取人数至少为 1。' };
  }
  if (n > max) {
    return { error: `抽取人数不能超过名单人数（${max} 人）。` };
  }
  return { value: n };
}

// 发起抽取请求；出错时把后端错误结构里的 message 抛给上层展示
async function pick(body) {
  if (USE_MOCK) {
    return mockPick(body);
  }

  const res = await fetch('/api/pick', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const message = data?.error?.message || `请求失败（HTTP ${res.status}）`;
    throw new Error(message);
  }
  return data;
}

// 符合契约的假数据：随机选 count 个不重复的人，模拟网络延迟
function mockPick(body) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const shuffled = [...body.candidates].sort(() => Math.random() - 0.5);
      const picked = shuffled.slice(0, body.count);
      resolve({ picked, candidate_count: body.candidates.length });
    }, 400);
  });
}

function renderResult(picked, candidateCount) {
  const list = picked
    .map((p) => `<li>${escapeHtml(p.name)}</li>`)
    .join('');
  resultEl.innerHTML = `
    <h2>抽中 ${picked.length} / ${candidateCount} 人</h2>
    <ul>${list}</ul>
  `;
  resultEl.hidden = false;
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = false;
}

function hideResult() {
  resultEl.hidden = true;
}

function hideError() {
  errorEl.hidden = true;
}

function setLoading(loading) {
  pickBtn.disabled = loading;
  pickBtn.textContent = loading ? '抽取中…' : '抽取';
}

function escapeHtml(value) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };
  return String(value).replace(/[&<>"']/g, (c) => map[c]);
}
