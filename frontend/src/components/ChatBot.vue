<script setup>
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { CHAT_STREAM_URL } from '../api.js'

const STORAGE_KEY = 'ranking_chatbot_history_v1'
const MAX_HISTORY = 30

const open = ref(false)
const input = ref('')
const sending = ref(false)
const messages = ref([])
const listRef = ref(null)
const abortCtrl = ref(null)

// === 加载历史 ===
onMounted(() => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) messages.value = parsed
    }
  } catch (_) {}
  if (messages.value.length === 0) {
    messages.value.push({
      role: 'assistant',
      content:
        '你好，我是 **短剧小助手** 🎬\n你可以问我：\n- 哪个 APP 投放素材最多？\n- 美国市场有哪些产品？\n- 昆仑万维旗下有几款产品？'
    })
  }
})

watch(
  messages,
  (val) => {
    try {
      // 只持久化最近 N 条，避免越来越大
      const trimmed = val.slice(-MAX_HISTORY)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
    } catch (_) {}
  },
  { deep: true }
)

watch(open, (v) => {
  if (v) nextTick(scrollBottom)
})

function scrollBottom() {
  const el = listRef.value
  if (el) el.scrollTop = el.scrollHeight
}

// === 极简 Markdown 渲染 ===
function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function renderMarkdown(text) {
  if (!text) return ''
  let html = escapeHtml(text)
  // 代码块 ```xxx```
  html = html.replace(/```([\s\S]*?)```/g, (_, c) => `<pre><code>${c}</code></pre>`)
  // 行内代码 `xxx`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  // **加粗**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
  // 列表 - xxx
  html = html.replace(/(^|\n)- (.+)/g, '$1<li>$2</li>')
  html = html.replace(/(<li>[\s\S]*?<\/li>)(?!\s*<li>)/g, '<ul>$1</ul>')
  // 换行
  html = html.replace(/\n/g, '<br/>')
  return html
}

// === 发送消息（SSE 流式接收）===
async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return

  messages.value.push({ role: 'user', content: text })
  messages.value.push({ role: 'assistant', content: '' })
  input.value = ''
  sending.value = true
  await nextTick(scrollBottom)

  // 取最近 N 条作为上下文
  const history = messages.value
    .filter((m) => m.content || m.role === 'user')
    .slice(-12)
    .map(({ role, content }) => ({ role, content }))
  // 丢掉最后一条空 assistant
  if (history.length && history[history.length - 1].role === 'assistant' && !history[history.length - 1].content) {
    history.pop()
  }

  const ctrl = new AbortController()
  abortCtrl.value = ctrl

  try {
    const resp = await fetch(CHAT_STREAM_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history }),
      signal: ctrl.signal
    })
    if (!resp.ok || !resp.body) {
      throw new Error(`HTTP ${resp.status}`)
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // 按 SSE 事件分隔（双换行）
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const ev of events) {
        const line = ev.trim()
        if (!line.startsWith('data:')) continue
        const data = line.slice(5).trim()
        if (data === '[DONE]') {
          break
        }
        try {
          const obj = JSON.parse(data)
          if (obj.type === 'delta' && obj.content) {
            const last = messages.value[messages.value.length - 1]
            last.content += obj.content
            scrollBottom()
          } else if (obj.type === 'error') {
            const last = messages.value[messages.value.length - 1]
            last.content += `\n\n⚠️ ${obj.error}`
          }
        } catch (_) {
          // 忽略非 JSON 行
        }
      }
    }
  } catch (e) {
    const last = messages.value[messages.value.length - 1]
    if (e.name === 'AbortError') {
      last.content += '\n\n_(已中断)_'
    } else {
      last.content = `❌ 请求失败：${e.message}\n请确认后端 8001 已启动且 .env 中配置了 VOLCANO_API_KEY`
    }
  } finally {
    sending.value = false
    abortCtrl.value = null
    nextTick(scrollBottom)
  }
}

function stop() {
  if (abortCtrl.value) abortCtrl.value.abort()
}

function clearHistory() {
  if (!confirm('确定清空聊天记录吗？')) return
  messages.value = []
  localStorage.removeItem(STORAGE_KEY)
  messages.value.push({
    role: 'assistant',
    content: '已清空，我们重新开始聊吧 ✨'
  })
}

function onEnter(e) {
  if (e.shiftKey) return
  e.preventDefault()
  send()
}

const visibleMessages = computed(() =>
  messages.value.map((m, i) => ({ ...m, _i: i, _html: renderMarkdown(m.content) }))
)
</script>

<template>
  <!-- 浮动按钮 -->
  <button
    class="fab"
    :class="{ active: open }"
    @click="open = !open"
    :title="open ? '收起' : '咨询短剧小助手'"
  >
    <svg v-if="!open" width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 2C6.48 2 2 6.04 2 11c0 2.52 1.21 4.79 3.16 6.39-.13.99-.5 2.4-1.27 3.42-.18.24.04.58.32.49 1.96-.66 3.46-1.74 4.32-2.45.78.13 1.59.2 2.47.2 5.52 0 10-4.04 10-9S17.52 2 12 2z"
        fill="white"
      />
      <circle cx="8.5" cy="11" r="1.3" fill="#ff5677" />
      <circle cx="12" cy="11" r="1.3" fill="#ff5677" />
      <circle cx="15.5" cy="11" r="1.3" fill="#ff5677" />
    </svg>
    <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="white">
      <path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
    </svg>
  </button>

  <!-- 聊天面板 -->
  <transition name="pop">
    <div v-if="open" class="panel">
      <header class="panel-head">
        <div class="avatar">🎬</div>
        <div class="title-block">
          <div class="title">短剧小助手</div>
          <div class="subtitle">基于 DataEye 海外榜单 · 豆包驱动</div>
        </div>
        <button class="icon-btn" title="清空" @click="clearHistory">🗑</button>
        <button class="icon-btn close-btn" title="关闭" @click="open = false">✕</button>
      </header>

      <div ref="listRef" class="msg-list">
        <div
          v-for="m in visibleMessages"
          :key="m._i"
          class="msg-row"
          :class="m.role"
        >
          <div class="bubble" v-html="m._html || '<span class=\'cursor\'>▍</span>'"></div>
        </div>
      </div>

      <div class="input-area">
        <textarea
          v-model="input"
          rows="1"
          :disabled="sending"
          placeholder="问问榜单数据，例如：投放最多的是哪个 APP？"
          @keydown.enter="onEnter"
        />
        <button v-if="!sending" class="send" :disabled="!input.trim()" @click="send">发送</button>
        <button v-else class="send stop" @click="stop">停止</button>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #ff5677, #ff9f7a);
  color: #fff;
  box-shadow: 0 12px 30px rgba(255, 86, 119, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 999;
  transition: transform 0.2s, box-shadow 0.2s;
}
.fab:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 16px 36px rgba(255, 86, 119, 0.5);
}
.fab.active {
  background: linear-gradient(135deg, #888, #555);
}

.panel {
  position: fixed;
  right: 28px;
  bottom: 100px;
  width: 380px;
  height: 540px;
  max-height: calc(100vh - 140px);
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(255, 86, 119, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 999;
}

.pop-enter-active,
.pop-leave-active {
  transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform-origin: bottom right;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.92);
}

.panel-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #ff7a8b 0%, #ff9f7a 100%);
  color: #fff;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.title-block {
  flex: 1;
  line-height: 1.2;
}
.title {
  font-weight: 700;
  font-size: 15px;
}
.subtitle {
  font-size: 11px;
  opacity: 0.85;
}
.icon-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.35);
}

.close-btn {
  margin-left: 4px;
  display: none;
}

.close-btn {
  margin-left: 4px;
  display: none;
}

.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: linear-gradient(180deg, #fff8f6 0%, #fff 100%);
}
.msg-row {
  display: flex;
  margin-bottom: 12px;
}
.msg-row.user {
  justify-content: flex-end;
}
.msg-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.6;
  word-break: break-word;
}
.msg-row.user .bubble {
  background: linear-gradient(135deg, #ff7a8b, #ff9f7a);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-row.assistant .bubble {
  background: #fff0f0;
  color: #2d1b22;
  border-bottom-left-radius: 4px;
}
.bubble :deep(b) {
  color: #d23a55;
}
.bubble :deep(ul) {
  margin: 6px 0;
  padding-left: 20px;
}
.bubble :deep(li) {
  margin: 2px 0;
}
.bubble :deep(code) {
  background: rgba(255, 86, 119, 0.12);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12.5px;
}
.bubble :deep(pre) {
  background: #2d1b22;
  color: #ffe1e6;
  padding: 10px 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 6px 0;
}
.bubble :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}
.cursor {
  display: inline-block;
  animation: blink 1s steps(2) infinite;
  color: #ff5677;
}
@keyframes blink {
  50% { opacity: 0; }
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid #ffe1e6;
  background: #fff;
}
textarea {
  flex: 1;
  resize: none;
  border: 1px solid #ffd0d0;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
  font-family: inherit;
  outline: none;
  max-height: 80px;
  line-height: 1.4;
}
textarea:focus {
  border-color: #ff7a8b;
}
.send {
  border: none;
  border-radius: 12px;
  padding: 0 16px;
  background: linear-gradient(135deg, #ff5677, #ff9f7a);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  flex-shrink: 0;
}
.send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.send.stop {
  background: linear-gradient(135deg, #888, #666);
}

@media (max-width: 640px) {
  .fab {
    right: 14px;
    bottom: calc(14px + env(safe-area-inset-bottom));
    width: 52px;
    height: 52px;
  }
  .fab svg {
    width: 24px;
    height: 24px;
  }

  .panel {
    right: 0;
    left: 0;
    bottom: 0;
    top: 0;
    width: 100%;
    height: 100%;
    max-height: 100%;
    border-radius: 0;
    padding-top: env(safe-area-inset-top);
    padding-bottom: env(safe-area-inset-bottom);
  }

  .close-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .pop-enter-from,
  .pop-leave-to {
    opacity: 0;
    transform: translateY(40px);
  }

  .panel-head {
    padding: 12px 14px;
  }
  .title {
    font-size: 16px;
  }
  .subtitle {
    font-size: 11px;
  }

  .bubble {
    max-width: 86%;
    font-size: 14px;
  }

  textarea {
    font-size: 16px; /* iOS 防止聚焦放大 */
    padding: 9px 12px;
  }

  .send {
    padding: 0 14px;
    font-size: 14px;
  }
}
</style>
