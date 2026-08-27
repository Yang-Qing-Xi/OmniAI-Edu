<template>
  <div class="discussion-container">
    <h1>讨论区</h1>
    <p class="subtitle">在这里交流学习心得、反馈使用问题 ✏️</p>

    <button class="btn-post" @click="showPostForm = !showPostForm">发布新帖</button>

    <div v-if="showPostForm" class="post-form">
      <input v-model="newPost.title" placeholder="标题" />
      <textarea v-model="newPost.content" placeholder="内容"></textarea>
      <button @click="submitPost">提交</button>
      <button @click="showPostForm = false">取消</button>
    </div>

    <div v-if="loading" class="empty-tip">加载中...</div>
    <div v-else-if="posts.length === 0" class="empty-tip">还没有帖子，来发第一帖吧！</div>

    <div v-for="post in posts" :key="post._id" class="post-card" @click="viewPost(post._id)">
      <h3>{{ post.title }}</h3>
      <p>{{ post.content.substring(0, 100) }}{{ post.content.length > 100 ? '...' : '' }}</p>
      <div class="post-meta">
        <span>{{ post.username }}</span>
        <span>{{ formatTime(post.created_at) }}</span>
        <span class="meta-btn" @click.stop="likePost(post)">👍 {{ post.likes || 0 }}</span>
        <span>💬 {{ post.reply_count || 0 }}</span>
        <span>👁️ {{ post.views || 0 }}</span>
        <span
          v-if="isOwnPost(post)"
          class="meta-btn delete-btn"
          @click.stop="deletePost(post)"
        >🗑️ 删除</span>
      </div>
    </div>

    <div class="pagination">
      <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
      <span>{{ page }} / {{ pages }}</span>
      <button :disabled="page >= pages" @click="changePage(page + 1)">下一页</button>
    </div>

    <div v-if="selectedPost" class="modal-overlay" @click.self="closeDetail">
      <div class="modal-content">
        <h2>{{ selectedPost.title }}</h2>
        <div class="post-info">
          <span>{{ selectedPost.username }}</span>
          <span>{{ formatTime(selectedPost.created_at) }}</span>
          <span>👁️ {{ selectedPost.views || 0 }}</span>
        </div>
        <p class="post-body">{{ selectedPost.content }}</p>

        <div class="replies">
          <h4>回复 ({{ selectedPost.replies?.length || 0 }})</h4>
          <div v-for="reply in selectedPost.replies" :key="reply._id" class="reply-item">
            <strong>{{ reply.username }}</strong>
            <p>{{ reply.content }}</p>
            <small>{{ formatTime(reply.created_at) }}</small>
          </div>
        </div>

        <div class="reply-input">
          <textarea v-model="replyContent" placeholder="写下你的回复..."></textarea>
          <button @click="submitReply(selectedPost._id)">回复</button>
        </div>

        <button class="close-btn" @click="closeDetail">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '../store/user'

const API_BASE = '/api/discussions'

export default {
  data() {
    return {
      posts: [],
      page: 1,
      pages: 1,
      loading: false,
      showPostForm: false,
      newPost: { title: '', content: '' },
      selectedPost: null,
      replyContent: ''
    }
  },
  computed: {
    userStore() {
      return useUserStore()
    },
    currentUserId() {
      return this.userStore.user?._id || localStorage.getItem('user_id') || ''
    },
    currentUsername() {
      return this.userStore.user?.username || localStorage.getItem('username') || '匿名用户'
    }
  },
  mounted() {
    this.fetchPosts()
  },
  methods: {
    isOwnPost(post) {
      return this.currentUserId && String(post.user_id || '') === String(this.currentUserId)
    },
    async fetchPosts() {
      this.loading = true
      try {
        const res = await fetch(`${API_BASE}?page=${this.page}&limit=10`)
        const data = await res.json()
        if (data.code === 200) {
          this.posts = data.data.posts
          this.pages = data.data.pages
        }
      } catch (e) {
        console.error('获取帖子失败:', e)
      } finally {
        this.loading = false
      }
    },
    changePage(p) {
      this.page = p
      this.fetchPosts()
    },
    async submitPost() {
      if (!this.newPost.title || !this.newPost.content) return alert('请填写标题和内容')
      try {
        const res = await fetch(API_BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...this.newPost,
            user_id: this.currentUserId,
            username: this.currentUsername
          })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.showPostForm = false
          this.newPost = { title: '', content: '' }
          this.fetchPosts()
        } else {
          alert(data.message)
        }
      } catch (e) {
        alert('发布失败')
      }
    },
    async viewPost(id) {
      try {
        const res = await fetch(`${API_BASE}/${id}`)
        const data = await res.json()
        if (data.code === 200) {
          this.selectedPost = data.data
        }
      } catch (e) {
        console.error('获取帖子详情失败:', e)
      }
    },
    closeDetail() {
      this.selectedPost = null
      this.replyContent = ''
      this.fetchPosts()
    },
    async likePost(post) {
      try {
        const res = await fetch(`${API_BASE}/${post._id}/like`, { method: 'POST' })
        const data = await res.json()
        if (data.code === 200) {
          post.likes = data.likes
        }
      } catch (e) {
        console.error('点赞失败:', e)
      }
    },
    async deletePost(post) {
      if (!confirm('确定要删除这篇帖子吗？（回复也会一并删除）')) return
      try {
        const res = await fetch(`${API_BASE}/${post._id}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: this.currentUserId })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.fetchPosts()
        } else {
          alert(data.message)
        }
      } catch (e) {
        alert('删除失败')
      }
    },
    async submitReply(postId) {
      if (!this.replyContent.trim()) return alert('请输入回复内容')
      try {
        const res = await fetch(`${API_BASE}/${postId}/reply`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: this.replyContent,
            user_id: this.currentUserId,
            username: this.currentUsername
          })
        })
        const data = await res.json()
        if (data.code === 200) {
          this.replyContent = ''
          this.viewPost(postId)
        } else {
          alert(data.message)
        }
      } catch (e) {
        alert('回复失败')
      }
    },
    formatTime(t) {
      if (!t) return ''
      return new Date(t).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.discussion-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
.subtitle {
  color: #888;
  margin-top: -8px;
  margin-bottom: 12px;
}
.btn-post {
  background: #07c160;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 12px;
}
.post-form {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.post-form input, .post-form textarea {
  width: 100%;
  margin-bottom: 8px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
.post-form textarea {
  height: 80px;
}
.post-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 10px;
  cursor: pointer;
}
.post-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.post-card h3 {
  margin: 0 0 6px;
  font-size: 18px;
}
.post-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #888;
  margin-top: 8px;
  align-items: center;
}
.meta-btn {
  cursor: pointer;
  user-select: none;
}
.meta-btn:hover {
  color: #07c160;
}
.delete-btn:hover {
  color: #e74c3c;
}
.empty-tip {
  text-align: center;
  color: #999;
  padding: 32px 0;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.modal-content {
  background: white;
  border-radius: 12px;
  padding: 28px;
  max-width: 640px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
}
.post-info {
  display: flex;
  gap: 15px;
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}
.post-body {
  line-height: 1.6;
  white-space: pre-wrap;
}
.replies {
  margin-top: 22px;
  border-top: 1px solid #eee;
  padding-top: 14px;
}
.reply-item {
  background: #f9f9f9;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 8px;
}
.reply-item p {
  margin: 4px 0;
}
.reply-input {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}
.reply-input textarea {
  flex: 1;
  height: 50px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.close-btn {
  margin-top: 12px;
  background: #eee;
  border: none;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
