<template>
  <div class="api-mgmt-page" :class="{ 'dark-mode': isDark }">
    <div class="api-bg-filter"></div>
    <div class="api-mgmt-container">
      <div class="api-mgmt-header">
        <div class="header-left">
          <button class="back-btn" @click="goBack" title="返回首页">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          </button>
          <div class="header-title-group">
            <h1 class="header-title">API <span class="gradient-text">统一管理</span></h1>
            <span class="header-subtitle">管理所有模型供应商的 API Key、Base URL 和模型配置</span>
          </div>
        </div>
        <div class="header-right">
          <div class="env-sync-status" v-if="lastSyncTime" :class="{ syncing: isSyncing }">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span>环境变量已同步</span>
          </div>
        </div>
      </div>

      <div class="api-mgmt-body">
        <div class="provider-sidebar">
          <div v-if="loading" class="sidebar-loading">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <template v-else>
            <div class="sidebar-search">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" v-model="searchQuery" placeholder="搜索供应商..." class="sidebar-search-input">
            </div>
            <div class="sidebar-section" v-for="cat in filteredCategories" :key="cat.id">
              <div class="sidebar-section-title" @click="toggleSection(cat.id)">
                <span class="section-icon" v-html="cat.icon"></span>
                <span class="section-name">{{ cat.name }}</span>
                <span class="section-count">{{ getConfiguredCount(cat.id) }}/{{ getTotalCount(cat.id) }}</span>
                <svg class="section-arrow" :class="{ expanded: expandedSections[cat.id] }" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
              </div>
              <transition name="slide">
                <div v-show="expandedSections[cat.id]" class="sidebar-section-list">
                  <button
                    v-for="(meta, pid) in getProvidersForCategory(cat.id)"
                    :key="pid"
                    :class="['provider-btn', { active: selectedProvider === pid && activeCategory === cat.id }]"
                    @click="selectProvider(cat.id, pid)"
                  >
                    <div class="provider-btn-indicator" :class="getStatusClass(cat.id, pid)"></div>
                    <span class="provider-btn-name">{{ meta.name }}</span>
                    <span :class="['provider-badge', getStatusClass(cat.id, pid) + '-badge']">{{ getStatusLabel(cat.id, pid) }}</span>
                  </button>
                </div>
              </transition>
            </div>
          </template>
        </div>

        <div class="config-panel">
          <div v-if="!selectedProvider" class="empty-panel">
            <div class="empty-icon-wrapper">
              <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1" opacity="0.25">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <p class="empty-text">请从左侧选择一个模型供应商</p>
            <p class="empty-sub">选择后将在此处显示配置页面</p>
          </div>

          <div v-else class="config-form">
            <div class="config-form-header">
              <div class="config-form-title-group">
                <h2 class="config-form-title">{{ currentProviderMeta.name }}</h2>
                <span class="config-form-id">{{ selectedProvider }}</span>
                <span :class="['config-status-tag', getStatusClass(activeCategory, selectedProvider)]">{{ getStatusLabel(activeCategory, selectedProvider) }}</span>
              </div>
              <div class="config-form-actions">
                <button class="action-btn reset-btn" @click="resetProvider" :disabled="saving">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/></svg>
                  重置
                </button>
              </div>
            </div>

            <div v-if="configStatus[activeCategory]?.[selectedProvider]?.missing?.length" class="config-missing-hint">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <span>缺少必要配置：{{ configStatus[activeCategory][selectedProvider].missing.map(m => ({apiKey: 'API Key', baseUrl: 'API URL', models: '模型型号'}[m] || m)).join('、') }}</span>
            </div>

            <div class="config-form-body">
              <div class="form-group" :class="{ 'has-error': fieldErrors.model }">
                <label class="form-label">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
                  模型型号
                </label>
                <div class="model-input-area">
                  <div class="model-chips" v-if="formData.models.length > 0">
                    <transition-group name="chip">
                      <span v-for="(model, idx) in formData.models" :key="model" class="model-chip">
                        <span class="chip-text">{{ model }}</span>
                        <button class="chip-remove" @click="removeModel(idx)" title="移除模型">
                          <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                        </button>
                      </span>
                    </transition-group>
                  </div>
                  <div v-else class="no-models-hint">暂无模型，请在下方添加或从推荐中选择</div>
                  <div class="model-add-row">
                    <div class="input-wrap">
                      <input
                        type="text"
                        v-model="newModelInput"
                        placeholder="输入模型 ID，如 gpt-4o"
                        @keydown.enter.prevent="addModel"
                      >
                    </div>
                    <button class="add-model-btn" @click="addModel">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
                      添加
                    </button>
                  </div>
                  <div v-if="currentProviderMeta.defaultModels && currentProviderMeta.defaultModels.length > 0" class="model-suggestions">
                    <span class="suggestion-label">推荐模型：</span>
                    <button
                      v-for="model in suggestedModels"
                      :key="model"
                      class="suggestion-chip"
                      @click="addSuggestedModel(model)"
                    >+ {{ model }}</button>
                  </div>
                </div>
                <div v-if="fieldErrors.model" class="field-error">{{ fieldErrors.model }}</div>
              </div>

              <div class="form-group" :class="{ 'has-error': fieldErrors.baseUrl }">
                <label class="form-label">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
                  API URL
                </label>
                <input
                  type="url"
                  v-model="formData.baseUrl"
                  :placeholder="currentProviderMeta.defaultBaseUrl || 'https://api.example.com/v1'"
                  class="form-input"
                >
                <div v-if="currentProviderMeta.defaultBaseUrl && !formData.baseUrl" class="field-hint">
                  默认地址: {{ currentProviderMeta.defaultBaseUrl }}
                </div>
                <div v-if="fieldErrors.baseUrl" class="field-error">{{ fieldErrors.baseUrl }}</div>
              </div>

              <div class="form-group" :class="{ 'has-error': fieldErrors.apiKey }">
                <label class="form-label">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
                  API Key
                </label>
                <div class="key-input-wrap">
                  <input
                    :type="showApiKey ? 'text' : 'password'"
                    v-model="formData.apiKey"
                    placeholder="sk-..."
                    class="form-input mono-input"
                  >
                  <button class="toggle-visibility-btn" @click="showApiKey = !showApiKey" :title="showApiKey ? '隐藏' : '显示'">
                    <svg v-if="showApiKey" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                    <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  </button>
                </div>
                <div v-if="fieldErrors.apiKey" class="field-error">{{ fieldErrors.apiKey }}</div>
              </div>

              <div class="form-group">
                <label class="toggle-label">
                  <div class="toggle-switch" :class="{ on: formData.enabled }" @click="formData.enabled = !formData.enabled">
                    <div class="toggle-thumb"></div>
                  </div>
                  <span class="toggle-text">{{ formData.enabled ? '已启用' : '已停用' }}</span>
                </label>
              </div>
            </div>

            <div class="config-form-footer">
              <div v-if="saveMessage" :class="['save-message', saveMessageType]">
                <svg v-if="saveMessageType === 'success'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                <span>{{ saveMessage }}</span>
              </div>
              <div v-else class="save-message-placeholder"></div>
              <div class="footer-actions">
                <button class="test-conn-btn" @click="testConnection" :disabled="testing || !formData.apiKey">
                  <svg v-if="testing" class="spin" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
                  <svg v-else viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                  {{ testing ? '测试中...' : '测试连接' }}
                </button>
                <button class="save-btn" @click="saveProvider" :disabled="saving">
                  <svg v-if="saving" class="spin" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
                  <svg v-else viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                  {{ saving ? '保存中...' : '保存配置' }}
                </button>
              </div>
            </div>

            <transition name="slide-up">
              <div v-if="testResult" :class="['test-result-bar', testResult.success ? 'success' : 'error']">
                <svg v-if="testResult.success" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                <span>{{ testResult.message }}</span>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>

    <transition name="toast">
      <div class="toast" v-if="toast.show" :class="toast.type">
        <svg v-if="toast.type === 'success'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <svg v-else-if="toast.type === 'error'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = ''

export default {
  name: 'ApiManagement',
  data() {
    return {
      isDark: false,
      loading: true,
      activeCategory: '',
      selectedProvider: null,
      showApiKey: false,
      testing: false,
      saving: false,
      isSyncing: false,
      lastSyncTime: null,
      testResult: null,
      saveMessage: '',
      saveMessageType: 'success',
      newModelInput: '',
      searchQuery: '',
      fieldErrors: {},
      formData: {
        apiKey: '',
        baseUrl: '',
        models: [],
        enabled: true,
      },
      expandedSections: {
        llm: true,
        image: false,
        video: false,
        tts: false,
        asr: false,
        pdf: false,
        webSearch: false,
      },
      providerRegistry: {},
      config: {},
      configStatus: {},
      toast: { show: false, message: '', type: 'info' },
      toastTimer: null,
      categories: [
        { id: 'llm', name: 'LLM 大语言模型', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>' },
        { id: 'image', name: '图像生成', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>' },
        { id: 'video', name: '视频生成', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>' },
        { id: 'tts', name: '语音合成', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>' },
        { id: 'asr', name: '语音识别', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/></svg>' },
        { id: 'pdf', name: 'PDF 解析', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' },
        { id: 'webSearch', name: '网络搜索', icon: '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' },
      ],
    }
  },
  computed: {
    currentProviderMeta() {
      if (!this.selectedProvider || !this.activeCategory) return { name: '', defaultBaseUrl: '', defaultModels: [] }
      return this.providerRegistry[this.activeCategory]?.[this.selectedProvider] || { name: this.selectedProvider, defaultBaseUrl: '', defaultModels: [] }
    },
    suggestedModels() {
      if (!this.currentProviderMeta.defaultModels) return []
      return this.currentProviderMeta.defaultModels.filter(m => !this.formData.models.includes(m))
    },
    filteredCategories() {
      if (!this.searchQuery) return this.categories
      const q = this.searchQuery.toLowerCase()
      return this.categories.filter(cat => {
        const providers = this.providerRegistry[cat.id] || {}
        const catMatch = cat.name.toLowerCase().includes(q)
        const providerMatch = Object.values(providers).some(p => p.name.toLowerCase().includes(q))
        return catMatch || providerMatch
      })
    },
  },
  methods: {
    checkDarkMode() {
      this.isDark = document.documentElement.classList.contains('Dark') || document.documentElement.getAttribute('data-theme') === 'Dark'
    },
    goBack() {
      this.$router.push('/')
    },
    showToast(message, type = 'info') {
      if (this.toastTimer) clearTimeout(this.toastTimer)
      this.toast = { show: true, message, type }
      this.toastTimer = setTimeout(() => { this.toast.show = false }, 3000)
    },
    toggleSection(catId) {
      this.expandedSections[catId] = !this.expandedSections[catId]
    },
    getProvidersForCategory(catId) {
      const providers = this.providerRegistry[catId] || {}
      if (!this.searchQuery) return providers
      const q = this.searchQuery.toLowerCase()
      const filtered = {}
      for (const [pid, meta] of Object.entries(providers)) {
        if (meta.name.toLowerCase().includes(q) || pid.toLowerCase().includes(q)) {
          filtered[pid] = meta
        }
      }
      return filtered
    },
    getConfiguredCount(catId) {
      const providers = this.config[catId] || {}
      return Object.keys(providers).filter(pid => this.isProviderConfigured(catId, pid)).length
    },
    getTotalCount(catId) {
      return Object.keys(this.providerRegistry[catId] || {}).length
    },
    isProviderConfigured(catId, pid) {
      const data = this.config[catId]?.[pid]
      if (!data) return false
      const registryMeta = this.providerRegistry[catId]?.[pid] || {}
      const requiresApiKey = registryMeta.requiresApiKey !== false
      const apiKey = (data.apiKey || '').trim()
      const baseUrl = (data.baseUrl || '').trim()
      const defaultBaseUrl = (registryMeta.defaultBaseUrl || '').trim()
      if (requiresApiKey) {
        return !!apiKey
      } else {
        return !!baseUrl && baseUrl !== defaultBaseUrl
      }
    },
    getProviderStatus(catId, pid) {
      const statusInfo = this.configStatus[catId]?.[pid]
      if (statusInfo) return statusInfo.status
      return this.isProviderConfigured(catId, pid) ? 'configured' : 'unconfigured'
    },
    getStatusLabel(catId, pid) {
      const status = this.getProviderStatus(catId, pid)
      const labels = {
        configured: '已配置',
        incomplete: '配置不完整',
        unconfigured: '未配置',
        disabled: '已停用',
      }
      return labels[status] || '未配置'
    },
    getStatusClass(catId, pid) {
      const status = this.getProviderStatus(catId, pid)
      return status
    },
    getConfigData(catId, pid) {
      return this.config[catId]?.[pid] || null
    },
    selectProvider(catId, pid) {
      this.activeCategory = catId
      this.selectedProvider = pid
      this.fieldErrors = {}
      this.saveMessage = ''
      this.testResult = null
      this.showApiKey = false

      const data = this.config[catId]?.[pid] || {}
      this.formData = {
        apiKey: data.apiKey || '',
        baseUrl: data.baseUrl || '',
        models: Array.isArray(data.models) ? [...data.models] : [],
        enabled: data.enabled !== false,
      }
    },
    addModel() {
      const modelId = this.newModelInput.trim()
      if (!modelId) return
      if (this.formData.models.includes(modelId)) {
        this.fieldErrors = { ...this.fieldErrors, model: `模型 "${modelId}" 已存在` }
        return
      }
      this.formData.models.push(modelId)
      this.newModelInput = ''
      const newErrors = { ...this.fieldErrors }
      delete newErrors.model
      this.fieldErrors = newErrors
    },
    addSuggestedModel(model) {
      if (!this.formData.models.includes(model)) {
        this.formData.models.push(model)
      }
    },
    removeModel(idx) {
      this.formData.models.splice(idx, 1)
    },
    validateForm() {
      const errors = {}
      if (this.formData.baseUrl) {
        const urlPattern = /^https?:\/\/[^\s]+$/i
        if (!urlPattern.test(this.formData.baseUrl)) {
          errors.baseUrl = 'API URL 格式无效，请输入完整的 HTTP/HTTPS 地址'
        }
      }
      if (this.formData.apiKey && this.formData.apiKey.length < 8) {
        errors.apiKey = 'API Key 长度不能少于8个字符'
      }
      this.fieldErrors = errors
      return Object.keys(errors).length === 0
    },
    async saveProvider() {
      if (!this.validateForm()) {
        this.saveMessage = '请修正表单中的错误后再保存'
        this.saveMessageType = 'error'
        return
      }

      this.saving = true
      this.saveMessage = ''
      try {
        const res = await axios.put(`${API_BASE}/api/config/${this.activeCategory}/${this.selectedProvider}`, {
          apiKey: this.formData.apiKey,
          baseUrl: this.formData.baseUrl,
          models: this.formData.models,
          enabled: this.formData.enabled,
        })
        if (res.data.success) {
          if (!this.config[this.activeCategory]) {
            this.config[this.activeCategory] = {}
          }
          this.config[this.activeCategory][this.selectedProvider] = {
            ...(this.config[this.activeCategory][this.selectedProvider] || {}),
            apiKey: this.formData.apiKey,
            baseUrl: this.formData.baseUrl,
            models: [...this.formData.models],
            enabled: this.formData.enabled,
          }
          this.loadConfigStatus()
          this.saveMessage = '配置保存成功！已自动同步至环境变量'
          this.saveMessageType = 'success'
          this.showToast('配置已保存并自动同步至环境变量', 'success')
          this.lastSyncTime = new Date()
        } else if (res.data.errors) {
          this.fieldErrors = res.data.errors
          this.saveMessage = '验证失败，请检查错误字段'
          this.saveMessageType = 'error'
        }
      } catch (e) {
        if (e.response?.status === 422 && e.response?.data?.errors) {
          this.fieldErrors = e.response.data.errors
          this.saveMessage = '验证失败，请检查错误字段'
          this.saveMessageType = 'error'
        } else {
          this.saveMessage = '保存失败: ' + (e.response?.data?.error || e.message)
          this.saveMessageType = 'error'
        }
      } finally {
        this.saving = false
      }
    },
    async testConnection() {
      if (!this.formData.apiKey) {
        this.showToast('请先填写 API Key', 'error')
        return
      }
      this.testing = true
      this.testResult = null
      const providerType = this.getProviderType(this.selectedProvider)
      try {
        const res = await axios.post(`${API_BASE}/api/test-connection`, {
          providerType,
          apiKey: this.formData.apiKey,
          baseUrl: this.formData.baseUrl || this.currentProviderMeta.defaultBaseUrl,
          model: '',
        }, { timeout: 15000 })
        this.testResult = res.data
      } catch (e) {
        if (e.code === 'ECONNABORTED') {
          this.testResult = { success: false, message: '连接超时，请检查网络或API地址是否正确' }
        } else {
          this.testResult = { success: false, message: e.response?.data?.message || '连接测试失败' }
        }
      } finally {
        this.testing = false
      }
    },
    getProviderType(pid) {
      if (pid.includes('anthropic') || pid.includes('claude')) return 'anthropic'
      if (pid.includes('google') || pid.includes('gemini')) return 'google'
      return 'openai'
    },
    async resetProvider() {
      if (!confirm(`确定要重置 ${this.currentProviderMeta.name} 的配置吗？此操作不可撤销。`)) return
      try {
        await axios.delete(`${API_BASE}/api/config/${this.activeCategory}/${this.selectedProvider}`)
        await Promise.all([this.loadConfig(), this.loadConfigStatus()])
        this.formData = { apiKey: '', baseUrl: '', models: [], enabled: true }
        this.saveMessage = ''
        this.testResult = null
        this.fieldErrors = {}
        this.showToast('已重置配置并同步至环境变量', 'success')
      } catch (e) {
        this.showToast('重置失败: ' + (e.response?.data?.error || e.message), 'error')
      }
    },
    async loadRegistry() {
      try {
        const res = await axios.get(`${API_BASE}/api/providers`, { timeout: 10000 })
        this.providerRegistry = res.data
      } catch (e) {
        console.error('加载供应商注册表失败:', e)
        this.showToast('加载供应商列表失败，请检查API管理服务是否启动', 'error')
      }
    },
    async loadConfig() {
      try {
        const res = await axios.get(`${API_BASE}/api/config`, { timeout: 10000 })
        this.config = res.data
      } catch (e) {
        console.error('加载配置失败:', e)
        this.showToast('加载配置失败，请检查API管理服务是否启动', 'error')
      }
    },
    async loadConfigStatus() {
      try {
        const res = await axios.get(`${API_BASE}/api/config/status`, { timeout: 10000 })
        this.configStatus = res.data
      } catch (e) {
        console.error('加载配置状态失败:', e)
      }
    },
  },
  async mounted() {
    this.checkDarkMode()
    this.loading = true
    try {
      await Promise.all([this.loadRegistry(), this.loadConfig(), this.loadConfigStatus()])
    } finally {
      this.loading = false
    }
    this._darkObserver = new MutationObserver(() => { this.checkDarkMode() })
    this._darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
  },
  beforeUnmount() {
    if (this._darkObserver) this._darkObserver.disconnect()
    if (this.toastTimer) clearTimeout(this.toastTimer)
  },
}
</script>

<style scoped>
.api-mgmt-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--main_bg_color, url(../../static/img/background.jpg));
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  font-family: "b", "a", -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
  color: var(--main_text_color, #eeeeee);
  transition: all 0.3s ease;
  position: relative;
  padding: 20px;
  box-sizing: border-box;
}

.api-bg-filter {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--back_filter_color, #00000030);
  backdrop-filter: blur(var(--back_filter, 19px));
  -webkit-backdrop-filter: blur(var(--back_filter, 19px));
  z-index: 0;
  pointer-events: none;
}

.api-mgmt-page.dark-mode {
  background: #000000 !important;
}

.api-mgmt-page.dark-mode .api-bg-filter {
  background: rgba(0, 0, 0, 0.6);
}

.api-mgmt-container {
  width: 94vw;
  max-width: 1200px;
  height: 90vh;
  background: var(--item_bg_color, rgba(0, 0, 0, 0.22));
  backdrop-filter: blur(var(--card_filter, 15px));
  -webkit-backdrop-filter: blur(var(--card_filter, 15px));
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3),
              0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.dark-mode .api-mgmt-container {
  background: rgba(19, 20, 24, 0.95);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5),
              0 0 0 1px rgba(255, 255, 255, 0.04) inset;
}

.api-mgmt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: linear-gradient(135deg, rgba(147, 112, 219, 0.25), rgba(116, 123, 255, 0.15));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  flex-shrink: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

.dark-mode .api-mgmt-header {
  background: linear-gradient(135deg, rgba(90, 63, 160, 0.35), rgba(74, 77, 199, 0.2));
  border-bottom-color: rgba(255, 255, 255, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  color: #fff;
  cursor: pointer;
  transition: all 0.25s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.16);
  transform: translateX(-2px);
  box-shadow: 0 4px 12px rgba(147, 112, 219, 0.25);
}

.header-title-group {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: 0.5px;
}

.gradient-text {
  background: var(--gradient, linear-gradient(120deg, #bd34fe, #e0321b 30%, #41d1ff 60%));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.env-sync-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(34, 197, 94, 0.9);
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  transition: all 0.3s ease;
}

.env-sync-status.syncing {
  color: rgba(147, 112, 219, 0.9);
  background: rgba(147, 112, 219, 0.1);
  border-color: rgba(147, 112, 219, 0.2);
}

.api-mgmt-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.provider-sidebar {
  width: 260px;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.dark-mode .provider-sidebar {
  background: rgba(15, 15, 25, 0.7);
  border-right-color: rgba(255, 255, 255, 0.04);
}

.provider-sidebar::-webkit-scrollbar {
  width: 4px;
}

.provider-sidebar::-webkit-scrollbar-thumb {
  background: rgba(147, 112, 219, 0.25);
  border-radius: 2px;
}

.provider-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.sidebar-search-input {
  flex: 1;
  background: none;
  border: none;
  color: var(--main_text_color, #fff);
  font-size: 13px;
  outline: none;
}

.sidebar-search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.sidebar-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
  color: var(--main_text_color, rgba(255, 255, 255, 0.6));
  font-size: 13px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(147, 112, 219, 0.2);
  border-top-color: #9370DB;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.sidebar-section {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.sidebar-section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  color: var(--main_text_color, rgba(255, 255, 255, 0.9));
}

.sidebar-section-title:hover {
  background: rgba(147, 112, 219, 0.08);
}

.section-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  color: #9370DB;
}

.section-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
}

.section-count {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(147, 112, 219, 0.15);
  color: rgba(147, 112, 219, 0.9);
  font-weight: 600;
}

.section-arrow {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.4);
  transition: transform 0.25s ease;
}

.section-arrow.expanded {
  transform: rotate(180deg);
}

.sidebar-section-list {
  padding: 4px 10px 8px;
  overflow: hidden;
}

.provider-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 12px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--main_text_color, rgba(255, 255, 255, 0.75));
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 2px;
}

.provider-btn:hover {
  background: rgba(147, 112, 219, 0.1);
  border-color: rgba(147, 112, 219, 0.2);
}

.provider-btn.active {
  background: linear-gradient(135deg, rgba(147, 112, 219, 0.2), rgba(116, 123, 255, 0.15));
  border-color: rgba(147, 112, 219, 0.4);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(147, 112, 219, 0.15);
}

.provider-btn-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.provider-btn-indicator.configured {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.4);
}

.provider-btn-indicator.incomplete {
  background: #f59e0b;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.4);
}

.provider-btn-indicator.unconfigured {
  background: rgba(255, 255, 255, 0.15);
}

.provider-btn-indicator.disabled {
  background: #6b7280;
  box-shadow: 0 0 4px rgba(107, 114, 128, 0.3);
}

.provider-btn-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.provider-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  flex-shrink: 0;
}

.configured-badge {
  background: rgba(34, 197, 94, 0.15);
  color: rgba(34, 197, 94, 0.9);
}

.incomplete-badge {
  background: rgba(245, 158, 11, 0.15);
  color: rgba(245, 158, 11, 0.9);
}

.unconfigured-badge {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.35);
}

.disabled-badge {
  background: rgba(107, 114, 128, 0.15);
  color: rgba(107, 114, 128, 0.9);
}

.config-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.empty-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: var(--main_text_color, rgba(255, 255, 255, 0.4));
}

.empty-icon-wrapper {
  opacity: 0.3;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
}

.empty-sub {
  font-size: 13px;
  opacity: 0.7;
}

.config-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.config-form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.08);
}

.dark-mode .config-form-header {
  border-bottom-color: rgba(255, 255, 255, 0.04);
  background: rgba(0, 0, 0, 0.15);
}

.config-form-title-group {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.config-form-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  background: var(--gradient, linear-gradient(120deg, #bd34fe, #41d1ff));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.config-form-id {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  font-family: 'SF Mono', 'Cascadia Code', monospace;
  padding: 3px 8px;
  background: rgba(147, 112, 219, 0.1);
  border-radius: 4px;
}

.config-status-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.config-status-tag.configured {
  background: rgba(34, 197, 94, 0.15);
  color: rgba(34, 197, 94, 0.9);
}

.config-status-tag.incomplete {
  background: rgba(245, 158, 11, 0.15);
  color: rgba(245, 158, 11, 0.9);
}

.config-status-tag.unconfigured {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.4);
}

.config-status-tag.disabled {
  background: rgba(107, 114, 128, 0.15);
  color: rgba(107, 114, 128, 0.9);
}

.config-missing-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 24px;
  font-size: 12px;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.08);
  border-bottom: 1px solid rgba(245, 158, 11, 0.15);
}

.config-form-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 7px 14px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reset-btn {
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.6);
  background: transparent;
}

.reset-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.config-form-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.config-form-body::-webkit-scrollbar {
  width: 5px;
}

.config-form-body::-webkit-scrollbar-thumb {
  background: rgba(147, 112, 219, 0.2);
  border-radius: 3px;
}

.config-form-body::-webkit-scrollbar-track {
  background: transparent;
}

.form-group {
  margin-bottom: 24px;
}

.form-group.has-error .form-input,
.form-group.has-error .model-input-area {
  border-color: rgba(239, 68, 68, 0.4);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.08);
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--main_text_color, rgba(255, 255, 255, 0.85));
  margin-bottom: 8px;
}

.form-label svg {
  color: #9370DB;
}

.form-input {
  width: 100%;
  height: 42px;
  padding: 0 14px;
  background: rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: var(--main_text_color, #fff);
  font-size: 14px;
  outline: none;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.form-input:focus {
  border-color: rgba(147, 112, 219, 0.45);
  box-shadow: 0 0 0 3px rgba(147, 112, 219, 0.1),
              0 2px 8px rgba(147, 112, 219, 0.08);
}

.mono-input {
  font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', monospace;
  font-size: 13px;
}

.field-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  margin-top: 6px;
}

.field-error {
  font-size: 12px;
  color: #f87171;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.key-input-wrap {
  position: relative;
}

.key-input-wrap .form-input {
  padding-right: 48px;
}

.toggle-visibility-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  padding: 6px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.35);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
}

.toggle-visibility-btn:hover {
  color: #9370DB;
  background: rgba(147, 112, 219, 0.08);
}

.model-input-area {
  background: rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 14px;
  transition: all 0.25s ease;
}

.model-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.model-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  background: rgba(147, 112, 219, 0.12);
  border: 1px solid rgba(147, 112, 219, 0.2);
  font-size: 12px;
  font-family: 'SF Mono', 'Cascadia Code', monospace;
  font-weight: 500;
  color: #fff;
  transition: all 0.2s ease;
}

.model-chip:hover {
  background: rgba(147, 112, 219, 0.2);
  border-color: rgba(147, 112, 219, 0.35);
}

.chip-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-remove {
  display: flex;
  align-items: center;
  padding: 0;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.chip-remove:hover {
  color: #f87171;
}

.no-models-hint {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.3);
  padding: 6px 0 12px;
}

.model-add-row {
  display: flex;
  gap: 8px;
}

.model-add-row .input-wrap {
  flex: 1;
}

.model-add-row input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  outline: none;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.model-add-row input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.model-add-row input:focus {
  border-color: rgba(147, 112, 219, 0.4);
  box-shadow: 0 0 0 2px rgba(147, 112, 219, 0.08);
}

.add-model-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0 14px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(147, 112, 219, 0.3);
  background: rgba(147, 112, 219, 0.12);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.add-model-btn:hover {
  background: rgba(147, 112, 219, 0.22);
  border-color: rgba(147, 112, 219, 0.5);
}

.model-suggestions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.suggestion-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
}

.suggestion-chip {
  padding: 3px 10px;
  border-radius: 6px;
  border: 1px dashed rgba(147, 112, 219, 0.3);
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  font-family: 'SF Mono', 'Cascadia Code', monospace;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-chip:hover {
  border-color: rgba(147, 112, 219, 0.6);
  color: #9370DB;
  background: rgba(147, 112, 219, 0.08);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  font-size: 14px;
  color: var(--main_text_color, rgba(255, 255, 255, 0.8));
}

.toggle-switch {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  transition: all 0.25s ease;
  cursor: pointer;
  flex-shrink: 0;
}

.toggle-switch.on {
  background: rgba(147, 112, 219, 0.5);
  border-color: rgba(147, 112, 219, 0.6);
}

.toggle-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all 0.25s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-switch.on .toggle-thumb {
  left: 22px;
}

.toggle-text {
  font-size: 13px;
  font-weight: 500;
}

.config-form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.dark-mode .config-form-footer {
  border-top-color: rgba(255, 255, 255, 0.04);
  background: rgba(0, 0, 0, 0.2);
}

.save-message {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
}

.save-message-placeholder {
  flex: 1;
}

.save-message.success {
  color: #4ade80;
}

.save-message.error {
  color: #f87171;
}

.footer-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.test-conn-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 18px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(147, 112, 219, 0.3);
  background: transparent;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.test-conn-btn:hover:not(:disabled) {
  background: rgba(147, 112, 219, 0.1);
  border-color: rgba(147, 112, 219, 0.5);
}

.test-conn-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 24px;
  height: 38px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #9370DB, #7B68EE);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 14px rgba(147, 112, 219, 0.35);
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c5cbf, #6a5acd);
  box-shadow: 0 6px 18px rgba(147, 112, 219, 0.45);
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.test-result-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
}

.test-result-bar.success {
  background: rgba(34, 197, 94, 0.08);
  border-top: 1px solid rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.test-result-bar.error {
  background: rgba(239, 68, 68, 0.08);
  border-top: 1px solid rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.toast {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  z-index: 2000;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.toast.info {
  background: rgba(59, 130, 246, 0.9);
  color: #fff;
}

.toast.success {
  background: rgba(34, 197, 94, 0.9);
  color: #fff;
}

.toast.error {
  background: rgba(239, 68, 68, 0.9);
  color: #fff;
}

.spin {
  animation: spin 1s linear infinite;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.chip-enter-active,
.chip-leave-active {
  transition: all 0.2s ease;
}

.chip-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.chip-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.toast-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px) scale(0.95);
}

@media (max-width: 1024px) {
  .api-mgmt-container {
    width: 100%;
    height: 95vh;
    border-radius: 12px;
  }

  .provider-sidebar {
    width: 220px;
  }
}

@media (max-width: 768px) {
  .api-mgmt-page {
    padding: 0;
  }

  .api-mgmt-container {
    width: 100%;
    height: 100vh;
    border-radius: 0;
  }

  .api-mgmt-body {
    flex-direction: column;
  }

  .provider-sidebar {
    width: 100%;
    max-height: 180px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  .dark-mode .provider-sidebar {
    border-bottom-color: rgba(255, 255, 255, 0.04);
  }

  .config-form-body {
    padding: 18px;
  }

  .config-form-footer {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }

  .footer-actions {
    justify-content: flex-end;
  }

  .header-title {
    font-size: 16px;
  }

  .header-subtitle {
    display: none;
  }

  .env-sync-status {
    display: none;
  }
}

@media (max-width: 480px) {
  .config-form-title {
    font-size: 18px;
  }

  .save-btn,
  .test-conn-btn {
    height: 36px;
    font-size: 13px;
    padding: 0 14px;
  }

  .form-input {
    height: 38px;
  }

  .model-add-row {
    flex-direction: column;
  }

  .add-model-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
