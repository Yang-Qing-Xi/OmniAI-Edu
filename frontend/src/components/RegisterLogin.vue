<template>
  <div class="auth-container">
    <!-- Toast 通知 -->
    <transition name="toast-slide">
      <div v-if="toast.show" class="toast" :class="toast.type" @click="toast.show = false">
        {{ toast.msg }}
      </div>
    </transition>

    <div class="glass-card auth-box">
      <h1 class="auth-title">{{ isLogin ? '登录' : '注册' }}</h1>

      <div class="tab-bar">
        <button :class="{ active: tab === 'password' }" @click="tab='password'">密码</button>
        <button :class="{ active: tab === 'code' }" @click="tab='code'">验证码</button>
        <button :class="{ active: tab === 'social' }" @click="tab='social'">社交账号</button>
      </div>

      <!-- 密码登录/注册 -->
      <form v-if="tab === 'password'" @submit.prevent="handlePasswordAuth">
        <input v-model="form.username" class="glass-input" placeholder="用户名 / 手机号 / 邮箱" required />
        <input v-model="form.password" type="password" class="glass-input" placeholder="密码" required minlength="6" />
        <div v-if="!isLogin" class="extra-fields">
          <input v-model="form.phone" class="glass-input" placeholder="手机号（选填）" />
          <input v-model="form.email" type="email" class="glass-input" placeholder="邮箱（选填）" />
        </div>
        <button type="submit" class="btn-primary">{{ isLogin ? '登录' : '注册' }}</button>
      </form>

      <!-- 验证码登录/注册 -->
      <form v-if="tab === 'code'" @submit.prevent="handleCodeAuth">
        <input v-model="form.account" class="glass-input" placeholder="手机号 / 邮箱" required />
        <div class="code-row">
          <input v-model="form.code" class="glass-input" placeholder="验证码" required />
          <button type="button" class="btn-send-code" @click="sendCode" :disabled="codeSending">
            {{ codeSending ? `${countdown}s` : '发送验证码' }}
          </button>
        </div>
        <div v-if="codeHint" class="code-hint-box">
          <span class="hint-label">验证码</span>
          <strong class="hint-code">{{ codeHint }}</strong>
          <span class="hint-note">（调试模式，请输入上方验证码）</span>
        </div>
        <input v-if="!isLogin" v-model="form.password" type="password" class="glass-input" placeholder="设置密码（选填）" minlength="6" />
        <button type="submit" class="btn-primary">{{ isLogin ? '登录' : '注册' }}</button>
      </form>

      <!-- 社交账号 -->
      <div v-if="tab === 'social'" class="social-section">
        <p class="social-tip">选择社交账号登录，首次使用需绑定手机号或邮箱验证身份</p>
        <div class="social-buttons">
          <button class="btn-social btn-wechat" @click="startSocialLogin('wechat')">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
              <path d="M9.5 4C5.36 4 2 6.69 2 10c0 1.89 1.08 3.56 2.78 4.66L4 17l2.5-1.32c.91.2 1.94.32 3 .32.17 0 .33-.01.5-.02v-.48c0-2.49 2.69-4.5 6-4.5.17 0 .33.01.5.02C15.15 6.42 12.06 4 9.5 4z"/>
              <path d="M22 14.5C22 11.46 18.87 9 15 9s-7 2.46-7 5.5 3.13 5.5 7 5.5c.68 0 1.34-.07 1.97-.2L21 21l-1.07-1.78C21.5 18.27 22 16.45 22 14.5z"/>
            </svg>
            微信登录
          </button>
          <button class="btn-social btn-qq" @click="startSocialLogin('qq')">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
              <path d="M12 2C8.5 2 6 4.5 6 7.5c0 .8.15 1.55.42 2.23C5.23 10.3 4 12 4 14.2c0 1.3.5 2.5 1.3 3.4-.2.8-.6 1.7-1.2 2.3-.3.3-.4.7-.2 1.1.2.4.6.6 1 .6 1.3 0 2.5-.4 3.5-1 .9.4 1.9.6 2.9.6h2.4c1 0 2-.2 2.9-.6 1 .6 2.2 1 3.5 1 .4 0 .8-.2 1-.6.2-.4.1-.8-.2-1.1-.6-.6-1-1.5-1.2-2.3.8-.9 1.3-2.1 1.3-3.4 0-2.2-1.23-3.9-2.42-4.47.27-.68.42-1.43.42-2.23C18 4.5 15.5 2 12 2z"/>
            </svg>
            QQ登录
          </button>
        </div>
      </div>

      <div class="switch-link">
        <a href="#" @click.prevent="isLogin = !isLogin; resetForm()">
          {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
        </a>
        <a v-if="isLogin && tab !== 'social'" href="#" @click.prevent="showReset = true" class="reset-link">忘记密码？</a>
      </div>
    </div>

    <!-- 社交登录验证弹窗 -->
    <transition name="modal-fade">
      <div v-if="socialStep === 'verify'" class="modal-overlay" @click.self="cancelSocial">
        <div class="glass-card social-verify-box">
          <div class="verify-header">
            <span class="verify-icon" :class="socialType">
              {{ socialType === 'wechat' ? '💬' : '🐧' }}
            </span>
            <h3>{{ socialType === 'wechat' ? '微信' : 'QQ' }} 账号绑定</h3>
          </div>
          <p class="verify-tip">为保障账号安全，请先验证手机号或邮箱</p>
          <input v-model="socialAccount" class="glass-input" placeholder="手机号 / 邮箱" />
          <div class="code-row">
            <input v-model="socialCode" class="glass-input" placeholder="验证码" />
            <button type="button" class="btn-send-code" @click="sendSocialCode" :disabled="socialSending">
              {{ socialSending ? `${socialCountdown}s` : '发送' }}
            </button>
          </div>
          <div v-if="socialDebugCode" class="code-hint-box">
            <span class="hint-label">验证码</span>
            <strong class="hint-code">{{ socialDebugCode }}</strong>
          </div>
          <div class="form-actions">
            <button class="btn-ghost" @click="cancelSocial">取消</button>
            <button class="btn-primary" @click="verifyAndSocialLogin">验证并登录</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 重置密码弹窗 -->
    <transition name="modal-fade">
      <div v-if="showReset" class="modal-overlay" @click.self="showReset = false">
        <div class="glass-card reset-box">
          <h3 class="reset-title">重置密码</h3>
          <input v-model="resetAccount" class="glass-input" placeholder="手机号 / 邮箱" />
          <div class="code-row">
            <input v-model="resetCode" class="glass-input" placeholder="验证码" />
            <button type="button" class="btn-send-code" @click="sendResetCode" :disabled="resetSending">
              {{ resetSending ? `${resetCountdown}s` : '发送' }}
            </button>
          </div>
          <div v-if="resetCodeHint" class="code-hint-box">
            <span class="hint-label">验证码</span>
            <strong class="hint-code">{{ resetCodeHint }}</strong>
          </div>
          <input v-model="resetPassword" type="password" class="glass-input" placeholder="新密码（至少6位）" minlength="6" />
          <div class="form-actions">
            <button class="btn-ghost" @click="showReset = false">取消</button>
            <button class="btn-primary" @click="submitReset">确认重置</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { useUserStore } from '../store/user'

const AUTH_BASE = '/api/auth'

export default {
  data() {
    return {
      isLogin: true,
      tab: 'password',
      form: { username: '', password: '', phone: '', email: '', account: '', code: '' },
      codeSending: false,
      countdown: 60,
      timer: null,
      codeHint: '',
      showReset: false,
      resetAccount: '',
      resetCode: '',
      resetPassword: '',
      resetSending: false,
      resetCountdown: 60,
      resetTimer: null,
      resetCodeHint: '',
      socialStep: '',
      socialType: '',
      socialAccount: '',
      socialCode: '',
      socialSending: false,
      socialCountdown: 60,
      socialTimer: null,
      socialDebugCode: '',
      toast: { show: false, msg: '', type: 'info', timer: null }
    }
  },
  methods: {
    showToast(msg, type = 'info') {
      clearTimeout(this.toast.timer)
      this.toast = { show: true, msg, type, timer: setTimeout(() => { this.toast.show = false }, 3500) }
    },
    resetForm() {
      this.form = { username: '', password: '', phone: '', email: '', account: '', code: '' }
      this.codeHint = ''
    },
    handleAuthSuccess(userData, tip) {
      const userStore = useUserStore()
      userStore.login(userData)
      localStorage.setItem('user_id', userData._id)
      localStorage.setItem('username', userData.username)
      this.showToast(tip, 'success')
      setTimeout(() => {
        const redirect = this.$route.query.redirect || '/'
        this.$router.push(redirect)
      }, 600)
    },
    async handlePasswordAuth() {
      const url = this.isLogin ? `${AUTH_BASE}/login` : `${AUTH_BASE}/register`
      const body = this.isLogin
        ? { method: 'password', account: this.form.username, password: this.form.password }
        : { method: 'password', username: this.form.username, password: this.form.password, phone: this.form.phone, email: this.form.email }
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })
        const data = await res.json()
        if (data.code === 200) {
          this.handleAuthSuccess(data.data, this.isLogin ? '登录成功' : '注册成功')
        } else {
          this.showToast(data.message, 'error')
        }
      } catch (e) {
        this.showToast('网络错误，请检查后端服务是否运行', 'error')
      }
    },
    startCountdown(field, sendingField) {
      const t = setInterval(() => {
        this[field]--
        if (this[field] <= 0) {
          clearInterval(t)
          this[sendingField] = false
        }
      }, 1000)
      return t
    },
    async sendCode() {
      if (!this.form.account) return this.showToast('请输入手机号或邮箱', 'error')
      this.codeSending = true
      this.countdown = 60
      this.codeHint = ''
      try {
        const res = await fetch(`${AUTH_BASE}/send-code`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.form.account })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.codeHint = data.debug_code || ''
          this.showToast('验证码已发送（见下方提示框）', 'success')
          this.timer = this.startCountdown('countdown', 'codeSending')
        } else {
          this.showToast(data.message, 'error')
          this.codeSending = false
        }
      } catch (e) {
        this.showToast('发送失败，请检查后端服务', 'error')
        this.codeSending = false
      }
    },
    async handleCodeAuth() {
      const url = this.isLogin ? `${AUTH_BASE}/login` : `${AUTH_BASE}/register`
      const body = { method: 'code', account: this.form.account, code: this.form.code }
      if (!this.isLogin) body.password = this.form.password
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })
        const data = await res.json()
        if (data.code === 200) {
          this.handleAuthSuccess(data.data, this.isLogin ? '登录成功' : '注册成功')
        } else {
          this.showToast(data.message, 'error')
        }
      } catch (e) {
        this.showToast('网络错误', 'error')
      }
    },
    /* ====== 社交登录：验证流程 ====== */
    startSocialLogin(type) {
      this.socialType = type
      this.socialStep = 'verify'
      this.socialAccount = ''
      this.socialCode = ''
      this.socialDebugCode = ''
    },
    cancelSocial() {
      this.socialStep = ''
      this.socialType = ''
      this.socialAccount = ''
      this.socialCode = ''
      this.socialDebugCode = ''
      clearInterval(this.socialTimer)
      this.socialSending = false
      this.socialCountdown = 60
    },
    async sendSocialCode() {
      if (!this.socialAccount) return this.showToast('请输入手机号或邮箱', 'error')
      this.socialSending = true
      this.socialCountdown = 60
      this.socialDebugCode = ''
      try {
        const res = await fetch(`${AUTH_BASE}/send-code`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.socialAccount })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.socialDebugCode = data.debug_code || ''
          this.showToast('验证码已发送（见下方提示框）', 'success')
          this.socialTimer = this.startCountdown('socialCountdown', 'socialSending')
        } else {
          this.showToast(data.message, 'error')
          this.socialSending = false
        }
      } catch (e) {
        this.showToast('发送失败', 'error')
        this.socialSending = false
      }
    },
    async verifyAndSocialLogin() {
      if (!this.socialAccount) return this.showToast('请输入手机号或邮箱', 'error')
      if (!this.socialCode) return this.showToast('请输入验证码', 'error')
      // 前端校验验证码（后端 send-code 返回的 debug_code）
      if (this.socialDebugCode && this.socialCode !== this.socialDebugCode) {
        return this.showToast('验证码不正确', 'error')
      }
      // 验证通过，执行社交登录（模拟 openid）
      const fakeOpenid = `${this.socialType}_${this.socialAccount}_${Date.now()}`
      const field = this.socialType === 'wechat' ? 'openid' : 'qq_openid'
      try {
        const res = await fetch(`${AUTH_BASE}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ method: this.socialType, [field]: fakeOpenid })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.handleAuthSuccess(data.data, `${this.socialType === 'wechat' ? '微信' : 'QQ'}登录成功`)
        } else {
          this.showToast(data.message, 'error')
        }
      } catch (e) {
        this.showToast('网络错误', 'error')
      }
    },
    /* ====== 重置密码 ====== */
    async sendResetCode() {
      if (!this.resetAccount) return this.showToast('请输入手机号或邮箱', 'error')
      this.resetSending = true
      this.resetCountdown = 60
      this.resetCodeHint = ''
      try {
        const res = await fetch(`${AUTH_BASE}/send-code`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.resetAccount })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.resetCodeHint = data.debug_code || ''
          this.showToast('验证码已发送', 'success')
          this.resetTimer = this.startCountdown('resetCountdown', 'resetSending')
        } else {
          this.showToast(data.message, 'error')
          this.resetSending = false
        }
      } catch (e) {
        this.showToast('发送失败', 'error')
        this.resetSending = false
      }
    },
    async submitReset() {
      if (!this.resetAccount || !this.resetCode || !this.resetPassword)
        return this.showToast('请填写完整信息', 'error')
      try {
        const res = await fetch(`${AUTH_BASE}/reset-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.resetAccount, code: this.resetCode, new_password: this.resetPassword })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.showToast('密码重置成功，请重新登录', 'success')
          this.showReset = false
          this.isLogin = true
          this.resetForm()
        } else {
          this.showToast(data.message, 'error')
        }
      } catch (e) {
        this.showToast('网络错误', 'error')
      }
    }
  },
  beforeUnmount() {
    clearInterval(this.timer)
    clearInterval(this.resetTimer)
    clearInterval(this.socialTimer)
    clearTimeout(this.toast.timer)
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  position: relative;
}

/* ===== 玻璃拟态卡片 ===== */
.glass-card {
  background: var(--item_bg_color, rgba(20, 20, 35, 0.5));
  backdrop-filter: blur(18px) saturate(1.3);
  -webkit-backdrop-filter: blur(18px) saturate(1.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.25);
}

.auth-box {
  border-radius: 18px;
  padding: 36px 34px;
  width: 390px;
  max-width: 92vw;
}

/* ===== 标题 ===== */
.auth-title {
  text-align: center;
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 24px;
  background: var(--gradient, linear-gradient(120deg, #bd34fe, #41d1ff));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ===== Tab 切换 ===== */
.tab-bar {
  display: flex;
  gap: 6px;
  margin-bottom: 22px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 4px;
}
.tab-bar button {
  flex: 1;
  padding: 8px;
  border: none;
  background: transparent;
  color: var(--item_left_text_color, rgba(255, 255, 255, 0.55));
  border-radius: 9px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.25s;
}
.tab-bar button.active {
  background: linear-gradient(135deg, #6c5ce7, #a29bfe);
  color: #fff;
  box-shadow: 0 2px 12px rgba(108, 92, 231, 0.35);
}

/* ===== 输入框 ===== */
.glass-input {
  width: 100%;
  padding: 11px 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: var(--item_left_title_color, #ffffff);
  font-size: 14px;
  box-sizing: border-box;
  margin-bottom: 12px;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.glass-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}
.glass-input:focus {
  outline: none;
  border-color: rgba(108, 92, 231, 0.6);
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.15);
}

/* ===== 验证码行 ===== */
.code-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.code-row .glass-input {
  flex: 1;
  margin-bottom: 0;
}
.btn-send-code {
  white-space: nowrap;
  padding: 11px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: var(--item_left_title_color, rgba(255, 255, 255, 0.85));
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.btn-send-code:hover:not(:disabled) {
  background: rgba(108, 92, 231, 0.2);
  border-color: rgba(108, 92, 231, 0.4);
}
.btn-send-code:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== 验证码提示框 ===== */
.code-hint-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(108, 92, 231, 0.12);
  border: 1px solid rgba(108, 92, 231, 0.25);
  border-radius: 10px;
  margin-bottom: 14px;
  font-size: 14px;
  animation: hint-pop 0.3s ease;
}
.hint-label {
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
}
.hint-code {
  color: #a29bfe;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 2px;
}
.hint-note {
  color: rgba(255, 255, 255, 0.35);
  font-size: 12px;
}

@keyframes hint-pop {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* ===== 按钮 ===== */
.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #6c5ce7, #a29bfe);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(108, 92, 231, 0.4);
}
.btn-ghost {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--item_left_title_color, rgba(255, 255, 255, 0.8));
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.14);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 4px;
}

/* ===== 社交登录区 ===== */
.social-section {
  text-align: center;
}
.social-tip {
  font-size: 13px;
  color: var(--item_left_text_color, rgba(255, 255, 255, 0.5));
  margin-bottom: 20px;
  line-height: 1.6;
}
.social-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.btn-social {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 13px;
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-social:hover {
  transform: translateY(-2px);
}
.btn-wechat {
  background: linear-gradient(135deg, #07c160, #2dcf6e);
  box-shadow: 0 4px 16px rgba(7, 193, 96, 0.35);
}
.btn-wechat:hover {
  box-shadow: 0 6px 24px rgba(7, 193, 96, 0.5);
}
.btn-qq {
  background: linear-gradient(135deg, #12b7f5, #3ac8ff);
  box-shadow: 0 4px 16px rgba(18, 183, 245, 0.35);
}
.btn-qq:hover {
  box-shadow: 0 6px 24px rgba(18, 183, 245, 0.5);
}

/* ===== 切换链接 ===== */
.switch-link {
  text-align: center;
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
}
.switch-link a {
  color: #a29bfe;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}
.switch-link a:hover {
  color: #c4b8ff;
}

/* ===== 弹窗通用 ===== */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99;
  padding: 20px;
}
.social-verify-box, .reset-box {
  border-radius: 16px;
  padding: 30px 28px;
  width: 360px;
  max-width: 92vw;
}

/* ===== 社交验证弹窗 ===== */
.verify-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.verify-icon {
  font-size: 24px;
}
.verify-icon.wechat { color: #07c160; }
.verify-icon.qq { color: #12b7f5; }
.verify-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--item_left_title_color, #ffffff);
  margin: 0;
}
.verify-tip {
  font-size: 13px;
  color: var(--item_left_text_color, rgba(255, 255, 255, 0.5));
  margin-bottom: 18px;
}

/* ===== 重置密码弹窗 ===== */
.reset-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--item_left_title_color, #ffffff);
  margin-bottom: 20px;
  text-align: center;
}

/* ===== Toast ===== */
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  z-index: 9999;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  white-space: nowrap;
}
.toast.success {
  background: rgba(7, 193, 96, 0.85);
  color: #fff;
  border: 1px solid rgba(7, 193, 96, 0.5);
}
.toast.error {
  background: rgba(231, 76, 60, 0.85);
  color: #fff;
  border: 1px solid rgba(231, 76, 60, 0.5);
}
.toast.info {
  background: rgba(108, 92, 231, 0.85);
  color: #fff;
  border: 1px solid rgba(108, 92, 231, 0.5);
}

/* ===== 过渡动画 ===== */
.toast-slide-enter-active, .toast-slide-leave-active {
  transition: all 0.3s ease;
}
.toast-slide-enter-from, .toast-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-12px);
}

.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}

/* ===== 移动端 ===== */
@media (max-width: 480px) {
  .auth-box { padding: 28px 22px; width: 100%; }
  .auth-title { font-size: 22px; }
  .social-verify-box, .reset-box { padding: 24px 20px; width: 100%; }
}
</style>
