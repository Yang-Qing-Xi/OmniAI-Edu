<template>
  <div class="agent-widget">
    <transition
      name="agent-panel"
      @before-leave="onPanelBeforeLeave"
      @after-leave="onPanelAfterLeave"
      @before-enter="onPanelBeforeEnter"
      @after-enter="onPanelAfterEnter"
    >
      <div v-if="isOpen" class="agent-panel">
        <div class="agent-header">
          <div class="agent-header-left">
            <div class="agent-header-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="20" height="20">
                <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 0 1 1h1a2 2 0 0 1 2 2v1H4v-1a2 2 0 0 1 2-2h1a1 1 0 0 0 1-1V6a4 4 0 0 1 4-4z"/>
                <path d="M5 11h14v8a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-8z"/>
              </svg>
            </div>
            <div class="agent-header-info">
              <span class="agent-title">师小助 AI</span>
              <span class="agent-status">在线 · AI助教</span>
            </div>
          </div>
          <div class="agent-header-actions">
            <button class="agent-header-btn" @click="clearHistory" title="清空对话">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z"/>
              </svg>
            </button>
            <button class="agent-header-btn" @click="togglePanel" title="最小化">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="agent-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="agent-welcome">
            <div class="agent-welcome-logo">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" width="40" height="40">
                <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 0 1 1h1a2 2 0 0 1 2 2v1H4v-1a2 2 0 0 1 2-2h1a1 1 0 0 0 1-1V6a4 4 0 0 1 4-4z"/>
                <path d="M8 14v2m4-2v2m4-2v2"/>
                <path d="M5 11h14v8a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-8z"/>
              </svg>
            </div>
            <p class="agent-welcome-title">你好！我是师小助 AI</p>
            <p class="agent-welcome-sub">AI知识问答 · 学习数据分析 · 个性化指导</p>
            <div class="agent-suggestions">
              <button v-for="s in suggestions" :key="s.text" class="agent-suggestion-btn" @click="sendSuggestion(s.text)">
                <span class="agent-suggestion-icon">{{ s.icon }}</span>
                {{ s.text }}
              </button>
            </div>
          </div>
          <div v-for="(msg, i) in messages" :key="i" :class="['agent-msg', `agent-msg-${msg.role}`]">
            <div v-if="msg.role === 'assistant'" class="agent-msg-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
                <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 0 1 1h1a2 2 0 0 1 2 2v1H4v-1a2 2 0 0 1 2-2h1a1 1 0 0 0 1-1V6a4 4 0 0 1 4-4z"/>
                <path d="M5 11h14v8a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-8z"/>
              </svg>
            </div>
            <div class="agent-msg-content">
              <div v-if="msg.role === 'assistant'" class="agent-msg-bubble agent-md" v-html="renderMarkdown(msg.content)"></div>
              <div v-else class="agent-msg-bubble">{{ msg.content }}</div>
            </div>
          </div>
          <div v-if="loading && !streamingContent" class="agent-msg agent-msg-assistant">
            <div class="agent-msg-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
                <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 0 1 1h1a2 2 0 0 1 2 2v1H4v-1a2 2 0 0 1 2-2h1a1 1 0 0 0 1-1V6a4 4 0 0 1 4-4z"/>
                <path d="M5 11h14v8a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-8z"/>
              </svg>
            </div>
            <div class="agent-msg-content">
              <div class="agent-msg-bubble agent-typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          <div v-if="loading && streamingContent" class="agent-msg agent-msg-assistant">
            <div class="agent-msg-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
                <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 0 1 1h1a2 2 0 0 1 2 2v1H4v-1a2 2 0 0 1 2-2h1a1 1 0 0 0 1-1V6a4 4 0 0 1 4-4z"/>
                <path d="M5 11h14v8a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-8z"/>
              </svg>
            </div>
            <div class="agent-msg-content">
              <div class="agent-msg-bubble agent-md agent-streaming" v-html="renderMarkdown(streamingContent)"></div>
            </div>
          </div>
          <div v-if="toolIndicator" class="agent-tool-indicator">
            <div class="agent-tool-spinner"></div>
            <span>{{ toolIndicator }}</span>
          </div>
        </div>
        <div class="agent-input-area">
          <textarea
            ref="inputRef"
            v-model="inputText"
            class="agent-input"
            placeholder="输入你的问题..."
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            @input="autoResize"
          ></textarea>
          <button class="agent-send-btn" :disabled="!inputText.trim() || loading" @click="sendMessage">
            <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </transition>
    <button class="agent-fab" :class="{ 'agent-fab-hidden': isOpen }" @click="togglePanel" title="AI助教">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="26" height="26">
        <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 0 1 1h1a2 2 0 0 1 2 2v1H4v-1a2 2 0 0 1 2-2h1a1 1 0 0 0 1-1V6a4 4 0 0 1 4-4z"/>
        <path d="M8 14v2m4-2v2m4-2v2"/>
        <path d="M5 11h14v8a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-8z"/>
      </svg>
    </button>
  </div>
</template>

<script>
import { Marked } from 'marked'
import hljs from 'highlight.js'
import katex from 'katex'

const STORAGE_KEY = 'agent_chat_history'
const MAX_HISTORY = 50

const TOOL_NAME_MAP = {
  query_user_stats: '查询用户统计',
  query_practice_history: '查询练习记录',
  query_leaderboard: '查询排行榜',
  query_wrong_questions: '查询错题',
  query_system_overview: '查询系统概览'
}

function renderKatex(latex, displayMode) {
  try {
    return katex.renderToString(latex, {
      displayMode,
      throwOnError: false,
      trust: true,
      strict: false
    })
  } catch {
    return displayMode
      ? `<code class="agent-math-raw">${latex.replace(/</g, '&lt;')}</code>`
      : `<code class="agent-math-raw">${latex.replace(/</g, '&lt;')}</code>`
  }
}

function preprocessMath(text) {
  if (!text) return ''
  text = text.replace(/\\\$([\s\S]*?)\\\$/g, (_, m) => `%%MATH_BLOCK_${btoa(unescape(encodeURIComponent(m)))}%%`)
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, (_, m) => `%%MATH_BLOCK_${btoa(unescape(encodeURIComponent(m)))}%%`)
  text = text.replace(/\\\(([\s\S]*?)\\\)/g, (_, m) => `%%MATH_INLINE_${btoa(unescape(encodeURIComponent(m)))}%%`)
  text = text.replace(/\$([^\$\n]+?)\$/g, (_, m) => `%%MATH_INLINE_${btoa(unescape(encodeURIComponent(m)))}%%`)
  return text
}

function postprocessMath(html) {
  if (!html) return ''
  html = html.replace(/%%MATH_BLOCK_([A-Za-z0-9+/=]+)%%/g, (_, b64) => {
    const latex = decodeURIComponent(escape(atob(b64)))
    return renderKatex(latex, true)
  })
  html = html.replace(/%%MATH_INLINE_([A-Za-z0-9+/=]+)%%/g, (_, b64) => {
    const latex = decodeURIComponent(escape(atob(b64)))
    return renderKatex(latex, false)
  })
  return html
}

const marked = new Marked({
  renderer: {
    code({ text, lang }) {
      const isMermaid = lang === 'mermaid'
      if (isMermaid) {
        const escaped = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        return `<div class="agent-mermaid-wrapper"><div class="agent-mermaid-label">Mermaid 流程图</div><pre class="agent-mermaid-block"><code>${escaped}</code></pre></div>`
      }
      const language = lang && hljs.getLanguage(lang) ? lang : ''
      let highlighted
      try {
        highlighted = language
          ? hljs.highlight(text, { language }).value
          : hljs.highlightAuto(text).value
      } catch {
        highlighted = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      }
      const langLabel = language ? `<span class="agent-code-lang">${language}</span>` : ''
      return `<div class="agent-code-wrapper">${langLabel}<pre class="agent-code-block"><code>${highlighted}</code></pre></div>`
    }
  }
})

export default {
  name: 'FloatingAgent',
  data() {
    return {
      isOpen: false,
      messages: [],
      inputText: '',
      loading: false,
      streamingContent: '',
      toolIndicator: '',
      abortController: null,
      suggestions: [
        { icon: '🧠', text: '什么是Transformer？' },
        { icon: '📊', text: '查看我的学习统计' },
        { icon: '🏆', text: '查看排行榜' },
        { icon: '💡', text: '如何学习深度学习？' }
      ]
    }
  },
  mounted() {
    this.loadHistory()
  },
  beforeUnmount() {
    if (this.abortController) this.abortController.abort()
  },
  methods: {
    togglePanel() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.$nextTick(() => {
          this.scrollToBottom()
          if (this.$refs.inputRef) this.$refs.inputRef.focus()
        })
      }
    },
    onPanelBeforeEnter(el) {
      el.style.backdropFilter = 'none'
      el.style.webkitBackdropFilter = 'none'
    },
    onPanelAfterEnter(el) {
      el.style.backdropFilter = ''
      el.style.webkitBackdropFilter = ''
    },
    onPanelBeforeLeave(el) {
      el.style.backdropFilter = 'none'
      el.style.webkitBackdropFilter = 'none'
    },
    onPanelAfterLeave(el) {
      el.style.backdropFilter = ''
      el.style.webkitBackdropFilter = ''
    },
    loadHistory() {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) this.messages = JSON.parse(saved)
      } catch (e) {
        this.messages = []
      }
    },
    saveHistory() {
      try {
        const toSave = this.messages.slice(-MAX_HISTORY)
        localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
      } catch (e) {}
    },
    clearHistory() {
      this.messages = []
      localStorage.removeItem(STORAGE_KEY)
    },
    sendSuggestion(text) {
      this.inputText = text
      this.sendMessage()
    },
    async sendMessage() {
      const text = this.inputText.trim()
      if (!text || this.loading) return

      this.messages.push({ role: 'user', content: text })
      this.inputText = ''
      this.resetInputHeight()
      this.loading = true
      this.streamingContent = ''
      this.toolIndicator = ''
      this.scrollToBottom()
      this.saveHistory()

      this.abortController = new AbortController()

      try {
        const history = this.messages.slice(-10, -1)
        const response = await fetch('/api/agent/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history }),
          signal: this.abortController.signal
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const payload = line.slice(6).trim()
            if (payload === '[DONE]') continue

            try {
              const event = JSON.parse(payload)
              if (event.type === 'content') {
                this.streamingContent += event.content
                this.scrollToBottom()
              } else if (event.type === 'tool_call') {
                const label = TOOL_NAME_MAP[event.tool] || event.tool
                this.toolIndicator = `正在${label}...`
              } else if (event.type === 'tool_result') {
                this.toolIndicator = ''
              } else if (event.type === 'error') {
                this.streamingContent += `\n\n❌ ${event.content}`
              }
            } catch (e) {}
          }
        }

        if (this.streamingContent) {
          this.messages.push({ role: 'assistant', content: this.streamingContent })
        }
      } catch (e) {
        if (e.name !== 'AbortError') {
          this.messages.push({ role: 'assistant', content: '网络连接异常，请检查网络后重试。' })
        }
      } finally {
        this.loading = false
        this.streamingContent = ''
        this.toolIndicator = ''
        this.abortController = null
        this.scrollToBottom()
        this.saveHistory()
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.messagesContainer
        if (el) el.scrollTop = el.scrollHeight
      })
    },
    autoResize() {
      const el = this.$refs.inputRef
      if (!el) return
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 120) + 'px'
    },
    resetInputHeight() {
      const el = this.$refs.inputRef
      if (el) el.style.height = 'auto'
    },
    renderMarkdown(text) {
      if (!text) return ''
      try {
        const preprocessed = preprocessMath(text)
        const html = marked.parse(preprocessed)
        return postprocessMath(html)
      } catch (e) {
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

.agent-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: 'Noto Sans SC', sans-serif;
  width: 0;
  height: 0;
}

.agent-fab {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #bd34fe 0%, #764ba2 50%, #41d1ff 100%);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 24px rgba(189, 52, 254, 0.35);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.25s ease,
              opacity 0.2s ease;
  position: absolute;
  bottom: 0;
  right: 0;
  will-change: transform, opacity;
}

.agent-fab::after {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  background: linear-gradient(135deg, #bd34fe, #41d1ff);
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s;
  filter: blur(8px);
}

.agent-fab-hidden {
  opacity: 0;
  transform: scale(0.6);
  pointer-events: none;
}

.agent-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 32px rgba(189, 52, 254, 0.5);
}

.agent-fab:hover::after {
  opacity: 0.6;
}

.agent-fab:active {
  transform: scale(0.95);
}

.agent-panel {
  width: 420px;
  height: 580px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  will-change: transform, opacity;
  transform-origin: bottom right;
  position: absolute;
  bottom: 0;
  right: 0;
}

.agent-panel-enter-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1),
              opacity 0.25s ease-out;
}

.agent-panel-leave-active {
  transition: transform 0.22s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.18s ease-out;
}

.agent-panel-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.94);
}

.agent-panel-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

.agent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: linear-gradient(135deg, #bd34fe 0%, #764ba2 50%, #41d1ff 100%);
  color: #fff;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.agent-header::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.agent-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.agent-header-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.agent-header-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.agent-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.agent-status {
  font-size: 10.5px;
  opacity: 0.8;
  font-weight: 400;
}

.agent-header-actions {
  display: flex;
  gap: 4px;
  position: relative;
  z-index: 1;
}

.agent-header-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  backdrop-filter: blur(4px);
}

.agent-header-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.agent-messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  background: #f7f8fc;
}

.agent-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 24px;
}

.agent-welcome-logo {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(189, 52, 254, 0.12), rgba(65, 209, 255, 0.12));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: #bd34fe;
}

.agent-welcome-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.agent-welcome-sub {
  font-size: 12.5px;
  color: #94a3b8;
  margin-bottom: 24px;
}

.agent-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.agent-suggestion-btn {
  padding: 7px 14px;
  border-radius: 20px;
  border: 1px solid #e8ecf4;
  background: #fff;
  color: #475569;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  display: flex;
  align-items: center;
  gap: 5px;
}

.agent-suggestion-btn:hover {
  border-color: #bd34fe;
  color: #bd34fe;
  background: rgba(189, 52, 254, 0.04);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(189, 52, 254, 0.12);
}

.agent-suggestion-icon {
  font-size: 13px;
}

.agent-msg {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  align-items: flex-start;
  max-width: 100%;
}

.agent-msg-user {
  flex-direction: row-reverse;
}

.agent-msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #bd34fe, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.agent-msg-content {
  max-width: 82%;
  min-width: 0;
  overflow: hidden;
}

.agent-msg-bubble {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.65;
  overflow-wrap: anywhere;
  word-break: break-word;
  word-wrap: break-word;
  max-width: 100%;
  box-sizing: border-box;
}

.agent-md {
  overflow-wrap: anywhere;
  word-break: break-word;
  min-width: 0;
}

.agent-msg-assistant .agent-msg-bubble {
  background: #fff;
  color: #334155;
  border: 1px solid #e8ecf4;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.agent-msg-user .agent-msg-bubble {
  background: linear-gradient(135deg, #bd34fe, #764ba2);
  color: #fff;
  border-top-right-radius: 4px;
}

.agent-typing {
  display: flex;
  gap: 5px;
  padding: 14px 18px;
}

.agent-typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #94a3b8;
  animation: typingBounce 1.2s infinite;
}

.agent-typing span:nth-child(2) { animation-delay: 0.2s; }
.agent-typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.agent-streaming {
  min-height: 20px;
}

.agent-streaming::after {
  content: '▊';
  animation: blink 0.8s infinite;
  color: #bd34fe;
  font-size: 13px;
  margin-left: 1px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.agent-tool-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  margin-bottom: 10px;
  font-size: 12px;
  color: #747bff;
  background: rgba(116, 123, 255, 0.08);
  border-radius: 20px;
  width: fit-content;
}

.agent-tool-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(116, 123, 255, 0.2);
  border-top-color: #747bff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.agent-input-area {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-top: 1px solid #eef0f6;
  flex-shrink: 0;
}

.agent-input {
  flex: 1;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 9px 14px;
  font-size: 13.5px;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 120px;
  transition: border-color 0.2s, box-shadow 0.2s;
  color: #334155;
  background: #f8f9fc;
}

.agent-input:focus {
  border-color: #bd34fe;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(189, 52, 254, 0.08);
}

.agent-input::placeholder {
  color: #94a3b8;
}

.agent-send-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #bd34fe, #764ba2);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity 0.2s, transform 0.2s, box-shadow 0.2s;
}

.agent-send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.agent-send-btn:not(:disabled):hover {
  transform: scale(1.06);
  box-shadow: 0 2px 12px rgba(189, 52, 254, 0.35);
}

.agent-send-btn:not(:disabled):active {
  transform: scale(0.94);
}

.agent-md :deep(h1),
.agent-md :deep(h2),
.agent-md :deep(h3),
.agent-md :deep(h4) {
  margin: 12px 0 6px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.agent-md :deep(h1) { font-size: 16px; }
.agent-md :deep(h2) { font-size: 15px; border-bottom: 1px solid #e8ecf4; padding-bottom: 4px; }
.agent-md :deep(h3) { font-size: 14px; }
.agent-md :deep(h4) { font-size: 13.5px; }

.agent-md :deep(p) {
  margin: 6px 0;
  line-height: 1.65;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.agent-md :deep(ul),
.agent-md :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.agent-md :deep(li) {
  margin: 3px 0;
  line-height: 1.6;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.agent-md :deep(strong) {
  color: #1e293b;
  font-weight: 600;
}

.agent-md :deep(blockquote) {
  margin: 8px 0;
  padding: 6px 12px;
  border-left: 3px solid #bd34fe;
  background: rgba(189, 52, 254, 0.04);
  border-radius: 0 6px 6px 0;
  color: #475569;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.agent-md :deep(a) {
  color: #747bff;
  text-decoration: none;
  overflow-wrap: anywhere;
  word-break: break-all;
}

.agent-md :deep(a:hover) {
  text-decoration: underline;
}

.agent-md :deep(hr) {
  border: none;
  border-top: 1px solid #e8ecf4;
  margin: 10px 0;
}

.agent-md :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 12.5px;
  display: block;
  overflow-x: auto;
}

.agent-md :deep(tbody) {
  display: table;
  width: 100%;
}

.agent-md :deep(th),
.agent-md :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 6px 10px;
  text-align: left;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.agent-md :deep(th) {
  background: #f1f5f9;
  font-weight: 600;
  color: #334155;
}

.agent-md :deep(.agent-code-wrapper) {
  position: relative;
  margin: 8px 0;
  border-radius: 8px;
  background: #0f172a;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

.agent-md :deep(.agent-code-lang) {
  position: absolute;
  top: 0;
  right: 0;
  padding: 2px 8px;
  font-size: 10px;
  color: #64748b;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 0 8px 0 4px;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  z-index: 1;
}

.agent-md :deep(.agent-code-block) {
  padding: 14px 16px;
  font-size: 12px;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  line-height: 1.6;
  color: #e2e8f0;
  margin: 0;
  background: transparent;
  white-space: pre;
  overflow-x: auto;
  overflow-y: hidden;
}

.agent-md :deep(.agent-mermaid-wrapper) {
  position: relative;
  margin: 8px 0;
  border-radius: 8px;
  background: #1a1a2e;
  border: 1px solid #334155;
  overflow: hidden;
}

.agent-md :deep(.agent-mermaid-label) {
  padding: 4px 10px;
  font-size: 10px;
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.1);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.agent-md :deep(.agent-mermaid-block) {
  padding: 12px 16px;
  font-size: 12px;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  line-height: 1.6;
  color: #c4b5fd;
  margin: 0;
  background: transparent;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  overflow-x: auto;
}

.agent-md :deep(.agent-math-raw) {
  background: rgba(189, 52, 254, 0.08);
  color: #9333ea;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  overflow-wrap: anywhere;
  word-break: break-all;
}

.agent-md :deep(code) {
  background: rgba(189, 52, 254, 0.08);
  color: #9333ea;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  overflow-wrap: anywhere;
  word-break: break-all;
}

.agent-md :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
  overflow-wrap: normal;
  word-break: normal;
}

.agent-md :deep(.katex-display) {
  margin: 8px 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 0;
}

.agent-md :deep(.katex) {
  font-size: 1em;
  overflow-wrap: anywhere;
}

.agent-messages::-webkit-scrollbar {
  width: 5px;
}

.agent-messages::-webkit-scrollbar-track {
  background: transparent;
}

.agent-messages::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.agent-messages::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

html[data-theme="Dark"] .agent-panel {
  background: rgba(15, 23, 42, 0.95);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.06);
}

html[data-theme="Dark"] .agent-messages {
  background: #0a0f1e;
}

html[data-theme="Dark"] .agent-welcome-logo {
  background: linear-gradient(135deg, rgba(189, 52, 254, 0.2), rgba(65, 209, 255, 0.2));
}

html[data-theme="Dark"] .agent-welcome-title {
  color: #e2e8f0;
}

html[data-theme="Dark"] .agent-welcome-sub {
  color: #64748b;
}

html[data-theme="Dark"] .agent-suggestion-btn {
  background: rgba(30, 41, 59, 0.8);
  border-color: #334155;
  color: #94a3b8;
}

html[data-theme="Dark"] .agent-suggestion-btn:hover {
  border-color: #a78bfa;
  color: #c4b5fd;
  background: rgba(30, 41, 59, 1);
  box-shadow: 0 2px 8px rgba(167, 139, 250, 0.15);
}

html[data-theme="Dark"] .agent-msg-assistant .agent-msg-bubble {
  background: #1e293b;
  color: #e2e8f0;
  border-color: #334155;
  box-shadow: none;
}

html[data-theme="Dark"] .agent-msg-user .agent-msg-bubble {
  background: linear-gradient(135deg, #9333ea, #7c3aed);
}

html[data-theme="Dark"] .agent-input {
  background: #1e293b;
  border-color: #334155;
  color: #e2e8f0;
}

html[data-theme="Dark"] .agent-input:focus {
  background: #0f172a;
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

html[data-theme="Dark"] .agent-input::placeholder {
  color: #64748b;
}

html[data-theme="Dark"] .agent-input-area {
  background: rgba(15, 23, 42, 0.9);
  border-top-color: #1e293b;
}

html[data-theme="Dark"] .agent-tool-indicator {
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.1);
}

html[data-theme="Dark"] .agent-tool-spinner {
  border-color: rgba(167, 139, 250, 0.2);
  border-top-color: #a78bfa;
}

html[data-theme="Dark"] .agent-md :deep(h1),
html[data-theme="Dark"] .agent-md :deep(h2),
html[data-theme="Dark"] .agent-md :deep(h3),
html[data-theme="Dark"] .agent-md :deep(h4) {
  color: #e2e8f0;
}

html[data-theme="Dark"] .agent-md :deep(h2) {
  border-bottom-color: #334155;
}

html[data-theme="Dark"] .agent-md :deep(strong) {
  color: #f1f5f9;
}

html[data-theme="Dark"] .agent-md :deep(blockquote) {
  background: rgba(167, 139, 250, 0.08);
  border-left-color: #a78bfa;
  color: #94a3b8;
}

html[data-theme="Dark"] .agent-md :deep(a) {
  color: #a78bfa;
}

html[data-theme="Dark"] .agent-md :deep(hr) {
  border-top-color: #334155;
}

html[data-theme="Dark"] .agent-md :deep(th) {
  background: #1e293b;
  color: #e2e8f0;
}

html[data-theme="Dark"] .agent-md :deep(th),
html[data-theme="Dark"] .agent-md :deep(td) {
  border-color: #334155;
}

html[data-theme="Dark"] .agent-md :deep(code) {
  background: rgba(167, 139, 250, 0.12);
  color: #c4b5fd;
}

html[data-theme="Dark"] .agent-md :deep(.agent-math-raw) {
  background: rgba(167, 139, 250, 0.12);
  color: #c4b5fd;
}

html[data-theme="Dark"] .agent-md :deep(.agent-code-wrapper) {
  background: #020617;
}

html[data-theme="Dark"] .agent-md :deep(.agent-code-lang) {
  color: #475569;
  background: rgba(255, 255, 255, 0.03);
}

html[data-theme="Dark"] .agent-md :deep(.agent-mermaid-wrapper) {
  background: #0f172a;
  border-color: #1e293b;
}

html[data-theme="Dark"] .agent-md :deep(.agent-mermaid-label) {
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.08);
}

html[data-theme="Dark"] .agent-md :deep(.agent-mermaid-block) {
  color: #c4b5fd;
}

html[data-theme="Dark"] .agent-messages::-webkit-scrollbar-thumb {
  background: #334155;
}

html[data-theme="Dark"] .agent-messages::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

@media (max-width: 480px) {
  .agent-panel {
    width: calc(100vw - 16px);
    height: calc(100vh - 80px);
    bottom: 0;
    right: 0;
    border-radius: 16px 16px 0 0;
  }

  .agent-widget {
    bottom: 16px;
    right: 16px;
  }
}
</style>

<style>
@import url('https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css');
</style>
