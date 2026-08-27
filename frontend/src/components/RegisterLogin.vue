<template>
  <div class="auth-container">
    <div class="auth-box">
      <h1>{{ isLogin ? '登录' : '注册' }}</h1>
      
      <div class="tab-bar">
        <button :class="{ active: tab === 'password' }" @click="tab='password'">密码登录</button>
        <button :class="{ active: tab === 'code' }" @click="tab='code'">验证码登录</button>
        <button :class="{ active: tab === 'social' }" @click="tab='social'">社交账号</button>
      </div>
      
      <form v-if="tab === 'password'" @submit.prevent="handlePasswordAuth">
        <input v-model="form.username" placeholder="用户名 / 手机号 / 邮箱" required />
        <input v-model="form.password" type="password" placeholder="密码" required minlength="6" />
        
        <div v-if="!isLogin" class="extra-fields">
          <input v-model="form.phone" placeholder="手机号（选填）" />
          <input v-model="form.email" type="email" placeholder="邮箱（选填）" />
        </div>
        
        <button type="submit" class="btn-primary">{{ isLogin ? '登录' : '注册' }}</button>
      </form>
      
      <form v-if="tab === 'code'" @submit.prevent="handleCodeAuth">
        <input v-model="form.account" placeholder="手机号 / 邮箱" required />
        <div class="code-row">
          <input v-model="form.code" placeholder="验证码" required />
          <button type="button" class="btn-send-code" @click="sendCode" :disabled="codeSending">
            {{ codeSending ? `${countdown}s` : '发送验证码' }}
          </button>
        </div>
        <input v-if="!isLogin" v-model="form.password" type="password" placeholder="设置密码（选填）" minlength="6" />
        
        <button type="submit" class="btn-primary">{{ isLogin ? '登录' : '注册' }}</button>
      </form>
      
      <div v-if="tab === 'social'" class="social-buttons">
        <button class="btn-wechat" @click="socialLogin('wechat')">微信登录</button>
        <button class="btn-qq" @click="socialLogin('qq')">QQ登录</button>
      </div>
      
      <div class="switch-link">
        <a href="#" @click.prevent="isLogin = !isLogin; resetForm()">
          {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
        </a>
        <a v-if="isLogin && tab !== 'social'" href="#" @click.prevent="showReset = true" style="margin-left: 16px;">忘记密码？</a>
      </div>
      
      <div v-if="showReset" class="reset-modal">
        <h3>重置密码</h3>
        <input v-model="resetAccount" placeholder="手机号 / 邮箱" />
        <div class="code-row">
          <input v-model="resetCode" placeholder="验证码" />
          <button @click="sendResetCode" :disabled="resetSending">{{ resetSending ? `${resetCountdown}s` : '发送验证码' }}</button>
        </div>
        <input v-model="resetPassword" type="password" placeholder="新密码" minlength="6" />
        <button @click="submitReset">确认重置</button>
        <button @click="showReset = false">取消</button>
      </div>
    </div>
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
      showReset: false,
      resetAccount: '',
      resetCode: '',
      resetPassword: '',
      resetSending: false,
      resetCountdown: 60,
      resetTimer: null
    }
  },
  methods: {
    resetForm() {
      this.form = { username: '', password: '', phone: '', email: '', account: '', code: '' }
    },
    handleAuthSuccess(userData, tip) {
      // 写入 Pinia store，否则路由守卫会把用户拦回登录页
      const userStore = useUserStore()
      userStore.login(userData)
      // 兼容讨论区等直接读取 localStorage 的旧逻辑
      localStorage.setItem('user_id', userData._id)
      localStorage.setItem('username', userData.username)
      alert(tip)
      const redirect = this.$route.query.redirect || '/'
      this.$router.push(redirect)
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
          alert(data.message)
        }
      } catch (e) {
        alert('网络错误')
      }
    },
    async sendCode() {
      if (!this.form.account) return alert('请输入手机号或邮箱')
      this.codeSending = true
      this.countdown = 60

      try {
        const res = await fetch(`${AUTH_BASE}/send-code`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.form.account })
        })
        const data = await res.json()
        if (data.code === 200) {
          alert(`验证码已发送${data.debug_code ? '（调试: ' + data.debug_code + '）' : ''}`)
          this.startCountdown()
        } else {
          alert(data.message)
          this.codeSending = false
        }
      } catch (e) {
        alert('发送失败')
        this.codeSending = false
      }
    },
    startCountdown() {
      clearInterval(this.timer)
      this.timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(this.timer)
          this.codeSending = false
        }
      }, 1000)
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
          alert(data.message)
        }
      } catch (e) {
        alert('网络错误')
      }
    },
    async socialLogin(type) {
      const fakeOpenid = `${type}_${Date.now()}`
      fetch(`${AUTH_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ method: type, [type === 'wechat' ? 'openid' : 'qq_openid']: fakeOpenid })
      })
      .then(r => r.json())
      .then(data => {
        if (data.code === 200) {
          this.handleAuthSuccess(data.data, `${type === 'wechat' ? '微信' : 'QQ'}登录成功`)
        }
      })
    },
    async sendResetCode() {
      if (!this.resetAccount) return alert('请输入手机号或邮箱')
      this.resetSending = true
      this.resetCountdown = 60
      
      try {
        const res = await fetch(`${AUTH_BASE}/send-code`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.resetAccount })
        })
        const data = await res.json()
        if (data.code === 200) {
          alert(`验证码已发送${data.debug_code ? '（调试: ' + data.debug_code + '）' : ''}`)
          this.resetTimer = setInterval(() => {
            this.resetCountdown--
            if (this.resetCountdown <= 0) {
              clearInterval(this.resetTimer)
              this.resetSending = false
            }
          }, 1000)
        } else {
          alert(data.message)
          this.resetSending = false
        }
      } catch (e) {
        alert('发送失败')
        this.resetSending = false
      }
    },
    async submitReset() {
      if (!this.resetAccount || !this.resetCode || !this.resetPassword) return alert('请填写完整信息')
      
      try {
        const res = await fetch(`${AUTH_BASE}/reset-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account: this.resetAccount, code: this.resetCode, new_password: this.resetPassword })
        })
        const data = await res.json()
        if (data.code === 200) {
          alert('密码重置成功，请重新登录')
          this.showReset = false
          this.resetForm()
        } else {
          alert(data.message)
        }
      } catch (e) {
        alert('网络错误')
      }
    }
  },
  beforeUnmount() {
    clearInterval(this.timer)
    clearInterval(this.resetTimer)
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}
.auth-box {
  background: white;
  border-radius: 12px;
  padding: 36px;
  width: 380px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.08);
}
.auth-box h1 {
  text-align: center;
  margin-bottom: 24px;
}
.tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.tab-bar button {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.tab-bar button.active {
  background: #07c160;
  color: white;
  border-color: #07c160;
}
form input {
  width: 100%;
  padding: 10px;
  margin-bottom: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}
.code-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.code-row input {
  flex: 1;
  margin-bottom: 0;
}
.btn-send-code {
  white-space: nowrap;
  padding: 10px 14px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}
.btn-primary {
  width: 100%;
  padding: 11px;
  background: #07c160;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 4px;
}
.social-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.btn-wechat, .btn-qq {
  padding: 12px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 15px;
  cursor: pointer;
}
.btn-wechat { background: #07c160; }
.btn-qq { background: #12b7f5; }
.switch-link {
  text-align: center;
  margin-top: 16px;
}
.switch-link a {
  color: #07c160;
  text-decoration: none;
  font-size: 14px;
}
.reset-modal {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.15);
  width: 340px;
  z-index: 99;
}
.reset-modal input {
  width: 100%;
  padding: 10px;
  margin-bottom: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}
.reset-modal button {
  margin-right: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.extra-fields {
  border-top: 1px dashed #eee;
  padding-top: 8px;
  margin-top: 4px;
}
</style>