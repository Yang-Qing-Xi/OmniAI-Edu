<template>
  <div class="practice-page" :class="{ 'dark-mode': isDark }">
    <div class="practice-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 1024 1024" width="20" height="20">
          <path d="M669.6 849.6L368.8 548.8c-12-12-12-32 0-44l300.8-300.8c12-12 32-12 44 0s12 32 0 44L436 526.8l277.6 278.8c12 12 12 32 0 44-6 6-14 8.4-22 8.4s-16-2.8-22-8.4z" fill="currentColor"/>
        </svg>
        返回主页
      </button>
      <h1 class="page-title">动手做 - 手写数字识别练习</h1>
      <p class="page-subtitle">通过多种题型巩固知识，从代码理解到实践应用全面提升</p>
    </div>

    <div class="difficulty-section">
      <h3 class="section-label">
        <svg viewBox="0 0 1024 1024" width="18" height="18">
          <path d="M512 64L128 256v256c0 189.6 130.4 366.8 384 448 253.6-81.2 384-258.4 384-448V256L512 64z" fill="currentColor"/>
        </svg>
        难度选择
      </h3>
      <div class="difficulty-badges">
        <button
          v-for="(label, index) in difficultyLabels"
          :key="index"
          class="difficulty-badge"
          :class="{ active: globalDifficulty === index + 1 }"
          :style="globalDifficulty === index + 1 ? { borderColor: difficultyColors[index], color: difficultyColors[index], background: difficultyColors[index] + '18' } : {}"
          @click="setGlobalDifficulty(index + 1)"
        >
          {{ label }}
        </button>
      </div>
    </div>

    <div class="practice-grid">
      <div
        v-for="(mode, index) in practiceModes"
        :key="mode.type"
        class="practice-card"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <div class="card-glow" :style="{ background: `radial-gradient(circle at 50% 0%, ${mode.accent}25, transparent 70%)` }"></div>
        <div class="card-top-bar" :style="{ background: `linear-gradient(90deg, ${mode.accent}, transparent)` }"></div>
        <div class="card-icon" :style="{ background: `${mode.accent}18`, boxShadow: `0 4px 20px ${mode.accent}30` }">
          <svg v-if="mode.type === 'code_understanding'" viewBox="0 0 1024 1024" width="32" height="32">
            <path d="M316.8 748.8L64 512l252.8-236.8 44.8 48L172.8 512l188.8 188.8-44.8 48z m390.4 0l-44.8-48L851.2 512 662.4 323.2l44.8-48L960 512 707.2 748.8z" :fill="mode.accent"/>
          </svg>
          <svg v-else-if="mode.type === 'choice'" viewBox="0 0 1024 1024" width="32" height="32">
            <path d="M384 768L128 512l60.8-60.8L384 646.4 835.2 195.2 896 256 384 768z" :fill="mode.accent"/>
            <path d="M896 512H640v-64h256v64z m0 192H576v-64h320v64z m0 192H384v-64h512v64z" :fill="mode.accent" opacity="0.5"/>
          </svg>
          <svg v-else viewBox="0 0 1024 1024" width="32" height="32">
            <path d="M832 128H192c-35.2 0-64 28.8-64 64v640c0 35.2 28.8 64 64 64h640c35.2 0 64-28.8 64-64V192c0-35.2-28.8-64-64-64z m0 704H192V192h640v640z" :fill="mode.accent"/>
            <path d="M608 352c0-17.6-14.4-32-32-32H352c-17.6 0-32 14.4-32 32s14.4 32 32 32h224c17.6 0 32-14.4 32-32z m64 128c0-17.6-14.4-32-32-32H352c-17.6 0-32 14.4-32 32s14.4 32 32 32h288c17.6 0 32-14.4 32-32z m0 128c0-17.6-14.4-32-32-32H352c-17.6 0-32 14.4-32 32s14.4 32 32 32h288c17.6 0 32-14.4 32-32z" :fill="mode.accent"/>
          </svg>
        </div>
        <h2 class="card-title">{{ mode.title }}</h2>
        <p class="card-desc">{{ mode.description }}</p>
        <div class="card-difficulty">
          <span class="card-difficulty-label">难度</span>
          <div class="card-difficulty-dots">
            <button
              v-for="i in 5"
              :key="i"
              class="difficulty-dot"
              :class="{ filled: i <= (cardDifficulties[mode.type] || globalDifficulty) }"
              :style="i <= (cardDifficulties[mode.type] || globalDifficulty) ? { background: mode.accent, boxShadow: `0 0 6px ${mode.accent}60` } : {}"
              @click="setCardDifficulty(mode.type, i)"
            ></button>
          </div>
          <span class="card-difficulty-text">{{ difficultyLabels[(cardDifficulties[mode.type] || globalDifficulty) - 1] }}</span>
        </div>
        <button
          class="start-btn"
          :style="{ background: `linear-gradient(135deg, ${mode.accent}, ${mode.accentEnd})`, boxShadow: `0 4px 15px ${mode.accent}40` }"
          :disabled="isLoading"
          @click="startPractice(mode.type)"
        >
          <span v-if="isLoading && loadingType === mode.type" class="btn-spinner"></span>
          <span v-else>开始练习</span>
        </button>
      </div>
    </div>

    <div class="quick-start-section">
      <h3 class="section-label">
        <svg viewBox="0 0 1024 1024" width="18" height="18">
          <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64z m0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z" fill="currentColor"/>
          <path d="M512 256v256l170.6 102.4" fill="none" stroke="currentColor" stroke-width="60" stroke-linecap="round"/>
        </svg>
        快速开始
      </h3>
      <div class="quick-start-grid">
        <button
          class="quick-start-card"
          :class="{ disabled: isLoading }"
          @click="quickStart('comprehensive')"
        >
          <div class="quick-icon comprehensive-icon">
            <svg viewBox="0 0 1024 1024" width="24" height="24">
              <path d="M316.8 748.8L64 512l252.8-236.8 44.8 48L172.8 512l188.8 188.8-44.8 48z m390.4 0l-44.8-48L851.2 512 662.4 323.2l44.8-48L960 512 707.2 748.8z" fill="currentColor"/>
            </svg>
          </div>
          <div class="quick-info">
            <span class="quick-title">综合练习</span>
            <span class="quick-desc">混合所有题型，全面检验</span>
          </div>
          <span class="quick-badge">推荐</span>
        </button>
        <button
          class="quick-start-card"
          :class="{ disabled: isLoading }"
          @click="quickStart('code_focus')"
        >
          <div class="quick-icon code-focus-icon">
            <svg viewBox="0 0 1024 1024" width="24" height="24">
              <path d="M316.8 748.8L64 512l252.8-236.8 44.8 48L172.8 512l188.8 188.8-44.8 48z m390.4 0l-44.8-48L851.2 512 662.4 323.2l44.8-48L960 512 707.2 748.8z" fill="currentColor"/>
            </svg>
          </div>
          <div class="quick-info">
            <span class="quick-title">代码专练</span>
            <span class="quick-desc">专注核心代码理解能力</span>
          </div>
        </button>
        <button
          class="quick-start-card"
          :class="{ disabled: isLoading }"
          @click="quickStart('knowledge_focus')"
        >
          <div class="quick-icon knowledge-focus-icon">
            <svg viewBox="0 0 1024 1024" width="24" height="24">
              <path d="M384 768L128 512l60.8-60.8L384 646.4 835.2 195.2 896 256 384 768z" fill="currentColor"/>
            </svg>
          </div>
          <div class="quick-info">
            <span class="quick-title">知识专练</span>
            <span class="quick-desc">巩固理论知识与概念</span>
          </div>
        </button>
        <button
          class="quick-start-card"
          :class="{ disabled: isLoading }"
          @click="quickStart('challenge')"
        >
          <div class="quick-icon challenge-icon">
            <svg viewBox="0 0 1024 1024" width="24" height="24">
              <path d="M512 64L128 256v256c0 189.6 130.4 366.8 384 448 253.6-81.2 384-258.4 384-448V256L512 64z" fill="currentColor"/>
            </svg>
          </div>
          <div class="quick-info">
            <span class="quick-title">挑战模式</span>
            <span class="quick-desc">高难度题目，极限挑战</span>
          </div>
          <span class="quick-badge hard">困难</span>
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      <p class="loading-text">正在生成练习题...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = ''

export default {
  name: 'PracticePage',
  data() {
    return {
      globalDifficulty: 3,
      isDark: false,
      cardDifficulties: {},
      isLoading: false,
      loadingType: '',
      difficultyLabels: ['入门', '初级', '中级', '高级', '专家'],
      difficultyColors: ['#43e97b', '#38f9d7', '#667eea', '#f093fb', '#fa709a'],
      practiceModes: [
        {
          type: 'code_understanding',
          title: '核心代码理解题',
          description: '阅读手写数字识别项目的关键代码片段，理解其功能与逻辑，提升代码阅读与分析能力。',
          accent: '#43e97b',
          accentEnd: '#38f9d7'
        },
        {
          type: 'choice',
          title: '相关知识选择题',
          description: '涵盖CNN原理、MNIST数据集、模型训练与评估等知识点，巩固理论基础。',
          accent: '#667eea',
          accentEnd: '#764ba2'
        },
        {
          type: 'short_answer',
          title: '简答题',
          description: '针对手写数字识别的核心概念与实现细节进行深入思考与表达，锻炼综合理解能力。',
          accent: '#f093fb',
          accentEnd: '#fa709a'
        }
      ]
    }
  },
  methods: {
    checkDarkMode() {
      this.isDark = document.documentElement.classList.contains('Dark') || document.documentElement.getAttribute('data-theme') === 'Dark'
    },
    goBack() {
      this.$router.push('/')
    },
    setGlobalDifficulty(level) {
      this.globalDifficulty = level
    },
    setCardDifficulty(type, level) {
      this.cardDifficulties[type] = level
    },
    getUsername() {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        return user && user.username ? user.username : 'guest'
      } catch (e) {
        return 'guest'
      }
    },
    async startPractice(type) {
      if (this.isLoading) return
      const difficulty = this.cardDifficulties[type] || this.globalDifficulty
      this.isLoading = true
      this.loadingType = type
      try {
        const res = await axios.post(`${API_BASE}/api/practice/generate`, {
          topic: '手写数字识别',
          type: type,
          difficulty: difficulty,
          count: 5
        })
        const resData = res.data
        if (resData && resData.success && resData.data && resData.data.questions) {
          this.$router.push({
            path: '/practice/quiz',
            query: {
              data: encodeURIComponent(JSON.stringify({
                questions: resData.data.questions,
                type: resData.data.type,
                difficulty: resData.data.difficulty,
                topic: resData.data.topic
              })),
              username: this.getUsername()
            }
          })
        } else {
          alert('生成练习题失败：返回数据格式异常')
        }
      } catch (e) {
        console.error('生成练习题失败:', e)
        alert('生成练习题失败，请检查后端服务是否启动')
      } finally {
        this.isLoading = false
        this.loadingType = ''
      }
    },
    async quickStart(preset) {
      if (this.isLoading) return
      const presets = {
        comprehensive: { type: 'mixed', difficulty: this.globalDifficulty },
        code_focus: { type: 'code_understanding', difficulty: this.globalDifficulty },
        knowledge_focus: { type: 'choice', difficulty: this.globalDifficulty },
        challenge: { type: 'mixed', difficulty: 5 }
      }
      const config = presets[preset]
      if (!config) return
      this.isLoading = true
      this.loadingType = preset
      try {
        const res = await axios.post(`${API_BASE}/api/practice/generate`, {
          topic: '手写数字识别',
          type: config.type,
          difficulty: config.difficulty,
          count: 5
        })
        const resData = res.data
        if (resData && resData.success && resData.data && resData.data.questions) {
          this.$router.push({
            path: '/practice/quiz',
            query: {
              data: encodeURIComponent(JSON.stringify({
                questions: resData.data.questions,
                type: resData.data.type,
                difficulty: resData.data.difficulty,
                topic: resData.data.topic
              })),
              username: this.getUsername()
            }
          })
        } else {
          alert('生成练习题失败：返回数据格式异常')
        }
      } catch (e) {
        console.error('生成练习题失败:', e)
        alert('生成练习题失败，请检查后端服务是否启动')
      } finally {
        this.isLoading = false
        this.loadingType = ''
      }
    }
  },
  mounted() {
    this.checkDarkMode()
    this._darkObserver = new MutationObserver(() => { this.checkDarkMode() })
    this._darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
  },
  beforeUnmount() {
    if (this._darkObserver) this._darkObserver.disconnect()
  }
}
</script>

<style scoped>
.practice-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #0d0d2b 100%);
  padding: 24px;
  color: #fff;
  position: relative;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.practice-header {
  text-align: center;
  margin-bottom: 36px;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  color: #ccc;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
  transform: translateX(-2px);
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  animation: gradient-flow 5s ease infinite;
  background-size: 200% 100%;
}

@keyframes gradient-flow {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.page-subtitle {
  color: #999;
  font-size: 15px;
}

.difficulty-section {
  max-width: 900px;
  margin: 0 auto 32px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #ccc;
  margin-bottom: 14px;
}

.section-label svg {
  color: #667eea;
}

.difficulty-badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.difficulty-badge {
  padding: 6px 18px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #aaa;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.difficulty-badge:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  animation: pulse 0.6s ease;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.difficulty-badge.active {
  font-weight: 600;
  border-width: 1.5px;
}

.practice-grid {
  max-width: 900px;
  margin: 0 auto 40px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.practice-card {
  position: relative;
  padding: 28px 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  overflow: hidden;
  transition: all 0.4s ease;
  animation: fadeInUp 0.6s ease backwards;
}

.practice-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 120px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.practice-card:hover .card-glow {
  opacity: 1;
}

.card-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.practice-card:hover .card-top-bar {
  opacity: 1;
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
  transition: transform 0.3s ease;
}

.practice-card:hover .card-icon {
  transform: scale(1.08);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #eee;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 13px;
  color: #999;
  line-height: 1.6;
  margin-bottom: 18px;
  flex: 1;
}

.card-difficulty {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  width: 100%;
  justify-content: center;
}

.card-difficulty-label {
  font-size: 12px;
  color: #888;
}

.card-difficulty-dots {
  display: flex;
  gap: 5px;
}

.difficulty-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.difficulty-dot:hover {
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.2);
}

.difficulty-dot.filled {
  border-color: transparent;
}

.card-difficulty-text {
  font-size: 12px;
  color: #aaa;
  min-width: 32px;
}

.start-btn {
  width: 100%;
  padding: 12px 0;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.start-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.start-btn:hover:not(:disabled)::before {
  width: 200%;
  height: 200%;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.start-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.quick-start-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
}

.quick-start-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.quick-start-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  position: relative;
  color: #fff;
}

.quick-start-card:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.quick-start-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.comprehensive-icon {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.2), rgba(102, 126, 234, 0.2));
  color: #43e97b;
}

.code-focus-icon {
  background: rgba(67, 233, 123, 0.15);
  color: #43e97b;
}

.knowledge-focus-icon {
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
}

.challenge-icon {
  background: rgba(250, 112, 154, 0.15);
  color: #fa709a;
}

.quick-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.quick-title {
  font-size: 14px;
  font-weight: 600;
  color: #eee;
}

.quick-desc {
  font-size: 12px;
  color: #999;
}

.quick-badge {
  padding: 2px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(67, 233, 123, 0.15);
  color: #43e97b;
  border: 1px solid rgba(67, 233, 123, 0.25);
  flex-shrink: 0;
}

.quick-badge.hard {
  background: rgba(250, 112, 154, 0.15);
  color: #fa709a;
  border-color: rgba(250, 112, 154, 0.25);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(12, 12, 29, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeInUp 0.3s ease;
}

.loading-spinner {
  position: relative;
  width: 60px;
  height: 60px;
  margin-bottom: 20px;
}

.spinner-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spin 1.2s linear infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #43e97b;
  animation-duration: 1.2s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #667eea;
  animation-duration: 1.6s;
  animation-direction: reverse;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #f093fb;
  animation-duration: 2s;
}

.loading-text {
  font-size: 15px;
  color: #ccc;
  animation: pulse 1.5s ease-in-out infinite;
}

@media (max-width: 768px) {
  .practice-page {
    padding: 16px;
  }

  .practice-header {
    margin-bottom: 24px;
  }

  .back-btn {
    position: static;
    margin-bottom: 12px;
    display: inline-flex;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .practice-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .practice-card {
    padding: 22px 20px;
  }

  .card-icon {
    width: 52px;
    height: 52px;
    margin-bottom: 14px;
  }

  .card-title {
    font-size: 16px;
  }

  .card-desc {
    font-size: 12px;
  }

  .difficulty-section {
    padding: 16px 18px;
  }

  .quick-start-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .practice-page {
    padding: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .difficulty-badges {
    gap: 6px;
  }

  .difficulty-badge {
    padding: 5px 12px;
    font-size: 12px;
  }

  .practice-card {
    padding: 18px 16px;
  }

  .card-icon {
    width: 46px;
    height: 46px;
    border-radius: 12px;
  }

  .card-icon svg {
    width: 24px;
    height: 24px;
  }

  .card-title {
    font-size: 15px;
  }

  .start-btn {
    padding: 10px 0;
    font-size: 14px;
  }

  .quick-start-card {
    padding: 12px 14px;
  }

  .quick-icon {
    width: 38px;
    height: 38px;
  }

  .quick-icon svg {
    width: 20px;
    height: 20px;
  }
}

.practice-page:not(.dark-mode) {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%);
  color: #1a1a2e;
}

.practice-page:not(.dark-mode) .back-btn {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #4a4a6a;
}

.practice-page:not(.dark-mode) .back-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  color: #1a1a2e;
  transform: translateX(-2px);
}

.practice-page:not(.dark-mode) .page-subtitle {
  color: #6b7280;
}

.practice-page:not(.dark-mode) .difficulty-section {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.practice-page:not(.dark-mode) .section-label {
  color: #1a1a2e;
}

.practice-page:not(.dark-mode) .difficulty-badge {
  border-color: rgba(0, 0, 0, 0.12);
  background: rgba(0, 0, 0, 0.03);
  color: #6b7280;
}

.practice-page:not(.dark-mode) .difficulty-badge:hover {
  background: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.2);
  color: #1a1a2e;
}

.practice-page:not(.dark-mode) .practice-card {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.practice-page:not(.dark-mode) .practice-card:hover {
  border-color: rgba(0, 0, 0, 0.15);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.practice-page:not(.dark-mode) .card-title {
  color: #1a1a2e;
}

.practice-page:not(.dark-mode) .card-desc {
  color: #6b7280;
}

.practice-page:not(.dark-mode) .card-difficulty-label {
  color: #6b7280;
}

.practice-page:not(.dark-mode) .difficulty-dot {
  border-color: rgba(0, 0, 0, 0.15);
}

.practice-page:not(.dark-mode) .difficulty-dot:hover {
  border-color: rgba(0, 0, 0, 0.35);
}

.practice-page:not(.dark-mode) .card-difficulty-text {
  color: #6b7280;
}

.practice-page:not(.dark-mode) .quick-start-section {
  background: rgba(255, 255, 255, 0.5);
  border-color: rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(10px);
}

.practice-page:not(.dark-mode) .quick-start-card {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(0, 0, 0, 0.08);
  color: #1a1a2e;
}

.practice-page:not(.dark-mode) .quick-start-card:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.85);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}

.practice-page:not(.dark-mode) .quick-title {
  color: #1a1a2e;
}

.practice-page:not(.dark-mode) .quick-desc {
  color: #6b7280;
}

.practice-page:not(.dark-mode) .loading-overlay {
  background: rgba(240, 244, 255, 0.85);
}

.practice-page:not(.dark-mode) .loading-text {
  color: #4a4a6a;
}
</style>
