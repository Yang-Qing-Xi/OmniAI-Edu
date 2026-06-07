<template>
  <Transition name="overlay">
    <div class="explanation-overlay" :class="{ 'dark-mode': isDark }" v-if="visible" @click.self="close">
      <div class="explanation-modal">
        <div class="modal-header">
          <div class="header-left">
            <span class="header-icon">🔬</span>
            <h2 class="header-title">识别过程详解</h2>
            <span class="header-badge" v-if="!isLoading && steps.length">{{ steps.length }}个步骤</span>
          </div>
          <button class="close-btn" @click="close">
            <svg viewBox="0 0 1024 1024" width="20" height="20"><path d="M563.8 512l262.5-312.9c4.4-5.2 0.7-13.1-6.1-13.1h-79.8c-4.7 0-9.2 2.1-12.3 5.7L512 442.2 295.9 191.7c-3-3.6-7.5-5.7-12.3-5.7H203.8c-6.8 0-10.5 7.9-6.1 13.1L460.2 512 197.7 824.9c-4.4 5.2-0.7 13.1 6.1 13.1h79.8c4.7 0 9.2-2.1 12.3-5.7L512 581.8l216.1 250.5c3 3.6 7.5 5.7 12.3 5.7h79.8c6.8 0 10.5-7.9 6.1-13.1L563.8 512z" fill="currentColor"/></svg>
          </button>
        </div>

        <div class="loading-state" v-if="isLoading">
          <div class="loading-spinner"></div>
          <p>正在分析识别过程...</p>
        </div>

        <div class="error-state" v-else-if="errorMessage">
          <div class="error-icon">⚠️</div>
          <p>{{ errorMessage }}</p>
          <button class="retry-btn" @click="fetchExplanation">重新加载</button>
        </div>

        <div class="modal-body" v-else-if="steps.length">
          <div class="flowchart-panel">
            <div class="flowchart-scroll" ref="flowchartScroll">
              <template v-for="(phase, pIdx) in phases" :key="phase.id">
                <div class="phase-header" :class="{ active: currentPhase === phase.id }">
                  <span class="phase-icon">{{ phase.icon }}</span>
                  <span class="phase-name">{{ phase.name }}</span>
                </div>
                <div class="phase-steps">
                  <div
                    v-for="(step, sIdx) in phase.steps"
                    :key="step.id"
                    class="flow-node"
                    :class="{
                      active: currentStep === step.globalIndex,
                      completed: currentStep > step.globalIndex,
                      pending: currentStep < step.globalIndex
                    }"
                    :ref="'node-' + step.globalIndex"
                    @click="goToStep(step.globalIndex)"
                  >
                    <div class="node-connector-top"
                         v-if="sIdx > 0 || pIdx > 0"
                         :class="{ filled: currentStep >= step.globalIndex }">
                      <div class="connector-flow-dot" v-if="currentStep === step.globalIndex"></div>
                    </div>
                    <div class="node-dot">
                      <svg v-if="currentStep > step.globalIndex" viewBox="0 0 1024 1024" width="12" height="12">
                        <path d="M912 190h-69.9c-9.8 0-19.1 4.5-25.1 12.2L404.7 724.5 207 474c-6.1-7.7-15.3-12.2-25.1-12.2H112c-6.7 0-10.4 7.7-6.3 12.9l281.9 356c12.8 16.2 37.4 16.2 50.3 0l508.1-643.7c4-5.2 0.4-12.9-6.3-12.9z" fill="currentColor"/>
                      </svg>
                      <span v-else-if="currentStep === step.globalIndex" class="node-pulse"></span>
                      <span v-else class="node-number">{{ step.globalIndex + 1 }}</span>
                    </div>
                    <div class="node-label">{{ step.shortName }}</div>
                    <div class="node-connector-bottom"
                         v-if="!(pIdx === phases.length - 1 && sIdx === phase.steps.length - 1)"
                         :class="{ filled: currentStep > step.globalIndex }">
                      <div class="connector-flow-dot" v-if="currentStep === step.globalIndex"></div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <div class="detail-panel">
            <Transition name="detail-slide" mode="out-in">
              <div class="detail-content" :key="currentStep" v-if="currentStepData">
                <div class="detail-header">
                  <div class="detail-step-badge">步骤 {{ currentStep + 1 }}/{{ steps.length }}</div>
                  <h3 class="detail-title">{{ currentStepData.name }}</h3>
                </div>

                <p class="detail-desc">{{ currentStepData.description }}</p>

                <div class="preprocessing-pipeline" v-if="preprocessingSteps.length && currentStepData.phase === 'preprocessing'">
                  <h4 class="detail-section-title">🔄 预处理流水线</h4>
                  <div class="pipeline-track">
                    <template v-for="(ps, idx) in preprocessingSteps" :key="ps.id">
                      <div class="pipeline-step"
                           :class="{ active: currentStep === ps.globalIndex, completed: currentStep > ps.globalIndex }"
                           @click="goToStep(ps.globalIndex)">
                        <div class="pipeline-img-box">
                          <img :src="'data:image/png;base64,' + ps.image" alt="" v-if="ps.image" />
                          <div class="pipeline-img-placeholder" v-else>{{ ps.shortName }}</div>
                          <div class="pipeline-step-overlay" v-if="currentStep < ps.globalIndex"></div>
                        </div>
                        <div class="pipeline-step-name">{{ ps.shortName }}</div>
                      </div>
                      <div class="pipeline-arrow" v-if="idx < preprocessingSteps.length - 1"
                           :class="{ filled: currentStep > ps.globalIndex }">
                        <svg viewBox="0 0 24 24" width="16" height="16"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z" fill="currentColor"/></svg>
                      </div>
                    </template>
                  </div>
                </div>

                <div class="detail-image-section" v-if="currentStepData.image">
                  <h4 class="detail-section-title">📊 当前步骤处理结果</h4>
                  <div class="detail-image-wrapper">
                    <img :src="'data:image/png;base64,' + currentStepData.image" alt="处理结果" />
                  </div>
                  <div class="detail-shape" v-if="currentStepData.shape_info">
                    数据尺寸：{{ currentStepData.shape_info }}
                  </div>
                </div>

                <div class="detail-principle-section">
                  <h4 class="detail-section-title">💡 原理解释</h4>
                  <p class="detail-principle">{{ currentStepData.principle }}</p>
                </div>

                <div class="detail-stats-section" v-if="currentStepData.stats">
                  <h4 class="detail-section-title">📈 数据统计</h4>
                  <div class="stats-grid">
                    <div class="stat-group">
                      <div class="stat-group-title">归一化前</div>
                      <div class="stat-item" v-for="(val, key) in currentStepData.stats.before" :key="'b'+key">
                        <span class="stat-label">{{ statLabelMap[key] || key }}</span>
                        <span class="stat-value">{{ val }}</span>
                      </div>
                    </div>
                    <div class="stat-group">
                      <div class="stat-group-title">归一化后</div>
                      <div class="stat-item" v-for="(val, key) in currentStepData.stats.after" :key="'a'+key">
                        <span class="stat-label">{{ statLabelMap[key] || key }}</span>
                        <span class="stat-value">{{ val }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="detail-activations-section" v-if="currentStepData.top_activations">
                  <h4 class="detail-section-title">🔥 Top-10 激活神经元</h4>
                  <div class="activation-bars">
                    <div class="activation-item" v-for="(act, idx) in currentStepData.top_activations" :key="idx">
                      <span class="act-index">#{{ act.index }}</span>
                      <div class="act-bar-bg">
                        <div class="act-bar-fill" :style="{ width: activationWidth(act.value) + '%' }"></div>
                      </div>
                      <span class="act-value">{{ act.value.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>

                <div class="detail-logits-section" v-if="currentStepData.logits">
                  <h4 class="detail-section-title">📊 原始分数 (Logits)</h4>
                  <div class="logit-bars">
                    <div class="logit-item" v-for="(val, idx) in currentStepData.logits" :key="idx"
                         :class="{ highlight: result && idx === result.digit }">
                      <span class="logit-label">{{ idx }}</span>
                      <div class="logit-bar-bg">
                        <div class="logit-bar-fill" :style="{ width: logitWidth(val, currentStepData.logits) + '%' }"></div>
                      </div>
                      <span class="logit-value">{{ val.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>

                <div class="detail-probabilities-section" v-if="currentStepData.probabilities && (currentStepData.id === 'softmax' || currentStepData.id === 'result')">
                  <h4 class="detail-section-title">📊 概率分布</h4>
                  <div class="prob-bars-detail">
                    <div class="prob-item-detail" v-for="(prob, idx) in currentStepData.probabilities" :key="idx"
                         :class="{ highlight: result && idx === result.digit }">
                      <span class="prob-label-detail">{{ idx }}</span>
                      <div class="prob-bar-bg-detail">
                        <div class="prob-bar-fill-detail" :style="{ width: prob + '%' }"></div>
                      </div>
                      <span class="prob-value-detail">{{ prob.toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>

                <div class="detail-result-section" v-if="currentStepData.id === 'result'">
                  <div class="result-display">
                    <div class="result-digit-large">{{ currentStepData.digit }}</div>
                    <div class="result-confidence-large">置信度 {{ currentStepData.confidence.toFixed(1) }}%</div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <div class="modal-footer" v-if="steps.length">
          <div class="controls-left">
            <button class="ctrl-btn" @click="prevStep" :disabled="currentStep <= 0" title="上一步">
              <svg viewBox="0 0 1024 1024" width="16" height="16"><path d="M689 165.1L308.5 497.7c-10.4 9.4-10.4 25.2 0 34.6L689 864.9c14.5 13.1 37 2.2 37-17.3V182.4c0-19.5-22.5-30.4-37-17.3z" fill="currentColor"/></svg>
            </button>
            <button class="ctrl-btn play-btn" @click="togglePlay" :title="isPlaying ? '暂停' : '播放'">
              <svg v-if="!isPlaying" viewBox="0 0 1024 1024" width="18" height="18"><path d="M376.5 136.7l448 344.6c13.4 10.3 13.4 30.8 0 41.1l-448 344.6c-17.7 13.6-43.5 0.8-43.5-20.5V157.2c0-21.3 25.8-34.1 43.5-20.5z" fill="currentColor"/></svg>
              <svg v-else viewBox="0 0 1024 1024" width="18" height="18"><path d="M368 176v672c0 17.7 14.3 32 32 32s32-14.3 32-32V176c0-17.7-14.3-32-32-32s-32 14.3-32 32z m224 0v672c0 17.7 14.3 32 32 32s32-14.3 32-32V176c0-17.7-14.3-32-32-32s-32 14.3-32 32z" fill="currentColor"/></svg>
            </button>
            <button class="ctrl-btn" @click="nextStep" :disabled="currentStep >= steps.length - 1" title="下一步">
              <svg viewBox="0 0 1024 1024" width="16" height="16"><path d="M335 165.1l380.5 332.6c10.4 9.4 10.4 25.2 0 34.6L335 864.9c-14.5 13.1-37 2.2-37-17.3V182.4c0-19.5 22.5-30.4 37-17.3z" fill="currentColor"/></svg>
            </button>
          </div>
          <div class="controls-center">
            <button class="speed-btn" v-for="speed in speeds" :key="speed"
                    :class="{ active: playbackSpeed === speed }"
                    @click="setSpeed(speed)">
              {{ speed }}x
            </button>
          </div>
          <div class="controls-right">
            <div class="progress-bar-mini">
              <div class="progress-fill-mini" :style="{ width: ((currentStep + 1) / steps.length * 100) + '%' }"></div>
            </div>
            <span class="step-counter">{{ currentStep + 1 }} / {{ steps.length }}</span>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script>
import axios from 'axios'

const API_BASE = ''

export default {
  name: 'RecognitionExplanation',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    imageData: {
      type: String,
      default: ''
    }
  },
  emits: ['close'],
  data() {
    return {
      steps: [],
      currentStep: 0,
      isPlaying: false,
      playbackSpeed: 1,
      isLoading: false,
      errorMessage: '',
      playTimer: null,
      result: null,
      speeds: [0.5, 1, 2],
      statLabelMap: { min: '最小值', max: '最大值', mean: '均值' },
      isDark: false
    }
  },
  computed: {
    currentStepData() {
      if (this.steps.length === 0) return null
      return this.steps[this.currentStep]
    },
    currentPhase() {
      if (!this.currentStepData) return ''
      return this.currentStepData.phase
    },
    preprocessingSteps() {
      const result = []
      this.steps.forEach((s, i) => {
        if (s.phase === 'preprocessing') {
          const shortName = s.name.includes('·') ? s.name.split('·')[0].trim() : s.name
          result.push({ ...s, globalIndex: i, shortName })
        }
      })
      return result
    },
    phases() {
      const phaseConfig = [
        { id: 'preprocessing', name: '图像预处理', icon: '📥' },
        { id: 'feature_extraction', name: '卷积特征提取', icon: '🔍' },
        { id: 'classification', name: '全连接分类', icon: '🧠' },
        { id: 'output', name: '结果输出', icon: '📊' }
      ]

      return phaseConfig.map(phase => {
        const phaseSteps = []
        this.steps.forEach((s, i) => {
          if (s.phase === phase.id) {
            const shortName = s.name.includes('·') ? s.name.split('·')[0].trim() : s.name
            phaseSteps.push({ ...s, globalIndex: i, shortName })
          }
        })
        return { ...phase, steps: phaseSteps }
      }).filter(p => p.steps.length > 0)
    }
  },
  watch: {
    visible(val) {
      if (val && this.imageData) {
        this.fetchExplanation()
        this.checkDarkMode()
      }
      if (!val) {
        this.stopAutoPlay()
        this.steps = []
        this.currentStep = 0
      }
    },
    currentStep() {
      this.$nextTick(() => {
        this.scrollToActiveNode()
      })
    }
  },
  mounted() {
    this._darkObserver = new MutationObserver(() => { this.checkDarkMode() })
    this._darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
    this.checkDarkMode()
  },
  beforeUnmount() {
    this.stopAutoPlay()
    if (this._darkObserver) this._darkObserver.disconnect()
  },
  methods: {
    async fetchExplanation() {
      this.isLoading = true
      this.errorMessage = ''
      this.steps = []
      this.currentStep = 0

      try {
        const res = await axios.post(`${API_BASE}/api/digit/explain`, {
          image: this.imageData
        }, { timeout: 15000 })

        this.steps = res.data.steps
        this.result = res.data.result

        this.$nextTick(() => {
          this.startAutoPlay()
        })
      } catch (error) {
        console.error('获取详解失败:', error)
        this.errorMessage = '获取识别过程详解失败，请确保后端服务正在运行'
      } finally {
        this.isLoading = false
      }
    },
    close() {
      this.stopAutoPlay()
      this.$emit('close')
    },
    checkDarkMode() {
      this.isDark = document.documentElement.classList.contains('Dark') || document.documentElement.getAttribute('data-theme') === 'Dark'
    },
    togglePlay() {
      if (this.isPlaying) {
        this.stopAutoPlay()
      } else {
        if (this.currentStep >= this.steps.length - 1) {
          this.currentStep = 0
        }
        this.startAutoPlay()
      }
    },
    startAutoPlay() {
      this.stopAutoPlay()
      this.isPlaying = true
      this.scheduleNextStep()
    },
    stopAutoPlay() {
      this.isPlaying = false
      if (this.playTimer) {
        clearTimeout(this.playTimer)
        this.playTimer = null
      }
    },
    scheduleNextStep() {
      const duration = 2500 / this.playbackSpeed
      this.playTimer = setTimeout(() => {
        if (this.currentStep < this.steps.length - 1) {
          this.currentStep++
          this.scheduleNextStep()
        } else {
          this.isPlaying = false
        }
      }, duration)
    },
    prevStep() {
      this.stopAutoPlay()
      if (this.currentStep > 0) {
        this.currentStep--
      }
    },
    nextStep() {
      this.stopAutoPlay()
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++
      }
    },
    goToStep(index) {
      this.stopAutoPlay()
      this.currentStep = index
    },
    setSpeed(speed) {
      this.playbackSpeed = speed
      if (this.isPlaying) {
        this.stopAutoPlay()
        this.startAutoPlay()
      }
    },
    scrollToActiveNode() {
      const el = this.$refs['node-' + this.currentStep]
      if (el && el[0]) {
        el[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    },
    activationWidth(val) {
      if (!this.currentStepData || !this.currentStepData.top_activations) return 0
      const maxVal = Math.max(...this.currentStepData.top_activations.map(a => Math.abs(a.value)))
      return Math.min(100, (Math.abs(val) / (maxVal + 0.001)) * 100)
    },
    logitWidth(val, logits) {
      const minVal = Math.min(...logits)
      const maxVal = Math.max(...logits)
      const range = maxVal - minVal + 0.001
      return Math.max(2, ((val - minVal) / range) * 100)
    }
  }
}
</script>

<style scoped>
.preprocessing-pipeline {
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 14px;
}

.pipeline-track {
  display: flex;
  align-items: flex-start;
  gap: 0;
  overflow-x: auto;
  padding-bottom: 4px;
}

.pipeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pipeline-img-box {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.pipeline-img-box img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  image-rendering: pixelated;
}

.pipeline-img-placeholder {
  font-size: 10px;
  color: #555;
  text-align: center;
  padding: 4px;
}

.pipeline-step-overlay {
  position: absolute;
  inset: 0;
  background: rgba(12, 12, 29, 0.6);
  border-radius: 6px;
}

.pipeline-step.completed .pipeline-img-box {
  border-color: rgba(67, 233, 123, 0.3);
}

.pipeline-step.active .pipeline-img-box {
  border-color: #43e97b;
  box-shadow: 0 0 12px rgba(67, 233, 123, 0.3);
  transform: scale(1.08);
}

.pipeline-step-name {
  text-align: center;
  font-size: 10px;
  color: #888;
  margin-top: 4px;
  max-width: 80px;
  line-height: 1.2;
  word-break: keep-all;
  transition: color 0.3s;
}

.pipeline-step.active .pipeline-step-name {
  color: #43e97b;
  font-weight: 600;
}

.pipeline-step.completed .pipeline-step-name {
  color: #aaa;
}

.pipeline-arrow {
  color: rgba(255, 255, 255, 0.15);
  margin: 0 2px;
  align-self: center;
  flex-shrink: 0;
  transition: color 0.3s;
}

.pipeline-arrow.filled {
  color: rgba(67, 233, 123, 0.5);
}

.explanation-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.explanation-modal {
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #0d0d2b 100%);
  border: 1px solid rgba(67, 233, 123, 0.2);
  border-radius: 20px;
  width: 100%;
  max-width: 960px;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(67, 233, 123, 0.08);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 22px;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.header-badge {
  font-size: 11px;
  color: #43e97b;
  background: rgba(67, 233, 123, 0.1);
  border: 1px solid rgba(67, 233, 123, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 100, 100, 0.15);
  border-color: rgba(255, 100, 100, 0.4);
  color: #ff6464;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
  color: #888;
  font-size: 14px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(67, 233, 123, 0.15);
  border-top-color: #43e97b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 36px;
}

.retry-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid rgba(67, 233, 123, 0.3);
  background: rgba(67, 233, 123, 0.1);
  color: #43e97b;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.retry-btn:hover {
  background: rgba(67, 233, 123, 0.2);
}

.modal-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.flowchart-panel {
  width: 200px;
  flex-shrink: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  overflow-y: auto;
  padding: 16px 12px;
}

.flowchart-scroll {
  display: flex;
  flex-direction: column;
}

.phase-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  margin-bottom: 4px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s;
}

.phase-header.active {
  background: rgba(67, 233, 123, 0.08);
}

.phase-icon {
  font-size: 13px;
}

.phase-name {
  font-size: 11px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.phase-header.active .phase-name {
  color: #43e97b;
}

.phase-steps {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.node-connector-top,
.node-connector-bottom {
  width: 2px;
  height: 16px;
  background: rgba(255, 255, 255, 0.1);
  transition: background 0.5s ease;
  position: relative;
  overflow: hidden;
}

.node-connector-top.filled,
.node-connector-bottom.filled {
  background: linear-gradient(180deg, #43e97b, #38f9d7);
}

.connector-flow-dot {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #43e97b;
  box-shadow: 0 0 6px #43e97b;
  left: 50%;
  transform: translateX(-50%);
  animation: flowDot 1.2s ease-in-out infinite;
}

.node-connector-top .connector-flow-dot {
  bottom: 0;
  animation-name: flowDotUp;
}

.node-connector-bottom .connector-flow-dot {
  top: 0;
  animation-name: flowDotDown;
}

@keyframes flowDotDown {
  0% { top: 0; opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

@keyframes flowDotUp {
  0% { bottom: 0; opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { bottom: 100%; opacity: 0; }
}

.node-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.04);
  transition: all 0.4s ease;
  position: relative;
  flex-shrink: 0;
}

.flow-node.pending .node-dot {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.flow-node.completed .node-dot {
  border-color: #43e97b;
  background: rgba(67, 233, 123, 0.2);
  color: #43e97b;
}

.flow-node.active .node-dot {
  border-color: #43e97b;
  background: rgba(67, 233, 123, 0.15);
  box-shadow: 0 0 12px rgba(67, 233, 123, 0.3);
}

.node-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #43e97b;
  animation: nodePulse 1.5s ease-in-out infinite;
}

@keyframes nodePulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.5); opacity: 0; }
}

.node-number {
  font-size: 10px;
  color: #666;
  font-weight: 600;
}

.node-label {
  font-size: 11px;
  color: #888;
  margin-top: 4px;
  text-align: center;
  line-height: 1.3;
  transition: color 0.3s;
  max-width: 100px;
  word-break: keep-all;
}

.flow-node.active .node-label {
  color: #43e97b;
  font-weight: 600;
}

.flow-node.completed .node-label {
  color: #aaa;
}

.detail-panel {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  min-width: 0;
}

.detail-content {
  animation: detailFadeIn 0.3s ease;
}

@keyframes detailFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.detail-header {
  margin-bottom: 16px;
}

.detail-step-badge {
  display: inline-block;
  font-size: 11px;
  color: #43e97b;
  background: rgba(67, 233, 123, 0.1);
  border: 1px solid rgba(67, 233, 123, 0.2);
  padding: 2px 10px;
  border-radius: 10px;
  margin-bottom: 8px;
}

.detail-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.detail-desc {
  font-size: 14px;
  color: #bbb;
  line-height: 1.7;
  margin-bottom: 20px;
}

.detail-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #ddd;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-image-section {
  margin-bottom: 20px;
}

.detail-image-wrapper {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  justify-content: center;
}

.detail-image-wrapper img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 6px;
  image-rendering: pixelated;
}

.detail-shape {
  font-size: 12px;
  color: #888;
  margin-top: 8px;
  text-align: center;
}

.detail-principle-section {
  margin-bottom: 20px;
  background: rgba(67, 233, 123, 0.04);
  border: 1px solid rgba(67, 233, 123, 0.1);
  border-radius: 10px;
  padding: 14px;
}

.detail-principle {
  font-size: 13px;
  color: #bbb;
  line-height: 1.8;
  margin: 0;
}

.detail-stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-group {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 10px;
}

.stat-group-title {
  font-size: 11px;
  color: #888;
  margin-bottom: 6px;
  font-weight: 600;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 3px 0;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.stat-value {
  font-size: 12px;
  color: #43e97b;
  font-weight: 500;
}

.detail-activations-section {
  margin-bottom: 20px;
}

.activation-bars {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activation-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.act-index {
  font-size: 11px;
  color: #888;
  width: 36px;
  text-align: right;
  flex-shrink: 0;
}

.act-bar-bg {
  flex: 1;
  height: 12px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  overflow: hidden;
}

.act-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #43e97b, #38f9d7);
  border-radius: 6px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.act-value {
  font-size: 11px;
  color: #888;
  width: 44px;
  text-align: right;
  flex-shrink: 0;
}

.detail-logits-section {
  margin-bottom: 20px;
}

.logit-bars {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.logit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.logit-item.highlight {
  background: rgba(67, 233, 123, 0.08);
}

.logit-label {
  font-size: 12px;
  color: #aaa;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
  font-weight: 600;
}

.logit-item.highlight .logit-label {
  color: #43e97b;
}

.logit-bar-bg {
  flex: 1;
  height: 14px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 7px;
  overflow: hidden;
}

.logit-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 7px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.logit-item.highlight .logit-bar-fill {
  background: linear-gradient(90deg, #43e97b, #38f9d7);
}

.logit-value {
  font-size: 11px;
  color: #888;
  width: 44px;
  text-align: right;
  flex-shrink: 0;
}

.logit-item.highlight .logit-value {
  color: #43e97b;
}

.detail-probabilities-section {
  margin-bottom: 20px;
}

.prob-bars-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.prob-item-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.prob-item-detail.highlight {
  background: rgba(67, 233, 123, 0.08);
}

.prob-label-detail {
  font-size: 12px;
  color: #aaa;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
  font-weight: 600;
}

.prob-item-detail.highlight .prob-label-detail {
  color: #43e97b;
}

.prob-bar-bg-detail {
  flex: 1;
  height: 14px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 7px;
  overflow: hidden;
}

.prob-bar-fill-detail {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 7px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.prob-item-detail.highlight .prob-bar-fill-detail {
  background: linear-gradient(90deg, #43e97b, #38f9d7);
}

.prob-value-detail {
  font-size: 11px;
  color: #888;
  width: 48px;
  text-align: right;
  flex-shrink: 0;
}

.prob-item-detail.highlight .prob-value-detail {
  color: #43e97b;
}

.detail-result-section {
  margin-top: 16px;
}

.result-display {
  text-align: center;
  padding: 24px;
  background: rgba(67, 233, 123, 0.08);
  border: 1px solid rgba(67, 233, 123, 0.2);
  border-radius: 14px;
}

.result-digit-large {
  font-size: 64px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.result-confidence-large {
  font-size: 16px;
  color: #43e97b;
  margin-top: 8px;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
  gap: 16px;
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ctrl-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ctrl-btn:hover:not(:disabled) {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.3);
  color: #43e97b;
}

.ctrl-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.play-btn {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  border: none;
  color: #0c0c1d;
}

.play-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 16px rgba(67, 233, 123, 0.3);
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  color: #0c0c1d;
}

.controls-center {
  display: flex;
  align-items: center;
  gap: 4px;
}

.speed-btn {
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: #888;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.speed-btn:hover {
  border-color: rgba(67, 233, 123, 0.3);
  color: #ccc;
}

.speed-btn.active {
  background: rgba(67, 233, 123, 0.15);
  border-color: rgba(67, 233, 123, 0.4);
  color: #43e97b;
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar-mini {
  width: 80px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill-mini {
  height: 100%;
  background: linear-gradient(90deg, #43e97b, #38f9d7);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.step-counter {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
}

.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

.detail-slide-enter-active {
  transition: all 0.3s ease;
}

.detail-slide-leave-active {
  transition: all 0.15s ease;
}

.detail-slide-enter-from {
  opacity: 0;
  transform: translateX(16px);
}

.detail-slide-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}

.flowchart-panel::-webkit-scrollbar,
.detail-panel::-webkit-scrollbar {
  width: 4px;
}

.flowchart-panel::-webkit-scrollbar-track,
.detail-panel::-webkit-scrollbar-track {
  background: transparent;
}

.flowchart-panel::-webkit-scrollbar-thumb,
.detail-panel::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

@media (max-width: 768px) {
  .explanation-overlay {
    padding: 0;
  }

  .explanation-modal {
    max-height: 100vh;
    height: 100vh;
    border-radius: 0;
    max-width: 100%;
  }

  .modal-body {
    flex-direction: column;
  }

  .flowchart-panel {
    width: 100%;
    max-height: 140px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding: 10px;
  }

  .flowchart-scroll {
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
  }

  .phase-header {
    display: none;
  }

  .phase-steps {
    flex-direction: row;
    margin-bottom: 0;
    gap: 2px;
  }

  .flow-node {
    flex-direction: row;
    gap: 2px;
  }

  .node-connector-top,
  .node-connector-bottom {
    width: 12px;
    height: 2px;
  }

  .node-dot {
    width: 22px;
    height: 22px;
  }

  .node-number {
    font-size: 8px;
  }

  .node-label {
    display: none;
  }

  .connector-flow-dot {
    display: none;
  }

  .detail-panel {
    padding: 16px;
  }

  .detail-title {
    font-size: 16px;
  }

  .modal-footer {
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px 16px;
  }

  .controls-right {
    width: 100%;
    justify-content: center;
  }
}

.explanation-overlay:not(.dark-mode) {
  background: rgba(255, 255, 255, 0.7);
}

.explanation-modal:not(.dark-mode) {
  background: linear-gradient(135deg, #ffffff, #f5f5ff);
  border-color: rgba(67, 233, 123, 0.15);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), 0 0 40px rgba(67, 233, 123, 0.04);
}

.explanation-modal:not(.dark-mode) .modal-header {
  border-bottom-color: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .close-btn {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(0, 0, 0, 0.04);
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .loading-state,
.explanation-modal:not(.dark-mode) .error-state {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .retry-btn {
  border-color: rgba(67, 233, 123, 0.2);
  background: rgba(67, 233, 123, 0.06);
  color: #2d8659;
}

.explanation-modal:not(.dark-mode) .flowchart-panel {
  border-right-color: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .phase-header {
  background: rgba(0, 0, 0, 0.03);
}

.explanation-modal:not(.dark-mode) .phase-name {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .node-dot {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.7);
}

.explanation-modal:not(.dark-mode) .node-number {
  color: #999;
}

.explanation-modal:not(.dark-mode) .node-label {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .detail-title {
  color: #1a1a2e;
}

.explanation-modal:not(.dark-mode) .detail-desc {
  color: #4a4a6a;
}

.explanation-modal:not(.dark-mode) .detail-section-title {
  color: #1a1a2e;
}

.explanation-modal:not(.dark-mode) .detail-image-wrapper {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .detail-shape {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .detail-principle-section {
  background: rgba(67, 233, 123, 0.03);
  border-color: rgba(67, 233, 123, 0.08);
}

.explanation-modal:not(.dark-mode) .detail-principle {
  color: #4a4a6a;
}

.explanation-modal:not(.dark-mode) .stat-group {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .stat-group-title {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .stat-label {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .act-index {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .act-bar-bg {
  background: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .act-value {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .logit-label {
  color: #4a4a6a;
}

.explanation-modal:not(.dark-mode) .logit-bar-bg {
  background: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .logit-value {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .prob-label-detail {
  color: #4a4a6a;
}

.explanation-modal:not(.dark-mode) .prob-bar-bg-detail {
  background: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .prob-value-detail {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .modal-footer {
  border-top-color: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .ctrl-btn {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(0, 0, 0, 0.03);
  color: #4a4a6a;
}

.explanation-modal:not(.dark-mode) .ctrl-btn:hover:not(:disabled) {
  background: rgba(67, 233, 123, 0.06);
  border-color: rgba(67, 233, 123, 0.2);
  color: #2d8659;
}

.explanation-modal:not(.dark-mode) .speed-btn {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(0, 0, 0, 0.03);
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .speed-btn:hover {
  border-color: rgba(67, 233, 123, 0.2);
  color: #4a4a6a;
}

.explanation-modal:not(.dark-mode) .speed-btn.active {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.3);
  color: #2d8659;
}

.explanation-modal:not(.dark-mode) .progress-bar-mini {
  background: rgba(0, 0, 0, 0.08);
}

.explanation-modal:not(.dark-mode) .step-counter {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .preprocessing-pipeline {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.06);
}

.explanation-modal:not(.dark-mode) .pipeline-img-box {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.7);
}

.explanation-modal:not(.dark-mode) .pipeline-step-name {
  color: #6b7280;
}

.explanation-modal:not(.dark-mode) .pipeline-arrow {
  color: rgba(0, 0, 0, 0.15);
}

.explanation-modal:not(.dark-mode) .result-display {
  background: rgba(67, 233, 123, 0.06);
  border-color: rgba(67, 233, 123, 0.15);
}
</style>
