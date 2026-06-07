<template>
  <div class="quiz-page" :class="{ 'dark-mode': isDark }">
    <div class="quiz-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 1024 1024" width="20" height="20">
          <path d="M669.6 849.6L368.8 548.8c-12-12-12-32 0-44l300.8-300.8c12-12 32-12 44 0s12 32 0 44L436 526.8l277.6 278.8c12 12 12 32 0 44-6 6-14 8.4-22 8.4s-16-2.8-22-8.4z" fill="currentColor"/>
        </svg>
        返回练习
      </button>
      <div class="header-center">
        <h1 class="page-title">动手做 · 答题</h1>
        <div class="timer">
          <svg viewBox="0 0 1024 1024" width="16" height="16">
            <path d="M512 128c-211.2 0-384 172.8-384 384s172.8 384 384 384 384-172.8 384-384-172.8-384-384-384z m0 704c-176 0-320-144-320-320s144-320 320-320 320 144 320 320-144 320-320 320z" fill="currentColor"/>
            <path d="M544 288h-64v224l160 160 44.8-44.8L544 483.2z" fill="currentColor"/>
          </svg>
          <span>{{ formattedTime }}</span>
        </div>
      </div>
      <div class="header-right"></div>
    </div>

    <div class="progress-section">
      <div class="progress-info">
        <span class="progress-text">第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</span>
        <span class="progress-percent">{{ progressPercent }}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>

    <div class="quiz-content">
      <transition :name="transitionName" mode="out-in">
        <div class="question-card" :key="currentIndex">
          <div class="question-meta">
            <span class="type-badge" :class="currentQuestion.type">{{ typeLabel(currentQuestion.type) }}</span>
            <div class="difficulty-stars">
              <svg v-for="n in 5" :key="n" viewBox="0 0 1024 1024" width="16" height="16"
                :class="{ active: n <= currentQuestion.difficulty }">
                <path d="M512 88.32l124.16 251.52 277.44 40.32-200.8 195.84 47.36 276.8L512 726.72l-248.16 126.08 47.36-276.8L110.4 380.16l277.44-40.32z" fill="currentColor"/>
              </svg>
            </div>
          </div>

          <div class="question-text" v-html="renderQuestionText(currentQuestion.question)"></div>

          <div class="answer-area">
            <div v-if="currentQuestion.type === 'code_understanding'" class="code-input-area">
              <input
                type="text"
                class="code-input"
                v-model="answers[currentQuestion.id]"
                placeholder="请输入你的答案..."
                @input="onAnswerChange"
              />
            </div>

            <div v-else-if="currentQuestion.type === 'choice'" class="choice-area">
              <button
                v-for="(option, idx) in currentQuestion.options"
                :key="idx"
                class="option-btn"
                :class="{ selected: answers[currentQuestion.id] === option.value }"
                @click="selectOption(option.value)"
              >
                <span class="option-label">{{ option.value }}</span>
                <span class="option-text">{{ option.label }}</span>
              </button>
            </div>

            <div v-else-if="currentQuestion.type === 'short_answer'" class="short-answer-area">
              <textarea
                class="answer-textarea"
                v-model="answers[currentQuestion.id]"
                placeholder="请输入你的回答..."
                @input="onAnswerChange"
                rows="6"
              ></textarea>
              <div class="char-count">{{ currentAnswerLength }} 字</div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <div class="nav-buttons">
      <button class="nav-btn prev-btn" :disabled="currentIndex === 0" @click="prevQuestion">
        <svg viewBox="0 0 1024 1024" width="16" height="16">
          <path d="M669.6 849.6L368.8 548.8c-12-12-12-32 0-44l300.8-300.8c12-12 32-12 44 0s12 32 0 44L436 526.8l277.6 278.8c12 12 12 32 0 44-6 6-14 8.4-22 8.4s-16-2.8-22-8.4z" fill="currentColor"/>
        </svg>
        上一题
      </button>
      <button class="nav-btn submit-btn" @click="showConfirmDialog = true">
        提交答案
      </button>
      <button class="nav-btn next-btn" :disabled="currentIndex === questions.length - 1" @click="nextQuestion">
        下一题
        <svg viewBox="0 0 1024 1024" width="16" height="16">
          <path d="M354.4 174.4l300.8 300.8c12 12 12 32 0 44L354.4 820c-12 12-32 12-44 0s-12-32 0-44L588 477.2 310.4 218.4c-12-12-12-32 0-44s32-12 44 0z" fill="currentColor"/>
        </svg>
      </button>
    </div>

    <div class="confirm-overlay" v-if="showConfirmDialog" @click.self="showConfirmDialog = false">
      <div class="confirm-dialog">
        <div class="confirm-icon">
          <svg viewBox="0 0 1024 1024" width="40" height="40">
            <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64z m0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z" fill="#667eea"/>
            <path d="M512 300m-40 0a40 40 0 1 0 80 0 40 40 0 1 0-80 0Z" fill="#667eea"/>
            <path d="M512 420c-17.7 0-32 14.3-32 32v220c0 17.7 14.3 32 32 32s32-14.3 32-32V452c0-17.7-14.3-32-32-32z" fill="#667eea"/>
          </svg>
        </div>
        <h3 class="confirm-title">确认提交？</h3>
        <p class="confirm-message">
          你已完成 <span class="highlight">{{ answeredCount }}</span> / {{ questions.length }} 题，
          未作答的题目将记为空。
        </p>
        <div class="confirm-actions">
          <button class="confirm-btn cancel" @click="showConfirmDialog = false">继续答题</button>
          <button class="confirm-btn ok" @click="submitAnswers">确认提交</button>
        </div>
      </div>
    </div>

    <div class="loading-overlay" v-if="submitting">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <p class="loading-text">正在提交答案...</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useUserStore } from '../store/user'

export default {
  name: 'QuizPage',
  data() {
    return {
      isDark: false,
      questions: [],
      answers: {},
      currentIndex: 0,
      transitionName: 'slide-left',
      showConfirmDialog: false,
      submitting: false,
      elapsedSeconds: 0,
      timerInterval: null,
      quizMeta: {
        type: '',
        difficulty: '',
        topic: ''
      }
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex] || {}
    },
    progressPercent() {
      if (this.questions.length === 0) return 0
      return Math.round(((this.currentIndex + 1) / this.questions.length) * 100)
    },
    formattedTime() {
      const mins = Math.floor(this.elapsedSeconds / 60)
      const secs = this.elapsedSeconds % 60
      return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
    },
    answeredCount() {
      return Object.values(this.answers).filter(a => a && a.toString().trim() !== '').length
    },
    currentAnswerLength() {
      const ans = this.answers[this.currentQuestion.id]
      return ans ? ans.length : 0
    }
  },
  created() {
    this.parseRouteData()
  },
  mounted() {
    this.checkDarkMode()
    this._darkObserver = new MutationObserver(() => { this.checkDarkMode() })
    this._darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
    this.startTimer()
  },
  beforeUnmount() {
    if (this._darkObserver) this._darkObserver.disconnect()
    this.stopTimer()
  },
  methods: {
    checkDarkMode() {
      this.isDark = document.documentElement.classList.contains('Dark') || document.documentElement.getAttribute('data-theme') === 'Dark'
    },
    parseRouteData() {
      try {
        const dataStr = this.$route.query.data
        if (dataStr) {
          const parsed = JSON.parse(decodeURIComponent(dataStr))
          this.questions = (parsed.questions || []).map(q => {
            if (q.type === 'choice' && Array.isArray(q.options)) {
              q.options = q.options.map((opt, idx) => {
                const letter = String.fromCharCode(65 + idx)
                if (typeof opt === 'object' && opt !== null) return opt
                return { value: letter, label: opt }
              })
            }
            return q
          })
          this.quizMeta.type = parsed.type || ''
          this.quizMeta.difficulty = parsed.difficulty || ''
          this.quizMeta.topic = parsed.topic || ''
        }
      } catch (e) {
        console.error('解析题目数据失败:', e)
      }
    },
    startTimer() {
      this.timerInterval = setInterval(() => {
        this.elapsedSeconds++
      }, 1000)
    },
    stopTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
      }
    },
    goBack() {
      this.$router.push('/practice')
    },
    typeLabel(type) {
      const map = {
        code_understanding: '代码理解',
        choice: '选择题',
        short_answer: '简答题'
      }
      return map[type] || type
    },
    renderQuestionText(text) {
      if (!text) return ''
      return text.replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    },
    selectOption(value) {
      this.answers[this.currentQuestion.id] = value
    },
    onAnswerChange() {
    },
    prevQuestion() {
      if (this.currentIndex > 0) {
        this.transitionName = 'slide-right'
        this.currentIndex--
      }
    },
    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.transitionName = 'slide-left'
        this.currentIndex++
      }
    },
    async submitAnswers() {
      this.showConfirmDialog = false
      this.submitting = true
      this.stopTimer()

      const userStore = useUserStore()
      const username = userStore.user?.username || 'anonymous'

      const body = {
        username,
        questions: this.questions,
        answers: { ...this.answers },
        type: this.quizMeta.type,
        difficulty: this.quizMeta.difficulty,
        topic: this.quizMeta.topic
      }

      try {
        const response = await axios.post('/api/practice/submit', body)
        this.submitting = false
        const submitData = response.data
        if (submitData.success && submitData.data) {
          const reportData = {
            score: submitData.data.total_score,
            max_score: submitData.data.max_score,
            correct_count: submitData.data.correct_count,
            total_questions: submitData.data.total_questions,
            accuracy: submitData.data.accuracy,
            questions: submitData.data.results,
            report: submitData.data.report
          }
          this.$router.push({
            path: '/practice/report',
            query: {
              data: encodeURIComponent(JSON.stringify(reportData))
            }
          })
        } else {
          alert('提交失败：' + (submitData.message || '返回数据格式异常'))
          this.startTimer()
        }
      } catch (error) {
        this.submitting = false
        console.error('提交答案失败:', error)
        alert('提交失败，请重试')
        this.startTimer()
      }
    }
  }
}
</script>

<style scoped>
.quiz-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #0d0d2b 100%);
  padding: 20px;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.quiz-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.back-btn {
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
}

.header-center {
  text-align: center;
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}

.timer {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #999;
  font-size: 14px;
  font-variant-numeric: tabular-nums;
}

.timer svg {
  color: #667eea;
}

.header-right {
  width: 100px;
}

.progress-section {
  max-width: 800px;
  width: 100%;
  margin: 0 auto 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 13px;
  color: #aaa;
}

.progress-percent {
  font-size: 13px;
  color: #43e97b;
  font-weight: 600;
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #43e97b, #667eea);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.quiz-content {
  flex: 1;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.question-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 28px;
  position: relative;
  overflow: hidden;
}

.question-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #43e97b, #667eea, transparent);
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.type-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.type-badge.code_understanding {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.type-badge.choice {
  background: rgba(67, 233, 123, 0.2);
  color: #43e97b;
  border: 1px solid rgba(67, 233, 123, 0.3);
}

.type-badge.short_answer {
  background: rgba(240, 147, 251, 0.2);
  color: #f093fb;
  border: 1px solid rgba(240, 147, 251, 0.3);
}

.difficulty-stars {
  display: flex;
  gap: 2px;
}

.difficulty-stars svg {
  color: rgba(255, 255, 255, 0.15);
  transition: color 0.3s ease;
}

.difficulty-stars svg.active {
  color: #f5c842;
  filter: drop-shadow(0 0 4px rgba(245, 200, 66, 0.4));
}

.question-text {
  font-size: 16px;
  line-height: 1.8;
  color: #e0e0e0;
  margin-bottom: 24px;
}

.question-text :deep(.code-block) {
  background: #1e1e2e;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.question-text :deep(.code-block code) {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #cdd6f4;
  line-height: 1.6;
}

.question-text :deep(.inline-code) {
  background: #1e1e2e;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #a6e3a1;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.answer-area {
  margin-top: 8px;
}

.code-input-area {
  position: relative;
}

.code-input {
  width: 100%;
  padding: 14px 18px;
  background: rgba(30, 30, 46, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #cdd6f4;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 15px;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.code-input:focus {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.code-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.choice-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ccc;
  cursor: pointer;
  font-size: 15px;
  text-align: left;
  transition: all 0.3s ease;
}

.option-btn:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.15);
  color: #fff;
}

.option-btn.selected {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.5);
  box-shadow: 0 0 16px rgba(67, 233, 123, 0.2);
  color: #43e97b;
}

.option-label {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.option-btn.selected .option-label {
  background: rgba(67, 233, 123, 0.25);
  color: #43e97b;
}

.option-text {
  flex: 1;
  line-height: 1.5;
}

.short-answer-area {
  position: relative;
}

.answer-textarea {
  width: 100%;
  padding: 14px 18px;
  background: rgba(30, 30, 46, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #e0e0e0;
  font-size: 15px;
  font-family: inherit;
  line-height: 1.6;
  outline: none;
  resize: vertical;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.answer-textarea:focus {
  border-color: rgba(240, 147, 251, 0.6);
  box-shadow: 0 0 0 3px rgba(240, 147, 251, 0.15);
}

.answer-textarea::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.char-count {
  text-align: right;
  margin-top: 6px;
  font-size: 12px;
  color: #666;
}

.nav-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  max-width: 800px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.06);
  color: #ccc;
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.prev-btn:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
  color: #667eea;
}

.next-btn:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
  color: #667eea;
}

.submit-btn {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.2), rgba(102, 126, 234, 0.2));
  border-color: rgba(67, 233, 123, 0.3);
  color: #43e97b;
  padding: 10px 32px;
}

.submit-btn:hover {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.35), rgba(102, 126, 234, 0.35));
  border-color: rgba(67, 233, 123, 0.6);
  box-shadow: 0 4px 20px rgba(67, 233, 123, 0.25);
  color: #fff;
}

.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirm-dialog {
  background: linear-gradient(135deg, #1a1a3e, #0d0d2b);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 36px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.confirm-icon {
  margin-bottom: 16px;
}

.confirm-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #eee;
}

.confirm-message {
  font-size: 14px;
  color: #999;
  line-height: 1.6;
  margin-bottom: 24px;
}

.confirm-message .highlight {
  color: #43e97b;
  font-weight: 600;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.confirm-btn {
  padding: 10px 28px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.confirm-btn.cancel {
  background: rgba(255, 255, 255, 0.06);
  color: #aaa;
}

.confirm-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.confirm-btn.ok {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.25), rgba(102, 126, 234, 0.25));
  border-color: rgba(67, 233, 123, 0.4);
  color: #43e97b;
}

.confirm-btn.ok:hover {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.4), rgba(102, 126, 234, 0.4));
  box-shadow: 0 4px 16px rgba(67, 233, 123, 0.2);
  color: #fff;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-spinner {
  text-align: center;
}

.spinner-ring {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #43e97b;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #ccc;
  font-size: 15px;
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.quiz-page:not(.dark-mode) {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%);
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .back-btn {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #4a4a6a;
}

.quiz-page:not(.dark-mode) .back-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .timer {
  color: #6b7280;
}

.quiz-page:not(.dark-mode) .progress-text {
  color: #6b7280;
}

.quiz-page:not(.dark-mode) .progress-bar {
  background: rgba(0, 0, 0, 0.08);
}

.quiz-page:not(.dark-mode) .question-card {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
}

.quiz-page:not(.dark-mode) .question-text {
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .question-text :deep(.code-block) {
  background: #f5f5f5;
  border-color: rgba(0, 0, 0, 0.08);
}

.quiz-page:not(.dark-mode) .question-text :deep(.code-block code) {
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .question-text :deep(.inline-code) {
  background: #f5f5f5;
  border-color: rgba(0, 0, 0, 0.08);
  color: #2d5016;
}

.quiz-page:not(.dark-mode) .code-input {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(0, 0, 0, 0.15);
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .code-input::placeholder {
  color: rgba(0, 0, 0, 0.3);
}

.quiz-page:not(.dark-mode) .option-btn {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  color: #4a4a6a;
}

.quiz-page:not(.dark-mode) .option-btn:hover {
  background: rgba(102, 126, 234, 0.06);
  border-color: rgba(102, 126, 234, 0.2);
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .option-label {
  background: rgba(0, 0, 0, 0.05);
}

.quiz-page:not(.dark-mode) .answer-textarea {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(0, 0, 0, 0.15);
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .answer-textarea::placeholder {
  color: rgba(0, 0, 0, 0.3);
}

.quiz-page:not(.dark-mode) .char-count {
  color: #999;
}

.quiz-page:not(.dark-mode) .nav-btn {
  border-color: rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.7);
  color: #4a4a6a;
}

.quiz-page:not(.dark-mode) .confirm-overlay {
  background: rgba(0, 0, 0, 0.3);
}

.quiz-page:not(.dark-mode) .confirm-dialog {
  background: linear-gradient(135deg, #ffffff, #f5f5ff);
  border-color: rgba(0, 0, 0, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.quiz-page:not(.dark-mode) .confirm-title {
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .confirm-message {
  color: #6b7280;
}

.quiz-page:not(.dark-mode) .confirm-btn.cancel {
  background: rgba(0, 0, 0, 0.05);
  color: #4a4a6a;
}

.quiz-page:not(.dark-mode) .confirm-btn.cancel:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #1a1a2e;
}

.quiz-page:not(.dark-mode) .loading-overlay {
  background: rgba(255, 255, 255, 0.7);
}

.quiz-page:not(.dark-mode) .spinner-ring {
  border-color: rgba(0, 0, 0, 0.1);
}

.quiz-page:not(.dark-mode) .loading-text {
  color: #4a4a6a;
}

@media (max-width: 768px) {
  .quiz-page {
    padding: 12px;
  }

  .quiz-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-center {
    order: -1;
    width: 100%;
    text-align: center;
  }

  .header-right {
    display: none;
  }

  .page-title {
    font-size: 20px;
  }

  .question-card {
    padding: 20px;
  }

  .question-text {
    font-size: 15px;
  }

  .nav-buttons {
    flex-wrap: wrap;
    gap: 10px;
  }

  .nav-btn {
    flex: 1;
    justify-content: center;
    min-width: 0;
    padding: 10px 12px;
    font-size: 14px;
  }

  .option-btn {
    padding: 12px 14px;
    font-size: 14px;
  }

  .confirm-dialog {
    padding: 24px;
  }
}
</style>
