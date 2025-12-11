<!-- PostDetail.vue -->
<template>
  <div class="cassette-post-terminal">
    <!-- CRT 屏幕特效层 -->
    <div class="crt-overlay">
      <div class="scanlines"></div>
      <div class="noise"></div>
    </div>

    <div v-if="post" class="post-file">
      <!-- 文章头部 -->
      <header class="file-header">
        <div class="breadcrumb-trail">
          <button class="echo-btn" @click="$router.push('/')">
            <span class="icon">🏠</span>
            HOME
          </button>
          <span class="separator">→</span>
          <button class="echo-btn" @click="$router.push('/posts')">
            <span class="icon">📁</span>
            ARCHIVES
          </button>
          <span class="separator">→</span>
          <span class="current-file">{{ post.title }}</span>
        </div>

        <h1 class="file-title">{{ post.title }}</h1>

        <div class="file-meta">
          <div class="meta-left">
            <div class="author-badge">
              <div class="avatar-placeholder">
                {{ post.author.nickname?.[0] || post.author.username[0] }}
              </div>
            </div>
            <div class="author-info">
              <router-link
                :to="`/users/${post.author.username}`"
                class="author-name"
              >
                {{ post.author.nickname || post.author.username }}
              </router-link>
              <div class="file-timestamp">
                <span class="icon">📅</span>
                <span>{{
                  formatDate(post.published_at || post.created_at)
                }}</span>
                <span class="separator">|</span>
                <span class="icon">👁</span>
                <span>{{ post.view_count }} VIEWS</span>
              </div>
            </div>
          </div>

          <div class="meta-right">
            <button
              v-for="tag in post.tags"
              :key="tag.id"
              class="tag-badge"
              @click="$router.push(`/tags/${tag.slug}`)"
            >
              #{{ tag.name }}
            </button>
          </div>
        </div>
      </header>

      <!-- 文章内容 -->
      <main class="file-content">
        <div class="content-wrapper">
          <!-- 文章摘要 -->
          <div v-if="post.summary" class="file-summary">
            <div class="summary-header">ABSTRACT</div>
            <div class="summary-content">{{ post.summary }}</div>
          </div>

          <!-- 正文 -->
          <article
            class="file-text article-content"
            v-html="postContentHtml"
          ></article>

          <!-- 分类 -->
          <div v-if="post.categories.length" class="file-categories">
            <span class="icon">📂</span>
            <button
              v-for="cat in post.categories"
              :key="cat.id"
              class="category-link"
              @click="$router.push(`/categories/${cat.slug}`)"
            >
              {{ cat.name }}
            </button>
          </div>

          <!-- 版权声明 -->
          <div class="file-license">
            <div class="license-header">LICENSE</div>
            <div class="license-content">
              CONTENT PROTECTED UNDER
              <a
                href="https://creativecommons.org/licenses/by-nc-sa/4.0/"
                target="_blank"
                class="license-link"
              >
                CC BY-NC-SA 4.0
              </a>
              PROTOCOL
            </div>
          </div>
        </div>
      </main>

      <!-- 互动栏 -->
      <section class="file-actions">
        <div class="action-console">
          <button
            class="action-btn"
            :class="{ active: post.liked }"
            @click="toggleLike"
          >
            <span class="icon">👍</span>
            <span class="action-label">LIKE</span>
            <span class="action-count">{{ post.like_count }}</span>
          </button>

          <button
            class="action-btn"
            :class="{ active: post.favorited }"
            @click="toggleFavorite"
          >
            <span class="icon">⭐</span>
            <span class="action-label">FAVORITE</span>
            <span class="action-count">{{ post.favorite_count }}</span>
          </button>

          <button class="action-btn" @click="copyLink">
            <span class="icon">🔗</span>
            <span class="action-label">SHARE</span>
          </button>

          <div class="more-actions">
            <button class="action-btn" @click="showMoreMenu = !showMoreMenu">
              <span class="icon">⚙</span>
              <span class="action-label">MORE</span>
            </button>
            <div v-if="showMoreMenu" class="action-menu">
              <button class="menu-item" @click="handleMoreAction('report')">
                <span class="icon">🚨</span>
                REPORT
              </button>
              <button
                v-if="canEdit"
                class="menu-item"
                @click="handleMoreAction('edit')"
              >
                <span class="icon">✎</span>
                EDIT
              </button>
              <button
                v-if="canEdit"
                class="menu-item danger"
                @click="handleMoreAction('delete')"
              >
                <span class="icon">🗑</span>
                DELETE
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 评论区 -->
      <section v-if="post && post.allow_comments" class="file-comments">
        <div class="comments-console">
          <h3 class="comments-header">TERMINAL LOGS</h3>
          <CommentList
            v-model:comment-count="post.comment_count"
            :post-id="post.id"
            @posted="post.comment_count += 1"
          />
        </div>
      </section>
    </div>

    <!-- 404 / 无权限 -->
    <div v-else-if="!loading" class="error-terminal">
      <div class="error-console">
        <div class="error-icon">⚠</div>
        <div class="error-title">FILE NOT FOUND OR ACCESS DENIED</div>
        <div class="error-message">CHECK LINK VALIDITY OR LOGIN STATUS</div>
        <button class="cassette-btn" @click="$router.push('/posts')">
          <span class="icon">📁</span>
          RETURN TO ARCHIVES
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { marked } from "marked";
import hljs from "highlight.js";
import CommentList from "@/components/posts/CommentList.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const postStore = usePostsStore();

const loading = ref(true);
const post = ref(null);
const showMoreMenu = ref(false);

const canEdit = computed(
  () =>
    authStore.isAuthenticated &&
    post.value &&
    (post.value.author.id === authStore.user.id || authStore.user.is_admin),
);

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
});

const renderMarkdown = (raw) => marked.parse(raw || "");
const postContentHtml = computed(
  () => post.value?.content_html || renderMarkdown(post.value?.content || ""),
);

const formatDate = (iso) => {
  const date = new Date(iso);
  return date.toLocaleString("zh-CN");
};

const fetchPost = async () => {
  loading.value = true;
  try {
    const res = await fetch(`/api/posts/${route.params.id}`, {
      headers: authStore.token
        ? { Authorization: `Bearer ${authStore.token}` }
        : {},
    });
    if (!res.ok) throw new Error("fetch error");
    const data = await res.json();
    post.value = data.post;
  } catch (e) {
    post.value = null;
  } finally {
    loading.value = false;
  }
};

const toggleLike = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning("LOGIN REQUIRED");
    return;
  }
  await postStore.toggleLike(post.value.id);
  post.value.liked = !post.value.liked;
  post.value.like_count += post.value.liked ? 1 : -1;
};

const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning("LOGIN REQUIRED");
    return;
  }
  await postStore.toggleFavorite(post.value.id);
  post.value.favorited = !post.value.favorited;
  post.value.favorite_count += post.value.favorited ? 1 : -1;
};

const copyLink = () => {
  navigator.clipboard.writeText(location.href);
  ElMessage.success("LINK COPIED TO CLIPBOARD");
};

const handleMoreAction = (cmd) => {
  showMoreMenu.value = false;
  switch (cmd) {
    case "edit":
      router.push(`/write?id=${post.value.id}`);
      break;
    case "delete":
      ElMessageBox.confirm("CONFIRM FILE DELETION?", "SYSTEM WARNING", {
        type: "warning",
      })
        .then(async () => {
          await postStore.deletePost(post.value.id);
          ElMessage.success("FILE DELETED");
          router.replace("/posts");
        })
        .catch(() => {});
      break;
    case "report":
      ElMessage.info("REPORT FUNCTION UNDER DEVELOPMENT");
      break;
  }
};

onMounted(() => {
  fetchPost();
});
</script>

<style scoped>
.cassette-post-terminal {
  position: relative;
  min-height: 100vh;
  background-color: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  overflow: hidden;
}

/* CRT 屏幕特效 */
.crt-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(21, 21, 21, 0.1) 0px,
    rgba(21, 21, 21, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  animation: scanlines 8s linear infinite;
}

.noise {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  animation: noise 0.5s steps(10) infinite;
}

@keyframes scanlines {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(10px);
  }
}

@keyframes noise {
  0%,
  100% {
    transform: translate(0, 0);
  }
  10% {
    transform: translate(-5%, -5%);
  }
  20% {
    transform: translate(-10%, 5%);
  }
  30% {
    transform: translate(5%, -10%);
  }
  40% {
    transform: translate(-5%, 15%);
  }
  50% {
    transform: translate(-10%, 5%);
  }
  60% {
    transform: translate(15%, 0);
  }
  70% {
    transform: translate(0, 10%);
  }
  80% {
    transform: translate(-15%, 0);
  }
  90% {
    transform: translate(10%, 5%);
  }
}

.post-file {
  position: relative;
  z-index: 2;
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 20px;
}

.file-header {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 30px;
  margin-bottom: 30px;
}

.breadcrumb-trail {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.separator {
  color: var(--color-dark-black);
  font-weight: 900;
  font-size: 18px;
}

.current-file {
  font-weight: 600;
  color: var(--color-dark-black);
  opacity: 0.8;
}

.file-title {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--color-dark-black);
  text-shadow: 4px 4px 0 var(--color-warning-orange);
  margin: 0 0 20px 0;
  line-height: 1.2;
  letter-spacing: 1px;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.author-badge {
  width: 50px;
  height: 50px;
  border: 3px solid var(--color-dark-black);
  background: var(--color-eggshell);
  box-shadow: 2px 2px 0 var(--color-dark-black);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-placeholder {
  font-size: 24px;
  font-weight: 900;
  color: var(--color-dark-black);
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.author-name {
  font-weight: 900;
  color: var(--color-dark-black);
  text-decoration: none;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.author-name:hover {
  color: var(--color-warning-orange);
}

.file-timestamp {
  font-size: 14px;
  color: var(--color-dark-black);
  opacity: 0.7;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Courier New", monospace;
}

.meta-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-badge {
  padding: 6px 12px;
  border: 2px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
}

.tag-badge:hover {
  background: var(--color-warning-orange);
  transform: translate(-1px, -1px);
  box-shadow: 2px 2px 0 var(--color-dark-black);
}

.file-content {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 30px;
  margin-bottom: 30px;
}

.content-wrapper {
  max-width: 100%;
}

.file-summary {
  margin-bottom: 30px;
  padding: 20px;
  border: 2px dashed var(--color-dark-black);
  background: rgba(21, 21, 21, 0.05);
}

.summary-header {
  font-size: 18px;
  font-weight: 900;
  color: var(--color-dark-black);
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.summary-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-dark-black);
  opacity: 0.9;
}

.file-text {
  font-size: 16px;
  line-height: 1.8;
  color: var(--color-dark-black);
}

.file-categories {
  margin-top: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--color-dark-black);
  opacity: 0.8;
}

.category-link {
  padding: 6px 12px;
  border: 2px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
}

.category-link:hover {
  background: var(--color-warning-orange);
  transform: translate(-1px, -1px);
  box-shadow: 2px 2px 0 var(--color-dark-black);
}

.file-license {
  margin-top: 30px;
  padding: 20px;
  border: 2px solid var(--color-dark-black);
  background: rgba(255, 107, 0, 0.1);
}

.license-header {
  font-size: 18px;
  font-weight: 900;
  color: var(--color-dark-black);
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.license-content {
  font-size: 14px;
  color: var(--color-dark-black);
  opacity: 0.9;
  font-family: "Courier New", monospace;
}

.license-link {
  color: var(--color-warning-orange);
  text-decoration: none;
  font-weight: 600;
}

.license-link:hover {
  text-decoration: underline;
}

.file-actions {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 20px;
  margin-bottom: 30px;
  position: sticky;
  bottom: 20px;
  z-index: 10;
}

.action-console {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 3px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow: 2px 2px 0 var(--color-dark-black);
}

.action-btn:hover {
  box-shadow: 4px 4px 0 var(--color-dark-black);
  transform: translate(-2px, -2px);
}

.action-btn.active {
  background: var(--color-warning-orange);
  box-shadow: 2px 2px 0 var(--color-dark-black);
}

.action-btn.active:hover {
  box-shadow: 4px 4px 0 var(--color-dark-black);
}

.action-label {
  font-weight: 900;
  letter-spacing: 0.5px;
}

.action-count {
  font-size: 14px;
  font-weight: 900;
  color: var(--color-dark-black);
  margin-left: 5px;
}

.more-actions {
  position: relative;
}

.action-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  z-index: 100;
  min-width: 200px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
}

.menu-item:hover {
  background: var(--color-warning-orange);
}

.menu-item.danger {
  color: #dc3545;
}

.menu-item.danger:hover {
  background: #dc3545;
  color: white;
}

.file-comments {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 30px;
}

.comments-header {
  font-size: 24px;
  font-weight: 900;
  color: var(--color-dark-black);
  margin: 0 0 20px 0;
  text-shadow: 3px 3px 0 var(--color-warning-orange);
  letter-spacing: 1px;
}

.error-terminal {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px 20px;
}

.error-console {
  background: var(--color-eggshell);
  border: 3px solid var(--color-dark-black);
  box-shadow: 4px 4px 0 var(--color-dark-black);
  padding: 40px;
  text-align: center;
  max-width: 500px;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: var(--color-dark-black);
}

.error-title {
  font-size: 24px;
  font-weight: 900;
  color: var(--color-dark-black);
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.error-message {
  font-size: 16px;
  color: var(--color-dark-black);
  opacity: 0.7;
  margin-bottom: 30px;
  font-family: "Courier New", monospace;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-file {
    padding: 20px 15px;
  }

  .file-header,
  .file-content,
  .file-actions,
  .file-comments {
    padding: 20px;
  }

  .file-title {
    font-size: 2rem;
  }

  .file-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .action-console {
    justify-content: center;
  }

  .breadcrumb-trail {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .file-title {
    font-size: 1.5rem;
  }

  .action-console {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .pagination-console {
    flex-direction: column;
    text-align: center;
  }
}
</style>
