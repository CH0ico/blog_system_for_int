<template>
  <el-footer class="app-footer">
    <div class="footer-container">
      <!-- 页脚内容 -->
      <div class="footer-content">
        <!-- 关于网站 -->
        <div class="footer-section">
          <h4>关于博客</h4>
          <p>一个现代化的博客系统，采用Vue.js + Flask技术栈构建，支持实时通信、社交互动等功能。</p>
        </div>
        
        <!-- 快速链接 -->
        <div class="footer-section">
          <h4>快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/posts">文章</router-link></li>
            <li><router-link to="/archives">归档</router-link></li>
            <li><router-link to="/tags">标签</router-link></li>
            <li><router-link to="/categories">分类</router-link></li>
            <li><router-link to="/about">关于</router-link></li>
          </ul>
        </div>
        
        <!-- 技术栈 -->
        <div class="footer-section">
          <h4>技术栈</h4>
          <div class="tech-stack">
            <el-tag>Vue.js 3</el-tag>
            <el-tag>Element Plus</el-tag>
            <el-tag>Flask</el-tag>
            <el-tag>Socket.IO</el-tag>
            <el-tag>JWT</el-tag>
            <el-tag>SQLite/MySQL</el-tag>
          </div>
        </div>
        
        <!-- 联系信息 -->
        <div class="footer-section">
          <h4>联系我们</h4>
          <div class="contact-info">
            <p><el-icon><Message /></el-icon> contact@blog.com</p>
            <p><el-icon><Link /></el-icon> https://blog.example.com</p>
          </div>
        </div>
      </div>
      
      <!-- 版权信息 -->
      <div class="footer-bottom">
        <div class="copyright">
          <p>&copy; {{ currentYear }} 博客系统. All rights reserved.</p>
          <p>Powered by Vue.js & Flask</p>
        </div>
        
        <!-- 统计信息 -->
        <div class="stats" v-if="stats.totalPosts > 0">
          <span>文章总数: {{ stats.totalPosts }}</span>
          <span>运行天数: {{ stats.runningDays }}</span>
          <span v-if="onlineCount > 0">在线用户: {{ onlineCount }}</span>
        </div>
      </div>
    </div>
  </el-footer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Message, Link, User, Document, CollectionTag,
  Calendar, Folder, PriceTag
} from '@element-plus/icons-vue'
import { usePostsStore } from '@/stores/posts'
import { useSocketStore } from '@/stores/socket'

const postsStore = usePostsStore()
const socketStore = useSocketStore()

// 状态
const stats = ref({
  totalPosts: 0,
  runningDays: 0
})

// 计算属性
const currentYear = computed(() => new Date().getFullYear())
const onlineCount = computed(() => socketStore.onlineCount)

// 获取统计信息
const fetchStats = async () => {
  try {
    // 获取文章总数
    await postsStore.fetchPosts({ per_page: 1 })
    stats.value.totalPosts = postsStore.pagination.total
    
    // 计算运行天数（假设从2024年1月1日开始）
    const startDate = new Date('2024-01-01')
    const now = new Date()
    const diffTime = Math.abs(now - startDate)
    stats.value.runningDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.app-footer {
  background-color: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-lighter);
  padding: 40px 0 20px;
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.footer-section h4 {
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.footer-section p {
  color: var(--el-text-color-secondary);
  line-height: 1.6;
  margin-bottom: 8px;
}

.footer-links {
  list-style: none;
  padding: 0;
}

.footer-links li {
  margin-bottom: 8px;
}

.footer-links a {
  color: var(--el-text-color-secondary);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: var(--el-color-primary);
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.contact-info p {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-bottom {
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.copyright {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.copyright p {
  margin: 0;
}

.stats {
  display: flex;
  gap: 16px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
  
  .stats {
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .app-footer {
    padding: 20px 0 10px;
  }
  
  .footer-container {
    padding: 0 16px;
  }
  
  .footer-content {
    gap: 16px;
  }
  
  .footer-section h4 {
    font-size: 14px;
  }
  
  .footer-section p {
    font-size: 12px;
  }
  
  .copyright {
    font-size: 12px;
  }
  
  .stats {
    font-size: 12px;
    gap: 8px;
  }
}
</style>