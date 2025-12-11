<template>
  <el-header class="cassette-header">
    <div class="cassette-header-container">
      <!-- Logo -->
      <div class="cassette-logo-section">
        <router-link to="/" class="cassette-logo">
          <div class="cassette-wheel"></div>
          <span class="cassette-logo-text">PROJECT INSIGHT</span>
        </router-link>
      </div>

      <!-- 导航菜单 -->
      <nav class="cassette-nav-menu">
        <div class="nav-directory">
          <div class="nav-item-wrapper" @click="$router.push('/')">
            <div class="echo-btn" :class="{ active: activeIndex === 'home' }">
              <span class="icon">⌂</span>
              HOME
            </div>
          </div>
          <div class="nav-item-wrapper" @click="$router.push('/posts')">
            <div class="echo-btn" :class="{ active: activeIndex === 'posts' }">
              <span class="icon">✎</span>
              ARCHIVES
            </div>
          </div>
          <div class="nav-item-wrapper" @click="$router.push('/tags')">
            <div class="echo-btn" :class="{ active: activeIndex === 'tags' }">
              <span class="icon">🏷</span>
              TAGS
            </div>
          </div>
          <div class="nav-item-wrapper" @click="$router.push('/categories')">
            <div
              class="echo-btn"
              :class="{ active: activeIndex === 'categories' }"
            >
              <span class="icon">⚏</span>
              CATEGORIES
            </div>
          </div>
          <div class="nav-item-wrapper" @click="$router.push('/about')">
            <div class="echo-btn" :class="{ active: activeIndex === 'about' }">
              <span class="icon">ℹ</span>
              ABOUT
            </div>
          </div>
        </div>
      </nav>

      <!-- 用户操作区 -->
      <div class="cassette-user-section">
        <!-- 搜索框 -->
        <div class="cassette-search-box">
          <input
            v-model="searchQuery"
            placeholder="[SEARCH_PROTOCOL]"
            class="cassette-search-input"
            @keyup.enter="handleSearch"
            @input="handleSearchInput"
          />
          <span class="search-icon">🔍</span>

          <!-- 搜索建议 -->
          <div
            v-if="searchSuggestions.length > 0"
            class="cassette-search-suggestions"
          >
            <div
              v-for="suggestion in searchSuggestions"
              :key="suggestion.id"
              class="cassette-suggestion-item"
              @click="handleSuggestionClick(suggestion)"
            >
              <span class="suggestion-icon">
                {{ suggestion.type === "post" ? "📄" : "🏷" }}
              </span>
              <span class="suggestion-text">{{ suggestion.text }}</span>
            </div>
          </div>
        </div>

        <!-- 写文章按钮 -->
        <button
          v-if="
            authStore.isAuthenticated && authStore.hasPermission('create_posts')
          "
          class="cassette-btn tech"
          @click="$router.push('/write')"
        >
          <span class="icon">✎</span>
          NEW LOG
        </button>

        <!-- 用户菜单 -->
        <div v-if="authStore.isAuthenticated" class="cassette-user-menu">
          <!-- 通知 -->
          <div
            class="cassette-notification-badge"
            @click="$router.push('/notifications')"
          >
            <span class="notification-icon">🔔</span>
            <span
              v-if="notificationStore.unreadCount > 0"
              class="notification-count"
            >
              {{ notificationStore.unreadCount }}
            </span>
          </div>
        </div>

        <!-- 登录/注册按钮 -->
        <div v-else class="cassette-auth-buttons">
          <button class="cassette-btn" @click="$router.push('/login')">
            <span class="icon">🔓</span>
            LOGIN
          </button>
          <button class="cassette-btn tech" @click="$router.push('/register')">
            <span class="icon">➕</span>
            REGISTER
          </button>
        </div>
      </div>

      <!-- 移动端菜单按钮 -->
      <div class="cassette-mobile-menu-btn">
        <button
          class="cassette-btn"
          @click="mobileMenuVisible = !mobileMenuVisible"
        >
          <span class="icon">{{ mobileMenuVisible ? "✕" : "☰" }}</span>
        </button>
      </div>
    </div>

    <!-- 移动端菜单 -->
    <div v-if="mobileMenuVisible" class="cassette-mobile-menu">
      <div class="mobile-nav-directory">
        <div class="nav-item-wrapper" @click="handleMobileMenuSelect('home')">
          <div class="echo-btn" :class="{ active: activeIndex === 'home' }">
            <span class="icon">⌂</span>
            HOME
          </div>
        </div>
        <div class="nav-item-wrapper" @click="handleMobileMenuSelect('posts')">
          <div class="echo-btn" :class="{ active: activeIndex === 'posts' }">
            <span class="icon">✎</span>
            ARCHIVES
          </div>
        </div>
        <div class="nav-item-wrapper" @click="handleMobileMenuSelect('tags')">
          <div class="echo-btn" :class="{ active: activeIndex === 'tags' }">
            <span class="icon">🏷</span>
            TAGS
          </div>
        </div>
        <div
          class="nav-item-wrapper"
          @click="handleMobileMenuSelect('categories')"
        >
          <div
            class="echo-btn"
            :class="{ active: activeIndex === 'categories' }"
          >
            <span class="icon">⚏</span>
            CATEGORIES
          </div>
        </div>
        <div class="nav-item-wrapper" @click="handleMobileMenuSelect('about')">
          <div class="echo-btn" :class="{ active: activeIndex === 'about' }">
            <span class="icon">ℹ</span>
            ABOUT
          </div>
        </div>
        <div
          v-if="authStore.isAuthenticated"
          class="nav-item-wrapper"
          @click="handleMobileMenuSelect('write')"
        >
          <div class="echo-btn">
            <span class="icon">✎</span>
            NEW LOG
          </div>
        </div>
      </div>
    </div>
  </el-header>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Edit,
  Search,
  EditPen,
  Bell,
  User,
  Setting,
  SwitchButton,
  ArrowDown,
  Menu,
  Close,
  Document,
  CollectionTag,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notification";
import { usePostsStore } from "@/stores/posts";
import { debounce } from "lodash-es";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const postsStore = usePostsStore();

// 状态
const searchQuery = ref("");
const searchSuggestions = ref([]);
const mobileMenuVisible = ref(false);

// 计算属性
const activeIndex = computed(() => {
  const path = route.path;
  if (path === "/") return "home";
  if (path.startsWith("/posts")) return "posts";
  if (path.startsWith("/archives")) return "archives";
  if (path.startsWith("/tags")) return "tags";
  if (path.startsWith("/categories")) return "categories";
  if (path.startsWith("/about")) return "about";
  return "home";
});

// 处理方法
const handleMenuSelect = (index) => {
  // 菜单选择处理
};

const handleMobileMenuSelect = (index) => {
  mobileMenuVisible.value = false;
};

const handleSearch = () => {
  if (!searchQuery.value.trim()) return;

  router.push({
    path: "/search",
    query: { q: searchQuery.value.trim() },
  });

  searchSuggestions.value = [];
};

const handleSearchInput = debounce(async () => {
  const query = searchQuery.value.trim();
  if (!query || query.length < 2) {
    searchSuggestions.value = [];
    return;
  }

  try {
    const suggestions = await postsStore.getSearchSuggestions(query);
    searchSuggestions.value = suggestions;
  } catch (error) {
    console.error("Search suggestions error:", error);
    searchSuggestions.value = [];
  }
}, 300);

const handleSuggestionClick = (suggestion) => {
  searchQuery.value = "";
  searchSuggestions.value = [];

  if (suggestion.type === "post") {
    router.push(`/post/${suggestion.id}`);
  } else if (suggestion.type === "tag") {
    router.push(`/tags/${suggestion.slug}`);
  }
};

const handleUserCommand = async (command) => {
  switch (command) {
    case "profile":
      router.push("/profile");
      break;
    case "admin":
      // 跳转到后台管理
      window.open("/admin", "_blank");
      break;
    case "logout":
      try {
        await authStore.logout();
      } catch (error) {
        console.error("Logout error:", error);
      }
      break;
  }
};

// 点击外部关闭搜索建议
const handleClickOutside = (event) => {
  const searchBox = event.target.closest(".search-box");
  if (!searchBox) {
    searchSuggestions.value = [];
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);

  // 初始化通知
  if (authStore.isAuthenticated) {
    notificationStore.fetchNotifications({ unread_only: true });
  }
});
</script>

<style scoped>
.cassette-header {
  background: #fff9ed;
  border-bottom: 2px solid #2c2c2c;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 70px;
  margin: 0;
  box-shadow: 0 2px 0 #e67e22;
}

.cassette-header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 70px; /* 与header高度一致 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo部分 */
.cassette-logo-section {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cassette-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2c2c2c;
  text-decoration: none;
  transition: color 0.2s ease;
}

.cassette-wheel {
  width: 32px;
  height: 32px;
  background: #e67e22;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.2s ease;
}

.cassette-logo:hover .cassette-wheel {
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.cassette-logo-text {
  font-size: 18px;
  font-weight: 900;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 导航菜单 */
.cassette-nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-directory {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-item-wrapper {
  cursor: pointer;
}

.echo-btn {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 10px 18px;
  font-size: 13px;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Courier New", monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
}

.echo-btn:hover {
  background: #e67e22;
  color: white;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.echo-btn.active {
  background: #e67e22;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
  font-weight: 600;
}

.echo-btn .icon {
  font-size: 14px;
}

/* 用户操作区 */
.cassette-user-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 搜索框 */
.cassette-search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.cassette-search-input {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  border-radius: 0;
  padding: 10px 40px 10px 20px;
  font-size: 13px;
  color: #2c2c2c;
  width: 180px;
  transition: all 0.2s ease;
  outline: none;
  font-family: "Courier New", monospace;
  margin: 0;
}

.cassette-search-input:focus {
  border-color: #e67e22;
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
  width: 220px;
}

.cassette-search-input::placeholder {
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: "Courier New", monospace;
}

.search-icon {
  position: absolute;
  right: 15px;
  color: #2c2c2c;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s ease;
}

.search-icon:hover {
  color: #e67e22;
}

/* 搜索建议 */
.cassette-search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  margin-top: 5px;
  z-index: 1002;
  max-height: 200px;
  overflow-y: auto;
}

.cassette-suggestion-item {
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Courier New", monospace;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.cassette-suggestion-item:last-child {
  border-bottom: none;
}

.cassette-suggestion-item:hover {
  background: #fff9ed;
  color: #e67e22;
}

.suggestion-icon {
  font-size: 14px;
}

.suggestion-text {
  font-size: 13px;
  color: #2c2c2c;
}

/* 按钮样式 */
.cassette-btn {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  border-radius: 0;
  padding: 10px 16px;
  font-size: 13px;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Courier New", monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
}

.cassette-btn:hover {
  background: #f8f8f8;
  border-color: #e67e22;
  color: #e67e22;
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.cassette-btn.tech {
  background: #e67e22;
  border-color: #2c2c2c;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.cassette-btn.tech:hover {
  background: #d35400;
  border-color: #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.cassette-btn.danger {
  background: #e74c3c;
  border-color: #2c2c2c;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.cassette-btn.danger:hover {
  background: #c0392b;
  border-color: #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.cassette-btn.warning {
  background: #f39c12;
  border-color: #2c2c2c;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.cassette-btn.warning:hover {
  background: #e67e22;
  border-color: #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

/* 用户菜单 */
.cassette-user-menu {
  display: flex;
  align-items: center;
  gap: 15px;
}

.cassette-notification-badge {
  position: relative;
  cursor: pointer;
  padding: 8px;
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  transition: all 0.2s ease;
}

.cassette-notification-badge:hover {
  background: #fff9ed;
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.notification-icon {
  font-size: 18px;
  color: #2c2c2c;
}

.notification-count {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #e74c3c;
  color: white;
  border: 2px solid #2c2c2c;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: bold;
  min-width: 16px;
  text-align: center;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.cassette-user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cassette-auth-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 移动端菜单 */
.cassette-mobile-menu-btn {
  display: none;
}

.cassette-mobile-menu {
  display: none;
}

@media (max-width: 768px) {
  .cassette-header-container {
    padding: 0 16px;
  }

  .cassette-nav-menu {
    display: none;
  }

  .cassette-user-section {
    display: none;
  }

  .cassette-mobile-menu-btn {
    display: block;
  }

  .cassette-mobile-menu {
    display: block;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff9ed;
    border: 2px solid #2c2c2c;
    box-shadow: 3px 3px 0 #e67e22;
    z-index: 1001;
  }

  .mobile-nav-directory {
    display: flex;
    flex-direction: column;
    padding: 16px;
    gap: 8px;
  }

  .nav-item-wrapper {
    cursor: pointer;
  }

  .nav-item-wrapper .echo-btn {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
