<template>
  <div class="plugins-container">
    <div class="plugins-header">
      <h2>🔌 插件管理</h2>
      <p class="subtitle">管理运维插件</p>
    </div>
    
    <div class="plugins-list">
      <div v-for="plugin in plugins" :key="plugin.name" class="plugin-card">
        <div class="plugin-info">
          <div class="plugin-icon">
            {{ getPluginIcon(plugin.name) }}
          </div>
          <div class="plugin-details">
            <h3>{{ plugin.name }}</h3>
            <p class="plugin-desc">{{ plugin.description || '暂无描述' }}</p>
          </div>
        </div>
        
        <div class="plugin-actions">
          <label class="switch">
            <input 
              type="checkbox" 
              :checked="plugin.enabled"
              @change="togglePlugin(plugin.name, $event.target.checked)"
            >
            <span class="slider"></span>
          </label>
          
          <button class="config-btn" @click="showConfig(plugin)">
            配置
          </button>
        </div>
      </div>
      
      <div v-if="plugins.length === 0" class="empty-state">
        <p>暂无插件</p>
      </div>
    </div>
    
    <!-- 配置弹窗 -->
    <div v-if="configVisible" class="modal" @click.self="configVisible = false">
      <div class="modal-content">
        <h3>{{ currentPlugin?.name }} 配置</h3>
        <textarea 
          v-model="configText" 
          rows="15"
          class="config-editor"
        ></textarea>
        <div class="modal-actions">
          <button @click="configVisible = false">取消</button>
          <button class="primary" @click="saveConfig">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import yaml from 'yaml'

const plugins = ref([])
const configVisible = ref(false)
const currentPlugin = ref(null)
const configText = ref('')

const getPluginIcon = (name) => {
  const icons = {
    nginx: '🌐',
    k8s: '☸️',
    mysql: '🐬',
    docker: '🐳',
  }
  return icons[name] || '📦'
}

const loadPlugins = async () => {
  try {
    const res = await axios.get('/api/plugins')
    plugins.value = res.data.plugins
  } catch (err) {
    console.error('加载插件失败:', err)
  }
}

const togglePlugin = async (name, enabled) => {
  try {
    const url = enabled ? `/api/plugins/${name}/enable` : `/api/plugins/${name}/disable`
    await axios.post(url)
    await loadPlugins()
  } catch (err) {
    console.error('操作失败:', err)
    await loadPlugins()
  }
}

const showConfig = async (plugin) => {
  currentPlugin.value = plugin
  try {
    const res = await axios.get(`/api/plugins/${plugin.name}/config`)
    configText.value = yaml.stringify(res.data.config || {})
  } catch (err) {
    configText.value = '# 无配置'
  }
  configVisible.value = true
}

const saveConfig = async () => {
  try {
    await axios.put(`/api/plugins/${currentPlugin.value.name}/config`, {
      config: yaml.parse(configText.value) || {}
    })
    configVisible.value = false
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

onMounted(loadPlugins)
</script>

<style scoped>
.plugins-container {
  max-width: 900px;
  margin: 0 auto;
}

.plugins-header {
  margin-bottom: 24px;
}

.plugins-header h2 {
  font-size: 20px;
  color: #1f2937;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
}

.plugins-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plugin-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.plugin-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.plugin-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.plugin-details h3 {
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 4px;
}

.plugin-desc {
  font-size: 13px;
  color: #6b7280;
}

.plugin-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.switch {
  position: relative;
  width: 48px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #d1d5db;
  border-radius: 26px;
  transition: 0.3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background: #fff;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .slider {
  background: #3b82f6;
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.config-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  color: #6b7280;
  cursor: pointer;
  font-size: 13px;
}

.config-btn:hover {
  background: #e5e7eb;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #6b7280;
  background: #fff;
  border-radius: 12px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 600px;
}

.modal-content h3 {
  margin-bottom: 16px;
  font-size: 18px;
}

.config-editor {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-family: monospace;
  font-size: 13px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.modal-actions button {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.modal-actions button:not(.primary) {
  background: #f3f4f6;
  color: #6b7280;
}

.modal-actions button.primary {
  background: #3b82f6;
  color: #fff;
}
</style>
