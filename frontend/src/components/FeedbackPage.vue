<template>
  <div class="feedback-page" :class="{ 'dark-mode': isDark }">
    <div class="feedback-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 1024 1024" width="20" height="20">
          <path d="M669.6 849.6L368.8 548.8c-12-12-12-32 0-44l300.8-300.8c12-12 32-12 44 0s12 32 0 44L436 526.8l277.6 278.8c12 12 12 32 0 44-6 6-14 8.4-22 8.4s-16-2.8-22-8.4z" fill="currentColor"/>
        </svg>
        返回主页
      </button>
      <h1 class="page-title">得反馈</h1>
      <p class="page-subtitle">查看练习历史、错题本、能力分析与排行榜</p>
    </div>

    <div class="tab-bar">
      <div class="tab-list">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
        <div class="tab-indicator" :style="indicatorStyle"></div>
      </div>
    </div>

    <div class="tab-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="activeTab === 'history'" class="tab-panel">
        <div v-if="historyList.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <p>暂无做题记录</p>
          <p class="empty-sub">完成练习后，历史记录将在此显示</p>
        </div>
        <div v-else class="history-list">
          <div
            v-for="record in historyList"
            :key="record.id"
            class="history-card"
            :class="{ expanded: expandedRecord === record.id }"
            @click="toggleRecord(record.id)"
          >
            <div class="history-card-main">
              <div class="history-left">
                <span class="type-badge" :class="getTypeBadgeClass(record.type)">{{ getTypeBadgeLabel(record.type) }}</span>
                <span class="difficulty-badge" :class="getDifficultyClass(record.difficulty)">{{ difficultyLabel(record.difficulty) }}</span>
              </div>
              <div class="history-center">
                <span class="history-topic">{{ record.topic || '综合练习' }}</span>
                <span class="history-time">{{ record.created_at }}</span>
              </div>
              <div class="history-right">
                <span class="history-score">{{ record.score }}<small>分</small></span>
                <span class="history-accuracy">正确率 {{ record.accuracy }}%</span>
              </div>
              <span class="expand-arrow" :class="{ rotated: expandedRecord === record.id }">▼</span>
            </div>
            <div v-if="expandedRecord === record.id" class="history-detail">
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">题目数量</span>
                  <span class="detail-value">{{ record.total_count || '-' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">正确数量</span>
                  <span class="detail-value correct">{{ record.correct_count || '-' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">用时</span>
                  <span class="detail-value">{{ record.duration || '-' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">得分</span>
                  <span class="detail-value score">{{ record.score }}</span>
                </div>
              </div>
              <div v-if="record.details && record.details.length" class="detail-questions">
                <div v-for="(q, qi) in record.details" :key="qi" class="detail-question">
                  <span class="q-index">Q{{ qi + 1 }}</span>
                  <span class="q-text">{{ q.question }}</span>
                  <span class="q-result" :class="q.is_correct ? 'correct' : 'wrong'">{{ q.is_correct ? '✓' : '✗' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="historyList.length > 0" class="pagination">
          <button class="page-btn" :disabled="historyPage <= 1" @click="changePage(historyPage - 1)">上一页</button>
          <span class="page-info">第 {{ historyPage }} 页</span>
          <button class="page-btn" :disabled="historyList.length < historyPageSize" @click="changePage(historyPage + 1)">下一页</button>
        </div>
      </div>

      <div v-else-if="activeTab === 'wrong'" class="tab-panel">
        <div class="wrong-toolbar">
          <select v-model="wrongCategory" class="category-select" @change="fetchWrongQuestions">
            <option value="">全部分类</option>
            <option v-for="cat in wrongCategories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <button class="export-btn" @click="exportWrongQuestions">
            <svg viewBox="0 0 1024 1024" width="16" height="16"><path d="M832 768v128H192v-128H128v128c0 35.3 28.7 64 64 64h640c35.3 0 64-28.7 64-64v-128h-64zM624 565.6l-80 80V128h-64v517.6l-80-80-45.2 45.2L511.6 867.6l156.8-256.8-44.4-45.2z" fill="currentColor"/></svg>
            导出错题
          </button>
        </div>
        <div v-if="wrongQuestions.length === 0" class="empty-state">
          <div class="empty-icon">🎉</div>
          <p>暂无错题</p>
          <p class="empty-sub">所有题目都已掌握，继续保持！</p>
        </div>
        <div v-else class="wrong-list">
          <div
            v-for="q in filteredWrongQuestions"
            :key="q.id"
            class="wrong-card"
            :class="{ mastered: q.mastered }"
          >
            <div class="wrong-card-header">
              <span class="mastered-indicator" :class="q.mastered ? 'mastered' : 'unmastered'">
                {{ q.mastered ? '✓ 已掌握' : '● 未掌握' }}
              </span>
              <span class="retry-count">重做 {{ q.retry_count || 0 }} 次</span>
            </div>
            <div class="wrong-question-text">{{ q.question }}</div>
            <div class="wrong-answers">
              <div class="answer-row wrong-answer">
                <span class="answer-label">你的答案</span>
                <span class="answer-value">{{ q.user_answer }}</span>
              </div>
              <div class="answer-row correct-answer">
                <span class="answer-label">正确答案</span>
                <span class="answer-value">{{ q.correct_answer }}</span>
              </div>
            </div>
            <div v-if="q.explanation" class="wrong-explanation">
              <span class="explanation-label">解析</span>
              <span class="explanation-text">{{ q.explanation }}</span>
            </div>
            <div v-if="retryingId === q.id" class="retry-input-area">
              <input
                v-model="retryAnswer"
                class="retry-input"
                placeholder="输入你的答案"
                @keyup.enter="submitRetry(q.id)"
              />
              <button class="retry-submit-btn" @click="submitRetry(q.id)" :disabled="!retryAnswer.trim()">提交</button>
              <button class="retry-cancel-btn" @click="cancelRetry">取消</button>
            </div>
            <div v-else class="wrong-card-actions">
              <button class="retry-btn" @click="startRetry(q.id)">重做</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'radar'" class="tab-panel">
        <div v-if="radarData.length === 0 && !radarLoading" class="empty-state">
          <div class="empty-icon">📊</div>
          <p>暂无能力数据</p>
          <p class="empty-sub">完成更多练习后，能力分析将在此显示</p>
        </div>
        <template v-else>
          <div class="radar-chart-container" ref="radarChart"></div>
          <div class="radar-scores">
            <div v-for="dim in radarData" :key="dim.name" class="radar-score-item">
              <div class="radar-score-header">
                <span class="radar-dim-name">{{ dim.name }}</span>
                <span class="radar-dim-value">{{ dim.value }}%</span>
              </div>
              <div class="radar-progress-bar">
                <div class="radar-progress-fill" :style="{ width: dim.value + '%' }"></div>
              </div>
            </div>
          </div>
          <div v-if="statsData" class="stats-summary">
            <div class="stats-card">
              <div class="stats-value">{{ statsData.total_practices || 0 }}</div>
              <div class="stats-label">总练习次数</div>
            </div>
            <div class="stats-card">
              <div class="stats-value">{{ statsData.avg_score || 0 }}</div>
              <div class="stats-label">平均得分</div>
            </div>
            <div class="stats-card">
              <div class="stats-value">{{ statsData.avg_accuracy || 0 }}%</div>
              <div class="stats-label">平均正确率</div>
            </div>
            <div class="stats-card">
              <div class="stats-value">{{ statsData.mastered_count || 0 }}</div>
              <div class="stats-label">已掌握题目</div>
            </div>
          </div>
        </template>
      </div>

      <div v-else-if="activeTab === 'leaderboard'" class="tab-panel">
        <div class="leaderboard-sub-tabs">
          <button
            class="sub-tab-btn"
            :class="{ active: leaderboardType === 'total' }"
            @click="switchLeaderboardType('total')"
          >总积分排行</button>
          <button
            class="sub-tab-btn"
            :class="{ active: leaderboardType === 'weekly' }"
            @click="switchLeaderboardType('weekly')"
          >周活跃排行</button>
        </div>
        <div v-if="leaderboardList.length === 0" class="empty-state">
          <div class="empty-icon">🏆</div>
          <p>暂无排行数据</p>
          <p class="empty-sub">完成练习获取积分，登上排行榜！</p>
        </div>
        <div v-else class="leaderboard-content">
          <div v-if="topThree.length" class="top-three">
            <div v-for="(user, idx) in topThree" :key="user.username" class="top-user" :class="'rank-' + (idx + 1)">
              <div class="medal">{{ ['🥇', '🥈', '🥉'][idx] }}</div>
              <div class="top-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
              <div class="top-name">{{ user.username }}</div>
              <div class="top-score">{{ user.score }}<small>分</small></div>
            </div>
          </div>
          <div class="rank-list">
            <div
              v-for="user in remainingRanks"
              :key="user.username"
              class="rank-item"
              :class="{ 'is-me': user.username === currentUsername }"
            >
              <span class="rank-number">{{ user.rank }}</span>
              <span class="rank-name">{{ user.username }}</span>
              <span class="rank-score">{{ user.score }}分</span>
              <span v-if="user.gap_prev" class="rank-gap">距上名 +{{ user.gap_prev }}</span>
              <span v-if="user.gap_next" class="rank-gap next">距下名 -{{ user.gap_next }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'FeedbackPage',
  data() {
    return {
      activeTab: 'history',
      isDark: false,
      tabs: [
        { key: 'history', label: '做题历史', icon: '📋' },
        { key: 'wrong', label: '错题本', icon: '❌' },
        { key: 'radar', label: '能力雷达图', icon: '📊' },
        { key: 'leaderboard', label: '排行榜', icon: '🏆' }
      ],
      loading: false,
      expandedRecord: null,
      historyList: [],
      historyPage: 1,
      historyPageSize: 10,
      wrongQuestions: [],
      wrongCategory: '',
      retryingId: null,
      retryAnswer: '',
      radarData: [],
      radarLoading: false,
      radarChartInstance: null,
      statsData: null,
      leaderboardType: 'total',
      leaderboardList: [],
      leaderboardTimer: null
    }
  },
  computed: {
    currentUsername() {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        return user ? user.username : ''
      } catch {
        return ''
      }
    },
    indicatorStyle() {
      const idx = this.tabs.findIndex(t => t.key === this.activeTab)
      return {
        left: (idx * 25) + '%',
        width: '25%'
      }
    },
    wrongCategories() {
      const cats = new Set()
      this.wrongQuestions.forEach(q => {
        if (q.category) cats.add(q.category)
      })
      return Array.from(cats)
    },
    filteredWrongQuestions() {
      if (!this.wrongCategory) return this.wrongQuestions
      return this.wrongQuestions.filter(q => q.category === this.wrongCategory)
    },
    topThree() {
      return this.leaderboardList.slice(0, 3)
    },
    remainingRanks() {
      return this.leaderboardList.slice(3)
    }
  },
  watch: {
    isDark() {
      if (this.activeTab === 'radar' && this.radarData.length > 0) {
        this.$nextTick(() => {
          this.initRadarChart()
        })
      }
    }
  },
  methods: {
    checkDarkMode() {
      this.isDark = document.documentElement.classList.contains('Dark') || document.documentElement.getAttribute('data-theme') === 'Dark'
    },
    goBack() {
      this.$router.push('/')
    },
    switchTab(key) {
      this.activeTab = key
      this.loading = true
      this.expandedRecord = null
      setTimeout(() => {
        this.loading = false
        if (key === 'history') this.fetchHistory()
        else if (key === 'wrong') this.fetchWrongQuestions()
        else if (key === 'radar') this.fetchRadar()
        else if (key === 'leaderboard') this.fetchLeaderboard()
      }, 100)
    },
    difficultyLabel(d) {
      const map = { 1: '入门', 2: '初级', 3: '中级', 4: '高级', 5: '专家', easy: '简单', medium: '中等', hard: '困难' }
      return map[d] || d
    },
    getTypeBadgeClass(type) {
      const map = { choice: 'choice', code_understanding: 'code', short_answer: 'fill', code: 'code' }
      return map[type] || 'choice'
    },
    getTypeBadgeLabel(type) {
      const map = { choice: '选择题', code_understanding: '代码理解', short_answer: '简答题', code: '编程题' }
      return map[type] || '练习'
    },
    getDifficultyClass(d) {
      if (typeof d === 'number') {
        if (d <= 2) return 'easy'
        if (d <= 3) return 'medium'
        return 'hard'
      }
      return d
    },
    toggleRecord(id) {
      this.expandedRecord = this.expandedRecord === id ? null : id
    },
    changePage(page) {
      this.historyPage = page
      this.fetchHistory()
    },
    async fetchHistory() {
      try {
        const res = await fetch(`/api/practice/history?username=${this.currentUsername}&page=${this.historyPage}&page_size=${this.historyPageSize}`)
        const data = await res.json()
        if (data.success && data.data && data.data.records) {
          this.historyList = data.data.records.map(r => ({
            id: r._id || r.id || Math.random().toString(),
            type: r.type || 'choice',
            difficulty: r.difficulty || 1,
            topic: r.topic || '综合练习',
            created_at: r.created_at || '',
            score: r.total_score || 0,
            accuracy: r.accuracy || 0,
            total_count: r.total_questions || 0,
            correct_count: r.correct_count || 0
          }))
        } else {
          this.historyList = []
        }
      } catch {
        this.historyList = []
      }
    },
    async fetchWrongQuestions() {
      try {
        const res = await fetch(`/api/practice/wrong-questions?username=${this.currentUsername}`)
        const data = await res.json()
        if (data.success && data.data && data.data.questions) {
          this.wrongQuestions = data.data.questions.map(q => ({
            id: q._id || q.question_id || '',
            question: q.question || '',
            type: q.type || 'choice',
            difficulty: q.difficulty || 1,
            user_answer: q.user_answer || '',
            correct_answer: q.correct_answer || '',
            explanation: q.explanation || '',
            category: q.category || '',
            mastered: q.mastered || false,
            retry_count: q.retry_count || 0
          }))
          if (data.data.categories) {
            this.wrongCategory = ''
          }
        } else {
          this.wrongQuestions = []
        }
      } catch {
        this.wrongQuestions = []
      }
    },
    startRetry(id) {
      this.retryingId = id
      this.retryAnswer = ''
    },
    cancelRetry() {
      this.retryingId = null
      this.retryAnswer = ''
    },
    async submitRetry(id) {
      if (!this.retryAnswer.trim()) return
      try {
        const res = await fetch(`/api/practice/wrong-questions/${id}/retry`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.currentUsername, answer: this.retryAnswer })
        })
        const data = await res.json()
        if (data.success && data.data && data.data.is_correct) {
          const q = this.wrongQuestions.find(q => q.id === id)
          if (q) q.mastered = true
        }
        this.retryingId = null
        this.retryAnswer = ''
      } catch {
        this.retryingId = null
        this.retryAnswer = ''
      }
    },
    async exportWrongQuestions() {
      try {
        const res = await fetch('/api/practice/wrong-questions/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.currentUsername })
        })
        const data = await res.json()
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'wrong_questions.json'
        a.click()
        URL.revokeObjectURL(url)
      } catch {}
    },
    async fetchRadar() {
      this.radarLoading = true
      try {
        const [radarRes, statsRes] = await Promise.all([
          fetch(`/api/practice/radar?username=${this.currentUsername}`),
          fetch(`/api/practice/stats?username=${this.currentUsername}`)
        ])
        const radarJson = await radarRes.json()
        const statsJson = await statsRes.json()

        if (radarJson.success && radarJson.data) {
          const radarApiData = radarJson.data
          if (radarApiData.indicators && radarApiData.values) {
            this.radarData = radarApiData.indicators.map((ind, i) => ({
              name: ind.name,
              value: radarApiData.values[i] || 0
            }))
          } else {
            this.radarData = [
              { name: '算法理解能力', value: 0 },
              { name: '代码实现能力', value: 0 },
              { name: '问题分析能力', value: 0 },
              { name: '模型应用能力', value: 0 },
              { name: '创新思维能力', value: 0 }
            ]
          }
        } else {
          this.radarData = [
            { name: '算法理解能力', value: 0 },
            { name: '代码实现能力', value: 0 },
            { name: '问题分析能力', value: 0 },
            { name: '模型应用能力', value: 0 },
            { name: '创新思维能力', value: 0 }
          ]
        }

        if (statsJson.success && statsJson.data) {
          const s = statsJson.data
          this.statsData = {
            total_practices: s.total_practices || 0,
            avg_score: s.total_practices > 0 ? Math.round((s.total_score || 0) / s.total_practices) : 0,
            avg_accuracy: s.total_questions > 0 ? Math.round((s.total_correct || 0) / s.total_questions * 100) : 0,
            mastered_count: 0
          }
        } else {
          this.statsData = null
        }

        this.$nextTick(() => {
          this.initRadarChart()
        })
      } catch {
        this.radarData = []
        this.statsData = null
      } finally {
        this.radarLoading = false
      }
    },
    initRadarChart() {
      const container = this.$refs.radarChart
      if (!container) return
      if (this.radarChartInstance) {
        this.radarChartInstance.dispose()
      }
      this.radarChartInstance = echarts.init(container)
      const indicator = this.radarData.map(d => ({
        name: d.name,
        max: 100
      }))
      const values = this.radarData.map(d => d.value)
      const option = {
        backgroundColor: 'transparent',
        radar: {
          indicator,
          shape: 'polygon',
          splitNumber: 5,
          axisName: {
            color: this.isDark ? '#fff' : '#1a1a2e',
            fontSize: 12,
            fontWeight: 500
          },
          splitLine: {
            lineStyle: {
              color: this.isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)'
            }
          },
          splitArea: {
            areaStyle: {
              color: this.isDark
                ? ['rgba(102, 126, 234, 0.02)', 'rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.02)', 'rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.02)']
                : ['rgba(102, 126, 234, 0.03)', 'rgba(102, 126, 234, 0.06)', 'rgba(102, 126, 234, 0.03)', 'rgba(102, 126, 234, 0.06)', 'rgba(102, 126, 234, 0.03)']
            }
          },
          axisLine: {
            lineStyle: {
              color: this.isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)'
            }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: values,
            name: '能力值',
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(67, 233, 123, 0.4)' },
                { offset: 1, color: 'rgba(102, 126, 234, 0.4)' }
              ])
            },
            lineStyle: {
              color: '#43e97b',
              width: 2
            },
            itemStyle: {
              color: '#43e97b',
              borderColor: '#43e97b',
              borderWidth: 2
            },
            symbol: 'circle',
            symbolSize: 6
          }]
        }]
      }
      this.radarChartInstance.setOption(option)
    },
    async fetchLeaderboard() {
      try {
        const res = await fetch(`/api/practice/leaderboard?username=${this.currentUsername}&type=${this.leaderboardType}`)
        const data = await res.json()
        if (data.success && data.data && data.data.entries) {
          const scoreField = this.leaderboardType === 'weekly' ? 'weekly_score' : 'total_score'
          this.leaderboardList = data.data.entries.map((u, i) => ({
            username: u.username || '',
            score: u[scoreField] || 0,
            rank: i + 1,
            gap_prev: i > 0 ? (data.data.entries[i - 1][scoreField] || 0) - (u[scoreField] || 0) : 0,
            gap_next: 0
          }))
          for (let i = 0; i < this.leaderboardList.length - 1; i++) {
            this.leaderboardList[i].gap_next = this.leaderboardList[i].score - this.leaderboardList[i + 1].score
          }
        } else {
          this.leaderboardList = []
        }
      } catch {
        this.leaderboardList = []
      }
    },
    switchLeaderboardType(type) {
      this.leaderboardType = type
      this.fetchLeaderboard()
    },
    startLeaderboardTimer() {
      this.leaderboardTimer = setInterval(() => {
        if (this.activeTab === 'leaderboard') {
          this.fetchLeaderboard()
        }
      }, 300000)
    },
    handleResize() {
      if (this.radarChartInstance) {
        this.radarChartInstance.resize()
      }
    }
  },
  mounted() {
    this.checkDarkMode()
    this._darkObserver = new MutationObserver(() => { this.checkDarkMode() })
    this._darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
    this.fetchHistory()
    this.startLeaderboardTimer()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this._darkObserver) this._darkObserver.disconnect()
    if (this.radarChartInstance) {
      this.radarChartInstance.dispose()
      this.radarChartInstance = null
    }
    if (this.leaderboardTimer) {
      clearInterval(this.leaderboardTimer)
    }
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.feedback-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #0d0d2b 100%);
  padding: 20px;
  color: #fff;
}

.feedback-header {
  text-align: center;
  margin-bottom: 20px;
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
  background: rgba(67, 233, 123, 0.2);
  border-color: rgba(67, 233, 123, 0.5);
  color: #fff;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}

.page-subtitle {
  color: #999;
  font-size: 14px;
}

.tab-bar {
  margin-bottom: 24px;
}

.tab-list {
  display: flex;
  position: relative;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px;
  overflow: hidden;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 8px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  border-radius: 10px;
}

.tab-btn:hover {
  color: rgba(255, 255, 255, 0.9);
}

.tab-btn.active {
  color: #fff;
  font-weight: 600;
}

.tab-icon {
  font-size: 16px;
}

.tab-label {
  white-space: nowrap;
}

.tab-indicator {
  position: absolute;
  bottom: 4px;
  height: 3px;
  background: linear-gradient(90deg, #43e97b, #38f9d7);
  border-radius: 2px;
  transition: left 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(67, 233, 123, 0.5);
}

.tab-content {
  max-width: 900px;
  margin: 0 auto;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
  color: rgba(255, 255, 255, 0.6);
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(67, 233, 123, 0.2);
  border-top-color: #43e97b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 10px;
  color: rgba(255, 255, 255, 0.6);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 16px;
}

.empty-sub {
  font-size: 13px !important;
  color: rgba(255, 255, 255, 0.4) !important;
}

.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-card:hover {
  border-color: rgba(67, 233, 123, 0.3);
  box-shadow: 0 4px 20px rgba(67, 233, 123, 0.1);
}

.history-card-main {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
}

.history-left {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.type-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.type-badge.choice {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.type-badge.code, .type-badge.code_understanding {
  background: rgba(67, 233, 123, 0.2);
  color: #43e97b;
}

.type-badge.fill {
  background: rgba(240, 147, 251, 0.2);
  color: #f093fb;
}

.difficulty-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.difficulty-badge.easy {
  background: rgba(67, 233, 123, 0.15);
  color: #43e97b;
}

.difficulty-badge.medium {
  background: rgba(245, 175, 25, 0.15);
  color: #f5af19;
}

.difficulty-badge.hard {
  background: rgba(250, 112, 154, 0.15);
  color: #fa709a;
}

.history-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-topic {
  font-size: 14px;
  font-weight: 500;
  color: #ddd;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.history-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.history-score {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.history-score small {
  font-size: 12px;
  font-weight: 400;
}

.history-accuracy {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.expand-arrow {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.expand-arrow.rotated {
  transform: rotate(180deg);
}

.history-detail {
  padding: 0 20px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 500px; }
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 16px 0;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: #ddd;
}

.detail-value.correct {
  color: #43e97b;
}

.detail-value.score {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.detail-questions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.detail-question {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
}

.q-index {
  font-size: 11px;
  font-weight: 700;
  color: #667eea;
  min-width: 24px;
}

.q-text {
  flex: 1;
  font-size: 13px;
  color: #bbb;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.q-result {
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.q-result.correct {
  color: #43e97b;
}

.q-result.wrong {
  color: #fa709a;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px 0;
}

.page-btn {
  padding: 8px 20px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #ccc;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: rgba(67, 233, 123, 0.15);
  border-color: rgba(67, 233, 123, 0.4);
  color: #fff;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.wrong-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}

.category-select {
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #ccc;
  font-size: 13px;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
  -webkit-appearance: none;
  min-width: 140px;
}

.category-select:focus {
  border-color: rgba(67, 233, 123, 0.5);
}

.category-select option {
  background: #1a1a3e;
  color: #fff;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.15));
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.35), rgba(118, 75, 162, 0.3));
  border-color: rgba(102, 126, 234, 0.6);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.wrong-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.wrong-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 20px;
  transition: all 0.3s ease;
}

.wrong-card:hover {
  border-color: rgba(250, 112, 154, 0.3);
  box-shadow: 0 4px 20px rgba(250, 112, 154, 0.08);
}

.wrong-card.mastered {
  border-color: rgba(67, 233, 123, 0.2);
}

.wrong-card.mastered:hover {
  border-color: rgba(67, 233, 123, 0.4);
  box-shadow: 0 4px 20px rgba(67, 233, 123, 0.08);
}

.wrong-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.mastered-indicator {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 10px;
}

.mastered-indicator.mastered {
  background: rgba(67, 233, 123, 0.15);
  color: #43e97b;
}

.mastered-indicator.unmastered {
  background: rgba(245, 175, 25, 0.15);
  color: #f5af19;
}

.retry-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.wrong-question-text {
  font-size: 15px;
  line-height: 1.6;
  color: #ddd;
  margin-bottom: 14px;
}

.wrong-answers {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}

.answer-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
}

.answer-row.wrong-answer {
  background: rgba(250, 112, 154, 0.08);
  border: 1px solid rgba(250, 112, 154, 0.15);
}

.answer-row.correct-answer {
  background: rgba(67, 233, 123, 0.08);
  border: 1px solid rgba(67, 233, 123, 0.15);
}

.answer-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  min-width: 60px;
}

.answer-row.wrong-answer .answer-value {
  color: #fa709a;
}

.answer-row.correct-answer .answer-value {
  color: #43e97b;
}

.answer-value {
  font-size: 14px;
  font-weight: 500;
}

.wrong-explanation {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(102, 126, 234, 0.06);
  border-radius: 8px;
  margin-bottom: 14px;
}

.explanation-label {
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  white-space: nowrap;
}

.explanation-text {
  font-size: 13px;
  color: #bbb;
  line-height: 1.5;
}

.wrong-card-actions {
  display: flex;
  justify-content: flex-end;
}

.retry-btn {
  padding: 6px 16px;
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.1));
  color: #667eea;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.2));
  border-color: rgba(102, 126, 234, 0.6);
  color: #fff;
}

.retry-input-area {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 4px;
}

.retry-input {
  flex: 1;
  height: 38px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  font-size: 13px;
  outline: none;
  transition: all 0.3s ease;
}

.retry-input:focus {
  border-color: rgba(67, 233, 123, 0.5);
  box-shadow: 0 0 0 2px rgba(67, 233, 123, 0.1);
}

.retry-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.retry-submit-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  color: #0c0c1d;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(67, 233, 123, 0.3);
}

.retry-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.retry-cancel-btn {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #ccc;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-cancel-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.radar-chart-container {
  width: 100%;
  height: 400px;
  margin-bottom: 24px;
}

.radar-scores {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 28px;
}

.radar-score-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.radar-score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.radar-dim-name {
  font-size: 13px;
  color: #bbb;
}

.radar-dim-value {
  font-size: 13px;
  font-weight: 600;
  background: linear-gradient(135deg, #43e97b, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.radar-progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.radar-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #43e97b, #667eea);
  border-radius: 3px;
  transition: width 0.6s ease;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stats-card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.stats-card:hover {
  border-color: rgba(67, 233, 123, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(67, 233, 123, 0.1);
}

.stats-value {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}

.stats-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.leaderboard-sub-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.sub-tab-btn {
  flex: 1;
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sub-tab-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ddd;
}

.sub-tab-btn.active {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.15), rgba(102, 126, 234, 0.15));
  border-color: rgba(67, 233, 123, 0.4);
  color: #fff;
  font-weight: 600;
}

.top-three {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 28px;
  padding: 20px 0;
}

.top-user {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.top-user:hover {
  transform: translateY(-4px);
}

.top-user.rank-1 {
  border-color: rgba(255, 215, 0, 0.4);
  box-shadow: 0 4px 24px rgba(255, 215, 0, 0.15);
  padding: 28px 32px;
}

.top-user.rank-2 {
  border-color: rgba(192, 192, 192, 0.3);
  box-shadow: 0 4px 20px rgba(192, 192, 192, 0.1);
}

.top-user.rank-3 {
  border-color: rgba(205, 127, 50, 0.3);
  box-shadow: 0 4px 20px rgba(205, 127, 50, 0.1);
}

.medal {
  font-size: 32px;
}

.top-user.rank-1 .medal {
  font-size: 40px;
}

.top-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.top-user.rank-1 .top-avatar {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  width: 56px;
  height: 56px;
  font-size: 24px;
}

.top-user.rank-2 .top-avatar {
  background: linear-gradient(135deg, #c0c0c0, #a0a0a0);
}

.top-user.rank-3 .top-avatar {
  background: linear-gradient(135deg, #cd7f32, #b06820);
}

.top-name {
  font-size: 14px;
  font-weight: 600;
  color: #ddd;
}

.top-score {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.top-score small {
  font-size: 12px;
  font-weight: 400;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.rank-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.rank-item.is-me {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.1), rgba(102, 126, 234, 0.1));
  border-color: rgba(67, 233, 123, 0.3);
}

.rank-number {
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.4);
  min-width: 28px;
  text-align: center;
}

.rank-item.is-me .rank-number {
  color: #43e97b;
}

.rank-name {
  flex: 1;
  font-size: 14px;
  color: #ccc;
}

.rank-item.is-me .rank-name {
  color: #fff;
  font-weight: 600;
}

.rank-score {
  font-size: 14px;
  font-weight: 600;
  color: #ddd;
}

.rank-item.is-me .rank-score {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.rank-gap {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  min-width: 70px;
  text-align: right;
}

.rank-gap.next {
  color: rgba(67, 233, 123, 0.5);
}

@media (max-width: 768px) {
  .feedback-page {
    padding: 16px;
  }

  .history-card-main {
    flex-wrap: wrap;
    gap: 10px;
  }

  .history-left {
    width: 100%;
  }

  .history-right {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .top-three {
    flex-direction: column;
    align-items: center;
  }

  .top-user {
    width: 100%;
    max-width: 280px;
  }

  .top-user.rank-1 {
    order: -1;
  }

  .radar-chart-container {
    height: 320px;
  }

  .wrong-toolbar {
    flex-direction: column;
  }

  .category-select {
    width: 100%;
  }

  .export-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 22px;
  }

  .back-btn {
    position: static;
    margin-bottom: 12px;
  }

  .feedback-header {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .tab-label {
    display: none;
  }

  .tab-icon {
    font-size: 20px;
  }

  .tab-btn {
    padding: 10px 6px;
  }

  .history-card-main {
    padding: 12px 14px;
  }

  .history-score {
    font-size: 18px;
  }

  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .stats-summary {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .stats-card {
    padding: 14px 10px;
  }

  .stats-value {
    font-size: 20px;
  }

  .radar-chart-container {
    height: 260px;
  }

  .wrong-card {
    padding: 14px;
  }

  .rank-item {
    padding: 10px 12px;
    gap: 10px;
  }

  .rank-gap {
    display: none;
  }
}

.feedback-page:not(.dark-mode) {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%);
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .back-btn {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #4a4a6a;
}

.feedback-page:not(.dark-mode) .back-btn:hover {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.3);
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .page-subtitle {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .tab-list {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
}

.feedback-page:not(.dark-mode) .tab-btn {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .tab-btn:hover {
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .loading-state {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .empty-state {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .empty-sub {
  color: #9ca3af !important;
}

.feedback-page:not(.dark-mode) .history-card {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.feedback-page:not(.dark-mode) .history-card:hover {
  border-color: rgba(67, 233, 123, 0.3);
  box-shadow: 0 4px 20px rgba(67, 233, 123, 0.08);
}

.feedback-page:not(.dark-mode) .history-topic {
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .history-time {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .history-accuracy {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .expand-arrow {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .history-detail {
  border-top-color: rgba(0, 0, 0, 0.06);
}

.feedback-page:not(.dark-mode) .detail-label {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .detail-value {
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .q-text {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .pagination .page-btn {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.12);
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .pagination .page-btn:hover:not(:disabled) {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.3);
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .page-info {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .category-select {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(0, 0, 0, 0.15);
  color: #4a4a6a;
}

.feedback-page:not(.dark-mode) .category-select option {
  background: #fff;
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .export-btn {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.06));
  border-color: rgba(102, 126, 234, 0.3);
  color: #667eea;
}

.feedback-page:not(.dark-mode) .export-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.18), rgba(118, 75, 162, 0.14));
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.feedback-page:not(.dark-mode) .wrong-card {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.feedback-page:not(.dark-mode) .wrong-card:hover {
  border-color: rgba(250, 112, 154, 0.3);
  box-shadow: 0 4px 20px rgba(250, 112, 154, 0.06);
}

.feedback-page:not(.dark-mode) .retry-count {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .wrong-question-text {
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .answer-label {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .explanation-text {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .retry-input {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.15);
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .retry-input::placeholder {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .retry-cancel-btn {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.12);
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .radar-dim-name {
  color: #4a4a6a;
}

.feedback-page:not(.dark-mode) .radar-progress-bar {
  background: rgba(0, 0, 0, 0.06);
}

.feedback-page:not(.dark-mode) .stats-card {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.feedback-page:not(.dark-mode) .stats-card:hover {
  border-color: rgba(67, 233, 123, 0.3);
  box-shadow: 0 4px 16px rgba(67, 233, 123, 0.08);
}

.feedback-page:not(.dark-mode) .stats-label {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .sub-tab-btn {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(0, 0, 0, 0.1);
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .sub-tab-btn:hover {
  background: rgba(255, 255, 255, 0.85);
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .sub-tab-btn.active {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.1), rgba(102, 126, 234, 0.1));
  border-color: rgba(67, 233, 123, 0.35);
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .top-user {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.feedback-page:not(.dark-mode) .top-user.rank-1 {
  border-color: rgba(255, 215, 0, 0.4);
  box-shadow: 0 4px 24px rgba(255, 215, 0, 0.1);
}

.feedback-page:not(.dark-mode) .top-user.rank-2 {
  border-color: rgba(192, 192, 192, 0.3);
  box-shadow: 0 4px 20px rgba(192, 192, 192, 0.08);
}

.feedback-page:not(.dark-mode) .top-user.rank-3 {
  border-color: rgba(205, 127, 50, 0.3);
  box-shadow: 0 4px 20px rgba(205, 127, 50, 0.08);
}

.feedback-page:not(.dark-mode) .top-name {
  color: #1a1a2e;
}

.feedback-page:not(.dark-mode) .rank-item {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(0, 0, 0, 0.06);
}

.feedback-page:not(.dark-mode) .rank-item:hover {
  background: rgba(255, 255, 255, 0.85);
}

.feedback-page:not(.dark-mode) .rank-number {
  color: #9ca3af;
}

.feedback-page:not(.dark-mode) .rank-name {
  color: #6b7280;
}

.feedback-page:not(.dark-mode) .rank-score {
  color: #4a4a6a;
}

.feedback-page:not(.dark-mode) .rank-gap {
  color: #9ca3af;
}
</style>
