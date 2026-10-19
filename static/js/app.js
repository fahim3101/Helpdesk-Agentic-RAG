/* ==========================================================================
   Enterprise IT Support Agentic RAG Copilot — front-end logic
   Pipeline state machine + markdown rendering + citation cards
   ========================================================================== */

const chat        = document.getElementById('chat');
const form        = document.getElementById('chatForm');
const question    = document.getElementById('question');
const sendBtn     = document.getElementById('sendBtn');
const traceEl     = document.getElementById('trace');
const sourceUsed  = document.getElementById('sourceUsed');
const sourceCard  = document.getElementById('sourceCard');
const sourceHint  = document.getElementById('sourceHint');
const topSource   = document.getElementById('topSource');
const pipelineEl  = document.getElementById('pipeline');
const pipelineState = document.getElementById('pipelineState');
const healthDot   = document.getElementById('healthDot');
const inspector   = document.getElementById('inspector');

/* ---------- pipeline definition ----------------------------------------- */

const STEP_ORDER = ['route', 'retrieve', 'grade', 'web', 'rewrite', 'generate'];

const STEP_RULES = [
  { key: 'route',    re: /^Router\b/i,                         cls: '' },
  { key: 'retrieve', re: /Private KB retrieval/i,               cls: '' },
  { key: 'grade',    re: /evidence grade/i,                     cls: '' },
  { key: 'web',      re: /Web fallback/i,                       cls: 'web' },
  { key: 'rewrite',  re: /Query rewrite/i,                      cls: 'warn' },
  { key: 'generate', re: /Answer generation|Direct response|Stopped/i, cls: '' },
];

const SOURCE_META = {
  private_kb:           { label: 'Private KB',          chip: 'chip-accent',  hint: 'Answered from the company knowledge base only. No public web call was made.' },
  web_search:           { label: 'Web Search',          chip: 'chip-blue',    hint: 'Private evidence was weak, so the answer was grounded in external web results. Validate before changing company systems.' },
  web:                  { label: 'Web Search',          chip: 'chip-blue',    hint: 'Answered from external web results. Validate before changing company systems.' },
  direct:               { label: 'Direct',              chip: 'chip-neutral', hint: 'Casual message — no retrieval was needed.' },
  insufficient_evidence:{ label: 'Insufficient',        chip: 'chip-danger',  hint: 'No reliable evidence was found in the knowledge base or on the web.' },
};

const nodes = {};
pipelineEl.querySelectorAll('.node').forEach(n => { nodes[n.dataset.step] = n; });

/* ---------- helpers ----------------------------------------------------- */

function asText(s) {
  if (typeof s === 'string') return s;
  if (Array.isArray(s)) return s.map(asText).join('');
  if (s && typeof s === 'object') {
    if (typeof s.text === 'string') return s.text;
    if (typeof s.content === 'string') return s.content;
    return '';
  }
  return s == null ? '' : String(s);
}

function escapeHtml(s) {
  return asText(s).replace(/[&<>'"]/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[c]));
}

function baseName(p) { return asText(p).split(/[\\/]/).pop(); }

/* ---------- minimal markdown (escaped first, so XSS-safe) --------------- */

function inlineMd(s) {
  return s
    .replace(/`([^`]+)`/g, '<code class="md-code">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
}

function mdToHtml(src) {
  const lines = escapeHtml(src).split(/\r?\n/);
  let html = '', listType = null, inCode = false, codeBuf = [];

  const closeList = () => { if (listType) { html += `</${listType}>`; listType = null; } };

  for (const raw of lines) {
    if (/^```/.test(raw.trim())) {
      if (inCode) {
        html += `<pre class="md-pre"><code>${codeBuf.join('\n')}</code></pre>`;
        codeBuf = []; inCode = false;
      } else {
        closeList(); inCode = true;
      }
      continue;
    }
    if (inCode) { codeBuf.push(raw); continue; }

    const line = raw.trim();

    if (/^[-*]\s+/.test(line)) {
      if (listType !== 'ul') { closeList(); html += '<ul class="md-list">'; listType = 'ul'; }
      html += `<li>${inlineMd(line.replace(/^[-*]\s+/, ''))}</li>`;
      continue;
    }
    if (/^\d+\.\s+/.test(line)) {
      if (listType !== 'ol') { closeList(); html += '<ol class="md-list">'; listType = 'ol'; }
      html += `<li>${inlineMd(line.replace(/^\d+\.\s+/, ''))}</li>`;
      continue;
    }

    closeList();
    if (!line) continue;

    const h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      const lvl = Math.min(Math.max(h[1].length + 1, 3), 5);
      html += `<h${lvl}>${inlineMd(h[2])}</h${lvl}>`;
      continue;
    }
    html += `<p>${inlineMd(line)}</p>`;
  }

  if (inCode && codeBuf.length) html += `<pre class="md-pre"><code>${codeBuf.join('\n')}</code></pre>`;
  closeList();
  return html || '<p></p>';
}

/* ---------- chat rendering ---------------------------------------------- */

function citationsHtml(citations) {
  if (!citations || !citations.length) return '';
  const rows = citations.map(c => {
    const kind = c.type === 'web' ? 'web' : 'kb';
    const kindLabel = kind === 'web' ? 'Web' : 'KB';
    const name = baseName(c.title || c.url || 'source');
    const inner = `<span class="cite-kind ${kind}">${kindLabel}</span><span class="cite-name">${escapeHtml(name)}</span>`;
    return c.url
      ? `<a class="cite" href="${escapeHtml(c.url)}" target="_blank" rel="noopener noreferrer">${inner}</a>`
      : `<div class="cite">${inner}</div>`;
  }).join('');
  return `<div class="citations"><span class="citations-label">Sources</span>${rows}</div>`;
}

function addMessage(role, html, source, citations) {
  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? 'You' : 'AI';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = html;

  if (source) {
    const tag = document.createElement('div');
    tag.className = 'answer-source';
    tag.textContent = `Source: ${SOURCE_META[source] ? SOURCE_META[source].label : source}`;
    bubble.appendChild(tag);
  }

  if (citations && citations.length) {
    const c = document.createElement('div');
    c.innerHTML = citationsHtml(citations);
    bubble.appendChild(c.firstElementChild);
  }

  if (role === 'assistant') {
    const actions = document.createElement('div');
    actions.className = 'bubble-actions';

    const copy = document.createElement('button');
    copy.className = 'icon-btn';
    copy.type = 'button';
    copy.textContent = 'Copy answer';
    copy.addEventListener('click', () => {
      const text = bubble.querySelector('.bubble-body');
      navigator.clipboard.writeText(text ? text.innerText : bubble.innerText).then(() => {
        copy.textContent = 'Copied';
        copy.classList.add('ok');
        setTimeout(() => { copy.textContent = 'Copy answer'; copy.classList.remove('ok'); }, 1600);
      }).catch(() => { copy.textContent = 'Copy failed'; });
    });

    actions.appendChild(copy);
    bubble.appendChild(actions);
  }

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap;
}

function addTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'message assistant';
  wrap.id = 'typingRow';
  wrap.innerHTML =
    '<div class="avatar">AI</div>' +
    '<div class="bubble"><div class="typing"><i></i><i></i><i></i></div></div>';
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap;
}

/* ---------- pipeline state --------------------------------------------- */

function setNode(key, state, detail) {
  const node = nodes[key];
  if (!node) return;
  node.classList.remove('active', 'done', 'skip', 'fail');
  if (state) node.classList.add(state);

  const stateEl = node.querySelector('.node-state');
  const label = { active: 'running', done: 'done', skip: 'skipped', fail: 'stopped' }[state] || 'idle';
  stateEl.textContent = label;

  if (detail !== undefined) {
    const d = node.querySelector('.node-detail');
    d.textContent = detail;
    d.classList.toggle('trace-hit', !!detail);
  }
}

function resetPipeline() {
  STEP_ORDER.forEach(k => {
    const node = nodes[k];
    if (!node) return;
    node.classList.remove('active', 'done', 'skip', 'fail');
    node.querySelector('.node-state').textContent = 'idle';
    const d = node.querySelector('.node-detail');
    d.classList.remove('trace-hit');
  });
  pipelineState.textContent = 'idle';
  pipelineState.className = 'chip chip-neutral';
}

function applyTrace(items) {
  resetPipeline();
  let lastIdx = -1;

  items.forEach(t => {
    const text = asText(t);
    const rule = STEP_RULES.find(r => r.re.test(text));
    if (!rule) return;

    const idx = STEP_ORDER.indexOf(rule.key);
    if (idx <= lastIdx) return;

    for (let i = lastIdx + 1; i < idx; i++) setNode(STEP_ORDER[i], 'skip');
    lastIdx = idx;

    setNode(rule.key, 'done', text);

    // routing to a direct reply bypasses retrieval entirely
    if (rule.key === 'route' && /DIRECT/i.test(text)) {
      ['retrieve', 'grade', 'web', 'rewrite'].forEach(k => setNode(k, 'skip'));
      setNode('generate', 'active');
      pipelineState.textContent = 'routing';
      pipelineState.className = 'chip chip-neutral';
      return;
    }

    const next = STEP_ORDER[idx + 1];
    if (next) {
      setNode(next, 'active');
      pipelineState.textContent = 'running';
      pipelineState.className = 'chip chip-accent';
    }
  });
}

function renderTrace(items) {
  if (!items || !items.length) {
    traceEl.innerHTML = '<div class="empty">No request yet.</div>';
    return;
  }
  traceEl.innerHTML = items.map(x => {
    const text = asText(x);
    const cls = /Web fallback/i.test(text) ? 'trace-item web'
              : /Query rewrite|Stopped/i.test(text) ? 'trace-item warn'
              : 'trace-item';
    return `<div class="${cls}">${escapeHtml(text)}</div>`;
  }).join('');
}

function setSource(source) {
  const meta = SOURCE_META[source];
  sourceUsed.textContent = meta ? meta.label : (source || '—');
  sourceHint.textContent = meta ? meta.hint : 'Ask a question to see which knowledge source answered it.';
  sourceCard.className = 'source-card' + (source ? ` s-${source}` : '');
  topSource.textContent = meta ? meta.label : (source || 'idle');
  topSource.className = 'chip ' + (meta ? meta.chip : 'chip-neutral');
}

/* ---------- request flow ------------------------------------------------ */

let busy = false;

async function askAgent(q) {
  if (busy) return;
  busy = true;
  sendBtn.disabled = true;

  addMessage('user', `<div class="bubble-body"><p>${escapeHtml(q)}</p></div>`, '', []);
  question.value = '';
  autoGrow();

  resetPipeline();
  renderTrace(['Running LangGraph workflow…']);
  setSource('');
  pipelineState.textContent = 'running';
  pipelineState.className = 'chip chip-accent';
  setNode('route', 'active');
  topSource.textContent = 'running';
  topSource.className = 'chip chip-accent';

  const typing = addTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');

    typing.remove();

    const trace = data.trace || [];
    renderTrace(trace);
    applyTrace(trace);

    // everything the agent planned is finished
    STEP_ORDER.forEach(k => {
      const node = nodes[k];
      if (node && !node.classList.contains('skip')) {
        node.classList.remove('active');
        if (!node.classList.contains('done')) node.classList.add('done');
        node.querySelector('.node-state').textContent = 'done';
      }
    });

    const source = data.source_used || '';
    setSource(source);

    if (source === 'insufficient_evidence') {
      setNode('generate', 'fail', 'Stopped → insufficient reliable evidence');
    }

    pipelineState.textContent = 'complete';
    pipelineState.className = 'chip ' + (SOURCE_META[source] ? SOURCE_META[source].chip : 'chip-neutral');

    const body = document.createElement('div');
    body.className = 'bubble-body';
    body.innerHTML = mdToHtml(data.answer || '');
    addMessage('assistant', body.innerHTML, source, data.citations || []);

  } catch (e) {
    typing.remove();
    renderTrace(['Request failed']);
    pipelineState.textContent = 'error';
    pipelineState.className = 'chip chip-danger';
    setNode('generate', 'fail', asText(e.message));
    addMessage('assistant', `<div class="bubble-body"><p>Error: ${escapeHtml(e.message)}</p></div>`, '', []);
  } finally {
    busy = false;
    sendBtn.disabled = false;
    question.focus();
  }
}

/* ---------- composer ---------------------------------------------------- */

function autoGrow() {
  question.style.height = 'auto';
  question.style.height = Math.min(question.scrollHeight, 190) + 'px';
}

question.addEventListener('input', autoGrow);

question.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

form.addEventListener('submit', e => {
  e.preventDefault();
  const q = question.value.trim();
  if (q) askAgent(q);
});

document.querySelectorAll('.example').forEach(b => {
  b.addEventListener('click', () => {
    const q = b.textContent.trim();
    if (q) askAgent(q);
  });
});

/* ---------- upload modal ----------------------------------------------- */

const modal = document.getElementById('uploadModal');
document.getElementById('openUpload').onclick = () => modal.classList.remove('hidden');
document.getElementById('closeUpload').onclick = () => modal.classList.add('hidden');
modal.addEventListener('click', e => { if (e.target === modal) modal.classList.add('hidden'); });

document.getElementById('uploadBtn').onclick = async () => {
  const file = document.getElementById('fileInput').files[0];
  const key = document.getElementById('adminKey').value;
  const status = document.getElementById('uploadStatus');
  status.className = 'upload-status';

  if (!file) { status.textContent = 'Choose a file first.'; status.className = 'upload-status err'; return; }
  if (!key) { status.textContent = 'Admin API key is required.'; status.className = 'upload-status err'; return; }

  status.textContent = 'Indexing document…';
  const fd = new FormData();
  fd.append('file', file);

  try {
    const r = await fetch('/api/ingest', {
      method: 'POST',
      headers: { 'X-Admin-Key': key },
      body: fd
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || 'Upload failed');
    status.textContent = `Indexed ${d.file} — ${d.chunks} chunks added. It is searchable now.`;
    status.className = 'upload-status ok';
    document.getElementById('fileInput').value = '';
  } catch (e) {
    status.textContent = `Error: ${asText(e.message)}`;
    status.className = 'upload-status err';
  }
};

/* ---------- mobile pipeline drawer -------------------------------------- */

const pipelineBtn = document.getElementById('openPipelineMobile');
if (pipelineBtn) pipelineBtn.onclick = () => inspector.classList.toggle('open');

/* ---------- health ----------------------------------------------------- */

fetch('/api/health')
  .then(r => r.json())
  .then(() => { healthDot.classList.remove('down'); })
  .catch(() => { healthDot.classList.add('down'); });

autoGrow();
