<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>🤖 与 Agent 对话</h2>
      <p class="subtitle">用自然语言管理你的运维对象</p>
    </div>
    
    <div class="chat-messages" ref="messagesRef">
      <div v-if="messages.length === 0" class="empty-state">
        <p>开始对话吧！比如：</p>
        <ul>
          <li>nginx 状态怎么样？</li>
          <li>检查下 nginx 配置</li>
          <li>查看最近 nginx 错误日志</li>
        </ul>
      </div>
      
      <div v-for="(msg, index) in messages" :key="index" 
           class="message" 
           :class="msg.role">
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-content">
          <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
        </div>
      </div>
      
      <div v-if="loading" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="message-text typing">
            <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <input 
        v-model="input" 
        @keyup.enter="send"
        placeholder="输入消息... (Ctrl+Enter 发送)"
        :disabled="loading"
      />
      <button @click="send" :disabled="loading || !input.trim()">
        {{ loading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const input = ref('')
const loading = ref(false)
const messages = ref([])
const messagesRef = ref(null)

const renderMarkdown = (text) => {
  return marked(text || '')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const send = async () => {
  if (!input.value.trim() || loading.value) return
  
  const userMsg = input.value.trim()
  input.value = ''
  
  messages.value.push({ role: 'user', content: userMsg })
  loading.value = true
  scrollToBottom()
  
  try {
    const res = await axios.post('/api/chat', {
      message: userMsg,
      session_id: 'web:default'
    })
    
    messages.value.push({ role: 'assistant', content: res.data.response })
  } catch (err) {
    messages.value.push({ 
      role: 'assistant', 
      content: `错误: ${err.response?.data?.detail || err.message}` 
    })
  }
  
  loading.value = false
  scrollToBottom()
}
</script>

<style scoped>
.chat-container {
  max-width: 900px;
  margin: 0 auto;
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.chat-header h2 {
  font-size: 18px;
  color: #1f2937;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.empty-state ul {
  list-style: none;
  margin-top: 20px;
}

.empty-state li {
  padding: 8px 0;
  color: #3b82f6;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background: #eff6ff;
}

.message-content {
  max: calc(100% - 60px);
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f3f4f6;
  color: #1f2937;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message.assistant .message-text {
  background: #f9fafb;
}

.typing {
  display: flex;
  gap: 4px;
}

.typing .dot {
  animation: bounce 1.4s infinite ease-in-out;
}

.typing .dot:nth-child(1) { animation-delay: 0s; }
.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.typing .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input input:focus {
  border-color: #3b82f6;
}

.chat-input button {
  padding: 12px 24px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-input button:hover:not(:disabled) {
  background: #2563eb;
}

.chat-input button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
