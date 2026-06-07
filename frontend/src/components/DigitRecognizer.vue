<template>
  <div class="digit-recognizer" :class="{ 'dark-mode': isDark }">
    <div class="digit-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 1024 1024" width="20" height="20"><path d="M669.6 849.6L368.8 548.8c-12-12-12-32 0-44l300.8-300.8c12-12 32-12 44 0s12 32 0 44L436 526.8l277.6 278.8c12 12 12 32 0 44-6 6-14 8.4-22 8.4s-16-2.8-22-8.4z" fill="currentColor"/></svg>
        返回
      </button>
      <h1 class="page-title">手写数字识别</h1>
      <p class="page-subtitle">在画板上书写数字，AI实时识别你的笔迹 · CNN + GPU加速</p>
    </div>

    <div class="digit-body">
      <div class="canvas-section">
        <div class="canvas-wrapper">
          <canvas
            ref="drawCanvas"
            @mousedown="startDrawing"
            @mousemove="draw"
            @mouseup="stopDrawing"
            @mouseleave="stopDrawing"
            @touchstart.prevent="startDrawingTouch"
            @touchmove.prevent="drawTouch"
            @touchend="stopDrawing"
          ></canvas>
          <div class="canvas-hint" v-if="!hasDrawn">
            <span>✏️ 在此处书写数字 (0-9)</span>
          </div>
        </div>
        <div class="canvas-actions">
          <button class="clear-btn" @click="clearCanvas">
            <svg viewBox="0 0 1024 1024" width="16" height="16"><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64z m0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z" fill="currentColor"/><path d="M464 688a48 48 0 1 0 96 0 48 48 0 1 0-96 0z m16-304v176c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V384c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8z" fill="currentColor"/></svg>
            清除画板
          </button>
          <button class="recognize-btn" @click="recognize" :disabled="!hasDrawn || isRecognizing">
            {{ isRecognizing ? '识别中...' : '🔍 识别数字' }}
          </button>
        </div>
        <div class="pen-settings">
          <label>笔画粗细</label>
          <input type="range" min="8" max="30" v-model="penSize" />
          <span class="pen-size-label">{{ penSize }}px</span>
        </div>
      </div>

      <div class="result-section">
        <div class="result-card" v-if="result">
          <div class="result-main">
            <div class="result-number">{{ result.digit }}</div>
            <div class="result-confidence">
              <div class="confidence-bar">
                <div class="confidence-fill" :style="{ width: result.confidence + '%' }"></div>
              </div>
              <span class="confidence-text">置信度 {{ result.confidence.toFixed(1) }}%</span>
            </div>
          </div>
          <div class="result-meta">
            <span class="meta-item" v-if="result.inference_time_ms">
              ⚡ 推理耗时 {{ result.inference_time_ms }}ms
            </span>
            <span class="meta-item gpu" v-if="result.device === 'cuda'">
              🚀 GPU加速
            </span>
            <span class="meta-item" v-else>
              💻 CPU推理
            </span>
          </div>
        </div>

        <div class="result-placeholder" v-else>
          <div class="placeholder-icon">🔢</div>
          <p>在左侧画板书写数字后点击识别</p>
          <p class="placeholder-sub">基于CNN卷积神经网络 + MNIST数据集训练</p>
        </div>

        <button class="explain-btn" v-if="result" @click="openExplanation">
          <svg viewBox="0 0 1024 1024" width="18" height="18"><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z" fill="currentColor"/><path d="M464 336a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z" fill="currentColor"/></svg>
          识别过程详解
        </button>

        <div class="probability-chart" v-if="probabilities.length">
          <h3 class="chart-title">各数字概率分布</h3>
          <div class="prob-bars">
            <div class="prob-item" v-for="(prob, idx) in probabilities" :key="idx"
              :class="{ active: idx === result?.digit }">
              <span class="prob-label">{{ idx }}</span>
              <div class="prob-bar-bg">
                <div class="prob-bar-fill" :style="{ width: prob + '%', backgroundColor: idx === result?.digit ? '#43e97b' : '#667eea' }"></div>
              </div>
              <span class="prob-value">{{ prob.toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <div class="preview-section" v-if="hasDrawn">
          <h3 class="chart-title">28×28 像素化预览</h3>
          <canvas ref="previewCanvas" width="140" height="140" class="preview-canvas"></canvas>
          <p class="preview-hint">AI将手写图像缩小为28×28像素后进行识别</p>
        </div>

        <div class="gpu-info-card" v-if="gpuInfo">
          <h3 class="chart-title">GPU 加速信息</h3>
          <div class="gpu-details">
            <div class="gpu-row">
              <span class="gpu-label">设备</span>
              <span class="gpu-value">{{ gpuInfo.device_name || 'N/A' }}</span>
            </div>
            <div class="gpu-row" v-if="gpuInfo.cuda_version">
              <span class="gpu-label">CUDA版本</span>
              <span class="gpu-value">{{ gpuInfo.cuda_version }}</span>
            </div>
            <div class="gpu-row" v-if="gpuInfo.memory_total_gb">
              <span class="gpu-label">显存总量</span>
              <span class="gpu-value">{{ gpuInfo.memory_total_gb }} GB</span>
            </div>
            <div class="gpu-row" v-if="gpuInfo.memory_allocated_mb !== undefined">
              <span class="gpu-label">已用显存</span>
              <span class="gpu-value">{{ gpuInfo.memory_allocated_mb }} MB</span>
            </div>
          </div>
        </div>

        <div class="principle-section">
          <h3 class="chart-title">工作原理</h3>
          <div class="principle-steps">
            <div class="step">
              <div class="step-num">1</div>
              <div class="step-text">手写输入 → 图像采集</div>
            </div>
            <div class="step">
              <div class="step-num">2</div>
              <div class="step-text">图像预处理 → 缩放至28×28 + 归一化</div>
            </div>
            <div class="step">
              <div class="step-num">3</div>
              <div class="step-text">CNN特征提取 → 3层卷积+池化 (GPU加速)</div>
            </div>
            <div class="step">
              <div class="step-num">4</div>
              <div class="step-text">全连接分类 → Softmax输出概率分布</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <RecognitionExplanation
      :visible="showExplanation"
      :imageData="lastImageData"
      @close="closeExplanation"
    />
  </div>
</template>

<script>
import axios from 'axios'
import RecognitionExplanation from './RecognitionExplanation.vue'

const API_BASE = ''

export default {
  name: 'DigitRecognizer',
  components: { RecognitionExplanation },
  data() {
    return {
      isDrawing: false,
      hasDrawn: false,
      isRecognizing: false,
      penSize: 16,
      result: null,
      probabilities: [],
      gpuInfo: null,
      ctx: null,
      showExplanation: false,
      lastImageData: '',
      isDark: false
    }
  },
  mounted() {
    this.initCanvas()
    this.checkServiceStatus()
    this._darkObserver = new MutationObserver(() => { this.checkDarkMode() })
    this._darkObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
    this.checkDarkMode()
  },
  beforeUnmount() {
    if (this._darkObserver) this._darkObserver.disconnect()
  },
  methods: {
    goBack() {
      this.$router.push('/demo')
    },
    checkDarkMode() {
      this.isDark = document.documentElement.classList.contains('Dark') || document.documentElement.getAttribute('data-theme') === 'Dark'
    },
    async checkServiceStatus() {
      try {
        const res = await axios.get(`${API_BASE}/api/digit/status`, { timeout: 3000 })
        this.gpuInfo = res.data.gpu_info
      } catch (e) {
        console.warn('识别服务未启动')
      }
    },
    initCanvas() {
      const canvas = this.$refs.drawCanvas
      const size = 280
      canvas.width = size
      canvas.height = size
      this.ctx = canvas.getContext('2d')
      this.ctx.fillStyle = '#000'
      this.ctx.fillRect(0, 0, size, size)
      this.ctx.strokeStyle = '#fff'
      this.ctx.lineWidth = this.penSize
      this.ctx.lineCap = 'round'
      this.ctx.lineJoin = 'round'
    },
    getPos(e) {
      const canvas = this.$refs.drawCanvas
      const rect = canvas.getBoundingClientRect()
      const scaleX = canvas.width / rect.width
      const scaleY = canvas.height / rect.height
      return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
      }
    },
    startDrawing(e) {
      this.isDrawing = true
      const pos = this.getPos(e)
      this.ctx.beginPath()
      this.ctx.moveTo(pos.x, pos.y)
      this.ctx.lineWidth = this.penSize
    },
    draw(e) {
      if (!this.isDrawing) return
      const pos = this.getPos(e)
      this.ctx.lineTo(pos.x, pos.y)
      this.ctx.stroke()
      this.hasDrawn = true
    },
    stopDrawing() {
      this.isDrawing = false
    },
    startDrawingTouch(e) {
      const touch = e.touches[0]
      this.isDrawing = true
      const pos = this.getPos(touch)
      this.ctx.beginPath()
      this.ctx.moveTo(pos.x, pos.y)
      this.ctx.lineWidth = this.penSize
    },
    drawTouch(e) {
      if (!this.isDrawing) return
      const touch = e.touches[0]
      const pos = this.getPos(touch)
      this.ctx.lineTo(pos.x, pos.y)
      this.ctx.stroke()
      this.hasDrawn = true
    },
    openExplanation() {
      this.showExplanation = true
    },
    closeExplanation() {
      this.showExplanation = false
    },
    clearCanvas() {
      this.ctx.fillStyle = '#000'
      this.ctx.fillRect(0, 0, 280, 280)
      this.ctx.strokeStyle = '#fff'
      this.hasDrawn = false
      this.result = null
      this.probabilities = []
      this.showExplanation = false
      this.lastImageData = ''
      const previewCanvas = this.$refs.previewCanvas
      if (previewCanvas) {
        const pCtx = previewCanvas.getContext('2d')
        pCtx.clearRect(0, 0, 140, 140)
      }
    },
    updatePreview() {
      const canvas = this.$refs.drawCanvas
      const tempCanvas = document.createElement('canvas')
      tempCanvas.width = 28
      tempCanvas.height = 28
      const tempCtx = tempCanvas.getContext('2d')
      tempCtx.drawImage(canvas, 0, 0, 28, 28)
      const imageData = tempCtx.getImageData(0, 0, 28, 28)

      const previewCanvas = this.$refs.previewCanvas
      if (!previewCanvas) return
      const pCtx = previewCanvas.getContext('2d')
      pCtx.clearRect(0, 0, 140, 140)

      const cellSize = 5
      for (let y = 0; y < 28; y++) {
        for (let x = 0; x < 28; x++) {
          const idx = (y * 28 + x) * 4
          const brightness = imageData.data[idx]
          pCtx.fillStyle = `rgb(${brightness},${brightness},${brightness})`
          pCtx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize)
        }
      }
    },
    async recognize() {
      if (!this.hasDrawn || this.isRecognizing) return
      this.isRecognizing = true

      this.updatePreview()

      const canvas = this.$refs.drawCanvas
      const imageDataBase64 = canvas.toDataURL('image/png')
      this.lastImageData = imageDataBase64

      try {
        const res = await axios.post(`${API_BASE}/api/digit/recognize`, {
          image: imageDataBase64
        }, { timeout: 10000 })

        const data = res.data
        this.result = {
          digit: data.digit,
          confidence: data.confidence,
          inference_time_ms: data.inference_time_ms,
          device: data.device
        }
        this.probabilities = data.probabilities || []

        if (data.gpu_info) {
          this.gpuInfo = data.gpu_info
          this.gpuInfo.device_name = this.gpuInfo.device_name || (data.device === 'cuda' ? 'NVIDIA RTX 3090' : 'CPU')
          this.gpuInfo.cuda_version = this.gpuInfo.cuda_version || 'N/A'
          this.gpuInfo.memory_total_gb = this.gpuInfo.memory_total_gb || 'N/A'
        }

      } catch (error) {
        console.error('识别请求失败:', error)
        if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
          alert('识别服务未启动，请先启动后端服务：\ncd backend/DigitRecognition && python app.py')
        } else {
          alert('识别失败: ' + (error.response?.data?.error || error.message))
        }
      } finally {
        this.isRecognizing = false
      }
    }
  },
  watch: {
    penSize() {
      if (this.ctx) {
        this.ctx.lineWidth = this.penSize
      }
    }
  }
}
</script>

<style scoped>
.digit-recognizer {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #0d0d2b 100%);
  color: #fff;
  padding: 20px;
}

.digit-header {
  text-align: center;
  margin-bottom: 24px;
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

.digit-body {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.canvas-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.canvas-wrapper {
  position: relative;
  width: 280px;
  height: 280px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(67, 233, 123, 0.3);
  box-shadow: 0 0 20px rgba(67, 233, 123, 0.1);
}

.canvas-wrapper canvas {
  width: 100%;
  height: 100%;
  cursor: crosshair;
  touch-action: none;
}

.canvas-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #555;
  font-size: 14px;
  pointer-events: none;
  text-align: center;
}

.canvas-actions {
  display: flex;
  gap: 10px;
}

.clear-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #ccc;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.clear-btn:hover {
  background: rgba(255, 100, 100, 0.15);
  border-color: rgba(255, 100, 100, 0.4);
}

.recognize-btn {
  flex: 2;
  padding: 10px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  color: #0c0c1d;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.recognize-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);
}

.recognize-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pen-settings {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
}

.pen-settings label {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.pen-settings input[type="range"] {
  flex: 1;
  accent-color: #43e97b;
}

.pen-size-label {
  font-size: 12px;
  color: #667eea;
  min-width: 36px;
  text-align: right;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  background: rgba(67, 233, 123, 0.08);
  border: 1px solid rgba(67, 233, 123, 0.2);
  border-radius: 14px;
  padding: 24px;
  text-align: center;
  animation: resultAppear 0.4s ease;
}

@keyframes resultAppear {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.result-number {
  font-size: 72px;
  font-weight: 700;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 12px;
}

.confidence-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #43e97b, #38f9d7);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.confidence-text {
  font-size: 13px;
  color: #43e97b;
}

.result-meta {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
}

.meta-item {
  font-size: 12px;
  color: #888;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
}

.meta-item.gpu {
  color: #43e97b;
  background: rgba(67, 233, 123, 0.1);
}

.result-placeholder {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 40px;
  text-align: center;
}

.placeholder-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.result-placeholder p {
  color: #666;
  font-size: 14px;
}

.placeholder-sub {
  font-size: 12px !important;
  color: #555 !important;
  margin-top: 4px;
}

.probability-chart {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #ddd;
  margin-bottom: 12px;
}

.prob-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.prob-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
  transition: all 0.2s;
}

.prob-item.active .prob-label {
  color: #43e97b;
  font-weight: 700;
}

.prob-label {
  width: 16px;
  text-align: center;
  font-size: 13px;
  color: #aaa;
}

.prob-bar-bg {
  flex: 1;
  height: 14px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 7px;
  overflow: hidden;
}

.prob-bar-fill {
  height: 100%;
  border-radius: 7px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.prob-value {
  width: 48px;
  text-align: right;
  font-size: 12px;
  color: #888;
}

.preview-section {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.preview-canvas {
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  image-rendering: pixelated;
  width: 140px;
  height: 140px;
}

.preview-hint {
  font-size: 11px;
  color: #666;
  margin-top: 8px;
}

.gpu-info-card {
  background: rgba(67, 233, 123, 0.05);
  border: 1px solid rgba(67, 233, 123, 0.15);
  border-radius: 12px;
  padding: 16px;
}

.gpu-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.gpu-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gpu-label {
  font-size: 12px;
  color: #888;
}

.gpu-value {
  font-size: 12px;
  color: #43e97b;
  font-weight: 500;
}

.principle-section {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
}

.explain-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid rgba(67, 233, 123, 0.3);
  background: rgba(67, 233, 123, 0.06);
  color: #43e97b;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: explainBtnAppear 0.5s ease;
}

@keyframes explainBtnAppear {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.explain-btn:hover {
  background: rgba(67, 233, 123, 0.12);
  border-color: rgba(67, 233, 123, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(67, 233, 123, 0.15);
}

.principle-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  color: #0c0c1d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-text {
  font-size: 13px;
  color: #bbb;
}

@media (max-width: 768px) {
  .digit-body {
    grid-template-columns: 1fr;
  }

  .canvas-wrapper {
    width: 240px;
    height: 240px;
  }

  .back-btn {
    position: static;
    display: inline-flex;
    margin-bottom: 8px;
  }

  .page-title {
    font-size: 22px;
  }
}

.digit-recognizer:not(.dark-mode) {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%);
  color: #1a1a2e;
}

.digit-recognizer:not(.dark-mode) .back-btn {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #4a4a6a;
}

.digit-recognizer:not(.dark-mode) .back-btn:hover {
  background: rgba(67, 233, 123, 0.1);
  border-color: rgba(67, 233, 123, 0.3);
  color: #1a1a2e;
}

.digit-recognizer:not(.dark-mode) .page-subtitle {
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .canvas-wrapper {
  border-color: rgba(67, 233, 123, 0.2);
  box-shadow: 0 0 20px rgba(67, 233, 123, 0.05);
}

.digit-recognizer:not(.dark-mode) .canvas-hint {
  color: #999;
}

.digit-recognizer:not(.dark-mode) .clear-btn {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #4a4a6a;
}

.digit-recognizer:not(.dark-mode) .recognize-btn {
  color: #fff;
}

.digit-recognizer:not(.dark-mode) .pen-settings {
  background: rgba(0, 0, 0, 0.03);
}

.digit-recognizer:not(.dark-mode) .pen-settings label {
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .result-card {
  background: rgba(67, 233, 123, 0.06);
  border-color: rgba(67, 233, 123, 0.15);
}

.digit-recognizer:not(.dark-mode) .confidence-bar {
  background: rgba(0, 0, 0, 0.08);
}

.digit-recognizer:not(.dark-mode) .meta-item {
  background: rgba(0, 0, 0, 0.04);
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .result-placeholder {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
}

.digit-recognizer:not(.dark-mode) .result-placeholder p {
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .placeholder-sub {
  color: #999 !important;
}

.digit-recognizer:not(.dark-mode) .probability-chart {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
}

.digit-recognizer:not(.dark-mode) .chart-title {
  color: #1a1a2e;
}

.digit-recognizer:not(.dark-mode) .prob-label {
  color: #4a4a6a;
}

.digit-recognizer:not(.dark-mode) .prob-bar-bg {
  background: rgba(0, 0, 0, 0.06);
}

.digit-recognizer:not(.dark-mode) .prob-value {
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .preview-section {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
}

.digit-recognizer:not(.dark-mode) .preview-canvas {
  border-color: rgba(0, 0, 0, 0.1);
}

.digit-recognizer:not(.dark-mode) .preview-hint {
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .gpu-info-card {
  background: rgba(67, 233, 123, 0.04);
  border-color: rgba(67, 233, 123, 0.1);
}

.digit-recognizer:not(.dark-mode) .gpu-label {
  color: #6b7280;
}

.digit-recognizer:not(.dark-mode) .principle-section {
  background: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 0, 0, 0.08);
}

.digit-recognizer:not(.dark-mode) .step-text {
  color: #4a4a6a;
}

.digit-recognizer:not(.dark-mode) .explain-btn {
  background: rgba(67, 233, 123, 0.04);
  border-color: rgba(67, 233, 123, 0.2);
}
</style>
