<template>
  <el-header class="app-header">
    <div class="header-container">
      <!-- Logo -->
      <div class="logo-section">
        <router-link to="/" class="logo">
          <el-icon size="32"><Edit /></el-icon>
          <span class="logo-text">博客系统</span>
        </router-link>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <el-menu
          mode="horizontal"
          :default-active="activeIndex"
          class="nav-menu-inner"
          :ellipsis="false"
          @select="handleMenuSelect"
        >
          <el-menu-item index="home">
            <router-link to="/">首页</router-link>
          </el-menu-item>
          <el-menu-item index="posts">
            <router-link to="/posts">文章</router-link>
          </el-menu-item>
          <el-menu-item index="archives">
            <router-link to="/archives">归档</router-link>
          </el-menu-item>
          <el-menu-item index="tags">
            <router-link to="/tags">标签</router-link>
          </el-menu-item>
          <el-menu-item index="categories">
            <router-link to="/categories">分类</router-link>
          </el-menu-item>
          <el-menu-item index="about">
            <router-link to="/about">关于</router-link>
          </el-menu-item>
        </el-menu>
      </nav>
      
      <!-- 用户操作区 -->
      <div class="user-section">
        <!-- 搜索框 -->
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文章..."
            class="search-input"
            @keyup.enter="handleSearch"
            @input="handleSearchInput"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <!-- 搜索建议 -->
          <div v-if="searchSuggestions.length > 0" class="search-suggestions">
            <div
              v-for="suggestion in searchSuggestions"
              :key="suggestion.id"
              class="suggestion-item"
              @click="handleSuggestionClick(suggestion)"
            >
              <el-icon class="suggestion-icon">
                <component :is="suggestion.type === 'post' ? 'Document' : 'CollectionTag'" />
              </el-icon>
              <span class="suggestion-text">{{ suggestion.text }}</span>
            </div>
          </div>
        </div>
        
        <!-- 写文章按钮 -->
        <el-button
          v-if="authStore.isAuthenticated && authStore.hasPermission('create_posts')"
          type="primary"
          class="write-btn"
          @click="$router.push('/write')"
        >
          <el-icon><EditPen /></el-icon>
          写文章
        </el-button>
        
        <!-- 用户菜单 -->
        <div v-if="authStore.isAuthenticated" class="user-menu">
          <!-- 通知 -->
          <el-badge
            :value="notificationStore.unreadCount"
            :hidden="notificationStore.unreadCount === 0"
            class="notification-badge"
          >
            <el-button
              circle
              @click="$router.push('/notifications')"
            >
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          
          <!-- 用户头像和下拉菜单 -->
          <el-dropdown @command="handleUserCommand">
            <div class="user-avatar">
              <el-avatar
                :src="authStore.user?.avatar"
                :size="36"
                class="avatar"
              >
                {{ authStore.user?.nickname?.charAt(0) || authStore.user?.username?.charAt(0) }}
              </el-avatar>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isAdmin" command="admin">
                  <el-icon><Setting /></el-icon>
                  后台管理
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <!-- 登录/注册按钮 -->
        <div v-else class="auth-buttons">
          <el-button @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </div>
      </div>
      
      <!-- 移动端菜单按钮 -->
      <div class="mobile-menu-btn">
        <el-button
          @click="mobileMenuVisible = !mobileMenuVisible"
        >
          <el-icon>
            <component :is="mobileMenuVisible ? Close : Menu" />
          </el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 移动端菜单 -->
    <div v-if="mobileMenuVisible" class="mobile-menu">
      <el-menu
        mode="vertical"
        :default-active="activeIndex"
        @select="handleMobileMenuSelect"
      >
        <el-menu-item index="home">
          <router-link to="/">首页</router-link>
        </el-menu-item>
        <el-menu-item index="posts">
          <router-link to="/posts">文章</router-link>
        </el-menu-item>
        <el-menu-item index="archives">
          <router-link to="/archives">归档</router-link>
        </el-menu-item>
        <el-menu-item index="tags">
          <router-link to="/tags">标签</router-link>
        </el-menu-item>
        <el-menu-item index="categories">
          <router-link to="/categories">分类</router-link>
        </el-menu-item>
        <el-menu-item index="about">
          <router-link to="/about">关于</router-link>
        </el-menu-item>
        <el-menu-item v-if="authStore.isAuthenticated" index="write">
          <router-link to="/write">写文章</router-link>
        </el-menu-item>
      </el-menu>
    </div>
  </el-header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Edit, Search, EditPen, Bell, User, Setting, 
  SwitchButton, ArrowDown, Menu, Close, Document,
  CollectionTag
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { usePostsStore } from '@/stores/posts'
import { debounce } from 'lodash-es'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const postsStore = usePostsStore()

// 状态
const searchQuery = ref('')
const searchSuggestions = ref([])
const mobileMenuVisible = ref(false)

// 计算属性
const activeIndex = computed(() => {
  const path = route.path
  if (path === '/') return 'home'
  if (path.startsWith('/posts')) return 'posts'
  if (path.startsWith('/archives')) return 'archives'
  if (path.startsWith('/tags')) return 'tags'
  if (path.startsWith('/categories')) return 'categories'
  if (path.startsWith('/about')) return 'about'
  return 'home'
})

// 处理方法
const handleMenuSelect = (index) => {
  // 菜单选择处理
}

const handleMobileMenuSelect = (index) => {
  mobileMenuVisible.value = false
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  
  router.push({
    path: '/search',
    query: { q: searchQuery.value.trim() }
  })
  
  searchSuggestions.value = []
}

const handleSearchInput = debounce(async () => {
  const query = searchQuery.value.trim()
  if (!query || query.length < 2) {
    searchSuggestions.value = []
    return
  }
  
  try {
    const suggestions = await postsStore.getSearchSuggestions(query)
    searchSuggestions.value = suggestions
  } catch (error) {
    console.error('Search suggestions error:', error)
    searchSuggestions.value = []
  }
}, 300)

const handleSuggestionClick = (suggestion) => {
  searchQuery.value = ''
  searchSuggestions.value = []
  
  if (suggestion.type === 'post') {
    router.push(`/post/${suggestion.id}`)
  } else if (suggestion.type === 'tag') {
    router.push(`/tags/${suggestion.slug}`)
  }
}

const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'admin':
      // 跳转到后台管理
      window.open('/admin', '_blank')
      break
    case 'logout':
      try {
        await authStore.logout()
      } catch (error) {
        console.error('Logout error:', error)
      }
      break
  }
}

// 点击外部关闭搜索建议
const handleClickOutside = (event) => {
  const searchBox = event.target.closest('.search-box')
  if (!searchBox) {
    searchSuggestions.value = []
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // 初始化通知
  if (authStore.isAuthenticated) {
    notificationStore.fetchNotifications({ unread_only: true })
  }
})
</script>

<style scoped>
.app-header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--el-text-color-primary);
  font-weight: bold;
  font-size: 20px;
}

.logo-text {
  margin-left: 8px;
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
  display: flex;
  justify-content: center;
}

.nav-menu-inner {
  border-bottom: none;
}

.nav-menu-inner .el-menu-item a {
  text-decoration: none;
  color: inherit;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  position: relative;
}

.search-input {
  width: 200px;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  box-shadow: var(--el-box-shadow);
  z-index: 1001;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.suggestion-item:hover {
  background-color: var(--el-fill-color-light);
}

.suggestion-icon {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.suggestion-text {
  font-size: 14px;
}

.write-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  margin-right: 8px;
}

.user-avatar {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 4px;
}

.avatar {
  flex-shrink: 0;
}

.dropdown-icon {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.auth-buttons {
  display: flex;
  gap: 8px;
}

.mobile-menu-btn {
  display: none;
}

.mobile-menu {
  position: absolute;
  top: 60px;
  left: 0;
  right: 0;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  box-shadow: var(--el-box-shadow);
  z-index: 999;
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .search-input {
    width: 150px;
  }
  
  .write-btn {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .user-menu {
    gap: 8px;
  }
  
  .notification-badge {
    margin-right: 4px;
  }
}

@media (max-width: 480px) {
  .search-box {
    display: none;
  }
  
  .auth-buttons {
    gap: 4px;
  }
  
  .auth-buttons .el-button {
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>