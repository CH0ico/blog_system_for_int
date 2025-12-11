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
  background-color: #f5f0e6;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  overflow: hidden;
}

.post-file {
  position: relative;
  z-index: 2;
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 文件头部 */
.file-header {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
  margin-bottom: 30px;
  position: relative;
}

.file-header::before {
  content: "DOCUMENT FILE";
  position: absolute;
  top: -10px;
  left: 10px;
  background: #e67e22;
  color: white;
  padding: 5px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.breadcrumb-trail {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.separator {
  color: #2c2c2c;
  font-weight: 900;
  font-size: 16px;
}

.current-file {
  font-weight: 600;
  color: #2c2c2c;
  opacity: 0.8;
}

.echo-btn {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 8px 15px;
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: bold;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.echo-btn:hover {
  background: #e67e22;
  color: white;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.file-title {
  font-size: 2.5rem;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 20px 0;
  line-height: 1.2;
  letter-spacing: 2px;
  text-transform: uppercase;
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
  border: 2px solid #2c2c2c;
  background: white;
  box-shadow: 3px 3px 0 #e67e22;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 900;
  color: #2c2c2c;
}

.avatar-placeholder {
  font-size: 24px;
  font-weight: 900;
  color: #2c2c2c;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.author-name {
  font-weight: 900;
  color: #2c2c2c;
  text-decoration: none;
  font-size: 16px;
  letter-spacing: 0.5px;
  transition: color 0.2s;
}

.author-name:hover {
  color: #e67e22;
}

.file-timestamp {
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Courier New", monospace;
}

.meta-right {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tag-badge {
  padding: 6px 12px;
  border: 1px solid #2c2c2c;
  background: white;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.tag-badge:hover {
  background: #e67e22;
  color: white;
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0 #2c2c2c;
}

/* 文件内容 */
.file-content {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
  margin-bottom: 30px;
  position: relative;
}

.file-content::before {
  content: "CONTENT BODY";
  position: absolute;
  top: -10px;
  left: 10px;
  background: #e67e22;
  color: white;
  padding: 5px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.content-wrapper {
  max-width: 100%;
}

.file-summary {
  margin-bottom: 30px;
  padding: 20px;
  border: 2px dashed #2c2c2c;
  background: rgba(230, 126, 34, 0.05);
}

.summary-header {
  font-size: 16px;
  font-weight: 900;
  color: #e67e22;
  margin-bottom: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.summary-content {
  font-size: 14px;
  line-height: 1.6;
  color: #2c2c2c;
  opacity: 0.9;
}

.file-text {
  font-size: 16px;
  line-height: 1.8;
  color: #2c2c2c;
}

/* 文章内容样式 */
.file-text h1,
.file-text h2,
.file-text h3,
.file-text h4,
.file-text h5,
.file-text h6 {
  color: #2c2c2c;
  margin-top: 30px;
  margin-bottom: 15px;
  font-weight: 900;
  line-height: 1.3;
}

.file-text h1 {
  font-size: 24px;
  border-bottom: 2px solid #e67e22;
  padding-bottom: 10px;
}

.file-text h2 {
  font-size: 20px;
}

.file-text h3 {
  font-size: 18px;
  color: #e67e22;
}

.file-text p {
  margin-bottom: 15px;
  text-align: justify;
}

.file-text ul,
.file-text ol {
  margin-bottom: 15px;
  padding-left: 25px;
}

.file-text li {
  margin-bottom: 8px;
}

.file-text a {
  color: #e67e22;
  text-decoration: none;
  border-bottom: 1px dashed #e67e22;
  transition: all 0.2s;
}

.file-text a:hover {
  background: #e67e22;
  color: white;
  padding: 2px 5px;
  border-bottom: none;
}

.file-text code {
  background: #fff;
  border: 1px solid #2c2c2c;
  padding: 2px 5px;
  font-family: "Courier New", monospace;
  font-size: 14px;
  color: #e67e22;
}

.file-text pre {
  background: #fff;
  border: 2px solid #2c2c2c;
  padding: 20px;
  margin-bottom: 15px;
  overflow-x: auto;
  box-shadow: 2px 2px 0 #e67e22;
}

.file-text pre code {
  background: none;
  border: none;
  padding: 0;
  color: #2c2c2c;
}

.file-categories {
  margin-top: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.8;
}

.category-link {
  padding: 6px 12px;
  border: 1px solid #2c2c2c;
  background: white;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.category-link:hover {
  background: #e67e22;
  color: white;
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0 #2c2c2c;
}

.file-license {
  margin-top: 30px;
  padding: 20px;
  border: 2px solid #2c2c2c;
  background: rgba(230, 126, 34, 0.1);
}

.license-header {
  font-size: 16px;
  font-weight: 900;
  color: #e67e22;
  margin-bottom: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.license-content {
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.9;
  font-family: "Courier New", monospace;
}

.license-link {
  color: #e67e22;
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dashed #e67e22;
}

.license-link:hover {
  text-decoration: none;
  background: #e67e22;
  color: white;
  padding: 2px 5px;
  border-bottom: none;
}

/* 文件操作 */
.file-actions {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
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
  padding: 10px 18px;
  border: 2px solid #2c2c2c;
  background: white;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow: 2px 2px 0 #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.action-btn:hover {
  background: #e67e22;
  color: white;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.action-btn.active {
  background: #e67e22;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.action-btn.active:hover {
  box-shadow: 3px 3px 0 #2c2c2c;
}

.action-label {
  font-weight: 900;
  letter-spacing: 0.5px;
}

.action-count {
  font-size: 12px;
  font-weight: 900;
  color: #2c2c2c;
  margin-left: 5px;
}

.action-btn.active .action-count {
  color: white;
}

.more-actions {
  position: relative;
}

.action-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
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
  background: #fff9ed;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.menu-item:hover {
  background: #e67e22;
  color: white;
}

.menu-item.danger {
  color: #c0392b;
}

.menu-item.danger:hover {
  background: #c0392b;
  color: white;
}

/* 评论区 */
.file-comments {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
  position: relative;
}

.file-comments::before {
  content: "TERMINAL LOGS";
  position: absolute;
  top: -10px;
  left: 10px;
  background: #e67e22;
  color: white;
  padding: 5px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.comments-header {
  font-size: 20px;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 20px 0;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 错误页面 */
.error-terminal {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px 20px;
}

.error-console {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 40px;
  text-align: center;
  max-width: 500px;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #e67e22;
}

.error-title {
  font-size: 24px;
  font-weight: 900;
  color: #2c2c2c;
  margin-bottom: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.error-message {
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.7;
  margin-bottom: 30px;
  font-family: "Courier New", monospace;
}

.cassette-btn {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 10px 20px;
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: bold;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cassette-btn:hover {
  background: #e67e22;
  color: white;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
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
}
</style>
